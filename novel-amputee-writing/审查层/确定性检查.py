# -*- coding: utf-8 -*-
"""确定性检查执行器。

读取 审查层/确定性检查清单.md 的规则表，逐条扫描正文文件并列出命中行。
用法：python 审查层/确定性检查.py <正文文件> [更多文件]
退出码：0 无「高」级命中；1 存在「高」级命中；2 用法错误。
本脚本只读，不改写任何文件。
"""
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RULES_FILE = Path(__file__).resolve().parent / "确定性检查清单.md"
ROW = re.compile(r"^\|\s*L\d+\s*\|")
SPLIT = re.compile(r"(?<!\\)\|")


def load_rules():
    rules = []
    for line in RULES_FILE.read_text(encoding="utf-8").splitlines():
        if not ROW.match(line):
            continue
        cells = [c.strip() for c in SPLIT.split(line.strip())[1:-1]]
        if len(cells) < 5:
            continue
        rid, name, sev, pat = cells[0], cells[1], cells[2], cells[3].replace("\\|", "|")
        rules.append((rid, name, sev, re.compile(pat)))
    return rules


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


def main():
    if len(sys.argv) < 2:
        print("用法：python 审查层/确定性检查.py <正文文件> [更多文件]")
        return 2
    rules = load_rules()
    high = 0
    for arg in sys.argv[1:]:
        high += scan(Path(arg), rules)
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
