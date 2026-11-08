#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本章规则包展开（方向②）
用法: python scripts/query_rules.py --genre 现实向 --type hip-disarticulation \
          --tier "A 含蓄" --mode pro --chapter-kind 日常 [--chapter 3] \
          [--format text|json|markdown] [--out <文件>]

职责：按 scope 从 rules/rules.yaml **只展开本章适用的规则**，产出一份小体积规则包，
     替代「让 AI 自己判断该读哪 20 个文件」。参数来自账本（结构化），结果确定。
双形态：
  - CLI 形态：有 shell 的平台直接调用（--out 写文件）；
  - --format text：纯文本，无 shell 平台可由宿主拼进 system prompt。
硬层（rules/hard-layer.md）**永远单独附带、不参与 scope 过滤、不参与检索**。

⚠ 本脚本不做语义相似度召回。禁令是「低频但致命」的，按场景相似度检索会漏掉它。
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


def load_ir(root):
    p = os.path.join(root, "rules", "rules.yaml")
    if not os.path.isfile(p):
        raise SystemExit(f"FAIL 缺 {p}")
    return yaml.safe_load(read(p)) or {}


def normalize_genre(ir, value):
    """题材别名归一：口语简称/历史写法 → enumerations.题材大类 的唯一取值。"""
    if not value:
        return value
    aliases = (ir.get("enumerations") or {}).get("题材别名") or {}
    v = str(value).strip()
    return aliases.get(v, v)


def matches(rule, ctx):
    """scope 匹配：省略某维＝该维全适用；任一已声明的维不匹配即排除。
    ⚠ 只消费 scope；rules.yaml 的 scope_key 是预留维度标注，当前不参与过滤。"""
    scope = rule.get("scope") or {}
    for key, values in scope.items():
        want = ctx.get(key)
        if want is None:
            continue
        if want not in (values or []):
            return False
    return True


def expand(ir, ctx):
    rules = ir.get("rules") or []
    selected = [r for r in rules if isinstance(r, dict) and matches(r, ctx)]
    hard = [r for r in selected if r.get("layer") == "hard"]
    std = [r for r in selected if r.get("layer") == "standard"]
    soft = [r for r in selected if r.get("layer") == "soft"]
    return {"hard": hard, "standard": std, "soft": soft, "all": selected}


def render_text(ctx, pack, hard_layer_path):
    lines = []
    lines.append("=== 本章规则包（由 query_rules.py 展开，勿凭记忆补写规则）===")
    lines.append(f"题材={ctx.get('题材大类') or '未指定'} | 类型={ctx.get('截肢类型') or '未指定'} | "
                 f"尺度档={ctx.get('亲密尺度档') or '未指定'} | 模式={ctx.get('工作流模式') or '未指定'} | "
                 f"冲突强度档={ctx.get('冲突强度档') or '未指定'} | 章型={ctx.get('chapter_kind') or '未指定'} | "
                 f"章号={ctx.get('chapter') or '未指定'}")
    lines.append("")
    lines.append("【硬约束常驻层】整段见 rules/hard-layer.md，❌ 不参与检索、不得省略；")
    lines.append("  三条硬闸 / 回避清单 / 器具损耗禁令 / 类型生理红线 / 移动承重 / 环境归因。")
    if os.path.isfile(hard_layer_path):
        lines.append("")
        lines.append(read(hard_layer_path).rstrip())
    for title, key in (("本章适用·硬层规则", "hard"),
                       ("本章适用·标准规则", "standard"),
                       ("本章适用·体检提示（软）", "soft")):
        lines.append("")
        lines.append(f"【{title}】{len(pack[key])} 条")
        for r in pack[key]:
            lines.append(f"  - {r.get('id')} {r.get('title', '')}：{r.get('assertion', '')}")
            if r.get("enforced_by"):
                lines.append(f"    机检：{r['enforced_by']}")
            if r.get("source"):
                lines.append(f"    权威源：{r['source']}")
    lines.append("")
    lines.append("=== 规则包结束：本包未载的事实一律回读源文件，❌ 不得凭摘要写作 ===")
    return "\n".join(lines)


def render_markdown(ctx, pack, hard_layer_path):
    t = render_text(ctx, pack, hard_layer_path)
    return "# 本章规则包\n\n```text\n" + t + "\n```\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--genre", default=None, help="题材大类")
    ap.add_argument("--type", dest="amp_type", default=None, help="截肢类型文件名（不含 .md）")
    ap.add_argument("--tier", default=None, help="亲密尺度档")
    ap.add_argument("--mode", default=None, help="工作流模式")
    ap.add_argument("--chapter-kind", default=None, help="章型：日常/战斗/亲密/开篇/收束")
    ap.add_argument("--conflict", default=None, help="冲突强度档（烈/高/中/低）；仅作坐标标注，当前不参与过滤")
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--format", default="text", choices=["text", "json", "markdown"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    ir = load_ir(root)
    ctx = {
        "题材大类": normalize_genre(ir, a.genre),
        "冲突强度档": a.conflict,
        "亲密尺度档": a.tier,
        "工作流模式": a.mode,
        "截肢类型": a.amp_type,
        "chapter_kind": a.chapter_kind,
        "chapter": a.chapter,
    }
    pack = expand(ir, ctx)
    hard_path = os.path.join(root, "rules", "hard-layer.md")

    if a.format == "json":
        out = {"context": {k: v for k, v in ctx.items() if v is not None},
               "hard_layer_file": "rules/hard-layer.md",
               "hard_layer_always_on": True,
               "counts": {k: len(pack[k]) for k in ("hard", "standard", "soft")},
               "rules": pack["all"]}
        text = json.dumps(out, ensure_ascii=False, indent=2)
    elif a.format == "markdown":
        text = render_markdown(ctx, pack, hard_path)
    else:
        text = render_text(ctx, pack, hard_path)

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print(f"规则包已写入 {a.out}（{len(text)} 字符；"
              f"硬 {len(pack['hard'])} / 标准 {len(pack['standard'])} / 软 {len(pack['soft'])} 条）")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
