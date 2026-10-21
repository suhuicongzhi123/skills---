# -*- coding: utf-8 -*-
"""novel-amputee-writing 自检脚本

用法：python scripts/selfcheck.py（在技能目录内运行）
检查三项：
  [1] 注入锚点是否落空（改小节名 = 改锚点，最容易踩）
  [2] 类型必填节是否齐（独立类型 11 节 / 叠加层最小集 6 节）
  [3] 已废止表述是否复发（跨版本残留的主要来源）

退出码：0 通过 / 1 有问题
"""
import re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fail = 0

# ── [1] 锚点落空 ──────────────────────────────────────────
norm = lambda s: re.sub(r"[\s★、（）()：:/·\-]+", "", s)
bad = set()
for f in glob.glob("**/*", recursive=True):
    if not os.path.isfile(f) or not f.endswith((".md", ".yaml")):
        continue
    src = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r"`([A-Za-z0-9_\-/\.\{\}]+\.(?:md|yaml))(?:#([^`]+))?`", src):
        if not m.group(2) or m.group(2) == "X":     # 无锚点 / 占位符，跳过
            continue
        for tp in glob.glob(m.group(1).replace("{type}", "*").replace("{题材}", "*")):
            hs = [l.lstrip("#").strip() for l in open(tp, encoding="utf-8", errors="ignore") if l.startswith("#")]
            if not any(norm(m.group(2)) in norm(h) for h in hs):
                bad.add((tp, m.group(2)))
print(f"[1] 锚点落空: {len(bad)}")
for x in sorted(bad):
    print("     ", x)
fail += len(bad)

# ── [2] 必填节（两级闸门）──────────────────────────────────
FULL = ["形态", "运动能力", "体位与动态", "拐杖使用差异", "假肢使用差异",
        "日常动作差异", "身体细节", "幻肢感", "服装", "不可能动作", "受限清单"]
MINI = ["适用范围", "失效条目", "移动样态", "身体细节", "幻肢感", "受限清单"]
miss_total = 0
for p in sorted(glob.glob("types/*.md")):
    name = os.path.basename(p)[:-3]
    if name == "_template":
        continue
    need = MINI if name == "bilateral" else FULL     # 叠加层按最小集
    lines = open(p, encoding="utf-8").readlines()
    miss = [r for r in need if not any(l.startswith("#") and r in l for l in lines)]
    if miss:
        miss_total += 1
        print(f"[2] {name} 缺节: {miss}")
print(f"[2] 必填节缺失类型数: {miss_total}")
fail += miss_total

# ── [3] 已废止表述复发 ────────────────────────────────────
DEAD = [
    "蹲不下", "全蹲做不到", "单腿蹲极难",      # 4.7.0 蹲豁免后废止
    "走路时完全不晃",                          # 4.7.2 空管晃动口径后废止
    # 注：「空裤管飘荡」4.7.2 后**部分合法**（未处理时可写），故不入表，避免误报
    "可半蹲",                                  # 4.7.0 蹲分级废止（S-5 曾漏网）
    "章五要素",                                # 4.8.0 改章六要素
    "那一半椅面是空的",                        # 4.8.0 空椅面口径（N-1 曾漏网）
    "没有裤管", "没有袖管",                    # 4.8.2 禁否定式缺失描写（写了收口还声明缺失）
]
hits = {}          # (file, line) -> [命中的词]，同一行多词只报一次
for w in DEAD:
    for f in glob.glob("**/*.md", recursive=True):
        # CHANGELOG 记录的是"清理了什么"，必须保留原文，不参与创作注入 → 跳过
        if os.path.basename(f) == "CHANGELOG.md":
            continue
        for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            if w in l:
                hits.setdefault((f, i), []).append(w)
for (f, i), ws in sorted(hits.items()):
    l = open(f, encoding="utf-8", errors="ignore").read().split("\n")[i - 1]
    # 出现在禁令句/废止声明里多半合法 → 列出上下文让维护者判断，不静默放行
    banned = ("已废止" in l or "❌" in l or "不写" in l
              or "禁止" in l or "反例" in l or "追加" in l)
    flag = "［禁令句，人工确认］" if banned else "［疑似复发］"
    print(f"[3] 「{'/'.join(ws)}」{flag} {f}:{i}")
    print(f"      {l.strip()[:100]}")
    if not banned:
        fail += 1
print(f"[3] 废止表述: {len(hits)} 处（上方［］标记项请人工确认）")

print("\n结果:", "PASS" if fail == 0 else f"FAIL ({fail})")
sys.exit(0 if fail == 0 else 1)
