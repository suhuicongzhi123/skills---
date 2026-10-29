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

v4.17.0 修复：
  ⑦ [1] 锚点检查盲区：引用正则反引号强制 → 反引号可选（裸引用如「见 core/chapter-planning.md#二」
     首次受检）；裸引用必须带锚点、锚点字符集排除中英文标点与空白
     （文件名的 .md/.yaml 后缀为强制特征），防普通文本误判为引用
  ⑧ [1] .yaml 目标锚点判定：yaml 无 # 标题（# 是注释）→ 收集全部键名（任意缩进 key: 形式），
     嵌套锚点（distribution.元素上次出现章）分段逐级匹配，兜底全键名子串匹配
  ⑨ [4] 孤儿判定引用源剔除 CHANGELOG.md（与 [1]/[3] 跳过 CHANGELOG 的口径一致）

v5.22.0 修订（对照 v5.22.0 全域审查）：
  ⑩ gatecheck.py 新增 [15] B/C 档三条硬闸机检（本章登记.亲密戏登记.硬闸自查
     四项：成年/非自愿/同意/疼痛非快感，B/C 档须齐备且实判），哈希基线随之更新
     a48154e2497e289e → d95694904024cb07；
  ⑪ DEAD 词表补 v5.22.0 废止项（跨障绝对化 / 时长档位字母误用 / C9 编号 / 重心低因果等）。

v5.23.0 修订（待观察项 3/5/6/7/8 落地）：
  ⑫ gatecheck.py 新增 [16] 资源账窗口空窗机检（仅末世题材 资源账.启用: 是 时，
     上次记账章与日志最大章号差 ≥3〔连续 3 章未记账〕→ FAIL），并升级 [13] 独立发现判定措辞与
     core/cold-review.md#五 受理验收③④ 对齐（判定主体＝主代理受理时裁定）；
     哈希基线 d95694904024cb07 → f7ca495ec16db568（含 [16] 差≥3 边界修正）；
  ⑬ 其余为 md/yaml 内容改动（贴身层轻骨架 / 角色弧接活 / 张力仲裁+低冲突豁免 /
     资源账字段 / 验收澄清），不改本脚本检查逻辑。

退出码：0 通过 / 1 有问题
"""
import re, glob, os, sys, hashlib

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
    # v4.17.0: 兼容裸引用（反引号可选）——裸引用必须带锚点，锚点字符集排除
    #          中英文标点与空白；文件名部分强制 .md/.yaml 后缀特征，防普通文本误判
    for m in re.finditer(
            r"`([A-Za-z0-9_\-/\.\{\}\u4e00-\u9fff]+\.(?:md|yaml))(?:#([^`]+))?`"
            r"|([A-Za-z0-9_\-/\.\{\}\u4e00-\u9fff]+\.(?:md|yaml))"
            r"#([^\s`，。；、：:（）()【】《》「」“”‘’\"'★—…！？!?]+)", src):
        pat = m.group(1) or m.group(3)
        anchor = m.group(2) if m.group(1) else m.group(4)
        if not anchor or anchor in ("X", "小节"):  # 无锚点 / 占位符（「小节」为 types/{type}.md 泛称示例），跳过
            continue
        if os.path.basename(pat) in RUNTIME:      # 运行时产物，跳过
            continue
        expanded = glob.glob(pat.replace("{type}", "*").replace("{题材}", "*"))
        if not expanded:
            if "{" not in pat:                    # 非通配引用却无匹配 → 悬空
                dangling.add((f, pat))
            continue
        for tp in expanded:
            if tp.endswith(".yaml"):
                # v4.17.0: yaml 中 # 是注释、无标题——改为收集全部键名（任意缩进 key: 形式）；
                # 嵌套锚点（如 distribution.元素上次出现章）分段逐级匹配，兜底全键名子串匹配
                ykeys = []
                for l in open(tp, encoding="utf-8", errors="ignore"):
                    km = re.match(r"^\s*-?\s*([^\s#:]+)\s*:", l)
                    if km:
                        ykeys.append(km.group(1))
                segs = anchor.split(".")
                hit = (all(any(norm(seg) in norm(k) for k in ykeys) for seg in segs)
                       or any(norm(anchor) in norm(k) for k in ykeys))
                if not hit:
                    bad.add((tp, anchor))
            else:
                hs = [l.lstrip("#").strip() for l in open(tp, encoding="utf-8", errors="ignore") if l.startswith("#")]
                if not any(norm(anchor) in norm(h) for h in hs):
                    bad.add((tp, anchor))
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
    # ── v4.11.0 废止项（排班制 → 限频/识别优先）──────────────
    "1 个的节奏轮转",                          # 排班语义 → 限频（同一元素间隔 ≥2 章）；
                                               #  timeline 档位频率「每 2 章 1 次为常态」不受影响
    "每章必备",                                # 裸词入表（v4.11.0 曾因完整短语匹配漏网 workflow 残留）；
                                               #  全库无合法场景（「每章必过审查」为合法词不受影响）
    # ── v5.x 废止项（辅具四类限定 / 轮换制废除）────────────────
    "就地取材充拐",                            # v5.0.0 辅具四类限定（夺拐应对改无拐周旋）
    "临时代步",                                # 同上（其他物品不得作辅具）
    "其他(注明)",                              # v5.0.0 辅具枚举收口（旧自由填写项废止）
    "单腿跳/替代移动",                          # v5.0.0 枚举值改「无(单腿跳)」（替代移动属特殊能力非辅具）
    "载体轮转须换场景域",                        # v5.0.0 轮换制废除（同域深挖合法，事件必须新）
    "通道强制轮换",                             # 同上（通道跟随剧情需要选）
    "全书分布目标",                            # v4.11.0 分配制修辞废止 → 契机内生供给
    "缺了日常底色",                            # 章六要素旧判据（否决无受限章）→ 窗口式判定
    # ── v4.11.1 废止项（移动方式口径）────────────────────────
    "单腿跳是默认",                            # 全局默认是辅具移动；单腿跳仅限无辅具三种情形
    "单腿跳是常态",                            # 同上（实测曾致拐杖分离错误）
    "（默认移动方式）",                        # 旧节名括号（crutch-usage 四-补已改「移动方式分层」）
    # ── v4.11.4 废止项（开篇推荐映射 → 排除式约束）───────────
    "推荐开篇",                                # 推荐映射收敛选择（同题材反复撞同一维度，
                                               #  新烂开篇）；题材只声明禁什么（排除式）
    # ── v4.12.0 废止项（破折号零容忍 → 频率闸门 ≤3）──────────
    "一切用法）：不得出现",                    # 旧总闸零容忍句式 → ≤3/章频率闸门
    "戏剧效果不损失",                          # 「句号断句替代不损失」的旧声明已撤回
                                               #  （悬停式合法——破折号是悬置续流，句号是完成定格）
    "即结构性破折号，应为 0",                  # 冷读稽查旧口径完整句 →「应 ≤3；四型应为 0」
    # ── v5.21.3 废止项（单腿跳连跳口径）───────────────────────
    "三步一停",                                # 连跳口径废止 → 熟练者可连续跳十几步以上
    "一，二，停",                              # 旧「跳跃节奏感」表述 → 同上废止
    "一、二、停",                              # 同上（顿号变体）
    "一步一停",                                # 同上（手的经济表曾误用）
    "连跳上限",                                # 旧字段名废止 → 不存在「三步内必停」的上限
    # ── v5.22.0 废止项（全域审查）────────────────────────────
    "凡需抬腿越过的都过不去",                  # 无辅具跨障绝对化 → 低障可跃过/高障须绕（mobility-modes 四）
    "站定后重心低",                            # 因果错：稳的是三角支撑，截断整腿后重心上移偏健侧（mobility-modes 四/combat 二）
    ("近期 B", "近期 B:"),                     # 时长档位字母误用 → 近期档（A/B/C 专指尺度档）
    ("多年 C", "多年 C:"),                     # 同上 → 多年档
    "跃迁后按 B 档",                           # wannabe 时长档位字母误用 → 跃迁后按近期档
    "时长档位（B/C）",                         # limitation-scenes 正交声明字母误用 → 中文档位
    "外部后果（C9）",                          # 悬空编号且撞 C01–C12 → 外部后果三章律
    "一-补2、主旨锚",                          # 与主冲突线「一-补2」重名 → 改一-补1-b
    "孩子（单亲家庭必写一次",                   # 未成年第三方写入的强制节拍 → 已删
    "腋下与手掌先吃不消",                      # 承重部位错（应手掌/虎口先）→ daily-scenes 四
    "残肢驱动假肢膝",                          # 膝上假肢「主动屈膝」歧义 → 被动/阻尼控制
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
texts = {f: open(f, encoding="utf-8", errors="ignore").read() for f in all_files
         if os.path.basename(f) != "CHANGELOG.md"}   # v4.17.0: 引用源剔除 CHANGELOG（与 [1]/[3] 口径一致）
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

# [5] gatecheck.py 哈希基线（防篡改验证机制——SKILL 〇-补 第 6 类红线支撑）
# 哈希前归一行尾（\r\n→\n）：git autocrlf 使磁盘行尾随克隆环境漂移（repo 存 LF，
# Windows 检出 CRLF）——按原始字节哈希会跨环境误报；归一后基线跨 LF/CRLF 稳定
GATECHECK_SHA = "f7ca495ec16db568"   # v5.23.0：gatecheck.py 增 [16] 资源账机检 + [13] 措辞升级后重算（原 d95694904024cb07）
_raw = open("scripts/gatecheck.py", "rb").read()
_cur = hashlib.sha256(_raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
if _cur != GATECHECK_SHA:
    fail += 1
    print("[5] gatecheck.py 哈希基线不符（当前 " + _cur + " 不等于 基线 " + GATECHECK_SHA + "）——脚本被篡改，恢复后重跑")
else:
    print("[5] gatecheck.py 哈希基线一致: " + _cur)

print("\n结果:", "PASS" if fail == 0 else f"FAIL ({fail})")
sys.exit(0 if fail == 0 else 1)
