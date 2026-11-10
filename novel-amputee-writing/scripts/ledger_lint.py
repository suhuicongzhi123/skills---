#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""账本体检：填之前跑一次，把「填完才发现结构错」的四类问题提前拦掉。

用法：
    python scripts/ledger_lint.py <项目目录>/state-ledger.yaml

查四件事：
  1. YAML 能否解析（结构错直接给到行号与上下文）
  2. 顶层键是否重复（YAML 后者覆盖前者，静默丢数据）
  3. 父键有没有被当标量填了值（这是最高频的错：填了父键，子键悬空，解析失败）
  4. 逐章必填字段是否为空

为什么要有这个脚本：
  实测两章，账本填充各失败 4 次，全是同一类——把父键当标量填。
  模板里已经写了「哪些是父键」，但**填的时候不会去读那段注释**。
  人写、机器查，比「靠人记得住」可靠。
"""
import io
import sys

import yaml

# 父键：有子键，不能当标量填值。填了就会让子键悬空、解析失败。
PARENT_KEYS = {
    "受限让路", "主旨锚", "情节事件登记", "大纲对齐", "用户指令变更", "幻肢触发",
    "能力受限", "拐杖", "假肢", "辅具空白期", "重要物品", "产物", "调用代理",
    "文风契约", "声口指纹", "特殊移动", "战斗豁免", "资源账", "题材契约",
    "当前状态", "章节状态", "本章登记", "本章自评", "distribution", "核查记录",
    "工作流执行日志", "解法台账", "open_setups", "时间线", "关系状态", "信息状态",
    "角色弧状态", "世界观锁定", "角色固定属性", "章节登记归档",
    # 已知的占位键名（须改写成具体物名，不是填值）
    "物品名",
}

# 逐章必填（对照 templates/state-ledger.yaml 顶部的「每章只改这些」）
REQUIRED = [
    ("当前状态", "章"),
    ("本章登记", "张力级"),
    ("本章登记", "节拍角色"),
    ("本章登记", "本章beat"),
    ("本章登记", "章末钩子类型"),
    ("本章登记", "钩子兑现锚"),
    ("本章登记", "受限beat"),
    ("本章自评", "最活的一句"),
    ("章节状态", "当前章"),
]


def top_level_keys(lines):
    """顶层键（零缩进、形如 key:）出现次数"""
    seen = {}
    for i, ln in enumerate(lines, 1):
        if not ln or ln.startswith(("#", " ", "\t", "-")):
            continue
        if ":" not in ln:
            continue
        k = ln.split(":", 1)[0].strip()
        if not k or " " in k:
            continue
        seen.setdefault(k, []).append(i)
    return seen


def scalar_parents(lines):
    """父键被填了标量值：`  键: 某值` 而后跟更深缩进的子键"""
    bad = []
    for i, ln in enumerate(lines):
        st = ln.strip()
        if not st or st.startswith("#"):
            continue
        key = st.split(":", 1)[0].strip() if ":" in st else ""
        if key not in PARENT_KEYS:
            continue
        rest = st.split(":", 1)[1].strip()
        if not rest or rest.startswith("#"):
            continue
        # 看后面紧跟的有效行是否更深缩进 → 说明本键其实是父键
        base = len(ln) - len(ln.lstrip())
        for j in range(i + 1, len(lines)):
            s2 = lines[j]
            if not s2.strip() or s2.strip().startswith("#"):
                continue
            if len(s2) - len(s2.lstrip()) > base:
                bad.append((i + 1, key, rest[:20]))
            break
    return bad


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/ledger_lint.py <项目目录>/state-ledger.yaml")
        return 2
    path = sys.argv[1]
    text = io.open(path, encoding="utf-8").read()
    lines = text.split("\n")
    fails, warns = [], []

    # 1) 解析
    data = None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f"第 {mark.line + 1} 行第 {mark.column + 1} 列" if mark else "位置未知"
        fails.append(f"YAML 解析失败（{where}）：{getattr(e, 'problem', e)}")
        if mark:
            lo, hi = max(0, mark.line - 2), min(len(lines), mark.line + 3)
            for n in range(lo, hi):
                flag = ">>" if n == mark.line else "  "
                fails.append(f"   {flag} {n + 1}| {lines[n]}")
        fails.append("  常见原因：父键被当标量填了值（见下方第 3 项），或列表项缩进不齐")

    # 2) 顶层键重复
    for k, ln_list in top_level_keys(lines).items():
        if len(ln_list) > 1:
            fails.append(f"顶层键重复：「{k}」出现在第 {ln_list} 行"
                         f"——YAML 后者覆盖前者，前一份数据连同注释会被静默丢弃")

    # 3) 父键填标量
    for ln_no, key, val in scalar_parents(lines):
        fails.append(f"父键被填了值：第 {ln_no} 行「{key}: {val}…」"
                     f"——该键有子键，应填子键；填父键会让子键悬空、解析失败"
                     f"（占位键「物品名」应改写成具体物名，如「记账本:」）")

    # 4) 必填非空
    if isinstance(data, dict):
        for blk, key in REQUIRED:
            node = data.get(blk)
            if not isinstance(node, dict):
                warns.append(f"缺少块「{blk}」")
                continue
            v = node.get(key)
            empty = v is None or (isinstance(v, str) and not v.strip()) or v == [] or v == {}
            if empty:
                warns.append(f"逐章必填为空：{blk}.{key}")

    for f in fails:
        print("FAIL " + f)
    for w in warns:
        print("WARN " + w)
    if not fails:
        print(f"PASS 账本结构完好（{len(warns)} 条提示）")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
