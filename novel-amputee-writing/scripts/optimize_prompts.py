#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注入顺序 / 自查提示的离线回归评估（方向④ · DSPy adapter 预留接口）
用法:
  python scripts/optimize_prompts.py --report   # 分层加权风险概览 + 逐条回归清单
  python scripts/optimize_prompts.py --check-hard-layer
  python scripts/optimize_prompts.py --with-dspy   # 探测 dspy 可用性；adapter 为预留接口，当前仍输出静态报告

设计取向：**离线工具，不进 agent 运行时**，因此跨平台兼容性最好——
     产物是普通文本/少样本示例，可以喂给任何平台。
 无 DSPy 时降级为「分层加权风险概览 + 逐条回归清单」，并**显式声明降级**
     （不假装优化、不产出命中率结论）。
 DSPy adapter 是**预留接口**：当前版本只做可用性探测与显式降级声明，
     ❌ 不执行自动优化、不把 mode 伪装成已优化。评测用例 L3 一律由人工逐字校对裁决。

⚠ 优化目标不是「让机检全绿」，而是**评测用例 L3 须由人工逐字裁决**——机检全绿时照样可能语义失真。
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


def try_dspy():
    try:
        import dspy  # noqa: F401
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--check-hard-layer", action="store_true")
    ap.add_argument("--with-dspy", action="store_true")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    ev_path = os.path.join(root, "eval", "eval-set.yaml")
    ev = yaml.safe_load(read(ev_path)) or {}
    cases = ev.get("cases") or []
    weights = (ev.get("scoring") or {}).get("weights") or {}
    hard_path = os.path.join(root, "rules", "hard-layer.md")
    hard = read(hard_path) if os.path.isfile(hard_path) else ""

    by_level = {}
    for c in cases:
        by_level.setdefault(c.get("level", "?"), []).append(c.get("id"))

    # 这是「是否登记了自动拦截层」，不是「是否需要人工」——
    # 后者由用例的 level 决定（L3 一律人工逐字校对），两者不可混为一谈。
    auto_hits = []
    no_auto_layer = []
    for c in cases:
        layer = str(c.get("catch_by", ""))
        if ("compile_rules.py" in layer or "selfcheck.py" in layer
                or "gatecheck" in layer or "硬层" in layer or "能力探测" in layer):
            auto_hits.append(c.get("id"))
        else:
            no_auto_layer.append(c.get("id"))
    l3_cases = [c.get("id") for c in cases if c.get("level") == "L3"]

    hard_ok = all(k in hard for k in ("成年闸", "回避清单", "器具损耗与更换禁令", "类型生理红线"))
    if a.check_hard_layer and not hard_ok:
        print("FAIL 硬约束常驻层缺必需小节")
        return 1

    dspy_available = try_dspy()

    # 分层加权风险概览：weights 真正参与计算；wrong / right 作为逐条人工核对项读出。
    # ⚠ 本表是「回归清单的风险权重分布」，不是「命中率」——命中与否只能由人工逐字校对裁决。
    by_level_risk = {}
    weighted_risk = 0.0
    checklist = []
    for c in cases:
        lv = str(c.get("level", "?"))
        w = float(weights.get(lv, 1.0))
        weighted_risk += w
        by_level_risk[lv] = round(by_level_risk.get(lv, 0.0) + w, 2)
        checklist.append({
            "id": c.get("id"),
            "title": c.get("title"),
            "level": lv,
            "weight": w,
            "catch_by": c.get("catch_by", ""),
            "wrong": str(c.get("wrong", ""))[:60],
            "right": str(c.get("right", ""))[:60],
            "human_only": lv == "L3",
        })
    l3_risk = by_level_risk.get("L3", 0.0)

    result = {
        "cases_total": len(cases),
        "by_level": {k: v for k, v in sorted(by_level.items())},
        "weights": weights,
        "weighted_risk": round(weighted_risk, 2),
        "by_level_risk": {k: v for k, v in sorted(by_level_risk.items())},
        "l3_risk_share": round(l3_risk / weighted_risk, 3) if weighted_risk else 0,
        "checklist": checklist,
        "auto_layer_hits": len(auto_hits),
        "no_auto_layer": no_auto_layer,
        "l3_cases": l3_cases,
        "hard_layer_complete": hard_ok,
        "dspy_available": dspy_available,
        "mode": "static_report",
        "dspy_adapter_status": "reserved（未接线，不执行自动优化）",
        "degradation_notice": (
            "未安装 dspy，已显式降级为静态评分；未执行自动优化"
            if a.with_dspy and not dspy_available else
            "检测到 dspy，但自动优化 adapter 尚未接线——本次仍输出静态报告（不假装优化）"
            if a.with_dspy and dspy_available else
            "静态报告模式：产物为文本/示例，可喂给任意平台"),
        "l3_rule": "L3 用例仅由人工逐字校对裁决，优化器不得代替；本工具不产出「命中率」结论",
    }
    if a.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"评测集: {len(cases)} 例 | 分层: {result['by_level']}")
        print(f"分层加权风险: {result['by_level_risk']} | 总风险 {result['weighted_risk']}"
              f" | 评测用例 L3 占比 {result['l3_risk_share']}")
        print(f"登记了自动拦截层: {len(auto_hits)} 例 | 无自动拦截层: {len(no_auto_layer)} 例 {no_auto_layer}")
        print(f"L3 语义层用例（一律人工逐字校对）: {len(l3_cases)} 例 {l3_cases}")
        print(f"硬层完整性: {'OK' if hard_ok else 'FAIL'}")
        print(f"DSPy: {'可用' if dspy_available else '未安装'} | 模式: {result['mode']}")
        print(result["degradation_notice"])
        print(result["l3_rule"])
        if a.report:
            print("")
            print("逐条回归清单（wrong / right 为人工核对项，不是检测结果）：")
            for x in checklist:
                mark = "人工裁决" if x["human_only"] else "机检/提示层"
                print(f"  {x['id']} [{x['level']} · w{x['weight']} · {mark}] {x['title']}")
                print(f"      wrong: {x['wrong']}")
                print(f"      right: {x['right']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
