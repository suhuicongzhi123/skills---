#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章循环状态机（方向③ · 平台无关内核）
用法:
  python scripts/state_machine.py --ledger <state-ledger.yaml> --show
  python scripts/state_machine.py --ledger <...> --advance <目标态> [--mode flash|pro|max]
  python scripts/state_machine.py --ledger <...> --check

职责：把「章末自查 → 冷读 → 修正 → 过闸 → 交付」的转移由**代码判定**，AI 跳不了步。
     状态与转移表的唯一事实源是 rules/rules.yaml chapter_states；
     gatecheck [17] 内嵌同一份表做交付闸校验（由 compile_rules.py 校验两处一致）。

兼容性：只需 PyYAML + 标准库。无 shell / 无 hooks 的平台可由宿主把
     `--show` 的输出拼进 prompt，由 AI 按输出自行核对（advisory 降级，见 PLATFORM-CN.md）。
"""
import argparse
import json
import os
import sys

try:
    import yaml
except ImportError:
    print("FAIL 需要 PyYAML：pip install pyyaml")
    sys.exit(2)

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_fsm(root):
    p = os.path.join(root, "rules", "rules.yaml")
    ir = yaml.safe_load(read(p)) or {}
    return ir.get("chapter_states") or {}


def get_state(ledger_path):
    if not os.path.isfile(ledger_path):
        raise SystemExit(f"FAIL 账本不存在: {ledger_path}")
    d = yaml.safe_load(read(ledger_path)) or {}
    return d, (d.get("章节状态") or {})


def patch_ledger(text, target, new_trail):
    """文本级推进：只改写「章节状态」块内的 当前态/轨迹 两行，其余逐字保留。

    为什么不用 yaml.safe_dump 全量重写：账本含大量行内注释与维护者手写格式，
    safe_dump 会把它们全部删除并漂移缩进（实测顶部注释会丢失，已修复）。
    识别规则：定位顶格「章节状态:」行，取其后连续缩进行（含缩进注释行）直至
    下一个顶格键；块内 当前态/轨迹 行替换值（保持原缩进），其余行原样保留；
    缺字段则按块内缩进追加。
    """
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("章节状态:"))
    except StopIteration:
        return None
    end = len(lines)
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if l.strip() and not l[0].isspace():
            end = i
            break
    block = lines[start + 1:end]
    trail_yaml = "[" + ", ".join(new_trail) + "]"
    has_state = any(l.lstrip().startswith("当前态:") for l in block if l.strip())
    has_trail = any(l.lstrip().startswith("轨迹:") for l in block if l.strip())
    new_block = []
    # v9.5 修：`轨迹:` 若原为块式列表（轨迹:\n  - 待规划），替换成流式值后
    # 必须吞掉其后的 `- xxx` 行，否则留下孤儿列表项，整份账本 YAML 解析崩掉
    # （实测：推进到「已规划」后 line 113-116 结构非法，后续所有脚本全炸）。
    _skip_sub = False
    for l in block:
        stripped = l.lstrip() if l.strip() else l
        indent = l[:len(l) - len(stripped)]
        if stripped.startswith("当前态:"):
            _skip_sub = False
            new_block.append(indent + f"当前态: {target}\n")
        elif stripped.startswith("轨迹:"):
            _skip_sub = True
            new_block.append(indent + f"轨迹: {trail_yaml}\n")
        elif _skip_sub and stripped.startswith("- "):
            continue          # 块式列表项，已并入上一行的流式值
        else:
            _skip_sub = False
            new_block.append(l)
    if not (has_state and has_trail):
        base_indent = "  "
        for l in block:
            if l.strip():
                s = l.lstrip()
                base_indent = l[:len(l) - len(s)]
                break
        if not has_state:
            new_block.append(base_indent + f"当前态: {target}\n")
        if not has_trail:
            new_block.append(base_indent + f"轨迹: {trail_yaml}\n")
    new_block = [l if l.endswith("\n") else l + "\n" for l in new_block]
    return "".join(lines[:start + 1] + new_block + lines[end:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--advance", default=None)
    ap.add_argument("--mode", default=None, choices=["flash", "pro", "max"])
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    fsm = load_fsm(root)
    allowed = fsm.get("allowed") or []
    trans = fsm.get("transitions") or {}
    forbidden = []
    for j in (fsm.get("forbidden_jumps") or []):
        if "→" in j:
            x, y = j.split("→", 1)
            forbidden.append((x.strip(), y.strip()))

    d, st = get_state(a.ledger)
    cur = str(st.get("当前态", "") or "").strip()
    trail = st.get("轨迹") or []
    if isinstance(trail, str):
        trail = [x.strip() for x in trail.replace("→", ",").split(",") if x.strip()]
    trail = [str(x).strip() for x in trail]
    mode = a.mode or str((d.get("角色固定属性") or {}).get("工作流模式", "") or "").strip()

    if a.show or (not a.check and not a.advance):
        info = {
            "当前态": cur or "（未登记）",
            "轨迹": trail,
            "模式": mode or "（未登记）",
            "合法后继": trans.get(cur, []),
            "禁用跳步": [f"{x} → {y}" for x, y in forbidden],
            "下一章起点": "待规划（已交付后回卷）",
        }
        print(json.dumps(info, ensure_ascii=False, indent=2) if a.as_json else
              "\n".join(f"{k}: {v}" for k, v in info.items()))
        return 0

    errors = []

    def fail(msg):
        errors.append(msg)

    if cur and cur not in allowed:
        fail(f"当前态「{cur}」非法")
    for x in trail:
        if x not in allowed:
            fail(f"轨迹含非法态「{x}」")
    for i in range(len(trail) - 1):
        x, y = trail[i], trail[i + 1]
        if x in trans and y not in trans[x]:
            fail(f"非法转移 {x} → {y}")
        if (x, y) in forbidden:
            fail(f"跳步 {x} → {y}")
    if mode == "flash" and "已冷读" in trail:
        fail("flash 模式不得出现「已冷读」（降级禁止）")
    # 与 gatecheck [17] 同口径：pro/max 冷读义务看**当前章段**（最后一次回卷点之后的段），
    # 历史章的「已冷读」不得掩盖当前章伪跳冷读（对齐修复）
    seg = trail
    for i in range(len(trail) - 1):
        if trail[i] == "已交付" and trail[i + 1] == "待规划":
            seg = trail[i + 1:]
    if mode in ("pro", "max") and seg and seg[-1] == "已交付" and "已冷读" not in seg:
        fail(f"{mode} 模式交付轨迹缺「已冷读」")

    pending = None
    if a.advance:
        target = a.advance.strip()
        if target not in allowed:
            fail(f"目标态「{target}」非法")
        elif cur and cur in trans and target not in trans[cur]:
            fail(f"不允许 {cur} → {target}（合法后继：{trans[cur]}）")
        elif (cur, target) in forbidden:
            fail(f"禁止跳步 {cur} → {target}")
        elif mode == "flash" and target == "已冷读":
            fail("flash 模式不得进入「已冷读」")
        else:
            new_trail = trail + [target] if trail else [cur or "待规划", target]
            if cur == target and trail:
                new_trail = trail
            pending = (target, new_trail)

    # 先统一判错，再落盘——❌ 不得因「目标态合法」就绕过轨迹/模式的既有错误
    if errors:
        for e in errors:
            print("FAIL", e)
        return 1

    if pending:
        target, new_trail = pending
        new_text = patch_ledger(read(a.ledger), target, new_trail)
        if new_text is None:
            print("FAIL 账本内未找到「章节状态」块，无法文本级推进（先按模板补块）")
            return 1
        with open(a.ledger, "w", encoding="utf-8", newline="") as f:
            f.write(new_text)
        print(f"OK 状态推进：{cur or '（未登记）'} → {target}")
        return 0

    print("OK 章节状态机校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
