# -*- coding: utf-8 -*-
"""确定性检查执行器。

读取 审查层/确定性检查清单.md：
- 规则表（L 编号）：逐条扫描正文并列出命中行。
- 跨章统计表（T 编号）：`--cross` 模式下统计招牌类别覆盖与复读片段。

用法：
  python 审查层/确定性检查.py <正文文件> [更多文件]      单文件规则检查
  python 审查层/确定性检查.py --cross <正文文件>...       跨章统计（按文件名顺序）
退出码：单文件模式 0 无「高」级命中，1 存在「高」级命中，2 用法错误；跨章模式恒为 0（只做预警）。
本脚本只读，不改写任何文件。
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RULES_FILE = Path(__file__).resolve().parent / "确定性检查清单.md"
ROW = re.compile(r"^\|\s*L\d+\s*\|")
CAT_ROW = re.compile(r"^\|\s*T\d+\s*\|")
SPLIT = re.compile(r"(?<!\\)\|")
WINDOW = 8
MIN_CATS = 4
SHINGLE = 12
REPEAT_FILES = 3
TOP_REPEATS = 10


def _cells(line):
    return [c.strip() for c in SPLIT.split(line.strip())[1:-1]]


def load_rules():
    rules = []
    for line in RULES_FILE.read_text(encoding="utf-8").splitlines():
        if not ROW.match(line):
            continue
        cells = _cells(line)
        if len(cells) < 5:
            continue
        rid, name, sev, pat = cells[0], cells[1], cells[2], cells[3].replace("\\|", "|")
        rules.append((rid, name, sev, re.compile(pat)))
    return rules


def load_categories():
    cats = []
    for line in RULES_FILE.read_text(encoding="utf-8").splitlines():
        if not CAT_ROW.match(line):
            continue
        cells = _cells(line)
        if len(cells) < 4:
            continue
        cid, name, pat = cells[0], cells[1], cells[2].replace("\\|", "|")
        cats.append((cid, name, re.compile(pat)))
    return cats


def scan(path, rules):
    lines = path.read_text(encoding="utf-8").splitlines()
    print(f"== {path}")
    counts = {"高": 0, "中": 0, "信息": 0}
    for rid, name, sev, rx in rules:
        hits = []
        for no, text in enumerate(lines, 1):
            for m in rx.finditer(text):
                hits.append((no, m.group(0), text.strip()[:60]))
        if not hits:
            continue
        counts[sev] = counts.get(sev, 0) + len(hits)
        if sev == "信息":
            print(f"  [信息] {rid} {name}：{len(hits)} 处（人工复核）")
            continue
        print(f"  [{sev}] {rid} {name}：{len(hits)} 处")
        for no, s, snippet in hits[:20]:
            print(f"      第 {no} 行「{s}」 ｜ {snippet}")
    print(f"  合计：高 {counts['高']}｜中 {counts['中']}｜信息 {counts['信息']}")
    return counts["高"]


def _plain(text):
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text)


def _overlap(a, b):
    for s in range(1, SHINGLE):
        if a[s:] == b[:SHINGLE - s] or b[s:] == a[:SHINGLE - s]:
            return True
    return False


def cross(paths, cats):
    paths = sorted(paths, key=lambda p: p.name)
    texts = [p.read_text(encoding="utf-8") for p in paths]
    names = [p.stem for p in paths]
    per_file = []
    for text in texts:
        hit = {}
        for cid, _, rx in cats:
            hit[cid] = len(rx.findall(text))
        per_file.append(hit)
    print(f"== 跨章统计：{len(paths)} 章")
    print("  单章类别密度（每千字命中数）：")
    for name, text, hit in zip(names, texts, per_file):
        kchars = max(len(_plain(text)) / 1000, 0.001)
        parts = " ".join(f"{cid}:{hit[cid] / kchars:.1f}" for cid, _, _ in cats)
        print(f"    {name}：{parts}")
    if len(paths) >= WINDOW:
        print(f"  {WINDOW} 章窗口覆盖（低于 {MIN_CATS} 类为看点面过窄）：")
        for start in range(len(paths) - WINDOW + 1):
            covered = {cid for cid, _, _ in cats
                       if any(per_file[i][cid] for i in range(start, start + WINDOW))}
            flag = "  ← 过窄" if len(covered) < MIN_CATS else ""
            print(f"    第 {start + 1}–{start + WINDOW} 章：{len(covered)} 类{flag}")
    else:
        covered = {cid for cid, _, _ in cats if any(h[cid] for h in per_file)}
        print(f"  全部章节覆盖：{len(covered)} 类（不足 {WINDOW} 章，窗口统计跳过）")
    seen = {}
    for name, text in zip(names, texts):
        plain = _plain(text)
        grams = {plain[i:i + SHINGLE] for i in range(len(plain) - SHINGLE + 1)}
        for g in grams:
            seen.setdefault(g, set()).add(name)
    repeats = [(g, sorted(fs)) for g, fs in seen.items() if len(fs) >= REPEAT_FILES]
    repeats.sort(key=lambda x: (-len(x[1]), x[0]))
    kept = []
    for g, fs in repeats:
        if any(_overlap(g, k) for k, _ in kept):
            continue
        kept.append((g, fs))
        if len(kept) >= TOP_REPEATS:
            break
    print(f"  跨 {REPEAT_FILES} 章以上重复的 {SHINGLE} 字片段（句式复读候选，相邻重叠已合并，取前 {TOP_REPEATS}）：")
    if not kept:
        print("    无")
    for g, fs in kept:
        print(f"    「{g}」 出现于 {len(fs)} 章：{', '.join(fs)}")
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        print("用法：python 审查层/确定性检查.py <正文文件> [更多文件]\n"
              "      python 审查层/确定性检查.py --cross <正文文件>...")
        return 2
    if args[0] == "--cross":
        paths = [Path(a) for a in args[1:]]
        if not paths:
            print("--cross 需要至少一个正文文件")
            return 2
        return cross(paths, load_categories())
    rules = load_rules()
    high = 0
    for arg in args:
        high += scan(Path(arg), rules)
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
