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
  [5] 产物三验：非空＋存在＋在项目目录内（realpath 防穿越）
  [6] 产物生成指纹：每个产物文件末行「生成指纹: X」== 账本签发角色凭证
      （角色↔产物映射：max 章任务包→队长/章草稿+自查报告→写作员/审查报告→
      审查员；pro 章草稿+自查报告→本体/审查报告→冷读）；缺指纹/不同号 → FAIL
  [7] 稽查全覆盖 22/22；审查报告「维度N」集合 == {1..22}
  [8] 输入隔离：审查报告出现自查报告文件名 → FAIL（冷读者不得看自查结论）
  [9] 自查覆盖 X/X 自洽＋与自查报告倒数第二行一致
  [10] 交付闸字段 == 通过（唯一合法值；无 python＝无法过闸＝不得交付）
  [11] 冷读引文实证：审查报告命中草稿原文引文 ≥3 条（「」内 ≥8 字）——
      零命中＝未读草稿的空报告
  [12] 主语污染：审查报告出现「我写/作为队长」类主上下文人称模式 → FAIL
  [13] 同源判定：审查与自查 22 维判定向量完全一致 → FAIL（同源伪装）
  [14] PASS 印章：每章 gate-pass-第N章.txt，末行印章 =
      sha256(章号+自查报告+审查报告)[:16] 重算比对；篡改/手写伪造 → FAIL

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
MODE_PRODUCTS = {"flash": ["自查报告"], "pro": ["章草稿", "审查报告", "自查报告"],
                 "max": ["章任务包", "章草稿", "审查报告", "自查报告"]}
ROLE_OF_PRODUCT = {"章任务包": "队长", "章草稿": "写作员", "自查报告": "写作员",
                   "审查报告": "审查员"}
ROLE_OF_PRODUCT_PRO = {"章草稿": "本体", "自查报告": "本体", "审查报告": "冷读"}
DIM_SET = set(range(1, 23))
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

def verdict_vector(text):
    out = {}
    for m in re.finditer(r"维度\s*(\d+)\s*[｜|]\s*([^\s｜|，。]+)", text):
        out[int(m.group(1))] = m.group(2)
    return out

def stamp_of(ch, sc_text, rp_text):
    h = hashlib.sha256()
    h.update(str(ch).encode("utf-8"))
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

    chs = []
    for e in logs:
        try: chs.append(int(e.get("章")))
        except (TypeError, ValueError): chs.append(None)
    if None in chs:
        errors.append("日志存在无法解析的章号（类型混淆）")
    if all(c is not None for c in chs) and sorted(chs) != list(range(1, len(chs) + 1)):
        errors.append(f"日志章号不连续（缺号漏登）: 现有 {sorted(chs)}")

    gen_stamps = []
    for e in logs:
        try: ch = int(e.get("章"))
        except (TypeError, ValueError): ch = e.get("章", "?")
        if a.chapter is not None and ch != a.chapter:
            pass  # 关注章外仍全量检查（历史章 FAIL 一并报）
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
        # [9] 自查覆盖（倒数第二行锚）
        sc = str(e.get("自查覆盖", ""))
        m = re.match(r"^(\d+)/(\d+)$", sc)
        if not m or m.group(1) != m.group(2) or int(m.group(2)) < 1:
            fail(ch, f"自查覆盖计数不自洽: {sc or '空'}（应 X/X 两数相等）")
        srp = prods.get("自查报告")
        if srp:
            fp = os.path.realpath(os.path.join(root, srp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                sc_text = open(fp, encoding="utf-8").read()
                lines = [l for l in sc_text.splitlines() if l.strip()]
                zone = lines[-3:] if lines else []
                tm = None
                for l in zone[:-1] if act in ("pro", "max") else zone:
                    tm = re.search(r"自查覆盖[:：]\s*(\d+)\s*/\s*(\d+)", l)
                    if tm: break
                if not tm: fail(ch, f"自查报告缺『自查覆盖: X/X 全查』机检锚: {srp}")
                elif m and (tm.group(1) != m.group(1) or tm.group(2) != m.group(2)):
                    fail(ch, f"自查报告 {tm.group(1)}/{tm.group(2)} ≠ 账本 {sc}——自报与文件不符")
        # [11] 冷读引文实证（pro/max）
        if act in ("pro", "max") and rp_text:
            quotes = QUOTE_PAT.findall(rp_text)
            hits = [q for q in quotes if q in draft_text]
            if len(hits) < 3:
                fail(ch, f"审查报告命中草稿的原文引文仅 {len(hits)}/3——未真实读草稿的空报告（引文实证不过）")
        # [13] 同源判定（pro/max）
        if act in ("pro", "max") and rp_text and sc_text:
            v1, v2 = verdict_vector(rp_text), verdict_vector(sc_text)
            common = set(v1) & set(v2)
            if len(common) >= 20 and all(v1[k] == v2[k] for k in common):
                fail(ch, f"审查报告与自查报告 {len(common)} 维判定完全一致——同源伪装强信号（独立视角必有权重差异）")
        # [10] 闸判定
        if e.get("交付闸") != "通过":
            fail(ch, f"交付闸={e.get('交付闸')}——未过闸章不得交付")
        # [14] PASS 印章
        if act in ("pro", "max"):
            try:
                st = stamp_of(ch, sc_text, rp_text)
            except Exception:
                st = None
            if st:
                sf = os.path.join(root, f"gate-pass-第{ch}章.txt")
                if os.path.isfile(sf):
                    tail = [l for l in open(sf, encoding="utf-8").read().splitlines() if l.strip()]
                    got = re.search(r"印章[:：]\s*(\S+)", tail[-1]) if tail else None
                    if not got or got.group(1) != st:
                        fail(ch, f"交付印章不符（gate-pass-第{ch}章.txt）——产物被篡改或印章伪造，须重跑 gatecheck 重新过闸")
                else:
                    gen_stamps.append((ch, sf, st))
    for w in warns: print("WARN", w)
    for ch, sf, st in gen_stamps:
        try:
            open(sf, "w", encoding="utf-8").write(f"交付印章（gatecheck.py 自动生成，勿手写）\n章: {ch}\n印章: {st}\n")
            print(f"STAMP 已生成 gate-pass-第{ch}章.txt（首跑补章）")
        except Exception as ex:
            fail(ch, f"印章文件写入失败: {ex}")
    if errors:
        print(f"FAIL 交付闸机检未过（{len(errors)} 项）:")
        for x in errors: print("  -", x)
        sys.exit(1)
    print("PASS 交付闸机检：模式保真(降级禁止)/代理凭证互异/产物三验/生成指纹/维度覆盖/输入隔离/引文实证/主语无污染/非同源/自查交叉/闸判定/印章 全过")
    sys.exit(0)

if __name__ == "__main__":
    main()