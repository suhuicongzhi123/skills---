#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""体量闸（方案 B：维护协议硬化）

用法:
  python scripts/size_gate.py             # 只检查，不改配置
  python scripts/size_gate.py --record   # 检查通过后把本次数据登记为基线
  python scripts/size_gate.py --json     # 结构化输出

检查项:
  [SG-1] 全库文本字符数 <= max_total_chars
  [SG-2] SKILL.md 字符数 <= max_skill_md_chars
  [SG-3] 净增闸：相对上次登记的字符增量 > allowed_delta_chars 时，必须在
         scripts/size_gate.json 显式登记 change_kind="feature" 且 change_note 非空；
         fix / 空理由一律 FAIL（对应 MAINTENANCE.md 五「纠错类改动只减不增」）。
         连续两次 feature 净增也 FAIL（对应「连续两版无新功能却净增＝先精简再继续」）。
  [SG-4] 规则编号计数（R-xxx / Sxx / Gxx / E-xxx）输出，供编号退役人工裁决。

强制力来自退出码，不来自文档约定；本脚本已由 verify.py 纳入统一校验。
配置自身不计入总量，避免自指。
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "scripts", "size_gate.json")
EXT = (".md", ".yaml", ".py", ".json", ".txt")
ID_PATTERNS = {
    "R": r"R-\d{3}",
    "S": r"S\d{2}",
    "G": r"G\d{2}",
    "E": r"E-\d{3}",
}


def load_cfg():
    if not os.path.isfile(CFG):
        print("FAIL 缺配置 scripts/size_gate.json")
        sys.exit(2)
    with open(CFG, encoding="utf-8") as f:
        return json.load(f)


def scan():
    total = 0
    texts = []
    for d, _, names in os.walk(ROOT):
        for n in names:
            if not n.endswith(EXT):
                continue
            p = os.path.join(d, n)
            if os.path.abspath(p) == os.path.abspath(CFG):
                continue
            try:
                with open(p, encoding="utf-8", errors="ignore") as f:
                    s = f.read()
            except OSError:
                continue
            total += len(s)
            texts.append(s)
    with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8", errors="ignore") as f:
        skill_len = len(f.read())
    alltext = "\n".join(texts)
    counts = {k: len(set(re.findall(p, alltext))) for k, p in ID_PATTERNS.items()}
    return total, skill_len, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    cfg = load_cfg()
    total, skill_len, counts = scan()
    errors = []
    lines = []

    max_total = int(cfg.get("max_total_chars", 0))
    max_skill = int(cfg.get("max_skill_md_chars", 0))
    allowed = int(cfg.get("allowed_delta_chars", 0))
    last = int(cfg.get("last_total_chars", 0))
    initialized = bool(cfg.get("initialized", False))
    delta = total - last if initialized else 0
    growth = int(cfg.get("consecutive_growth", 0))

    ok1 = total <= max_total
    lines.append("[SG-1] 全库 %d / %d 字符  %s" % (total, max_total, "OK" if ok1 else "FAIL"))
    if not ok1:
        errors.append("[SG-1] 全库体量超限 %d 字符" % (total - max_total))

    ok2 = skill_len <= max_skill
    lines.append("[SG-2] SKILL.md %d / %d 字符  %s" % (skill_len, max_skill, "OK" if ok2 else "FAIL"))
    if not ok2:
        errors.append("[SG-2] SKILL.md 超限 %d 字符" % (skill_len - max_skill))

    if not initialized:
        lines.append("[SG-3] 基线未初始化，本次仅检查 SG-1/SG-2；完成改造后跑 --record")
    elif delta > allowed:
        kind = str(cfg.get("change_kind", "")).strip()
        note = str(cfg.get("change_note", "")).strip()
        if kind != "feature" or not note:
            errors.append(
                "[SG-3] 净增 +%d 字符（阈值 %d）未登记功能理由："
                "须在 size_gate.json 设 change_kind=feature 且 change_note 非空；"
                "纠错类改动只减不增" % (delta, allowed)
            )
            lines.append("[SG-3] 净增 +%d 未登记理由  FAIL" % delta)
        elif growth + 1 >= 2:
            errors.append("[SG-3] 连续两版净增，按 MAINTENANCE.md 五须先精简再继续")
            lines.append("[SG-3] 连续两版净增  FAIL")
        else:
            lines.append("[SG-3] 净增 +%d 已登记功能理由  OK（累计 %d/2）" % (delta, growth + 1))
    else:
        lines.append("[SG-3] 相对基线 %+d 字符  OK" % delta)

    prev = cfg.get("rule_id_counts") or {}
    diff = {k: counts[k] - int(prev.get(k, counts[k])) for k in counts}
    lines.append("[SG-4] 编号 %s（较上次 %s）" % (
        " ".join("%s=%d" % (k, counts[k]) for k in ID_PATTERNS),
        " ".join("%s%+d" % (k, diff[k]) for k in ID_PATTERNS),
    ))

    result = {
        "total_chars": total,
        "skill_md_chars": skill_len,
        "delta": delta,
        "initialized": initialized,
        "rule_id_counts": counts,
        "rule_id_delta": diff,
        "errors": errors,
        "pass": not errors,
    }

    if a.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== 体量闸 size_gate ===")
        for line in lines:
            print("    " + line)
        for e in errors:
            print("    " + e)
        print("    结果: %s" % ("PASS" if not errors else "FAIL"))

    if a.record and not errors:
        cfg["last_total_chars"] = total
        cfg["initialized"] = True
        cfg["consecutive_growth"] = growth + 1 if (initialized and delta > allowed) else 0
        cfg["rule_id_counts"] = counts
        cfg["change_kind"] = "fix"
        cfg["change_note"] = ""
        with open(CFG, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        if not a.as_json:
            print("    已登记基线：last_total_chars=%d，change_kind 重置为 fix" % total)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
