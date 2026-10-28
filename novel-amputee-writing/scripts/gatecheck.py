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
  [7] 稽查全覆盖 22/22；审查报告「维度N」集合 == {1..22}
  [8] 输入隔离：审查报告出现自查报告文件名 → FAIL（冷读者不得看自查结论）
  [9] 自查覆盖 49/49 自洽＋与自查报告倒数第二行一致；且自查报告须有 49 行
      「Sxx｜判定」判定行（只列 ID 不写判定 → 判定向量为空，同源判定失效 → FAIL）
  [9-b] 模板初值黑名单：待填/待运行/未过/待查 → FAIL（防"复制模板即合规"）
  [10] 交付闸字段 == 通过（唯一合法值；无 python＝无法过闸＝不得交付）
  [11] 冷读引文实证：审查报告命中草稿原文引文 ≥3 条（「」内 ≥8 字）——
      零命中＝未读草稿的空报告
  [12] 主语污染：审查报告出现「我写/作为队长」类主上下文人称模式 → FAIL
  [13] 同源判定：审查 22 维判定向量与「自查 S 编号折算后的维度向量」高度一致
      （≥21/22 且审查存在不通过项）→ FAIL（同源伪装）；「独立发现」按
      维度判定=不通过 或 「## 反证轮」小节 ≥3 段核验计——裸子串不算
  [14] 交付凭证（三模式）：gate-pass-第N章.txt，含正文SHA（sha256(章草稿)
      [:16]）＋正文字数＋印章（sha256(章号+章草稿+自查+审查)[:16]）重算比对
      ——交付正文被替换 → SHA/印章不符 FAIL；FAIL 运行不生成凭证；
      交付正文须逐字节来自被检章草稿文件，交付时附凭证内 SHA 与字数

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
VERDICT_SET = {"通过", "不通过", "不适用"}
SELF_MARK = {"✓": "通过", "√": "通过", "✗": "不通过", "×": "不通过"}
CHECKLIST_IDS = {f"S{i:02d}" for i in range(1, 50)}
PERSONA_PAT = re.compile(r"我写|我设计|我编制|我自查|我刚才|作为队长|我画的大纲|上一轮我|我安排的剧情|我登记的账")
QUOTE_PAT = re.compile(r"[「『“]([^」』”]{8,})[」』”]")
errors, warns = [], []

def fail(ch, msg): errors.append(f"第{ch}章｜{msg}")

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
}

def verdict_vector(text):
    out = {}
    for m in re.finditer(r"维度\s*(\d+)\s*[｜|]\s*([^\s｜|，。]+)", text):
        out[int(m.group(1))] = m.group(2)
    return out

def selfcheck_dim_vector(text):
    """自查报告按 S 编号落盘 → 依 S2D 折算成维度级判定（任一 S 不通过即该维不通过）"""
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
    a = ap.parse_args()
    root = os.path.realpath(a.dir)
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
                        errors.append(f"第1章｜大纲契约块不完整（缺「{mark}」非空标记）")
                        break
    for e in logs:
        try: ch = int(e.get("章"))
        except (TypeError, ValueError): ch = e.get("章", "?")
        if a.chapter is not None and ch != a.chapter:
            pass  # 关注章外仍全量检查（历史章 FAIL 一并报）
        # [0-b] 模板初值黑名单：占位值出现＝未真实执行（防"复制模板即合规"）
        for _k in ("选定模式", "实际执行模式", "审查深度", "机检运行", "交付闸", "自查覆盖"):
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
            if not m or m.group(1) != "22" or m.group(2) != "22":
                fail(ch, f"稽查全覆盖应为 22/22，实为: {cov or '空'}")
            rp = prods.get("审查报告")
            if rp:
                fp = os.path.realpath(os.path.join(root, rp))
                if os.path.isfile(fp) and fp.startswith(root + os.sep):
                    rp_text = open(fp, encoding="utf-8").read()
                    dims = set(int(x) for x in re.findall(r"维度\s*(\d+)", rp_text))
                    if dims != DIM_SET:
                        fail(ch, f"审查报告维度覆盖 {len(dims)}/22，缺: {sorted(DIM_SET - dims)}")
                    # 判定值枚举（维度行判定域须为 通过/不通过/不适用）
                    bad_v = []
                    for m2 in re.finditer(r"维度\s*(\d+)\s*[｜|]\s*([^\s｜|，。]+)", rp_text):
                        if m2.group(2) not in VERDICT_SET:
                            bad_v.append(f"维度{m2.group(1)}:{m2.group(2)}")
                    if bad_v:
                        fail(ch, f"审查报告判定值非法（须 通过/不通过/不适用）: {'；'.join(bad_v[:3])}")
                    # 输入清单段必须存在
                    if "输入清单" not in rp_text:
                        fail(ch, "审查报告缺「输入清单」段（须列收到的文件）")
                    # 独立发现：≥1 条维度判定为「不通过」，或「## 反证轮」小节含 ≥3 段实质核验
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
                        fail(ch, "审查报告零独立发现（须 ≥1 条维度判定「不通过」，"
                                 "或「## 反证轮」小节含 ≥3 段实质核验——只写「无问题」不算）")
                    scf = prods.get("自查报告")
                    if scf and scf in rp_text:
                        fail(ch, f"审查报告出现自查报告文件名（{scf}）——输入污染：冷读者不得看自查结论")
                    # [12] 主语污染
                    pm = PERSONA_PAT.search(rp_text)
                    if pm:
                        fail(ch, f"审查报告含主上下文人称模式（「{pm.group(0)}」）——独立子代理无创作过程记忆，判非独立")
        dp = prods.get("章草稿")
        if dp:
            fp = os.path.realpath(os.path.join(root, dp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                draft_text = open(fp, encoding="utf-8").read()
        # [9] 自查覆盖：49/49 硬校验＋ID 全集＋49 行判定断言＋与自查报告倒数第二行一致
        sc = str(e.get("自查覆盖", ""))
        m = re.match(r"^(\d+)/(\d+)$", sc)
        if not m or m.group(1) != "49" or m.group(2) != "49":
            fail(ch, f"自查覆盖应为 49/49，实为: {sc or '空'}")
        srp = prods.get("自查报告")
        if srp:
            fp = os.path.realpath(os.path.join(root, srp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                sc_text = open(fp, encoding="utf-8").read()
                ids = set(re.findall(r"\b(S\d\d)\b", sc_text))
                if ids != CHECKLIST_IDS:
                    miss = sorted(CHECKLIST_IDS - ids)[:4]
                    extra = sorted(ids - CHECKLIST_IDS)[:3]
                    fail(ch, f"自查报告 ID 集合不全（缺 {miss}{'；非法 ' + str(extra) if extra else ''}）——须逐条列 S01…S49 全集")
                # [9-b] 判定行断言：须 49 行「Sxx｜判定」，判定值合法
                srows = []
                for _ln in sc_text.splitlines():
                    _m = re.match(r"^\s*S(\d\d)\s*[｜|]\s*([^\s｜|，。\n]+)", _ln)
                    if _m:
                        srows.append((_m.group(1), _m.group(2)))
                if len(srows) != 49:
                    fail(ch, f"自查报告判定行 {len(srows)}/49——每条须写成「Sxx｜判定｜项名｜证据」；"
                             f"只列 ID 不写判定＝判定向量为空，同源判定会静默失效")
                bad_sv = [f"S{n}:{v}" for n, v in srows
                          if SELF_MARK.get(v, v) not in VERDICT_SET]
                if bad_sv:
                    fail(ch, f"自查判定值非法（须 通过/不通过/不适用，或 ✓/✗）: {'；'.join(bad_sv[:3])}")
                # 不适用白名单：只有"本条法定不适用"的 5 项可填不适用，防用不适用稀释同源判定
                NA_ALLOWED = {"24", "39", "47", "48", "49"}
                bad_na = sorted({f"S{n}" for n, v in srows
                                 if SELF_MARK.get(v, v) == "不适用" and n not in NA_ALLOWED})
                if bad_na:
                    fail(ch, f"这些自查项不成立「不适用」: {bad_na[:4]}——"
                             f"不适用只允许 S24（仅首章）/S39（无 devotee 角色）/S47（flash）/S48·S49（flash）；"
                             f"其余须判 通过 或 不通过")
                lines = [l for l in sc_text.splitlines() if l.strip()]
                zone = lines[-3:] if lines else []
                tm = None
                for l in zone[:-1] if act in ("pro", "max") else zone:
                    tm = re.search(r"自查覆盖[:：]\s*(\d+)\s*/\s*(\d+)", l)
                    if tm: break
                if not tm: fail(ch, f"自查报告缺『自查覆盖: 49/49 全查』机检锚: {srp}")
                elif tm.group(1) != "49" or tm.group(2) != "49":
                    fail(ch, f"自查报告 {tm.group(1)}/{tm.group(2)} ≠ 49/49")
        # [11] 冷读引文实证（pro/max）
        if act in ("pro", "max") and rp_text:
            quotes = QUOTE_PAT.findall(rp_text)
            hits = [q for q in quotes if q in draft_text]
            if len(hits) < 3:
                fail(ch, f"审查报告命中草稿的原文引文仅 {len(hits)}/3——未真实读草稿的空报告（引文实证不过）")
        # [13] 同源判定（pro/max）：相同判定比例 ≥95%（21/22）即 FAIL——
        #     全同或仅 1 处差异＝同源伪装强信号（阈值避免误杀真实冷读）
        if act in ("pro", "max") and rp_text and sc_text:
            v1 = verdict_vector(rp_text)
            v2 = selfcheck_dim_vector(sc_text)   # 自查按 S 编号落盘，先折算成维度
            common = set(v1) & set(v2)
            same = sum(1 for k in common if v1[k] == v2[k])
            bad1 = {k for k in v1 if v1[k] == "不通过"}
            bad2 = {k for k in v2 if v2[k] == "不通过"}
            # 豁免：审查无「不通过」项时无差异空间，本项不成立（防误杀干净章）
            if bad1:
                if len(common) >= 20 and same >= 21:
                    fail(ch, f"审查与自查 {same}/{len(common)} 维判定相同（≥95%）——同源伪装强信号（独立视角必有权重差异）")
                elif bad2 == bad1:
                    fail(ch, f"自查的不通过维度与审查完全相同（{sorted(bad1)}）——无独立发现，"
                              f"判同源照抄；自查须有自己的命中项或明确反证")
        # [10] 闸判定＋机检运行
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
                cur_sha = hashlib.sha256((draft_text or "").encode("utf-8")).hexdigest()[:16]
                if got_sha and got_sha.group(1) != cur_sha:
                    fail(ch, f"正文SHA不符（gate-pass 记录 {got_sha.group(1)} ≠ 当前 {cur_sha}）——交付正文已被替换，须重跑完整流程")
                elif not got or got.group(1) != st:
                    fail(ch, f"交付印章不符（gate-pass-第{ch}章.txt）——产物被篡改或印章伪造，须重跑 gatecheck 重新过闸")
            elif not errors:
                gen_stamps.append((ch, sf, st, draft_text))
    # [0-c] 核查记录占位值：任一项仍为「待查」＝未实查（与日志初值黑名单同源）
    for rec in (data.get("核查记录") or []):
        if not isinstance(rec, dict):
            continue
        todo = [k for k, v in rec.items() if str(v).strip() == "待查"]
        if todo:
            fail(rec.get("章", "?"), f"核查记录仍有「待查」项 {todo[:4]}——未实查，须逐项改为 ✓/✗＋说明")

    if errors:
        print(f"FAIL 交付闸机检未过（{len(errors)} 项）:")
        for x in errors: print("  -", x)
        print("FAIL 运行不生成交付凭证——修复后重跑")
        sys.exit(1)
    for w in warns: print("WARN", w)
    for ch, sf, st, dtext in gen_stamps:
        try:
            dsha = hashlib.sha256((dtext or "").encode("utf-8")).hexdigest()[:16]
            dchars = len(re.sub(r"\s", "", dtext or ""))
            open(sf, "w", encoding="utf-8").write(
                f"交付凭证（gatecheck.py PASS 时自动生成，勿手写）\n章: {ch}\n"
                f"正文SHA: {dsha}\n正文字数: {dchars}\n印章: {st}\n")
            print(f"STAMP 已生成 gate-pass-第{ch}章.txt（首跑补章）")
        except Exception as ex:
            fail(ch, f"凭证文件写入失败: {ex}")
    if errors:
        for x in errors: print("  -", x)
        sys.exit(1)
    print("PASS 交付闸机检：模式保真(降级禁止)/代理凭证互异/产物三验/生成指纹/维度覆盖/输入隔离/引文实证/主语无污染/非同源/自查交叉/闸判定/印章 全过")
    sys.exit(0)

if __name__ == "__main__":
    main()