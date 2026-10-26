#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付闸机检脚本（v5.5.0 起）
用法: python gatecheck.py <小说项目目录> [--chapter N]
  --chapter N 只检第 N 章的日志条目（默认全部条目）

机检范围＝结构与覆盖数（格式可验部分）：
  [1] 账本存在且可解析；工作流执行日志块结构完整
  [2] 模式保真：选定模式 == 实际执行模式；不等时须有「降级确认」字段（真降级合法，
      谎报才违规——降级确认缺＝FAIL）
  [3] 调用代理集 ⊇ 模式必需集（flash=本体 / pro=本体+冷读 / max=队长+写作员+审查员+记账员）
  [4] 产物文件：pro 须登记审查报告且存在；max 须登记章任务包/章草稿/审查报告且均存在
  [5] 稽查全覆盖：flash=不适用；pro/max=22/22
  [6] 审查报告维度覆盖：文件内「维度N」标记集合 == {1..22}
  [7] 自查覆盖：X/X 两数相等且分母 ≥1（全查总计数自洽）
  [8] 交付闸字段 == 通过

机检边界（如实声明）：验格式与覆盖数，不验语义真伪（引句真伪/判定质量仍靠
冷读与用户抽核）。无 python 环境按 core/workflow.md 〇-补 三卡口人工对照。
"""
import sys, re, os, argparse

try:
    import yaml
except ImportError:
    print("FAIL 需要 pyyaml：pip install pyyaml"); sys.exit(1)

MODE_AGENTS = {"flash": ["本体"], "pro": ["本体", "冷读"],
               "max": ["队长", "写作员", "审查员", "记账员"]}
MODE_PRODUCTS = {"flash": [], "pro": ["审查报告"],
                 "max": ["章任务包", "章草稿", "审查报告"]}
DIM_SET = set(range(1, 23))
errors, warns = [], []

def fail(ch, msg): errors.append(f"第{ch}章｜{msg}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--chapter", type=int, default=None)
    a = ap.parse_args()
    ledger = os.path.join(a.dir, "state-ledger.yaml")
    if not os.path.isfile(ledger):
        print("FAIL 未找到 state-ledger.yaml（目录＝小说项目工作区）"); sys.exit(1)
    data = yaml.safe_load(open(ledger, encoding="utf-8")) or {}
    logs = data.get("工作流执行日志") or []
    if not logs:
        print("FAIL 工作流执行日志为空——无执行证据链（口头声明不作数）"); sys.exit(1)
    fixed = data.get("角色固定属性", {}).get("工作流模式")
    for e in logs:
        ch = e.get("章", "?")
        if a.chapter is not None and ch != a.chapter:
            continue
        sel, act = e.get("选定模式"), e.get("实际执行模式")
        if sel not in MODE_AGENTS: fail(ch, f"选定模式非法: {sel}"); continue
        if fixed and fixed != sel: fail(ch, f"选定模式({sel})≠固定属性({fixed})")
        if sel != act:
            if not e.get("降级确认"): fail(ch, f"选定{sel}实际{act}且无降级确认——判假执行")
            else: warns.append(f"第{ch}章｜降级 {sel}→{act}（有确认，合法）")
        agents = e.get("调用代理") or []
        missing = [x for x in MODE_AGENTS[act] if x not in agents] if act in MODE_AGENTS else ["?"]
        if missing != ["?"] and missing: fail(ch, f"调用代理缺必需集: {missing}")
        prods = e.get("产物") or {}
        for k in MODE_PRODUCTS.get(act, []):
            v = prods.get(k)
            if not v: fail(ch, f"产物缺登记: {k}")
            elif not os.path.isfile(os.path.join(a.dir, v)): fail(ch, f"产物文件不存在: {k}={v}")
        cov = str(e.get("稽查全覆盖", ""))
        if act == "flash":
            if "不适用" not in cov: fail(ch, "flash 须记 不适用")
        else:
            m = re.match(r"^(\d+)/(\d+)$", cov)
            if not m or m.group(1) != "22" or m.group(2) != "22":
                fail(ch, f"稽查全覆盖应为 22/22，实为: {cov or '空'}")
            rp = prods.get("审查报告")
            if rp and os.path.isfile(os.path.join(a.dir, rp)):
                dims = set(int(x) for x in
                           re.findall(r"维度\s*(\d+)", open(os.path.join(a.dir, rp), encoding="utf-8").read()))
                if dims != DIM_SET:
                    fail(ch, f"审查报告维度覆盖 {len(dims)}/22，缺: {sorted(DIM_SET - dims)}")
        sc = str(e.get("自查覆盖", ""))
        m = re.match(r"^(\d+)/(\d+)$", sc)
        if not m or m.group(1) != m.group(2) or int(m.group(2)) < 1:
            fail(ch, f"自查覆盖计数不自洽: {sc or '空'}（应 X/X 两数相等）")
        if e.get("交付闸") != "通过":
            fail(ch, f"交付闸={e.get('交付闸')}——未过闸章不得交付")
    for w in warns: print("WARN", w)
    if errors:
        print(f"FAIL 交付闸机检未过（{len(errors)} 项）:")
        for x in errors: print("  -", x)
        sys.exit(1)
    print("PASS 交付闸机检：模式保真/代理集/产物/维度覆盖/自查计数/闸判定 全过")
    sys.exit(0)

if __name__ == "__main__":
    main()