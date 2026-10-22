# -*- coding: utf-8 -*-
"""novel-amputee-writing 自检脚本

用法：python scripts/selfcheck.py（在技能目录内运行）
检查四项：
  [1]  注入锚点是否落空（改小节名 = 改锚点，最容易踩）
  [1b] 悬空引用（引用了不存在的文件）
  [2]  类型必填节是否齐（独立类型 11 节 / 叠加层最小集 6 节）
  [3]  已废止表述是否复发（跨版本残留的主要来源）
  [4]  孤儿文件（存在但全域零引用，防 equipment-risk 类残留复发）

v4.9.0 盲区修复（对照 v4.8.4 审查报告）：
  ① 引用正则支持中文占位符——`genre/{题材}.md#推荐开篇类型` 此前正则断裂，
     匹配到 `}.md` 后 glob 无结果被静默跳过，锚点从未真正受检
  ② glob 展开为空且非通配引用时报悬空引用（v4.8.4 的 timeline.md 孤儿引用
     即此类问题，当时靠人工通读才发现）
  ③ [3] 废止表述扫描范围扩展到 .yaml（crutch-spec / state-ledger 此前不受监控）
  ④ DEAD 词表补 v4.8.4 废止项（此前停在 v4.8.2）
  ⑤ 新增 [4] 孤儿文件检测
  ⑥ [1] 与 [3] 统一跳过 CHANGELOG（历史记录不参与创作注入判定）；
     banned 白名单移除语义漂移的「追加」

退出码：0 通过 / 1 有问题
"""
import re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fail = 0

# 运行时产物：包内不存在是正常的，不参与悬空/孤儿判定
RUNTIME = {"state-ledger-archive.yaml"}

# ── [1] 锚点落空 + [1b] 悬空引用 ──────────────────────────
norm = lambda s: re.sub(r"[\s★、（）()：:/·\-]+", "", s)
bad = set()
dangling = set()
for f in glob.glob("**/*", recursive=True):
    if not os.path.isfile(f) or not f.endswith((".md", ".yaml")):
        continue
    if os.path.basename(f) == "CHANGELOG.md":     # 历史记录不参与锚点判定
        continue
    src = open(f, encoding="utf-8", errors="ignore").read()
    # v4.9.0: 字符类加 \u4e00-\u9fff，支持 {题材} 等中文占位符
    for m in re.finditer(r"`([A-Za-z0-9_\-/\.\{\}\u4e00-\u9fff]+\.(?:md|yaml))(?:#([^`]+))?`", src):
        if not m.group(2) or m.group(2) == "X":   # 无锚点 / 占位符，跳过
            continue
        pat = m.group(1)
        if os.path.basename(pat) in RUNTIME:      # 运行时产物，跳过
            continue
        expanded = glob.glob(pat.replace("{type}", "*").replace("{题材}", "*"))
        if not expanded:
            if "{" not in pat:                    # 非通配引用却无匹配 → 悬空
                dangling.add((f, pat))
            continue
        for tp in expanded:
            hs = [l.lstrip("#").strip() for l in open(tp, encoding="utf-8", errors="ignore") if l.startswith("#")]
            if not any(norm(m.group(2)) in norm(h) for h in hs):
                bad.add((tp, m.group(2)))
print(f"[1] 锚点落空: {len(bad)}")
for x in sorted(bad):
    print("     ", x)
fail += len(bad)
print(f"[1b] 悬空引用: {len(dangling)}")
for f, p in sorted(dangling):
    print(f"      {p} <- 被引用于 {f}（目标文件不存在）")
fail += len(dangling)

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

# ── [3] 已废止表述复发（v4.9.0 起扫描含 .yaml）─────────────
# 词表项为 str 或 (word, exclude) 元组：exclude 为同行排除串——
# 行内含 exclude 时不判 word 命中（用于「器具剥夺」vs「辅助器具剥夺」消歧）
DEAD = [
    "蹲不下", "全蹲做不到", "单腿蹲极难",      # 4.7.0 蹲豁免后废止
    "走路时完全不晃",                          # 4.7.2 空管晃动口径后废止
    # 注：「空裤管飘荡」4.7.2 后**部分合法**（未处理时可写），故不入表，避免误报
    "可半蹲",                                  # 4.7.0 蹲分级废止（S-5 曾漏网）
    "章五要素",                                # 4.8.0 改章六要素
    "那一半椅面是空的",                        # 4.8.0 空椅面口径（N-1 曾漏网）
    "没有裤管", "没有袖管",                    # 4.8.2 禁否定式缺失描写（写了收口还声明缺失）
    # ── v4.8.4 废止项（v4.9.0 入表）────────────────────────
    "约平大转子",                              # 腋托高度物理错误 → 约两横指
    "健腿洗患侧",                              # 语病 → 洗低位与患侧够不着
    "拐靠墙/交手",                             # 如厕动作链 → 并到一手
    "长裙+假肢是唯一",                         # 唯一藏得住 → 穿假肢都不易察觉
    "=失去行动力=死",                          # 末世绝对化 → 危险倍增
    "上下楼是受限高发场景",                    # → 场景点缀口径
    "臀下到床面之间没有腿",                    # → 臀部压住承托面、患侧往前没有腿
    "髋离断没有空裤管",                        # 绝对化 → 已裁剪/未裁剪分流
    "受限高发场景",                            # 「X是受限高发场景」句式（daily-actions 漏网点）
    # ── v4.10.0 废止项──────────────────────────────────────
    "能力丧失",                                # 受限类改名 → 功能丧失（一主五衍）
    "五类之一",                                # 受限类型枚举 → 一主五衍六类
    "受限第六类",                              # 环境与他者改标衍生类 5
    "五类受限",                                # 旧结构称谓
    ("器具剥夺", "辅助器具剥夺"),              # 4.10.0 改名「辅助器具剥夺」；裸用旧名即复发
]
hits = {}          # (file, line) -> [命中的词]，同一行多词只报一次
scan = sorted(glob.glob("**/*.md", recursive=True) + glob.glob("**/*.yaml", recursive=True))
for entry in DEAD:
    w, excl = entry if isinstance(entry, tuple) else (entry, None)
    for f in scan:
        # CHANGELOG 记录的是"清理了什么"，必须保留原文，不参与创作注入 → 跳过
        if os.path.basename(f) == "CHANGELOG.md":
            continue
        for i, l in enumerate(open(f, encoding="utf-8", errors="ignore"), 1):
            if w in l and not (excl and excl in l):
                hits.setdefault((f, i), []).append(w)
for (f, i), ws in sorted(hits.items()):
    l = open(f, encoding="utf-8", errors="ignore").read().split("\n")[i - 1]
    # 出现在禁令句里多半合法 → 列出上下文让维护者判断，不静默放行
    banned = ("已废止" in l or "❌" in l or "不写" in l
              or "禁止" in l or "反例" in l)
    flag = "［禁令句，人工确认］" if banned else "［疑似复发］"
    print(f"[3] 「{'/'.join(ws)}」{flag} {f}:{i}")
    print(f"      {l.strip()[:100]}")
    if not banned:
        fail += 1
print(f"[3] 废止表述: {len(hits)} 处（上方［］标记项请人工确认）")

# ── [4] 孤儿文件（存在但全域零引用）────────────────────────
# 背景：equipment-risk.md 于 v4.6.3 声明删除却仍存活（疑似备份恢复带回），
#      零引用文件是「受限定义分散」的复发根源 → 机检兜底
all_files = [f for f in glob.glob("**/*", recursive=True)
             if os.path.isfile(f) and f.endswith((".md", ".yaml"))]
texts = {f: open(f, encoding="utf-8", errors="ignore").read() for f in all_files}
orphans = []
for f in all_files:
    base = os.path.basename(f)
    if base in RUNTIME or base in ("SKILL.md", "CHANGELOG.md"):
        continue        # 入口 / 变更史 / 运行时产物不适用本判定
    others = "".join(t for k, t in texts.items() if k != f)
    wildcard_covered = (
        (f.startswith("types" + os.sep) and "types/{type}.md" in others)
        or (f.startswith("genre" + os.sep) and "genre/{题材}.md" in others)
    )
    if base not in others and not wildcard_covered:
        orphans.append(f)
print(f"[4] 孤儿文件: {len(orphans)}")
for f in orphans:
    print(f"      {f}（全域零引用——确认是否为应删未删的残留）")
fail += len(orphans)

print("\n结果:", "PASS" if fail == 0 else f"FAIL ({fail})")
sys.exit(0 if fail == 0 else 1)
