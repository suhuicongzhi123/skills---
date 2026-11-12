#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付闸机检脚本
用法: python gatecheck.py <小说项目目录> [--chapter N]

机检项（结构与覆盖＋独立性内容信号）：
  [1] 账本存在且可解析；工作流执行日志块结构完整
  [2] 日志章号连续：章号集合 == {1..N}（int 归一防类型混淆）
  [3] 模式保真（降级禁止）：选定 == 实际，一律相等，任何不等 → FAIL
  [4] 调用代理凭证化：pro/max 须结构化 [{角色,凭证}]，必需角色凭证非空；
      同章各角色凭证两两互异（同凭证签多角色＝合并扮演）
  [5] 产物三验：非空＋存在＋在项目目录内（realpath 防穿越）；章草稿为三模式
      必需产物（交付正文绑定基准）
  [6] 产物生成指纹：每个产物文件末行「生成指纹: X」== 账本签发角色凭证
      （角色↔产物映射：max 章任务包→队长/章草稿+自查报告→写作员/审查报告→
      审查员；pro 章草稿+自查报告→本体/审查报告→冷读）；缺指纹/不同号 → FAIL
  [7] 稽查全覆盖 13/13（必判维度）＋读感七问 7 行（仅 6 行时 WARN 兼容旧报告）；
      审查报告须含必判维度 1,2,3,5,6,9,10,13,15,16,17,21,22
  [8] 输入隔离：审查报告出现自查报告文件名 → FAIL（冷读者不得看自查结论）
  [9] 自查覆盖（分级）：按账本 自查档 取期望全集——标准 G01–G12 共 12/12（组）、lite 5/5
      （短篇核心项）；报告 ID 集合==本档语义项全集、判定行数==全集数、与「自查覆盖: N/N」
      机检锚一致（只列 ID 不写判定 → 判定向量为空，同源判定失效 → FAIL）；
      机检 11 项（MACHINE_IDS）混入自查报告 → FAIL（[18] 代判项不占自查行）
  [9-b] 模板初值黑名单：待填/待运行/未过/待查 → FAIL（防"复制模板即合规"）
  [10] 交付闸字段 == 通过（唯一合法值；无 python＝无法过闸＝不得交付；
       --precheck 豁免本项，供 bootstrap 三步的第一步使用）
  [11] 冷读引文实证：审查报告命中草稿原文引文 ≥3 条（「」内 ≥8 字）——
      零命中＝未读草稿的空报告
  [12] 主语污染：审查报告出现「我写/作为队长」类主上下文人称模式 → FAIL
  [13] 同源判定：审查 22 维判定向量与「自查 S 编号折算后的维度向量」高度一致
      （比例 ≥95% 且审查存在不通过项）→ WARN（同源信号，交主代理受理裁定；引文/位置不同的合法同判不阻断，
      ❌ 不硬 FAIL 逼审查员造差异）。硬防伪由 [8] 输入隔离/[12] 主语纯净/[11] 引文实证/调用凭证兜底。
      「独立发现」分两层：本脚本只判「审查侧有 ≥1 条不通过 / 反证轮 ≥3 段实质核验」（裸子串不算）；
      「是否自查未发现」由本项比对+主代理复核裁定（审查员依 [8] 看不到自查报告，不自证）——
      见 core/cold-review.md#五 受理验收③④ 与 core/workflow.md#冷读报告受理验收流程。
  [14] 交付凭证（三模式）：gate-pass-第N章.txt，含正文SHA（sha256(章草稿)
      [:16]）＋正文字数＋印章（sha256(章号+章草稿+自查+审查)[:16]）重算比对
      ——交付正文被替换 → SHA/印章不符 FAIL；FAIL 运行不生成凭证；
      交付正文须逐字节来自被检章草稿文件，交付时附凭证内 SHA 与字数
  [15] 三条硬闸机检（B/C 档亲密章）：本章登记.亲密戏登记.档位 为 B/C 时，
      硬闸自查四项（成年/非自愿/同意/疼痛非快感）须齐备且均为「通过」；
      任一「待查」＝未实查 FAIL、任一「不通过」＝触硬闸 FAIL。
      硬闸不因题材/用户指令关闭（SKILL 〇-补）；缺失字段视为未登记 FAIL。
  [16] 资源账窗口空窗机检（仅末世/生存题材，账本 资源账.启用: 是 时）：
      资源账.上次记账章 与日志最大章号差 ≥3（＝连续 3 章未记账）→ FAIL（经济系统失效），
      与 genre/postapocalyptic.md「连续 3 章不记账＝经济系统失效」逐字对齐。
      「本章算不算一场危机」是叙事判断，由 cold-review 维度19 软查，本项只认章号窗口；
      现实/古装/幻想题材 启用: 否 → 跳过。
  [17] 章循环状态机（启用状态机层时；账本有 章节状态 块才校验，缺失则跳过以兼容旧账本）：
      状态轨迹须为合法转移、不得跳步；当前章段（轨迹中最后一次「已交付 → 待规划」回卷点
      之后的段——轨迹为跨章累计，回卷即 state_machine 的推进设计）出现「已过闸」或末态
      「已交付」时须闭合到「已过闸 → 已交付」；flash 不得伪填「已冷读」，pro/max 交付
      轨迹必须过「已冷读」。状态表内嵌于本脚本（自包含，运行时不依赖技能目录），
      与 rules/rules.yaml chapter_states 由 scripts/compile_rules.py 校验一致。
  [18] 自查形式化项机检（分级——11 项代判，AI 不再逐项自查；编号体系不变，
      权威清单见 templates/chapter.md 分级标注）：
      ⚠️ 边界声明：本项只判枚举合法性与可算术性，不判语义正确性。
      语义半区（如受限层级的判定依据、标点三禁的语境合法性）仍由冷读把关。

      登记类（全局段）：S05/S09 钩子类型枚举 H1–H7/h8–h10（首字符即强度标定）；
      S06 章节功能五枚举；S07 主冲突线beat三态；S12 张力级 1–5；
      S11 弱钩不连续（近五章窗口末 3 项全 h* → FAIL）；S14 受限beat层级枚举＋
      受限让路补法=无 → 破窗 FAIL；S38 首章beat数 ≤2（distribution 块，仅第 1 章）。
      正文类（章循环内）：S42 标点三禁——叙述层破折号 0／解释性冒号 0／翻案句 0
      （对话引号内白名单先剥离）＋注释式纠错变体家族 0。
      结构类（[9] 报告块内）：S48/S49 附页 A/B 行数证据存在性（pro/max 必填「A:N」「B:N」，N 可为 0；
      ❌ 不设行数下限，全覆盖属语义判定；flash 建议填缺则 WARN）。
  [19] 段落组织机检（WARN 档，不阻断交付）：走「叙述段」口径（不含对白引号的段），
  判碎片化率 >50%、叙述段最长 <80 字、连续 4 段叙述 ≤20 字、叙述段同型段首、
  连续 7 段含对白（v9.2 补对白侧基准）、三项并列 ≥5 处。
  ⚠ 只报形状，不判好坏——形状可疑不等于写得差，反例见 core/style.md#★加法十二条；
  真正的判断在冷读读感七问（core/cold-review.md#〇）。
  历史章一并检查，文案带「历史章·非当前章」标记，免看错章改错稿。
  [20] 章末钩子兑现（v9.1）：账本 `钩子兑现锚` 须仍出现在正文末三段。只对当前章生效——
      `本章登记` 是单章结构，拿当前章的锚去验历史章必然误报。
  [21] 特殊移动未登记（WARN）：正文出现变形/龙形等，而账本 `特殊移动.形态` 为空 → 提示先登记
      （规则是「未登记即不启用」，但旧版没有任何检查确认它登过）。
  [22] 定稿改名（WARN）：章节状态为「已交付/已过闸」而产物名仍含「草稿」→ 提示重命名为定稿。
  [23] 器具禁令词表（v9.2，硬 FAIL）：扫正文（含对话，禁令④含台词与内心独白）——
      缠布/重缠、换拐头/换胶垫/配一副新、拐头磨平/磨薄/磨出包浆/防滑纹磨光 → FAIL；
      送修/返厂/调校/包浆/「该换一副」→ WARN。
      立条原因：该禁令标题叫「损耗与更换」，实际范围还含缠布、调校与议论——标题比内容窄，
      凭标题判断必漏（实测作者判定「缠布是维护不是损耗」而写进正文）。
  [24] 章节登记归档（WARN）：`本章登记` 写完下一章即被覆盖，历史 beat/turn/钩型全丢。
      归档缺章号 → 提示补（只对当前章报一次）。
  [25] 枚举表一致性（WARN）：账本 `枚举表`（数据块，非注释）与脚本常量比对，
      五组：主冲突线beat／自查判定／受限层级／章节功能／章末钩子类型；
      不一致 → 提示两处同改；账本无该块 → 提示可能曾被脚本整份重写、枚举注释已蒸发。

      修复方法：
      1. 对比 templates/state-ledger.yaml 末尾的枚举表数据块
      2. 手动同步到账本文件（上述五组枚举）
      3. 或运行 `python scripts/state_machine.py --sync-enums` 自动同步（如果实现）
  [26] 豁免类动作写错（FAIL）：某些动作对该类型是正式豁免，写「做不了」即错。
      词表：蹲不下/蹲不了/没法蹲/不能蹲（单腿蹲是豁免）；⚠ 跪**不在**表内，
      因 types 明写「跪不了」是真受限——词表上线前必须核对判据。
  [27] 场景驱动四问（v9.4，FAIL）：chapter-contract-N.md 写作卡「★四行硬项」
      （动手与失败点／对手今天想干什么／篇幅第一名／三处不在状态）任一为空即 FAIL。
      立条原因：实测一章机检全绿、段落指标全达标，读起来是清单——五件事「答得出」，
      而第 3 件填「跟着走了一圈」、第 4/5 件填「无」。规则写在文档里没人执行，
      只有「落盘 + 机检」拦得住（同 [23]/[26] 的教训）。
      只对 --chapter 指定章生效；已交付章（交付闸＝通过）豁免，新规不追溯。
  [28] 创作注记残留（WARN）：正文含独立成段的全角括号注记（核心句/伏笔/不在状态/待改…）。
      实测第 3 章初稿留了两处，自查查「违规」不查「残留」，一路没拦下。
      写作时这类标记是必要的，故只 WARN；交付前必须删（读者会看见）。
  [0-c] 指定章必须已登记（FAIL）：账本「工作流执行日志」无该章时，后续检查全在空跑，
      最后仍打印 PASS——**假通过比 FAIL 危险**（同 9.2 版「报翻案句 0 处而冷读数出 5 处」）。
  [0-c2] 核查记录占位值（FAIL）：核查记录任一项仍为「待查」＝未实查
      （旧版与 [0-c] 共用编号，同一标签两种语义，v9.6 拆开）。
  [29] 表情套话（v9.5，WARN）：扫叙述层（对话引号内不算，人物说「哼」是合法台词）——
      冷嘲类（冷哼一声/冷嗤/轻嗤/嗤笑/讥诮）／眼神类（眸光/眼底闪过/眸色）／
      嘴角类（嘴角勾起/勾唇/扯出一抹）／微量类（露出一丝/闪过一抹）／模糊类（意味深长/不置可否）。
      立条原因：这批词是「给人物加表情」时最先被想到的，也恰是读者识别套路的第一个信号。
      中文网文有专帖问「除了冷哼一声还能怎么写」，回帖给的全是同义词——换汤不换药。
      正解见 core/emotion-signal.md#二：换成能看见的动作，让读者自己下结论。
  [30] 幻想向真实战斗冲突（v9.6，FAIL/WARN；R-033 的可形式化部分）：
      幻想向且本章登记为战斗章（章节功能=对抗危机／主冲突线beat=对抗／敌方阶非空）时——
      ① 叙述层非战斗化词表（没有动手/没打起来/一番周旋/交涉/误会化解/不战而屈人之兵）→ FAIL；
      ② 正文复用信号（又一次/像上次）→ WARN；
      ③ 账本 解法台账 近 5 章同场景域＋同招法 ≥2 次 → WARN（战斗过程/解法复用）。
      「有死有伤／过程丰富／严格按选定强度」属语义半区，交章末 G01/G07/G08、
      冷读维度 9/10/21 与独立子代理简报第三节判，❌ 本项不冒充语义判定。
      历史章的非战斗化命中降为 WARN（新规不追溯，同 [27] 教训）。
  [31] 默认性格与题材分割（v9.6，FAIL/WARN；R-034 全类型 / R-032 界限）：
      ① 角色固定属性.性格／.声口 命中「话少/冷漠/沉默寡言/寡言/高冷/冷淡/不爱说话/话不多」
         且 用户指令变更 无同源原话 → FAIL（四种合法用法见 R-034）；
      ② 非幻想向题材却把 战斗豁免.档位 登记为 E1–E3 → FAIL（现实向零豁免）；
      ③ 幻想向战斗章未登记豁免档位 → WARN（未登记即回落零豁免）；
      ④ 题材契约.题材大类 缺失 → WARN（兼容旧账本，提示补登记）。
  边界如实声明：只判枚举合法性与可算术性，不判登记与正文语义一致性
      （钩子兑现句是否真在末段等语义半区仍由冷读把关）。
      ⚠ v9.6：交付闸 FAIL 时也打印 WARN（旧版 sys.exit 吞掉全部 WARN，
      使 [30]/[31] 的复用／未登记提示在失败章不可见）。
      ⚠ 引文实证 [11] 只判「至少 3 条命中」，**不可反过来要求高命中率**：
      审查报告里的引号还用于举反例、给改法建议、引账本原文，那些本就不在正文里。
      「复核后是否又改过稿」改由 `复核字数: N` 比对（偏差 >8% 提示补复核）。

边界：机检由 AI 自行执行，强制力＝验证网＋成本压制（过闸嵌入每章循环，
伪造合规全套成本 ≥ 真实执行）；绝对强制需宿主级 hook，超出技能包能力。
"""
import sys, re, os, hashlib, argparse

try:
    import yaml
except ImportError:
    print("FAIL 需要 pyyaml：pip install pyyaml"); sys.exit(1)

MODE_AGENTS = {"flash": ["本体"], "pro": ["本体", "冷读"],
               "max": ["队长", "写作员", "审查员", "记账员"]}
MODE_PRODUCTS = {"flash": ["章草稿", "自查报告"], "pro": ["章草稿", "审查报告", "自查报告"],
                 "max": ["章任务包", "章草稿", "审查报告", "自查报告", "记账摘要"]}
ROLE_OF_PRODUCT = {"章任务包": "队长", "章草稿": "写作员", "自查报告": "写作员",
                   "审查报告": "审查员", "记账摘要": "记账员"}
ROLE_OF_PRODUCT_PRO = {"章草稿": "本体", "自查报告": "本体", "审查报告": "冷读"}
DIM_SET = set(range(1, 23))
# 必判维度（v8.0.0）：22 维保留定义与编号，必判集收为 13；其余本章涉及时再判
REQUIRED_DIMS = {1, 2, 3, 5, 6, 9, 10, 13, 15, 16, 17, 21, 22}
VERDICT_SET = {"通过", "不通过", "不适用", "通过·带条件", "通过.带条件"}
SELF_MARK = {"✓": "通过", "√": "通过", "✗": "不通过", "×": "不通过"}
CHECKLIST_IDS = {f"S{i:02d}" for i in range(1, 50)}
# 自查分级（templates/chapter.md 权威清单）：S01–S49 编号保留不重排，报告改按 12 组汇总。
# MACHINE_IDS 11 项由 [18] 机检代判（AI 不再逐项自查，写作时仍须遵守规则本身）；
# GROUP_IDS 12 组＝标准档自查报告全集；LITE_GROUPS 5 组＝短篇 lite 档核心（账本 自查档: lite）。
MACHINE_IDS = {"S05", "S06", "S07", "S09", "S11", "S12", "S14", "S38", "S42", "S48", "S49"}
GROUP_IDS = {f"G{i:02d}" for i in range(1, 13)}
LITE_GROUPS = {"G01", "G02", "G03", "G05", "G11"}
# 组 → 成员 S（与 templates/chapter.md 逐条一致；50 项全覆盖、不重不漏）
G2S = {
    "G01": ["S18", "S19", "S20", "S21", "S22", "S23"],
    "G02": ["S17", "S32", "S33", "S34", "S40"],
    "G03": ["S25", "S26", "S27", "S28", "S29", "S30", "S31"],
    "G04": ["S35", "S36"],
    "G05": ["S37", "S38"],
    "G06": ["S14", "S15", "S16"],
    "G07": ["S01", "S02", "S03", "S04", "S06", "S07", "S08", "S13"],
    "G08": ["S05", "S09", "S10", "S11", "S12"],
    "G09": ["S24", "S39"],
    "G10": ["S50"],
    "G11": ["S41", "S42", "S43", "S46"],
    "G12": ["S44", "S45", "S47", "S48", "S49"],
}
HOOK_ENUM = {f"H{i}" for i in range(1, 8)} | {f"h{i}" for i in range(8, 11)}
FUNC_ENUM = {"主线推进", "关系深化", "日常样态", "对抗危机", "生存危机"}
BEAT_ENUM = {"推进", "蓄势", "留白", "对抗"}
LIMIT_ENUM = {"核心", "在场", "余波", "弱受限"}
PERSONA_PAT = re.compile(r"我写|我设计|我编制|我自查|我刚才|作为队长|我画的大纲|上一轮我|我安排的剧情|我登记的账")
QUOTE_PAT = re.compile(r"[「『“]([^」』”]{8,})[」』”]")
errors, warns = [], []

def fail(ch, msg):
    # ch 为章号或 "本章"（全局登记类检查）——后者直接输出「本章｜」不套「第N章」壳
    errors.append(f"本章｜{msg}" if ch == "本章" else f"第{ch}章｜{msg}")

def parse_agents(raw):
    if not isinstance(raw, list) or not raw:
        return [], None, False
    if isinstance(raw[0], dict):
        names = [a.get("角色") for a in raw]
        creds = {a.get("角色"): (a.get("凭证") or "") for a in raw}
        return names, creds, True
    return list(raw), None, False

# 自查 S 编号 → 稽查维度（映射表权威源：core/cold-review.md#四-补）
S2D = {
    "S01": [10], "S02": [10], "S03": [10], "S04": [10], "S05": [10],
    "S06": [18, 19], "S07": [19], "S08": [18], "S09": [18], "S10": [18],
    "S11": [18], "S12": [18], "S13": [10], "S14": [13], "S15": [13],
    "S16": [13], "S17": [6], "S18": [1, 2, 3], "S19": [9], "S20": [16],
    "S21": [19, 20], "S22": [21], "S23": [22], "S24": [], "S25": [2],
    "S26": [3], "S27": [9], "S28": [9], "S29": [16], "S30": [4],
    "S31": [5], "S32": [6, 8], "S33": [6], "S34": [8], "S35": [12],
    "S36": [14], "S37": [12], "S38": [12], "S39": [], "S40": [7],
    "S41": [15], "S42": [15], "S43": [15], "S44": [10], "S45": [11],
    "S46": [17], "S47": [], "S48": [9], "S49": [9],
    "S50": [22],   # 声口可辨：G10 组的机检折算锚（v9 补，此前 G10 无映射＝白判）
}

def verdict_vector(text):
    out = {}
    for m in re.finditer(r"维度\s*(\d+)\s*[｜|]\s*([^\s｜|，。]+)", text):
        out[int(m.group(1))] = m.group(2)
    return out

def group_dim_vector(text):
    """自查报告按 G 组落盘 → 组内任一 S 不通过，折算为该组涉及的维度不通过"""
    per = {}
    for m in re.finditer(r"\bG(\d\d)\s*[｜|]\s*([^\s｜|，。]+)", text):
        per[f"G{m.group(1)}"] = SELF_MARK.get(m.group(2), m.group(2))
    dims = {}
    for gid, v in per.items():
        for sid in G2S.get(gid, []):
            for d in S2D.get(sid, []):
                dims.setdefault(d, []).append(v)
    out = {}
    for d, vs in dims.items():
        eff = [x for x in vs if x != "不适用"]
        if not eff:
            out[d] = "不适用"
        elif any(x == "不通过" for x in eff):
            out[d] = "不通过"
        else:
            out[d] = "通过"
    return out


def selfcheck_dim_vector(text):
    """自查报告按 S 编号落盘 → 依 S2D 折算成维度级判定（任一 S 不通过即该维不通过）。
    v8.0.0 起标准报告用 G 组；此处保留 S 路径以兼容旧项目。"""
    if re.search(r"\bG\d\d\s*[｜|]", text):
        return group_dim_vector(text)
    per = {}
    for m in re.finditer(r"\bS(\d\d)\s*[｜|]\s*([^\s｜|，。]+)", text):
        per[f"S{m.group(1)}"] = SELF_MARK.get(m.group(2), m.group(2))
    dims = {}
    for sid, v in per.items():
        for d in S2D.get(sid, []):
            docs = dims.setdefault(d, [])
            docs.append(v)
    out = {}
    for d, vs in dims.items():
        eff = [x for x in vs if x != "不适用"]      # 不适用不参与聚合（防"一条不适用被其余通过吞掉"）
        if not eff:
            out[d] = "不适用"
        elif any(x == "不通过" for x in eff):
            out[d] = "不通过"
        else:
            out[d] = "通过"
    return out

def stamp_of(ch, draft_text, sc_text, rp_text):
    h = hashlib.sha256()
    h.update(str(ch).encode("utf-8"))
    h.update((draft_text or "").encode("utf-8"))
    h.update((sc_text or "").encode("utf-8"))
    h.update((rp_text or "").encode("utf-8"))
    return h.hexdigest()[:16]

def tail_fingerprint(path):
    """末行「生成指纹: X」→ X；无则 None"""
    try:
        lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        return None, []
    if not lines:
        return None, lines
    m = re.search(r"生成指纹[:：]\s*(\S+)", lines[-1])
    return (m.group(1) if m else None), lines

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--precheck", action="store_true",
                    help="bootstrap 第一步：跳过 [10] 两字段（机检运行/交付闸），其余检查照跑")
    ap.add_argument("--report", default=None,
                    help="把本次输出同时写入 UTF-8 报告文件（Windows GBK 控制台可读）")
    args = ap.parse_args()
    # 命名空间统一命名 args：❌ 禁止再用单字母 a 作长生命周期变量——轨迹循环曾用 a, b 遮蔽本命名空间，
    # 导致全合规项目在 PASS 前 AttributeError（7.1.0 运行缺陷，见 CHANGELOG）。
    # Windows GBK 控制台输出中文报错会乱码 → stdout 强制 UTF-8；不支持时静默退回原编码
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass
    if args.report:
        import atexit
        _rf = open(args.report, "w", encoding="utf-8")
        _orig_stdout = sys.stdout

        class _Tee:
            def __init__(self, *ws): self.ws = ws
            def write(self, s):
                for w in self.ws: w.write(s)
                return len(s)
            def flush(self):
                for w in self.ws:
                    try: w.flush()
                    except ValueError: pass

        sys.stdout = _Tee(_orig_stdout, _rf)

        def _close_report():
            # 退出前先刷完、再还原 sys.stdout，最后关闭报告文件；
            # 否则解释器退出时 flush 到已关闭的 Tee 会 ValueError 并把退出码改成 120
            try: sys.stdout.flush()
            except Exception: pass
            sys.stdout = _orig_stdout
            _rf.close()
        atexit.register(_close_report)
    root = os.path.realpath(args.dir)
    ledger = os.path.join(root, "state-ledger.yaml")
    if not os.path.isfile(ledger):
        print("FAIL 未找到 state-ledger.yaml（目录＝小说项目工作区）"); sys.exit(1)
    data = yaml.safe_load(open(ledger, encoding="utf-8")) or {}
    logs = data.get("工作流执行日志") or []
    if not logs:
        print("FAIL 工作流执行日志为空——无执行证据链（口头声明不作数）"); sys.exit(1)
    fixed_mode = (data.get("角色固定属性") or {}).get("工作流模式")
    # [0] 模式空值闸：未选定模式（空值）＝未过第 13 题＝不得开写不得交付
    if not fixed_mode:
        errors.append("工作流模式未选定（空值＝未过收集第 13 题）——不得开写不得交付")

    chs = []
    for e in logs:
        try: chs.append(int(e.get("章")))
        except (TypeError, ValueError): chs.append(None)
    if None in chs:
        errors.append("日志存在无法解析的章号（类型混淆）")
    if all(c is not None for c in chs) and sorted(chs) != list(range(1, len(chs) + 1)):
        errors.append(f"日志章号不连续（缺号漏登）: 现有 {sorted(chs)}")

    gen_stamps = []
    # 首章前置：大纲须为第一章前置产物且契约块非空
    ch_nums = [c for c in chs if c is not None]
    # [0-c] 指定章的验收对象必须存在（v9.4）：账本没登记这一章时，后面所有检查都在空跑，
    # 最后仍然打印 PASS——这是**假通过**，比 FAIL 更危险。教训同 9.2 版「机检报翻案句 0 处、
    # 冷读同一份稿子数出 5 处」：一个让人放心的假数字，会让人不再去看真问题。
    # 实测触发：新章草稿已落盘但账本未登记，`--chapter N` 返回 PASS，实际一项都没验。
    if args.chapter is not None and args.chapter not in ch_nums:
        errors.append(
            f"第{args.chapter}章未在账本「工作流执行日志」登记——机检没有验收对象，"
            f"此时的 PASS 不作数。先按 core/workflow.md#8 登记本章日志与产物路径，再跑机检")
    if ch_nums and min(ch_nums) == 1:
        first_e = next((e for e in logs if str(e.get("章")) == "1" or e.get("章") == 1), None)
        outline = (first_e or {}).get("产物", {}).get("大纲") if first_e else None
        if not outline:
            errors.append("第1章｜产物缺登记: 大纲（首章交付前置——大纲为第一章必需产物）")
        else:
            ofp = os.path.realpath(os.path.join(root, outline))
            if not os.path.isfile(ofp) or not ofp.startswith(root + os.sep):
                errors.append(f"第1章｜大纲文件不存在或越出项目目录: {outline}")
            else:
                otext = open(ofp, encoding="utf-8").read()
                for mark in ("★主题材契约", "基调核心循环", "主冲突线"):
                    if mark not in otext:
                        errors.append(f"第1章｜大纲契约块不完整（缺「{mark}」标记）")
                        break
                    # 非空判定（防复制空模板即过）：取标记所在行，剥离 HTML 注释与冒号/空白后须有实值。
                    # ★主题材契约 是节标题，只查存在；基调核心循环/主冲突线 是字段，须有非空值。
                    if mark != "★主题材契约":
                        line = next((ln for ln in otext.splitlines() if mark in ln), "")
                        val = re.sub(r"<!--.*?-->", "", line.split(mark, 1)[1]).strip().lstrip("：:* ").strip()
                        if not val:
                            errors.append(f"第1章｜大纲契约块「{mark}」为空（仅标签/注释，无实值）——复制空模板不算已填大纲")
                            break
    if args.precheck:
        print("PRECHECK [10] 已豁免：机检运行／交付闸 两字段待回填（bootstrap 第一步）")
    for e in logs:
        try: ch = int(e.get("章"))
        except (TypeError, ValueError): ch = e.get("章", "?")
        if args.chapter is not None and ch != args.chapter:
            pass  # 关注章外仍全量检查（历史章 FAIL 一并报）
        # [0-b] 模板初值黑名单：占位值出现＝未真实执行（防"复制模板即合规"）
        for _k in ("选定模式", "实际执行模式", "审查深度", "机检运行", "交付闸", "自查覆盖"):
            # --precheck 时这两字段尚未回填，占位值属正常，不作初值黑名单判定
            if args.precheck and _k in ("机检运行", "交付闸"):
                continue
            _v = str(e.get(_k, "") or "").strip()
            if _v in ("待填", "待运行", "未过", "待查"):
                fail(ch, f"字段「{_k}」仍为模板占位值「{_v}」——未真实执行，须实跑后回填")
        sel, act = e.get("选定模式"), e.get("实际执行模式")
        if sel not in MODE_AGENTS: fail(ch, f"选定模式非法: {sel}"); continue
        if fixed_mode and fixed_mode != sel:
            fail(ch, f"选定模式({sel})≠固定属性({fixed_mode})")
        # [3] 模式保真（降级禁止：一律相等）
        if sel != act:
            fail(ch, f"选定{sel}实际{act}——降级禁止：选定模式全书锁定，须按选定模式重跑完整流程")
        # [4] 调用代理凭证化＋互异
        names, creds, structured = parse_agents(e.get("调用代理"))
        if act in MODE_AGENTS:
            required = list(MODE_AGENTS[act])
            missing = [x for x in required if x not in names]
            if missing: fail(ch, f"调用代理缺必需集: {missing}")
            if act in ("pro", "max"):
                if not structured:
                    fail(ch, "调用代理为纯名字列表（未凭证化）——pro/max 须结构化[角色+凭证]")
                else:
                    for r in required:
                        if not (creds or {}).get(r, "").strip():
                            fail(ch, f"调用代理[{r}]无宿主调用凭证——未经验证的声明")
                    present = [creds[r] for r in required if (creds or {}).get(r, "").strip()]
                    if len(present) != len(set(present)):
                        fail(ch, "同章各角色凭证须两两互异——同凭证签多角色＝合并扮演")
        # [5][6] 产物三验＋生成指纹
        prods = e.get("产物") or {}
        for k in MODE_PRODUCTS.get(act, []):
            v = prods.get(k)
            if not v: fail(ch, f"产物缺登记: {k}"); continue
            fp = os.path.realpath(os.path.join(root, v))
            if not fp.startswith(root + os.sep) and fp != root:
                fail(ch, f"产物路径越出项目目录: {k}={v}"); continue
            if not os.path.isfile(fp): fail(ch, f"产物文件不存在: {k}={v}"); continue
            try:
                nb = [l for l in open(fp, encoding="utf-8").read().splitlines() if l.strip()]
            except Exception:
                nb = None
            if not nb: fail(ch, f"产物文件为空/不可读: {k}={v}"); continue
            if act in ("pro", "max"):
                role = (ROLE_OF_PRODUCT if act == "max" else ROLE_OF_PRODUCT_PRO).get(k)
                fpv, _ = tail_fingerprint(fp)
                want = (creds or {}).get(role, "")
                if not fpv:
                    fail(ch, f"产物[{k}]末行缺「生成指纹:」行")
                elif not want or fpv != want:
                    fail(ch, f"产物[{k}]生成指纹 {fpv} ≠ {role}凭证——签发角色不符")
        # [7][8] 覆盖＋输入隔离
        cov = str(e.get("稽查全覆盖", ""))
        rp_text = sc_text = draft_text = ""
        if act == "flash":
            if "不适用" not in cov: fail(ch, "flash 须记 不适用")
        else:
            m = re.match(r"^(\d+)/(\d+)$", cov)
            n_req = len(REQUIRED_DIMS)
            if not m or m.group(1) != str(n_req) or m.group(2) != str(n_req):
                fail(ch, f"稽查全覆盖应为 {n_req}/{n_req}（必判维度；其余维涉及时再判），实为: {cov or '空'}")
            rp = prods.get("审查报告")
            if rp:
                fp = os.path.realpath(os.path.join(root, rp))
                if os.path.isfile(fp) and fp.startswith(root + os.sep):
                    rp_text = open(fp, encoding="utf-8").read()
                    # v9：判定向量只取「主报告」区，复核/复核补段一律剥离——
                    # 复核逐项对应维度是职业本能，写成「维度N｜解决」会覆盖主判定（BUG-008）
                    rp_main = re.split(r"\n##\s*复核", rp_text)[0]
                    dims = set(int(x) for x in re.findall(r"维度\s*(\d+)", rp_main))
                    if not REQUIRED_DIMS <= dims:
                        fail(ch, f"审查报告必判维度缺: {sorted(REQUIRED_DIMS - dims)}"
                                 f"（必判 {len(REQUIRED_DIMS)} 维，见 core/cold-review.md#三）")
                    # v9.1：问 7（情绪是否落地）为新增必答项；读到 6 问仍放行以兼容旧报告，
                    # 但只到 6 问时给 WARN，提示补问 7
                    nq = len(set(re.findall(r"问\s*([1-7])\s*[｜|]", rp_text)))
                    if nq == 6:
                        warns.append(f"第{ch}章｜审查报告只答到读感第 6 问——"
                                     f"v9.1 起须补第 7 问（她在乎什么，我能不能说出来），见 core/cold-review.md#〇")
                    if nq < 6:
                        fail(ch, f"审查报告读感七问仅 {nq}/7（格式「问N｜答案｜引文」）——"
                                 f"冷读第一动作未做，见 core/cold-review.md#〇；仅答 6 问按 WARN 兼容旧报告")
                    # 判定值枚举（维度行判定域须为 通过/不通过/不适用）
                    # v9.3（BUG-047）：判定列截到第一个全角/半角左括号为止再匹配——
                    # 审查员常想在判定旁加限定（「不通过（设定层）」），严格截断会取到半截串。
                    # 括注本身不违规（说明应写第三列），故宽容取前缀，不因写法把人卡死。
                    bad_v = []
                    for m2 in re.finditer(r"维度\s*(\d+)\s*[｜|]\s*([^\s｜|，。（(]+)", rp_main):
                        if m2.group(2) not in VERDICT_SET:
                            bad_v.append(f"维度{m2.group(1)}:{m2.group(2)}")
                    if bad_v:
                        fail(ch, f"审查报告判定值非法（须 通过/不通过/不适用）: {'；'.join(bad_v[:3])}"
                                 f"——**判定列只放纯值**，说明请写到第三列（`维度N｜通过｜结论＋引文`）")
                    # 输入清单段必须存在
                    if "输入清单" not in rp_text:
                        fail(ch, "审查报告缺「输入清单」段（须列收到的文件）")
                    # 独立发现（对应 core/cold-review.md#五 受理验收④）：
                    # 本项只判「审查侧有没有实质发现」——≥1 条维度判定「不通过」，或「## 反证轮」≥3 段核验。
                    # 「是否自查未发现」不在此判（审查员依③看不到自查报告，无法自证）：
                    #   由下方 [13] 同源判定用 selfcheck_dim_vector(自查) 比对兜底，主代理受理时裁定。
                    # （旧口径只看"不通过"三字是否出现——写"本轮无一项不通过"即可绕过，已废）
                    rp_fails = [k for k, v in verdict_vector(rp_text).items() if v == "不通过"]
                    rebut_ok = False
                    rb = re.search(r"^#{1,4}\s*反证轮.*$", rp_text, re.M)
                    if rb:
                        seg = rp_text[rb.end():]
                        nx = re.search(r"^#{1,4}\s", seg, re.M)
                        body = seg[:nx.start()] if nx else seg
                        paras = [x for x in re.split(r"\n\s*\n", body) if len(x.strip()) >= 20]
                        rebut_ok = len(paras) >= 3
                    if not rp_fails and not rebut_ok:
                        fail(ch, "审查报告零实质发现（须 ≥1 条维度判定「不通过」，"
                                 "或「## 反证轮」小节含 ≥3 段实质核验——只写「无问题」不算）。"
                                 "注：「是否自查未发现」由 [13] 同源判定比对、主代理受理时裁定，"
                                 "不要求看不到自查报告的审查员自证")
                    scf = prods.get("自查报告")
                    if scf and scf in rp_text:
                        fail(ch, f"审查报告出现自查报告文件名（{scf}）——输入污染：冷读者不得看自查结论")
                    # [12] 主语污染（先剥离引号内草稿引文——审查员引证草稿对话/第一人称叙述含「我写」等属合法引文，
                    # 只搜审查员自己的叙述文字，防误报；与 S42 破折号检查同口径剥离引号）
                    rp_plain = re.sub(r"[「『“][^」』”]*[」』”]", "", rp_text)
                    pm = PERSONA_PAT.search(rp_plain)
                    if pm:
                        fail(ch, f"审查报告含主上下文人称模式（「{pm.group(0)}」）——独立子代理无创作过程记忆，判非独立")
        dp = prods.get("章草稿")
        if dp:
            fp = os.path.realpath(os.path.join(root, dp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                draft_text = open(fp, encoding="utf-8").read()
        # [9] 自查覆盖（分级）：按账本 自查档 取期望全集——标准 G01–G12 共 12/12（组；
        #     机检 11 项由 [18] 代判不占自查行）、lite 5/5（短篇核心组）＋组全集＋行数断言
        self_tier = str(((data.get("当前状态") or {}).get("自查档")) or "标准").strip()
        if self_tier not in ("标准", "lite"):
            fail("本章", f"自查档取值非法: {self_tier or '空'}（须 标准 | lite，短篇 lite 见 templates/chapter.md lite 节）")
            self_tier = "标准"
        expect_ids = LITE_GROUPS if self_tier == "lite" else GROUP_IDS
        n_exp = len(expect_ids)
        sc = str(e.get("自查覆盖", ""))
        m = re.match(r"^(\d+)/(\d+)$", sc)
        if not m or m.group(1) != str(n_exp) or m.group(2) != str(n_exp):
            fail(ch, f"自查覆盖应为 {n_exp}/{n_exp}（{'lite 核心组' if self_tier == 'lite' else '12 组；机检 11 项由 gatecheck [18] 代判'}），实为: {sc or '空'}")
        srp = prods.get("自查报告")
        if srp:
            fp = os.path.realpath(os.path.join(root, srp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                sc_text = open(fp, encoding="utf-8").read()
                ids = set(re.findall(r"\b(G\d\d)\b", sc_text))
                sid_noise = sorted(set(re.findall(r"\b(S\d\d)\b", sc_text)))
                if ids != expect_ids:
                    miss = sorted(expect_ids - ids)[:4]
                    extra = sorted(ids - expect_ids)[:3]
                    if sid_noise and not ids:
                        fail(ch, f"自查报告用了旧 S 编号行 {sid_noise[:3]}——v8.0.0 起按 12 组"
                                 f"（G01–G12）汇总，组定义见 templates/chapter.md")
                    else:
                        fail(ch, f"自查报告组集合不全（缺 {miss}{'；多余 ' + str(extra) if extra else ''}）"
                                 f"——须逐组列本档全部组（{'lite 5 组' if self_tier == 'lite' else '标准 12 组'}）")
                # [9-b] 判定行断言：须与全集等行数「Sxx｜判定」，判定值合法
                srows = []
                for _ln in sc_text.splitlines():
                    _m = re.match(r"^\s*G(\d\d)\s*[｜|]\s*([^\s｜|，。\n]+)", _ln)
                    if _m:
                        srows.append((_m.group(1), _m.group(2)))
                if len(srows) != n_exp:
                    fail(ch, f"自查报告判定行 {len(srows)}/{n_exp}——每组须写成「Gxx｜判定｜组名｜证据」；"
                             f"只列组号不写判定＝判定向量为空，同源判定会静默失效")
                bad_sv = [f"G{n}:{v}" for n, v in srows
                          if SELF_MARK.get(v, v) not in VERDICT_SET]
                if bad_sv:
                    fail(ch, f"自查判定值非法（须 通过/不通过/不适用，或 ✓/✗）: {'；'.join(bad_sv[:3])}"
                             f"——**判定列只放纯值**，说明请写证据列（`Gxx｜通过｜组名｜证据`）")
                # 不适用白名单（调整后：S48/S49 转机检后移出；lite 档 10 项均须实判）
                NA_ALLOWED = set() if self_tier == "lite" else {"09", "12"}
                bad_na = sorted({f"S{n}" for n, v in srows
                                 if SELF_MARK.get(v, v) == "不适用" and n not in NA_ALLOWED})
                if bad_na:
                    fail(ch, f"这些自查组不成立「不适用」: {bad_na[:4]}——"
                             f"不适用只允许 G09（无开篇雷同检查场景/无 devotee 角色）/G12（flash 无冷读）；"
                             f"其余须判 通过 或 不通过")
                # v9：覆盖行改全文定位。旧版只查末三行（含指纹行时更窄），
                # 与「附页随报告落盘」直接冲突，第 1、2 章各失败一次（BUG-009/017）
                tm = None
                for l in sc_text.splitlines():
                    tm = re.search(r"自查覆盖[:：]\s*(\d+)\s*/\s*(\d+)", l)
                    if tm: break
                if not tm: fail(ch, f"自查报告缺『自查覆盖: {n_exp}/{n_exp} 全查』机检锚: {srp}")
                elif tm.group(1) != str(n_exp) or tm.group(2) != str(n_exp):
                    fail(ch, f"自查报告 {tm.group(1)}/{tm.group(2)} ≠ {n_exp}/{n_exp}")
                # [18-S48/S49] 附页 A/B 结构机检：pro/max 须附页已填（行数证据存在）；
                # ❌ 不设行数下限——有多少句查多少句，全覆盖属语义判定（冷读维度 17）；
                # A:0/B:0 合法（本章无发力支撑句/无可比对句），防固定行数下限逼造动作链与元素过密。
                if self_tier == "标准":
                    ma = re.search(r"(?<![A-Za-z0-9])A[:：]\s*(\d+)", sc_text)
                    mb = re.search(r"(?<![A-Za-z0-9])B[:：]\s*(\d+)", sc_text)
                    if act in ("pro", "max"):
                        if not ma:
                            fail(ch, "S48 附页A支点三问未填——须「A:N」行数证据（pro/max 必填，逐句全覆盖，N 可为 0）")
                        if not mb:
                            fail(ch, "S49 附页B示范比对未填——须「B:N」行数证据（pro/max 必填，逐句全覆盖，N 可为 0）")
                    elif not (ma and mb):
                        warns.append(f"第{ch}章｜S48/S49 附页 flash 为建议项（未填不阻断），pro/max 升级后必填")
        # [18-S42] 正文文本模式机检：标点三禁（叙述层破折号 0／解释性冒号 0／翻案句 0）
        # ＋ 注释式纠错变体 0（对话白名单：先剥离「」『』“” 引号内文本再计数）
        # v8.0.0 起取消配额制（旧版每章限若干处）——配额等于发通行证，实测一章用到 18 处
        if draft_text:
            plain = re.sub(r"[「『“][^」』”]*[」』”]", "", draft_text)
            ndash = plain.count("——")
            if ndash > 0:
                fail(ch, f"S42 叙述层破折号 {ndash} 处（上限 0；对话内白名单已剥离）——"
                         f"要停就断句，见 core/style.md#标点与句式三禁（叙述层）")
            ncolon = len(re.findall(r"[^：:\s]：[^\s「『“]", plain))
            if ncolon > 0:
                fail(ch, f"S42 叙述层解释性冒号 {ncolon} 处（上限 0；对话提示语后的冒号合法）")
            # v9.2（BUG-033）：旧正则只认带「而是」的完整式，漏掉中文里最常见的两种断法，
            # 「不是X，是Y」（逗号断开）与「不是X。是Y」（句号断开）。实测曾出现冷读报 5 处、
            # 机检报 0 处。假阴性比误报危险，它给出一个让人放心的「0」。
            _w = plain
            for _wl in ("要不是", "不是没", "不是不", "不但", "不经"):
                _w = _w.replace(_wl, "□" * len(_wl))
            flips = re.findall(
                r"不是[^。\n]{1,20}而是"                        # 不是X而是Y（完整式）
                r"|不是[^。\n，]{1,20}[，,]\s*(?:而)?是"         # 不是X，是Y ／ 不是X，而是Y
                r"|不是[^。\n]{1,20}。(?:而)?是"                 # 不是X。是Y
                r"|并非[^。\n]{1,20}(?:而)?是"
                r"|不在于[^。\n]{1,20}而在于"
                r"|与其说[^。\n]{1,20}不如说"
                r"|看似[^。\n]{1,20}实则", _w)
            if flips:
                fail(ch, f"S42 叙述层翻案句 {len(flips)} 处（上限 0）：{flips[:2]}——"
                         f"拆回事实陈述，见 core/style.md#三禁 翻案句")
            # 倒装式「Y，不是X」也是翻案（先立判断再否定），但单处很可能是正常的事实纠正
            # （「他姓周，不是姓邹」「这是三十文，不是二十文」都会命中）。故只在同章 ≥2 处时提示：
            # 单次是陈述，反复用同一个句式才是套路。
            rev = re.findall(r"[^。\n，]{2,14}[，,]\s*不是[^。\n，]{1,16}(?![吗呢])", _w)
            if len(rev) >= 2:
                warns.append(f"第{ch}章｜S42 倒装翻案 {len(rev)} 处（先立判断再否定，如「X是A，不是B」）："
                             f"{rev[:2]}——单处可能是事实纠正，同章反复用就是固定句式，"
                             f"改成并列陈述或删掉否定半句")
            fixes = re.findall(r"——(不对|不，)|不是[^。\n]{1,12}——是|——[^。\n]{1,6}——", plain)
            if fixes:
                fail(ch, f"S42 注释式纠错变体 {len(fixes)} 处（正文零容忍，变体家族见 core/style.md#★禁止注释式纠错）")
        # [23] 器具禁令词表（v9.2 新增，BUG-032）
        # 该禁令标题叫「损耗与更换」，实际禁止范围还含缠布、调校、以及任何人对它的议论——
        # 标题比内容窄，凭标题判断必漏（实测：作者判定「缠布不是损耗」而写进正文）。
        # 故改为机检扫描，不再依赖作者记得住四类范围。禁令④含台词与内心独白，故不剥离引号。
        if draft_text:
            _hard = [
                (r"重新缠|重缠|换缠布|拆开缠", "缠布／重缠（禁令② 维修）"),
                (r"换拐头|换胶垫|换防滑套|换防滑垫|配一副新|做一副新|配个新的",
                 "更换辅具部件（禁令②）"),
                # 部件名 + 六字内的磨损动词（不能只写「拐头」——胶垫、杖尖、杆身同样在禁令①内）
                (r"(拐头|杖尖|胶垫|胶皮|拐身|杆身|手柄)[^。\n]{0,6}(磨平|磨薄|磨亮|磨秃|磨光|起毛|开裂)"
                 r"|磨出包浆|磨出白边|防滑纹磨光|橡胶老化", "部件损耗（禁令①）"),
            ]
            _soft = [
                (r"送修|返厂|调校|找匠人修|找人修", "送修／调校（禁令②）"),
                # 「磨出包浆」已由 hard 命中，此处排除，免得同一处报两遍
                (r"(?<!磨出)包浆", "包浆（禁令① 变体）"),
                (r"该换一副|该换个新的|用了多少年了", "对辅具的议论（禁令④）"),
            ]
            for _pat, _why in _hard:
                _m = re.search(_pat, draft_text)
                if _m:
                    _a, _b = max(0, _m.start() - 12), min(len(draft_text), _m.end() + 12)
                    _ctx = re.sub(r"\s+", " ", draft_text[_a:_b]).strip()
                    # 即时事由豁免（v9.5 修跨题材冲突）：
                    # genre/postapocalyptic.md 明写「拐头包布静音」是末世核心动作，
                    # audience.md 也写明「有即时事由（防滑／止血／静音）＝豁免，
                    # 住下之后拆开重缠一遍＝维修保养才违规」。
                    # 但词表原先不认语境，扫到「重缠」一律 FAIL——规则有豁免，机检没实现，
                    # 于是整类末世写法被误伤。判据：命中处前后 30 字内有事由词 → 降为 WARN。
                    _wa, _wb = max(0, _m.start() - 30), min(len(draft_text), _m.end() + 30)
                    _win = re.sub(r"\s+", "", draft_text[_wa:_wb])
                    if re.search(r"静音|不响|出声|声音|防滑|止血|消音|包住|裹住|压住声", _win):
                        warns.append(
                            f"第{ch}章｜S19 疑似器具禁令（{_why}）：「…{_ctx}…」"
                            f"——上下文有即时事由（静音／防滑／止血），按 audience 属**豁免**；"
                            f"请人工确认是「临时处置」还是「住下来之后的维护保养」，后者仍须删")
                        continue
                    fail(ch, f"S19 器具禁令命中（{_why}）：「…{_ctx}…」——"
                             f"本条是禁令不是限频，根本不写。范围见 "
                             f"core/audience.md#★器具损耗与更换禁令")
            for _pat, _why in _soft:
                _m = re.search(_pat, draft_text)
                if _m:
                    _a, _b = max(0, _m.start() - 12), min(len(draft_text), _m.end() + 12)
                    _ctx = re.sub(r"\s+", " ", draft_text[_a:_b]).strip()
                    warns.append(f"第{ch}章｜S19 疑似器具禁令（{_why}）：「…{_ctx}…」"
                                 f"——若写的是辅具即违规；写的是别的东西可忽略")
        # [24] 章节登记归档（v9.2，BUG-037）：`本章登记` 写完下一章即被覆盖，
        # 历史章的 beat／turn／钩型／受限 beat 全部丢失——跨章比对缺数据源，日后复盘也查不到。
        # 缺归档只 WARN，不阻断（旧项目无此块属正常）。
        try:
            _arc = data.get("章节登记归档") or []
            _have = set()
            for _a in _arc:
                if isinstance(_a, dict) and _a.get("章") is not None:
                    try:
                        _have.add(int(_a.get("章")))
                    except (TypeError, ValueError):
                        pass
            _cur_i = int(str((data.get("当前状态") or {}).get("章", "") or "0").strip() or "0")
            _miss = [n for n in range(1, _cur_i + 1) if n not in _have]
            if _miss and _cur_i and _cur_i == ch:
                warns.append(f"第{ch}章｜[24] 章节登记归档缺章号 {_miss[:6]}——"
                             f"`本章登记` 是单章结构，不归档则历史 beat/turn/钩型全丢，"
                             f"见 core/workflow.md#登记归档")
        except Exception:
            pass
        # [25] 枚举表一致性：账本 `枚举表` 是给人和机器共读的枚举数据块，与脚本常量必须一致。
        # 不一致说明改了一处忘了另一处——文档说一套、机检判一套，作者按哪边写都可能被判违规。
        try:
            _et = data.get("枚举表") or {}
            _et_cur = str((data.get("当前状态") or {}).get("章", "") or "").strip()
            if isinstance(_et, dict) and _et:
                for _k, _set in (("主冲突线beat", BEAT_ENUM), ("自查判定", VERDICT_SET),
                                 ("受限层级", LIMIT_ENUM), ("章节功能", FUNC_ENUM),
                                 ("章末钩子类型", HOOK_ENUM)):
                    _vals = _et.get(_k)
                    if not isinstance(_vals, list):
                        continue
                    _a = set(str(x) for x in _vals)
                    # 脚本侧剔除别名（如「通过.带条件」是「通过·带条件」的兼容写法，不入表）
                    _b = set(str(x) for x in _set if "." not in str(x))
                    if _a != _b:
                        warns.append(f"第{ch}章｜[25] 枚举表「{_k}」与脚本常量不一致："
                                     f"表有脚本无 {sorted(_a - _b)}；脚本有表无 {sorted(_b - _a)}"
                                     f"——改枚举须两处同改（templates/state-ledger.yaml 枚举表 ＋ gatecheck 常量）")
            elif _et_cur and _et_cur == str(ch):
                # 旧项目从旧模板复制、或账本曾被脚本整份重写：注释与枚举可能已蒸发
                warns.append(f"第{ch}章｜[25] 账本无「枚举表」块——若本账本曾被脚本整份重写"
                             f"（yaml.safe_dump 等），字段后的枚举注释已全部丢失，填表将失去唯一依据。"
                             f"从 templates/state-ledger.yaml 末尾复制该块即可（只读参考，不影响判定）")
        except Exception:
            pass
        # [26] 豁免类动作词表（v9.3，BUG-049）：某些动作对该类型是**正式豁免**，写「做不了」即错。
        # 实测：一章之内写了两次「蹲不下去」，而单腿蹲是该类型明确豁免，且前一章她刚蹲着捡过米。
        # 这类错自查抓不到（写时自洽）、冷读要读 types 才判，只能靠词表兜。
        if draft_text:
            _p26 = re.sub(r"[「『“][^」』”]*[」』”]", "", draft_text)
            _typ = str((data.get("角色固定属性") or {}).get("截肢类型", "") or "")
            _single_lower = any(k in _typ for k in ("髋离断", "膝上", "膝下"))
            for _pat, _why in [
                (r"蹲不下|蹲不了|没法蹲|不能蹲",
                 "单腿蹲是本类型正式豁免（健腿单蹲＋一手支撑即可）。要写受限应写"
                 "「蹲着没法用两只手」，不是「蹲不下」——见 topics/daily-actions.md#蹲"),
                # 注：跪**不列入**本词表——髋离断等类型「跪不了」是 types 明写的真受限
                # （types/hip-disarticulation.md:159「跪不了：需要跪姿的事做不到」），
                # 写「跪不下去」是对的。只有「蹲」是豁免，别把两者混为一谈。
            ]:
                _m = re.search(_pat, _p26)
                if not _m:
                    continue
                _a, _b = max(0, _m.start() - 15), min(len(_p26), _m.end() + 15)
                _ctx = re.sub(r"\s+", " ", _p26[_a:_b]).strip()
                _msg = (f"S19 豁免类动作写错（{_why}）：「…{_ctx}…」")
                if _single_lower or "肘" in _typ or "肩" in _typ:
                    fail(ch, _msg)
                else:
                    warns.append(f"第{ch}章｜{_msg}——双侧类型请核对 types 是否豁免")
        # [27] 场景驱动四问（v9.4，FAIL）：chapter-contract-N.md 写作卡末尾「四行硬项」不得为空。
        # 立条原因（实测）：一章改 5 版仍在返工，根因不是句子，是「五件事答得出但第 3/4/5 件是空的」
        # ——第 3 件填「跟着走了一圈」，第 4、5 件填「无」；机检全绿、段落指标全达标，读起来是清单。
        # 规则写进 core/scene-drive.md 没人执行；只有「落盘 + 机检」拦得住（同 [23]/[26] 的教训）。
        # 只检「--chapter 指定的那一章」：历史章的契约多按旧模板填，拿新四行去验必然误报
        # （同 [20] 的教训）。未指定 --chapter 时整项跳过——不知道要交付哪章，就没有验收对象。
        # 另：已交付章豁免（交付闸 PASS）——新规不追溯，否则规则一升级历史章全废，
        # 作者会被逼着重填旧契约，而旧章的情节并没有变。
        _delivered27 = str(e.get("交付闸", "") or "").strip() in ("通过", "PASS", "pass")
        if args.chapter and ch == args.chapter and not _delivered27:
            _cf = os.path.join(root, f"chapter-contract-{ch}.md")
            _hard4 = [
                ("动手次数与失败点", "这一章没有任何一次「可能失败」的动手——全是做事，不是戏"),
                ("对手今天本来想干什么", "配角只剩功能、没有自己的目标，所有角色朝同一方向划桨"),
                ("篇幅第一名是谁", "权重未排——重要的那件事会被写得比搬东西还短，读者只能当清单读"),
                ("她的三处不在状态", "人是机器：每个动作都完整准确，没有一处多余、迟疑或改主意"),
            ]
            if not os.path.isfile(_cf):
                warns.append(
                    f"第{ch}章｜[27] 未找到 chapter-contract-{ch}.md——场景驱动四问无处落盘。"
                    f"按 templates/chapter-contract.md 补建（至少填「★四行硬项」）后再开写")
            else:
                _ct = open(_cf, encoding="utf-8").read()
                for _k, _why in _hard4:
                    _m = re.search(r"\*\*" + re.escape(_k) + r"\*\*\s*[:：]\s*(.*)", _ct)
                    _v = ""
                    if _m:
                        _v = re.split(r"[（(]", _m.group(1))[0]
                        _v = re.sub(r"[＿_\s﹍/／|｜、,，。·…\-—]+", "", _v)
                    if len(_v) <= 1 or _v in ("无", "没有", "待定", "空", "略"):
                        fail(ch, f"场景驱动四问未答「{_k}」——{_why}。"
                                 f"问法见 core/scene-drive.md#七；答不出＝这章还没有戏，"
                                 f"改事件（加一次会失败的动手），❌ 不要用描写补")
        # [28] 创作注记残留（v9.4，WARN）：正文里留下写给自己看的东西。
        # 实测：第 3 章初稿留了 2 处，第 4 章留了 13 处（张力越高，越需要给自己打拍子）。
        # 首版靠关键词词表（核心句/伏笔/不在状态），实测只能抓模式化的，
        # 抓不到自由书写的「（他站着，她坐着）」「（语气变了，她听懂了）」。
        # 改为**一律报**：小说正文里，独立成段的全角括号几乎只有一种用途，就是作者注记。
        # 合法例外（引文块、字幕、短信原文）若有，人工看过后忽略即可，WARN 不阻断。
        # _htag28 同时供 [28]/[29] 用，提到条件外面，避免依赖前一块的局部变量
        _cur28 = str((data.get("当前状态") or {}).get("章", "") or "").strip()
        _htag28 = "" if (not _cur28 or _cur28 == str(ch)) else "（历史章·非当前章）"
        if draft_text:
            _kw28 = re.compile(r"不在状态|核心句|伏笔|自查|判据|机检|待改|待补|这一段|这段要|峰值|节奏", re.I)
            for _m in re.finditer(r"(?m)^[ \t]*[（(]([^）)]{2,})[）)][ \t]*$", draft_text):
                _inner = _m.group(1)
                _mark = "疑似创作注记" if _kw28.search(_inner) else "独立括号段"
                warns.append(f"第{ch}章{_htag28}｜[28] {_mark}「{_inner[:28]}」"
                             f"——两种可能：①写给自己看的注记，交付前删；"
                             f"②括号独白（把内心计算用括号外挂），属风格选择，"
                             f"但**全章超过 5 处就不再是风格，是把叙述外包给了注释**（实测一章 33 处）；"
                             f"引文/字幕等排版需要，人工确认后忽略")
        # [29] 表情套话词表（v9.5，WARN）：最常被用来"给人物加表情"的那批词，
        # 恰恰是读者识别"这是套路"的第一批信号。中文网文有专门的帖子问
        # 「除了冷哼一声还能怎么写」，底下给的全是同义词（冷嗤／轻嗤／哂／讥诮），换汤不换药。
        # 正解不是换词，是换成可观察的动作（core/emotion-signal.md#二）：
        # 「他从鼻子里出了一口气，没接话」比「他冷哼一声」多一层信息，且读者能自己下结论。
        # 只扫叙述层：对话引号里人物说「哼」是合法台词，不该拦。
        if draft_text:
            _p29 = re.sub(r"[「『“][^」』”]*[」』”]", "", draft_text)
            _pat29 = [
                (r"冷哼一声|冷嗤|轻嗤|嗤笑|哂笑|哂然|讥诮", "冷嘲类"),
                (r"眸光|眼底(?:闪过|划过|浮起|掠过)|眸色|目光深邃|眼神幽深",
                 "眼神类（看不见的东西，读者只能接受结论）"),
                (r"嘴角(?:勾起|微扬|抽搐)|勾唇|扯出一抹|扯了扯嘴角|唇角",
                 "嘴角类"),
                (r"露出一丝|浮现出一丝|闪过一抹|划过一抹|泛起一丝", "微量情绪类"),
                (r"意味深长|不置可否|神色莫辨|神色不明|看不出喜怒", "模糊评价类"),
            ]
            for _pat, _kind in _pat29:
                _m29 = re.search(_pat, _p29)
                if not _m29:
                    continue
                _a29, _b29 = max(0, _m29.start() - 12), min(len(_p29), _m29.end() + 12)
                _ctx29 = re.sub(r"\s+", " ", _p29[_a29:_b29]).strip()
                warns.append(
                    f"第{ch}章{_htag28}｜[29] 表情套话（{_kind}）：「…{_ctx29}…」"
                    f"——换成能看见的动作（他把话咽回去／她笑得自己收住了／"
                    f"看她的时间比该有的长了一点）。判据见 core/emotion-signal.md#二")
        # [30] 幻想向真实战斗冲突（v9.6，R-033 的可形式化部分）：
        # 只判「非战斗化词表／复用信号／台账同域同招法」；「有死有伤／过程丰富／按选定强度」
        # 属语义半区，交章末 G01/G07/G08、冷读维度 9/10/21 与双简报第三节，❌ 不冒充语义判定。
        _genre30 = str((data.get("题材契约") or {}).get("题材大类", "") or "").strip()
        _reg30 = data.get("本章登记") or {}
        _func30 = str(_reg30.get("章节功能", "") or "").strip()
        _lb30 = str(_reg30.get("主冲突线beat", "") or "").strip()
        _foe30 = str(_reg30.get("敌方阶", "") or "").strip()
        _battle30 = (_func30 == "对抗危机" or _lb30 == "对抗"
                     or (_foe30 and _foe30 not in ("无", "—", "-")))
        _is_fantasy30 = _genre30 == "幻想向"
        _cur30 = str((data.get("当前状态") or {}).get("章", "") or "").strip()
        _now30 = (not _cur30 or _cur30 == str(ch))
        if _is_fantasy30 and _battle30 and draft_text:
            _p30 = re.sub(r"[「『“][^」』”]*[」』”]", "", draft_text)
            for _pat30, _why30 in [
                (r"没有动手|并未交手|不曾交手|没打起来|最终没有打|不战而屈人之兵",
                 "冲突被写成非战斗冲突"),
                (r"经过一番(?:周旋|交涉|对峙)|一番(?:周旋|交涉)之后|误会(?:就此)?化解|"
                 r"最终(?:握手|和解|谈妥|各自散去)|只是(?:对峙|僵持)",
                 "用概述或协商把交锋带过"),
            ]:
                _m30 = re.search(_pat30, _p30)
                if not _m30:
                    continue
                _a30, _b30 = max(0, _m30.start() - 15), min(len(_p30), _m30.end() + 15)
                _ctx30 = re.sub(r"\s+", " ", _p30[_a30:_b30]).strip()
                _msg30 = (f"[30] 幻想向战斗冲突非战斗化（{_why30}）：「…{_ctx30}…」"
                          f"——R-033 禁止把登记为战斗的冲突定义为非战斗冲突；"
                          f"须真打、有死有伤、按选定强度写足回合（genre/fantasy.md 第十一节）")
                if _now30:
                    fail(ch, _msg30)
                else:
                    warns.append(f"第{ch}章（历史章·非当前章）｜{_msg30}")
            if re.search(r"又一次(?:打|交手|遇上|施展)|像上次(?:那|一)?样|和上次(?:一样|相同)|同上章", _p30):
                warns.append(f"第{ch}章{_htag28}｜[30] 正文出现战斗过程复用信号——"
                             f"R-033 禁止复用已有战斗过程；核开局态势/攻防转换顺序/决胜招/伤亡后果四要素")
            _led30 = data.get("解法台账") or []
            if isinstance(_led30, list):
                _seen30 = {}
                for _r30 in _led30:
                    if not isinstance(_r30, dict):
                        continue
                    try:
                        _c30 = int(_r30.get("章", 0) or 0)
                    except (TypeError, ValueError):
                        continue
                    if not (ch - 5 <= _c30 <= ch):
                        continue
                    _k30 = (str(_r30.get("场景域", "") or "").strip(),
                            str(_r30.get("招法", "") or "").strip())
                    if all(_k30):
                        _seen30[_k30] = _seen30.get(_k30, 0) + 1
                for _k30, _n30 in _seen30.items():
                    if _n30 >= 2:
                        warns.append(f"第{ch}章{_htag28}｜[30] 近 5 章同场景域同招法 {_n30} 次"
                                     f"（{_k30[0]}／{_k30[1]}）——战斗过程/解法复用，须换招或升级"
                                     f"（core/chapter-planning.md#一-补3、genre/fantasy.md 第十一节）")
        # [31] 默认性格禁令（R-034 全类型）与题材分割（R-032）：
        _fixed31 = data.get("角色固定属性") or {}
        _persona31 = f"{_fixed31.get('性格', '') or ''} {_fixed31.get('声口', '') or ''}"
        _hits31 = [w for w in ("话少", "冷漠", "沉默寡言", "寡言", "高冷", "冷淡", "不爱说话", "话不多")
                   if w in _persona31]
        if _hits31:
            _src31 = (str(data.get("用户指令变更") or "")
                      + str((data.get("本章登记") or {}).get("用户指令变更") or ""))
            if not any(w in _src31 for w in _hits31):
                fail(ch, f"[31] 角色默认性格命中禁用词 {_hits31}——R-034 全类型禁止把"
                         f"话少／冷漠／沉默寡言当默认性格；须溯源用户原话或改填声音卡五项"
                         f"（core/character-setup.md「★默认性格禁令」节）")
        if not _genre30 and ch == (chs[-1] if chs else None):
            warns.append("[31] 账本 题材契约.题材大类 未登记——[30]/[31] 的题材判定退化为跳过；"
                         "按 templates/outline.md#★主题材契约 补填（旧账本兼容提示，只报一次）")
        _bx31 = data.get("战斗豁免") or {}
        _tier31 = str(_bx31.get("档位", "") or "").strip() if isinstance(_bx31, dict) else ""
        if _genre30 and not _is_fantasy30 and _tier31 and _tier31 not in ("无", "E0", "—", "-"):
            fail(ch, f"[31] 题材分割越界：题材大类「{_genre30}」非幻想向，"
                     f"战斗豁免档位却为「{_tier31}」——R-032 主角光环／能力强化补偿为幻想向专属，"
                     f"现实向及零豁免题材恒填「无」/E0（genre/realistic.md#六）")
        if _is_fantasy30 and _battle30 and _tier31 in ("", "无", "E0", "—", "-"):
            warns.append(f"第{ch}章{_htag28}｜[31] 幻想向战斗章未登记豁免档位——"
                         f"R-032 未登记即回落零豁免；本章若用了主角补偿，须先在世界观与账本登记")
        # [19] 段落组织（v9 重写；WARN 档，不阻断交付）
        # 旧版判「连续 3 段字数差 ≤10%」，对话章对白段天然同长，必然命中且改一处冒一处（BUG-024）。
        # 现改整章统计：只看叙述段，看的是「碎片化」与「有没有长段呼吸」，不再报具体段号。
        # 注：本检查对全部章节都跑（历史章一并报），故文案加历史章标记，免得看错章改错稿。
        _cur = str((data.get("当前状态") or {}).get("章", "") or "").strip()
        _htag = "" if (not _cur or _cur == str(ch)) else "（历史章·非当前章）"
        if draft_text:
            _b = re.sub(r"\n*生成指纹[:：].*$", "", draft_text)
            pa = [x.strip() for x in re.split(r"\n\s*\n", _b) if x.strip()]
            # 叙述段＝不含任何对白引号的段（含引号即算对白段，哪怕只有一句提示语）。
            # 此口径与 core/intensity.md#五 的「段的范围」表逐条一致（BUG-036）
            narr = [x for x in pa if not re.search(r"[「」『』“”]", x)]
            nlen = [len(re.sub(r"\s", "", x)) for x in narr]

            # ① 碎片化：叙述段里超过一半不超过 20 字 = 一句一敲桌子
            # v9.5 修：对白占比高的章（对话章）叙述段天然短——一句「她没说话。」就是一段，
            # 它夹在两轮对白之间，不是「没有段落组织」。实测对话章 59%，按 50% 判必然误报。
            # 改为按对白占比分档：对白 >35% 时阈值放宽到 65%；其余仍 50%。
            if len(narr) >= 8:
                _n_all = len(re.sub(r"\s", "", _b)) or 1
                _dlg = sum(len(re.sub(r"\s", "", x)) for x in pa if re.search(r"[「」『』“”]", x))
                _dlg_ratio = _dlg / _n_all
                _thr = 0.65 if _dlg_ratio > 0.35 else 0.50
                n_short = sum(1 for x in narr if len(re.sub(r"\s", "", x)) <= 20)
                ratio = n_short / len(narr)
                if ratio > _thr:
                    warns.append(f"第{ch}章{_htag}｜[19] 叙述段碎片化：{n_short}/{len(narr)} 段不超过 20 字"
                                 f"（{ratio:.0%}，阈值 {_thr:.0%}；本章对白 {_dlg_ratio:.0%}）"
                                 f"——一段一句＝没有段落组织，"
                                 f"见 core/intensity.md#五、段落卫生（v9.4 降级：❌ 本节不治流水账）——"
                                 f"这一段只是排版卫生，治不了流水账；流水账看 core/scene-drive.md#四 的详略差")

            # ② 长段不足：叙述段里 ≥80 字的不足 3 段（0 段＝全章都在短句上蹦）
            # 本项与 core/intensity.md#五「每章至少 3 段 ≥80 字」逐字对应，不可只查最长一段
            if narr:
                n_long = sum(1 for x in narr if len(re.sub(r"\s", "", x)) >= 80)
                if n_long < 3:
                    warns.append(f"第{ch}章{_htag}｜[19] 叙述段 ≥80 字的只有 {n_long}/3"
                                 f"（最长 {max(nlen)} 字）——长段是呼吸，全短段读起来是敲桌子")

            # ③ 同上限：连续 4 段叙述都 ≤20 字（只报一次，不报段号）
            # v9.5 修：原实现遍历的是**过滤后的 narr**，于是隔着对白的两段短叙述
            # 也被算成「连续」（实测：正文已无连续 4 段短叙述，仍持续报 WARN）。
            # 「连续」应按原文判断——中间夹一段对白就该断开。改为遍历全文段落，
            # 对白段只用来打断，不参与计数。
            run = 0
            for x in pa:
                if re.search(r"[「」『』“”]", x):
                    run = 0
                    continue
                if len(re.sub(r"\s", "", x)) <= 20:
                    run += 1
                    if run == 4:
                        warns.append(f"第{ch}章{_htag}｜[19] 有连续 4 段以上叙述句都不超过 20 字——"
                                     f"至少合并一次，让动作连成一条线")
                        break
                else:
                    run = 0

            # ④ 同型段首：只在叙述段里看（对白段首是「」，不算同型）
            run, prev = 1, ""
            for x in narr:
                head = re.sub(r"\s", "", x)[:2]
                if head and head == prev:
                    run += 1
                    if run == 3:
                        warns.append(f"第{ch}章{_htag}｜[19] 连续 3 段叙述同型段首「{head}」——"
                                     f"换起笔（一段用物、一段用声、一段用动作）")
                        break
                else:
                    run = 1
                prev = head

            # ⑤ 连续纯对白过长（v9.2 补，BUG-036 的对白侧基准）：对白段没有长度下限，
            # 但连续 6 段以上全是对白，读者会失去空间感——须插一句叙述（动作或物，不是「他说」）
            run = 0
            for x in pa:
                if re.search(r"[「」『』“”]", x):
                    run += 1
                    if run == 7:
                        warns.append(f"第{ch}章{_htag}｜[19] 连续 7 段以上全是含对白的段落——"
                                     f"插一句叙述（一个动作或一样东西），不要只插「他说」")
                        break
                else:
                    run = 0

            # ⑥ 三项并列密度（保留旧判据）
            n_tri = len(re.findall(r"[^、。\n]{1,6}、[^、。\n]{1,6}、[^、。\n]{1,6}", _b))
            if n_tri >= 5:
                warns.append(f"第{ch}章{_htag}｜[19] 三项并列 {n_tri} 处（阈值 5）——"
                             f"A 族结构痕迹，见 core/prose-craft.md#五")
        # [20] 章末钩子兑现（v9）：账本登记了钩子类型，但没有任何检查确认它在正文里还在。
        # 第 3 章重写全章时，H7 兑现句整句蒸发，账本仍写 H7，两轮自查都照判「已落最后一拍」（BUG-026）
        # ⚠ 只对当前章生效：账本 `本章登记` 是单章结构，历史章的登记已被覆盖，
        # 拿当前章的锚去验历史章必然误报（实测：第 5 章一填锚，1–4 章全红）
        _cur_ch = str((data.get("当前状态") or {}).get("章", "") or "").strip()
        if draft_text and _cur_ch and _cur_ch == str(ch):
            _body = re.sub(r"\n*生成指纹[:：].*$", "", draft_text)
            _paras = [x for x in re.split(r"\n\s*\n", _body) if x.strip()]
            _tail = "\n".join(_paras[-3:])
            _hook = str((data.get("本章登记") or {}).get("钩子兑现锚", "") or "").strip()
            if not _hook:
                warns.append(f"第{ch}章｜[20] 账本未填「钩子兑现锚」——无法核对章末钩子是否仍在正文"
                             f"（填末三拍内 4–10 字原句即可，如「一年到头不灭」）")
            elif _hook not in _tail:
                fail(ch, f"[20] 章末钩子兑现句不在正文末三段：「{_hook}」——"
                         f"账本登记钩型 {(data.get('本章登记') or {}).get('章末钩子类型') or '空'}，重写/大改后可能整句蒸发，"
                         f"核末三拍后重填账本")
        # [21] 特殊移动未登记（v9）：规则写「未登记即不启用」，但旧版没有任何检查确认它登了。
        # 四章实测：世界观把龙形写得很全，账本 `特殊移动` 从建账起一直为空，跑闸三次无一次提示（BUG-027）
        if draft_text:
            _sm = data.get("特殊移动") or {}
            if not str(_sm.get("形态") or "").strip():
                # v9.5 修：原词表含裸「变成」，会误伤一切正常表达（实测：「声音从哒变成噗」
                # 被判为龙形变形 1 处）。「变成」只在同句出现器官词时才算形态变化。
                _hit = re.findall(r"变回|变形|化龙|龙形|龙身", draft_text)
                _hit += re.findall(
                    r"(?:手臂|手指|指甲|四肢|身体|骨头|脊背|皮肤|肩膀)[^。\n]{0,10}变成", draft_text)
                if _hit:
                    warns.append(f"第{ch}章｜[21] 正文出现变形/龙形 {len(_hit)} 处，"
                                 f"但账本 `特殊移动.形态` 为空——按「未登记即不启用」须先登记"
                                 f"（形态/代价/失效/当前可用/空中手经济），"
                                 f"另核 `战斗豁免.种族与身体部位` 的代偿项与必留项")
        # [22] 定稿改名（v9.1）：交付闸 PASS 后章稿已过五道工序，不该还叫「草稿」（WARN，不阻断）
        if str((data.get("章节状态") or {}).get("当前态", "") or "").strip() in ("已交付", "已过闸"):
            for _k, _v in (prods or {}).items():
                _fn = str(_v or "").strip()
                if _fn and "草稿" in _fn and _fn.endswith(".md"):
                    warns.append(f"第{ch}章｜[22] 本章已过闸，但产物「{_k}」仍叫「{_fn}」——"
                                 f"按 core/workflow.md#定稿改名 重命名为 `-定稿` 并同步账本 "
                                 f"`工作流执行日志.产物`")
                    break
        # [11] 冷读引文实证（pro/max）
        # ⚠ 只判「至少 3 条命中」，❌ 不可反过来要求高命中率：
        # 审查报告里的「」不只用于引用正文，还用于举反例（「左腿经髋关节离断」这类正文禁用的
        # 术语）、给改法建议、引账本与规则原文——这些本来就不该出现在正文里。
        # 实测按 70% 命中率判，一份报告 80 条引文只有 24 条命中，其余全是反例与建议，
        # 属于误报。真正能判「报告与正文脱节」的是下面的复核字数比对。
        if act in ("pro", "max") and rp_text:
            quotes = QUOTE_PAT.findall(rp_text)
            hits = [q for q in quotes if q in draft_text]
            if len(hits) < 3:
                fail(ch, f"审查报告命中草稿的原文引文仅 {len(hits)}/3——未真实读草稿的空报告（引文实证不过）")

        # [11-补] 复核基线（v9.2，BUG-010/020）：复核之后再改稿，报告与正文会脱节，
        # 旧版只靠自觉（同一章曾连犯两次）。改为比对「复核完成时的正文字数」与交付时字数，
        # 偏差超阈值即提示补复核，把「靠自觉」变成「有数可查」。
        if act in ("pro", "max") and rp_text and draft_text:
            _mrev = re.search(r"复核字数[:：]\s*(\d+)", rp_text)
            _body11 = re.sub(r"\n*生成指纹[:：].*$", "", draft_text)
            _curc = len(re.sub(r"\s", "", _body11))
            if _mrev:
                _rv = int(_mrev.group(1))
                if _rv and abs(_curc - _rv) / _rv > 0.08:
                    warns.append(f"第{ch}章｜[11] 复核时正文 {_rv} 字，现 {_curc} 字"
                                 f"（差 {abs(_curc-_rv)/_rv:.0%}，阈值 8%）——复核后又大改，"
                                 f"须补一轮复核并更新「复核字数」")
            else:
                warns.append(f"第{ch}章｜[11] 审查报告缺「复核字数: N」——"
                             f"无法核对复核之后是否又改过稿（格式见 core/cold-review.md#五）")
        # [13] 同源判定（pro/max）：判定高度一致是同源「信号」而非照抄实据——独立审查常 converge 于多数维度通过，
        #     纯判定相似（引文/位置不同）属合法同判，降为 WARN 交主代理受理裁定（对齐 cold-review ④「主代理据此裁定」），
        #     ❌ 不再硬 FAIL 逼审查员造差异。硬防伪仍由输入隔离[8]/主语纯净[12]/引文实证[11]/调用凭证兜底。
        #     阈值用比例（修旧 bug：common=20/same=20 与 lite common=10 永不触发）。
        if act in ("pro", "max") and rp_text and sc_text:
            v1 = verdict_vector(rp_text)
            v2 = selfcheck_dim_vector(sc_text)   # 自查按 S 编号落盘，先折算成维度
            common = set(v1) & set(v2)
            same = sum(1 for k in common if v1[k] == v2[k])
            bad1 = {k for k in v1 if v1[k] == "不通过"}
            bad2 = {k for k in v2 if v2[k] == "不通过"}
            # 豁免：审查无「不通过」项时无差异空间，本项不成立（防误杀干净章）
            if bad1 and len(common) >= 10:
                if same / len(common) >= 0.95:
                    warns.append(f"第{ch}章｜[13] 审查与自查 {same}/{len(common)} 维判定高度一致——同源信号，交主代理受理裁定（引文/位置不同的合法同判不阻断）")
                elif bad2 == bad1:
                    warns.append(f"第{ch}章｜[13] 自查与审查不通过维度相同（{sorted(bad1)}）——交主代理裁定是否独立发现")
        # [10] 闸判定＋机检运行（bootstrap：--precheck 豁免这两字段，其余检查照跑）
        if not args.precheck:
            if e.get("机检运行") != "是":
                fail(ch, f"机检运行={e.get('机检运行') or '未登记'}——脚本漏跑＝严重制度失败，须实际运行 gatecheck 并取得 PASS 后交付")
            if e.get("交付闸") != "通过":
                fail(ch, f"交付闸={e.get('交付闸')}——未过闸章不得交付")
        # [14] 交付凭证（PASS 印章——哈希链含章草稿：交付正文被换→印章失效）
        try:
            st = stamp_of(ch, draft_text, sc_text, rp_text)
        except Exception:
            st = None
        if st:
            sf = os.path.join(root, f"gate-pass-第{ch}章.txt")
            if os.path.isfile(sf):
                ptext = open(sf, encoding="utf-8").read()
                got = re.search(r"印章[:：]\s*(\S+)", ptext)
                got_sha = re.search(r"正文SHA[:：]\s*(\S+)", ptext)
                _dbody = re.sub(r"\n*生成指纹[:：].*$", "", draft_text or "")
                cur_sha = hashlib.sha256(_dbody.encode("utf-8")).hexdigest()[:16]
                if got_sha and got_sha.group(1) != cur_sha:
                    fail(ch, f"正文SHA不符（gate-pass 记录 {got_sha.group(1)} ≠ 当前 {cur_sha}）——交付正文已被替换，须重跑完整流程")
                elif not got or got.group(1) != st:
                    fail(ch, f"交付印章不符（gate-pass-第{ch}章.txt）——产物被篡改或印章伪造，须重跑 gatecheck 重新过闸")
            elif not errors and not args.precheck:
                gen_stamps.append((ch, sf, st, draft_text))
        # [14-补] 历史章印章校验（v9）：已交付章正文被改后，其印章失效，但旧版跑后续章毫无提示（BUG-025）
        try:
            _chapfiles = {}
            for _lg in (data.get("工作流执行日志") or []):
                if not isinstance(_lg, dict):
                    continue
                _c = _lg.get("章")
                _p = (_lg.get("产物") or {}).get("章草稿")
                if _c is not None and _p:
                    try:
                        _chapfiles[int(_c)] = str(_p).strip()
                    except (ValueError, TypeError):
                        pass
            for _fn in os.listdir(root):
                _mm = re.match(r"gate-pass-第(\d+)章\.txt$", _fn)
                if not _mm:
                    continue
                _n = int(_mm.group(1))
                if _n == ch:
                    continue
                _rec = re.search(r"正文SHA[:：]\s*(\S+)", open(os.path.join(root, _fn), encoding="utf-8").read())
                _df = _chapfiles.get(_n)
                if not (_rec and _df):
                    continue
                _dp = os.path.join(root, _df)
                if not os.path.isfile(_dp):
                    continue
                _d2 = re.sub(r"\n*生成指纹[:：].*$", "", open(_dp, encoding="utf-8").read())
                _cur2 = hashlib.sha256(_d2.encode("utf-8")).hexdigest()[:16]
                if _cur2 != _rec.group(1):
                    warns.append(f"第{_n}章｜[14] 已交付章正文已改动（印章记录 {_rec.group(1)} ≠ 当前 {_cur2}），"
                                 f"其交付凭证失效——须对第{_n}章重跑 gatecheck")
        except Exception:
            pass
    # [0-c2] 核查记录占位值：任一项仍为「待查」＝未实查（与日志初值黑名单同源）
    for rec in (data.get("核查记录") or []):
        if not isinstance(rec, dict):
            continue
        todo = [k for k, v in rec.items() if str(v).strip() == "待查"]
        if todo:
            fail(rec.get("章", "?"), f"核查记录仍有「待查」项 {todo[:4]}——未实查，须逐项改为 ✓/✗＋说明")

    # [15] 三条硬闸机检（B/C 档亲密章）——硬闸不因题材/用户指令关闭（SKILL 〇-补）
    # 账本结构：本章登记.亲密戏登记.{档位, 硬闸自查{成年,非自愿,同意,疼痛非快感}}
    # 与 state-ledger.yaml 模板字段、core/workflow.md 章末核查、chapter-planning 6.1 第0条联动。
    hard_gates = ("成年", "非自愿", "同意", "疼痛非快感")
    intim = (data.get("本章登记") or {}).get("亲密戏登记")
    if isinstance(intim, dict):
        tier = str(intim.get("档位", "") or "").strip()
        # 仅当本章登记明确写了 B/C 档亲密戏时才强检；A 档或留空（本章无亲密戏）跳过
        if tier and (tier.startswith("B") or tier.startswith("C")):
            hg = intim.get("硬闸自查")
            if not isinstance(hg, dict) or not hg:
                fail("本章", "B/C 档亲密章缺 `本章登记.亲密戏登记.硬闸自查` 登记——三条硬闸不可判定，不得交付")
            else:
                missing = [g for g in hard_gates if g not in hg]
                if missing:
                    fail("本章", f"硬闸自查缺项 {missing}——须齐备成年/非自愿/同意/疼痛非快感四项")
                core_gates = ("成年", "非自愿", "疼痛非快感")
                for g in hard_gates:
                    v = str(hg.get(g, "") or "").strip()
                    if v in ("待查", ""):
                        fail("本章", f"硬闸自查[{g}]为「待查/空」——未实查，须逐条填 通过/不适用")
                    elif v == "不通过":
                        fail("本章", f"硬闸自查[{g}]＝不通过——触碰内容硬闸，本章不得交付（SKILL 〇-补）")
                    elif v == "不适用" and g in core_gates:
                        fail("本章", f"硬闸自查[{g}]＝不适用——{g}是绝对线（INV-01），B/C 档须实判「通过」；仅「同意」可视情境不适用")
                    elif v not in ("通过", "不适用"):
                        fail("本章", f"硬闸自查[{g}]取值非法「{v}」——须为 通过/不适用/不通过/待查")
                # 成年/非自愿/疼痛非快感 已在上方逐项强制「通过」（不适用即 FAIL），与 INV-01「四项齐备实判通过」对齐。

    # [16] 资源账窗口空窗机检（仅末世/生存题材，账本 资源账.启用: 是 时）
    # 只认章号窗口、不判「本章算不算一场危机」——那是 cold-review 维度19 的叙事软查。
    # 与 genre/postapocalyptic.md ★题材结构包「资源账」、state-ledger.yaml 资源账块联动。
    # 现实/古装/幻想题材 启用: 否 → 整块跳过，避免误卡非末世作品。
    res = data.get("资源账")
    if isinstance(res, dict) and str(res.get("启用", "") or "").strip() == "是":
        try:
            last_rec = int(res.get("上次记账章"))
        except (TypeError, ValueError):
            last_rec = None
        if ch_nums:
            cur_ch = max(ch_nums)
            if last_rec is None:
                fail(cur_ch, "末世资源账启用但 `资源账.上次记账章` 未填/非法——须填最近一次记账章号")
            elif cur_ch - last_rec >= 3:
                fail(cur_ch, f"资源账连续 {cur_ch - last_rec} 章未推进记账章（上次记账=第{last_rec}章）——"
                             f"经济系统失效（见 genre/postapocalyptic.md 资源账；每场危机须消耗或获得至少一项）。"
                             f"「算不算一场危机」由冷读维度19 判定，机检只认窗口")

    # [17] 章循环状态机——自包含状态表（运行时不依赖技能目录）。
    # ⚠ 本表与 rules/rules.yaml 的 chapter_states 是同一份口径的两个副本，
    #   由 scripts/compile_rules.py [FSM-*] 校验一致；改一处必须两处同步。
    # 账本缺 章节状态 块时整块跳过——兼容未启用状态机层的旧账本，不误卡。
    FSM_ALLOWED = ["待规划", "已规划", "写作中", "已自查", "已冷读", "已修正", "已过闸", "已交付"]
    FSM_TRANS = {
        "待规划": ["已规划"],
        "已规划": ["写作中"],
        "写作中": ["已自查"],
        "已自查": ["已冷读", "已修正"],   # flash 直接到已修正
        "已冷读": ["已修正"],
        "已修正": ["已过闸"],
        "已过闸": ["已交付"],
        "已交付": ["待规划"],             # 下一章
    }
    FSM_FORBIDDEN = [("写作中", "已交付"), ("已规划", "已过闸"), ("已自查", "已交付")]
    st = data.get("章节状态")
    if isinstance(st, dict) and st:
        cur_state = str(st.get("当前态", "") or "").strip()
        trail = st.get("轨迹") or []
        if isinstance(trail, str):
            trail = [x.strip() for x in re.split(r"[→,，、\s]+", trail) if x.strip()]
        trail = [str(x).strip() for x in trail if str(x).strip()]
        if cur_state and cur_state not in FSM_ALLOWED:
            fail("本章", f"章节状态.当前态「{cur_state}」非法——须为 {FSM_ALLOWED}")
        bad_states = [x for x in trail if x not in FSM_ALLOWED]
        if bad_states:
            fail("本章", f"章节状态.轨迹含非法态 {sorted(set(bad_states))}")
        for i in range(len(trail) - 1):
            s1, s2 = trail[i], trail[i + 1]
            if s1 in FSM_TRANS and s2 not in FSM_TRANS[s1]:
                fail("本章", f"章节状态非法转移 {s1} → {s2}（合法后继：{FSM_TRANS[s1]}）")
            if (s1, s2) in FSM_FORBIDDEN:
                fail("本章", f"章节状态跳步 {s1} → {s2}——不得跳过中间手续")
        # 闭环判定只看**当前章段**，不看全局日志、也不看历史章段：
        # ① 日志里前 N-1 章都标了「交付闸: 通过」，用全局日志触发会把本章误卡；
        # ② 轨迹是**跨章累计**的（「已交付 → 待规划」回卷即 state_machine 的推进设计），
        #    历史章的「已过闸」不构成当前章的闭环义务——当前章段＝最后一次回卷点之后的段。
        mode = str((data.get("角色固定属性") or {}).get("工作流模式", "") or "").strip()
        if mode == "flash" and "已冷读" in trail:
            fail("本章", "flash 模式轨迹出现「已冷读」——不得伪填冷读凭证（降级禁止）")
        seg = trail
        for i in range(len(trail) - 1):
            if trail[i] == "已交付" and trail[i + 1] == "待规划":
                seg = trail[i + 1:]
        if "已过闸" in seg or seg[-1:] == ["已交付"]:
            if seg[-1] != "已交付" or "已过闸" not in seg:
                fail("本章", "章节状态当前章段已过闸却未闭合到「已过闸 → 已交付」——不得跳步交付")
            if mode in ("pro", "max") and "已冷读" not in seg:
                fail("本章", f"{mode} 模式交付轨迹缺「已冷读」——冷读稽查不可跳过")

    # [18] 自查形式化项机检（分级剥离的 11 项之登记类——S05/S06/S07/S09/S11/S12/S14/S38；
    #      S42 正文文本模式在章循环内逐章判，S48/S49 附页结构在 [9] 报告块内判）。
    # 输入＝账本「本章登记」块（章末登记，跨章可查）；登记/枚举/可算术半区由本节代判。
    # 边界如实声明：本节判**登记的枚举合法性与可算术性**（含 S05/S09/S11 钩子窗口算术），
    # 不判登记与正文内容的一致（如钩子兑现句是否真在末段＝S05 的语义半区，仍由冷读维度 10/18 把关；
    # flash 无冷读时，语义半区由写作时点规则包＋章契约约束，作者须自觉保证）。
    reg = data.get("本章登记") if isinstance(data.get("本章登记"), dict) else {}
    cur_ch_int = None
    try:
        cur_ch_int = int(str(((data.get("当前状态") or {}).get("章")) or "").strip())
    except (ValueError, TypeError):
        pass
    # S05/S09 章末钩子类型枚举（H1–H7/h8–h10）＋强度标定（类型首字符即 H/h）
    hook = str(reg.get("章末钩子类型", "") or "").strip()
    if not hook:
        fail("本章", "S05 章末钩子类型未登记——每章必有章末钩子（追读线设计）")
    elif hook not in HOOK_ENUM:
        fail("本章", f"S05 章末钩子类型「{hook}」非法——须为 H1–H7 / h8–h10 枚举"
                     f"（H/h 首字符即强度标定，S09 一并代判）。"
                     f"⚠ 枚举字段**只填代码**，不要带描述：「H4 威胁」应写「H4」，"
                     f"「H4（威胁）」也不行。想让别人看懂类型，写进「钩子兑现锚」那一栏")
    # S06 章节功能枚举
    func = str(reg.get("章节功能", "") or "").strip()
    if not func:
        fail("本章", "S06 章节功能未登记——须为 主线推进/关系深化/日常样态/对抗危机/生存危机 之一")
    elif func not in FUNC_ENUM:
        fail("本章", f"S06 章节功能「{func}」非法——须为 {sorted(FUNC_ENUM)} 之一")
    # S07 主冲突线 beat 三态枚举
    lbeat = str(reg.get("主冲突线beat", "") or "").strip()
    if not lbeat:
        fail("本章", "S07 主冲突线beat未登记——须为 推进/蓄势/留白/对抗 之一（呼吸章计蓄势；crisis 章必为推进或对抗）")
    elif lbeat not in BEAT_ENUM:
        fail("本章", f"S07 主冲突线beat「{lbeat}」非法——须为 {sorted(BEAT_ENUM)} 之一")
    # S12 张力级 1–5
    tens = str(reg.get("张力级", "") or "").strip()
    if not tens:
        fail("本章", "S12 张力级未登记——须为 1–5（对照体验强度曲线设计值 ±1）")
    elif tens not in {"1", "2", "3", "4", "5"}:
        fail("本章", f"S12 张力级「{tens}」非法——须为 1–5 整数")
    # S05/S09/S11 钩子窗口算术（输入＝近五章钩子类型滚动窗口）。
    # 补 [18] 原仅判枚举的可算术半区，闭合 flash 无冷读时的追读轮转真空。
    # 边界如实声明：只判可算术项（同型轮转/余味池/强钩绝对下限/弱钩不连续）；
    # 钩子是否真落末段、正文兑现、温馨取向 2/3 细分＝语义半区，仍由冷读维度 10/18（pro/max）与写作时点规则把关。
    win = reg.get("近五章钩子类型") or []
    if isinstance(win, list):
        w = [str(x).strip() for x in win if str(x).strip()]
        # S11 弱钩不连续：末 3 项须均非空且全为 h* 才判（修复空窗 all([])==True 误报）
        if len(win) >= 3:
            tail3 = [str(x).strip() for x in win[-3:]]
            if all(x and x.startswith("h") for x in tail3):
                fail("本章", f"S11 弱钩连续 3 章 {tail3}——弱钩（h8–h10）不得连续出现 3 章，须改强钩或调整")
        # S05 近5章同型轮转：强钩 H1–H7 同型至多 1 次；弱钩 h8–h10 合并余味池至多 2 次
        if len(w) >= 2:
            hc = {}
            for x in w:
                if x.startswith("H"):
                    hc[x] = hc.get(x, 0) + 1
            dup = sorted(t for t, c in hc.items() if c >= 2)
            if dup:
                fail("本章", f"S05 近五章强钩同型复用 {dup}——同一强钩类型近 5 章至多 1 次，须换型或换载体")
            pool = sum(1 for x in w if x.startswith("h"))
            if pool >= 3:
                fail("本章", f"S05 近五章余味池 {pool}/2 超限——h8/h9/h10 合并近 5 章至多 2 次")
        # S09 强钩绝对下限：满 5 章窗口强钩 H 至少 2（温馨软下限 2/默认 3 的细分由冷读/题材契约判）
        if len(w) >= 5:
            strong = sum(1 for x in w if x.startswith("H"))
            if strong < 2:
                fail("本章", f"S09 近五章强钩 {strong}/2 低于绝对下限——追读动力不足，须加强钩（口径见 core/chapter-planning.md#二）")
        elif cur_ch_int and cur_ch_int >= 5:
            warns.append(f"第{cur_ch_int}章｜S05/S09 近五章钩子类型窗口不足 5 项（{len(w)}）——按账本维护规则补足，不回改不强造")
    # S14 受限beat层级枚举＋受限让路补法（破窗口径：补法=无 即报）
    lb = reg.get("受限beat")
    if isinstance(lb, dict):
        lvl = str(lb.get("层级", "") or "").strip()
        if lvl and lvl not in LIMIT_ENUM:
            fail("本章", f"S14 受限beat.层级「{lvl}」非法——须为 核心/在场/余波/弱受限 之一"
                         f"（点缀不计入；能力受限／高魔豁免另记 `能力受限`，不占本层）")
    detour = reg.get("受限让路") or {}
    if isinstance(detour, dict) and str(detour.get("补法", "") or "").strip() == "无":
        fail("本章", "S14 受限让路.补法＝「无」——破窗（无核心受限且无在场/余波补偿），不得交付；补法须为 在场/余波 并填补偿章")
    # S38 首章 beat 数 ≤2 类（仅第 1 章；字段在 distribution 块；非法值不得静默放行）
    if cur_ch_int == 1:
        fb = ((data.get("distribution") or {}).get("首章beat数"))
        if fb is not None:
            try:
                fb_int = int(str(fb).strip())
            except (ValueError, TypeError):
                fail("第1章", f"S38 首章beat数「{fb}」非法——须为整数（≤2 类，查账本 distribution.首章beat数）")
            else:
                if fb_int > 2:
                    fail("第1章", f"S38 首章beat数 {fb_int} >2 类——首章信息量过载（查账本 distribution.首章beat数）")

    if errors:
        print(f"FAIL 交付闸机检未过（{len(errors)} 项）:")
        for x in errors: print("  -", x)
        # v9.6：FAIL 时也输出 WARN——旧版 sys.exit 直接吞掉全部提示，
        # 使 [30]/[31] 的「复用／未登记豁免」等 WARN 在交付失败章永远不可见。
        for w in warns: print("WARN", w)
        print("FAIL 运行不生成交付凭证——修复后重跑")
        sys.exit(1)
    for w in warns: print("WARN", w)
    for ch, sf, st, dtext in gen_stamps:
        try:
            # v9：指纹行属产物元数据，不计入正文——旧版把它算进字数与段长，
            # 且要求写在末行，等于用元数据顶掉章节最后一拍（BUG-011）
            dbody = re.sub(r"\n*生成指纹[:：].*$", "", dtext or "")
            dsha = hashlib.sha256(dbody.encode("utf-8")).hexdigest()[:16]
            dchars = len(re.sub(r"\s", "", dbody))
            open(sf, "w", encoding="utf-8").write(
                f"交付凭证（gatecheck.py PASS 时自动生成，勿手写）\n章: {ch}\n"
                f"正文SHA: {dsha}\n正文字数: {dchars}\n印章: {st}\n")
            print(f"STAMP 已生成 gate-pass-第{ch}章.txt（首跑补章）")
        except Exception as ex:
            fail(ch, f"凭证文件写入失败: {ex}")
    if errors:
        for x in errors: print("  -", x)
        sys.exit(1)
    if args.precheck:
        print("PRECHECK 完成：未发现其他 FAIL（[10] 两字段已豁免）——回填「机检运行: 是」「交付闸: 通过」后，须正式运行一次取 PASS 才可交付")
        sys.exit(0)
    print("PASS 交付闸机检：模式保真(降级禁止)/代理凭证互异/产物三验/生成指纹/维度覆盖/输入隔离/引文实证/主语无污染/非同源/自查交叉(分级12组|5组)/闸判定/印章/三条硬闸(B·C档)/资源账窗口(末世)/章节状态机/形式化项[18] 全过")
    sys.exit(0)

if __name__ == "__main__":
    main()