#!/usr/bin/env python3
"""体积与格式闸门（维护期工具，不进创作注入链）。

用法（在库根目录运行）：
    python 维护/size_gate.py            # 检查
    python 维护/size_gate.py --quiet    # 只输出结论行

检查项（阈值单一事实源 = 维护/size_gate.json）：
  [SG-1] SKILL.md 体积上限
  [SG-2] 分目录单文件体积上限
  [SG-3] 全库合计体积上限（不含 维护/）
  [SG-4] 编码与换行：UTF-8 无 BOM、无 CRLF
  [SG-5] 超 100 行的文件须有目录块（前 10 行内含「目录」）

退出码：0 = PASS，1 = FAIL。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "size_gate.json"

UTF8 = "utf-8"


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def check():
    cfg = load_config()
    failures = []
    rows = []

    skill_md = ROOT / "SKILL.md"
    if skill_md.exists():
        size = skill_md.stat().st_size
        rows.append(("SKILL.md", size, cfg["skill_md_max"]))
        if size > cfg["skill_md_max"]:
            failures.append(f"[SG-1] SKILL.md 超限: {size} > {cfg['skill_md_max']} 字节")

    total = 0
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name != "维护"):
        cap = cfg["dir_caps"].get(d.name, cfg["default_file_max"])
        for f in sorted(d.rglob("*")):
            if not f.is_file():
                continue
            size = f.stat().st_size
            rel = f.relative_to(ROOT).as_posix()
            if f.suffix == ".md":
                total += size
                cap_here = cap
                top = f.parent.name if f.parent != d else ""
                if top in cfg["dir_caps"]:
                    cap_here = min(cap_here, cfg["dir_caps"][top])
                rows.append((rel, size, cap_here))
                if size > cap_here:
                    failures.append(f"[SG-2] {rel} 超限: {size} > {cap_here} 字节")
                raw = f.read_bytes()
                if raw.startswith(b"\xef\xbb\xbf"):
                    failures.append(f"[SG-4] {rel} 带 BOM")
                elif b"\r\n" in raw:
                    failures.append(f"[SG-4] {rel} 含 CRLF 换行")
                else:
                    try:
                        text = raw.decode(UTF8)
                    except UnicodeDecodeError as e:
                        failures.append(f"[SG-4] {rel} 非 UTF-8: {e}")
                        text = ""
                    n_lines = text.count("\n") + 1
                    if n_lines > 100 and "目录" not in "\n".join(text.split("\n")[:12]):
                        failures.append(f"[SG-5] {rel} 超 100 行但缺目录块")
            else:
                total += size

    if total > cfg["total_max"]:
        failures.append(f"[SG-3] 全库合计超限: {total} > {cfg['total_max']} 字节")

    return rows, total, failures


def main():
    quiet = "--quiet" in sys.argv
    rows, total, failures = check()
    if not quiet:
        for rel, size, cap in rows:
            mark = "OK " if size <= cap else "OVER"
            print(f"{mark} {size:>7} / {cap:>7}  {rel}")
        print(f"---- 全库合计: {total} / {json.load(open(CONFIG, encoding='utf-8'))['total_max']}")
    if failures:
        for x in failures:
            print(f"FAIL {x}")
        print(f"结论: FAIL（{len(failures)} 项）")
        sys.exit(1)
    print("结论: PASS")


if __name__ == "__main__":
    main()
