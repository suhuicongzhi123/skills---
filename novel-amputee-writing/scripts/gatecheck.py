#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付闸机检脚本（v5.6.0 起）
用法: python gatecheck.py <小说项目目录> [--chapter N]
  --chapter N 输出聚焦第 N 章（仍全量检其余章：历史章 FAIL 一并报，整体 FAIL
  ——防「展示性通过」隐藏历史假执行）

机检范围＝结构与覆盖数（格式可验部分），对抗性测试后七项强化：
  [1] 账本存在且可解析；工作流执行日志块结构完整
  [2] 日志章号连续：章号集合 == {1..N}（缺号＝漏登，拒过闸）
  [3] 模式保真：选定模式 == 实际执行模式；不等时须有「降级确认」字段
  [4] 调用代理集 ⊇ 模式必需集（flash=本体 / pro=本体+冷读 / max=四员各自独立）
  [5] 产物三验：登记非空＋文件存在＋**非空有内容（≥1 行非空白）**；
      路径须在项目目录内（realpath 防穿越）；**自查报告文件化**（三模式必填，
      末行 `自查覆盖: X/X 全查` 与账本数字一致——交叉验证防自报虚标）
  [6] 稽查全覆盖：flash=不适用；pro/max=22/22；审查报告内「维度N」集合 == {1..22}
  [7] 自查覆盖：X/X 两数相等且分母 ≥1；与自查报告文件末行数字一致
  [8] 交付闸字段 == 通过（人工验＝合法降验态，WARN 放行——无 python 环境的历史章）

机检边界（如实声明）：验格式与覆盖数，不验语义真伪（引句真伪/判定质量仍靠
冷读与用户抽核）。无 python 环境按 core/workflow.md 〇-补 三卡口人工对照，
日志注明「人工验」。
"""
import sys, re, os, argparse

try:
    import yaml
except ImportError:
    print("FAIL 需要 pyyaml：pip install pyyaml"); sys.exit(1)

MODE_AGENTS = {"flash": ["本体"], "pro": ["本体", "冷读"],
               "max": ["队长", "写作员", "审查员", "记账员"]}
MODE_PRODUCTS = {"flash": ["自查报告"], "pro": ["审查报告", "自查报告"],
                 "max": ["章任务包", "章草稿", "审查报告", "自查报告"]}
DIM_SET = set(range(1, 23))
errors, warns = [], []

def fail(ch, msg): errors.append(f"第{ch}章｜{msg}")

def read_nonblank(path):
    try:
        return [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    except Exception:
        return None

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
    fixed = data.get("角色固定属性", {}).get("工作流模式")

    # [2] 章号连续性（int 归一防类型混淆）
    chs = []
    for e in logs:
        try: chs.append(int(e.get("章")))
        except (TypeError, ValueError): chs.append(None)
    if None in chs:
        errors.append("日志存在无法解析的章号（类型混淆）")
    if all(c is not None for c in chs) and sorted(chs) != list(range(1, len(chs) + 1)):
        errors.append(f"日志章号不连续（缺号漏登）: 现有 {sorted(chs)}")

    for e in logs:
        try: ch = int(e.get("章"))
        except (TypeError, ValueError): ch = e.get("章", "?")
        if a.chapter is not None and ch != a.chapter:
            pass  # 关注章外的章仍全量检查（历史章 FAIL 一并报——防展示性通过隐藏假执行）
        sel, act = e.get("选定模式"), e.get("实际执行模式")
        if sel not in MODE_AGENTS: fail(ch, f"选定模式非法: {sel}"); continue
        if fixed and fixed != sel: fail(ch, f"选定模式({sel})≠固定属性({fixed})")
        if sel != act:
            if not e.get("降级确认"): fail(ch, f"选定{sel}实际{act}且无降级确认——判假执行")
            else: warns.append(f"第{ch}章｜降级 {sel}→{act}（有确认，合法）")
        agents = e.get("调用代理") or []
        if act in MODE_AGENTS:
            missing = [x for x in MODE_AGENTS[act] if x not in agents]
            if missing: fail(ch, f"调用代理缺必需集: {missing}")
        # [5] 产物三验＋路径约束
        prods = e.get("产物") or {}
        for k in MODE_PRODUCTS.get(act, []):
            v = prods.get(k)
            if not v: fail(ch, f"产物缺登记: {k}"); continue
            fp = os.path.realpath(os.path.join(root, v))
            if not fp.startswith(root + os.sep) and fp != root:
                fail(ch, f"产物路径越出项目目录: {k}={v}"); continue
            if not os.path.isfile(fp): fail(ch, f"产物文件不存在: {k}={v}"); continue
            nb = read_nonblank(fp)
            if nb is None or not nb: fail(ch, f"产物文件为空/不可读: {k}={v}")
        # [6][7] 覆盖数与交叉验证
        cov = str(e.get("稽查全覆盖", ""))
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
                    dims = set(int(x) for x in
                               re.findall(r"维度\s*(\d+)", open(fp, encoding="utf-8").read()))
                    if dims != DIM_SET:
                        fail(ch, f"审查报告维度覆盖 {len(dims)}/22，缺: {sorted(DIM_SET - dims)}")
        sc = str(e.get("自查覆盖", ""))
        m = re.match(r"^(\d+)/(\d+)$", sc)
        if not m or m.group(1) != m.group(2) or int(m.group(2)) < 1:
            fail(ch, f"自查覆盖计数不自洽: {sc or '空'}（应 X/X 两数相等）")
        srp = prods.get("自查报告")
        if srp:
            fp = os.path.realpath(os.path.join(root, srp))
            if os.path.isfile(fp) and fp.startswith(root + os.sep):
                tail = [l for l in open(fp, encoding="utf-8").read().splitlines() if l.strip()]
                tm = re.search(r"自查覆盖[:：]\s*(\d+)\s*/\s*(\d+)", tail[-1]) if tail else None
                if not tm: fail(ch, f"自查报告末行缺『自查覆盖: X/X 全查』机检锚: {srp}")
                elif m and (tm.group(1) != m.group(1) or tm.group(2) != m.group(2)):
                    fail(ch, f"自查报告末行 {tm.group(1)}/{tm.group(2)} ≠ 账本 {sc}——自报与文件不符")
        # [8] 闸判定（人工验＝合法降验态）
        gate = e.get("交付闸")
        if gate == "人工验":
            warns.append(f"第{ch}章｜交付闸=人工验（无 python 环境合法态，放行）")
        elif gate != "通过":
            fail(ch, f"交付闸={gate}——未过闸章不得交付")
    for w in warns: print("WARN", w)
    if errors:
        print(f"FAIL 交付闸机检未过（{len(errors)} 项）:")
        for x in errors: print("  -", x)
        sys.exit(1)
    print("PASS 交付闸机检：模式保真/代理集/产物三验/维度覆盖/自查交叉/闸判定 全过")
    sys.exit(0)

if __name__ == "__main__":
    main()