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
硬层（rules/hard-layer.md）不参与 scope 过滤、不参与检索，开写前须整段单独注入。
规则包**默认仍附硬层全文**（兼容只拼这一份规则包进 system prompt 的平台）；
已由宿主/hook 单独整段注入硬层时，用 --no-hard-layer 去掉重复全文（省约 4.3 KB/章）。
⚠ 去掉该参数前必须确认硬层确实已在场；拿不准就用默认，宁可重复不可遗漏。

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


# 章型 → 本章必读专项文件（v9：旧版 --chapter-kind 只写进包头，战斗章不带 K 表，BUG-015/023）
KIND_EXTRA = {
    "战斗": [("topics/combat-mechanics.md", "§十四 K01–K13 自查表、§八 制造四选一、§一 回合与三拍链（回合≠场）"),
             ("core/intensity.md", "三、战斗回合制：回合数、四拍写法、动作密度（每 100 字 ≥2 个动作）")],
    "亲密": [("topics/intimacy-explicit.md", "§〇 亲密戏也是戏、体位矩阵、露骨度下限"),
             ("core/intensity.md", "四、对话博弈（越近越短，但不许换人）")],
    "日常": [("topics/daily-actions.md", "蹲/坐/起身/弯腰/转身 分型速查"),
             ("core/intensity.md", "一、强度曲线（日常章最容易全章平坦）"),
             ("core/scene-drive.md", "四、详略差（日常章是第一大流水账灾区）、三、假戏六型")],
    "对话": [("core/voice.md", "二 声音四要素、四 语气切换矩阵、十一 自查三问"),
             ("core/emotion-signal.md", "一 三层信号（语言＞身体＞面部）、四 紧张时的语言失控六种"),
             ("core/intensity.md", "四、对话博弈（争夺物、抢话、答非所问）")],
    "开篇": [("core/opening.md", "前 3 章留存窗口与钩子"),
             ("core/intensity.md", "一、强度曲线（开篇章必须有峰值）")],
    "收束": [("core/structure.md", "弧线收口与回扣"),
             ("core/intensity.md", "一、强度曲线（收束章的峰值靠前）")],
}

# 本章型最容易犯的一个毛病（v9.2 推广，BUG-038）：
# 只给必读文件不够——文件是「该看什么」，毛病是「最容易写错什么」。
# 实测中这一类提示是全篇最有效的一行（「日常章最容易全章平坦」直接改掉了当章写法）。
KIND_PITFALL = {
    "战斗": "把「回合」当「场」——单回合三拍，一场要 3–6 回合；"
            "另一常见错是打中没有后果（打中了对方无伤无代价地走回来）；"
            "幻想向另忌把冲突写成非战斗冲突或复用旧战斗过程（genre/fantasy.md 第十一节）",
    "亲密": "按体位矩阵逐项打勾，写成清点式——矩阵是排除法工具，不是施工图；"
            "一场选一个体位写到站住，比换三个各写两段更有分量",
    "日常": "全章平坦，没有一个峰值——日常章最容易从头到尾一个音量，"
            "把最重的一件事用最平的句子写完；"
            "第二大坑是「只有做事、没有动手」：开门/搬椅/拖地/理货，件件必成，"
            "读起来是一份值班日志（见 core/scene-drive.md#一 做事≠动手）",
    "对话": "两个人只在交换信息，没有争任何东西；"
            "更常见的是所有配角都用主角的句长和语气（配角三律：反差／生活／记忆）；"
            "第三大坑是所有人共用一套表情动作——都「看了对方一眼」「没说话」"
            "（盖住名字认不出谁是谁，见 core/emotion-signal.md#七）",
    "开篇": "前三百字交代背景、身世、世界规则，主角还没遇上一件非解决不可的事；"
            "开篇的容忍度是「三句之内有事」",
    "收束": "把该给的结果一直拖到最后一段，前面全是铺垫；"
            "或者收得太干净——没有余波，读者合上书就忘了",
}

# 题材 → 本章必读 + 本题材红线 + 本题材最易犯的毛病（v9.3，BUG-044）
# 立条原因：题材包决定的是「这本书的骨架」（三幕、故事引擎、红线），比章型更上位，
# 但旧版只有章型会带出必读清单，题材这一层整层缺失。作者只能自己记得去读 genre/*.md。
GENRE_EXTRA = {
    "现实向": {
        "files": [
            ("genre/realistic.md", "两条红线／三幕骨架（常态→破裂→新常态）／故事引擎／日常章配比"),
            ("topics/daily-scenes.md", "通勤·厨房·如厕·租房 场景库"),
            ("core/worldbuilding.md", "受限来源恒为身体结构，不写环境控诉"),
        ],
        "redline": "❌ 不写超自然（出现任何即非现实向）｜❌ 不写治愈（截肢不可逆）｜"
                   "❌ 破裂不归因于残疾（破裂来自生活，残疾只提高代价）",
        "pitfall": "把日常写成「不便清单」——应写她怎么把日子过顺，不写她有多难；"
                   "另一常见错是让受限全挂在环境上（台阶、水汽、东西太小），而不是身体结构",
    },
    "幻想向": {
        "files": [
            ("genre/fantasy.md", "第十节 受限豁免与主角补偿（R-032）／第十一节 真实战斗冲突（R-033）／第八节 特殊移动体系"),
            ("topics/combat-magic.md", "1.5 六条红线 A/B 分组／1.7 M01–M08"),
            ("core/worldbuilding.md", "缺失解释框架＋幻想向豁免四界登记"),
        ],
        "redline": "❌ 能力来源须独立于截肢（不写「失去腿换来神力」）｜"
                   "❌ 不得改写生理事实（1.5 A 组红线全书有效）｜"
                   "❌ 战斗章禁止写成非战斗冲突、禁止复用近 5 章战斗过程｜"
                   "❌ 现实向零豁免（主角光环／能力强化补偿不得外溢）",
        "pitfall": "把登记为战斗的章写成对峙、协商或「经过一番周旋」；"
                   "或让主角打赢得爽却不给真打过程（对手降智／一两招结束）",
    },
    "末世生存": {
        "files": [
            ("genre/postapocalyptic.md", "资源账／器具可得性／危机节奏"),
            ("core/worldbuilding.md", "秩序崩解后的无障碍与辅具来源"),
        ],
        "redline": "❌ 不写高科技修复（除非题材明写）｜❌ 资源账连续 3 章不记账＝经济系统失效",
        "pitfall": "把末世写成背景布——资源账不记，危机就没有重量；"
                   "或者反过来，把每一天都写成生存危机，读者会疲劳",
    },
    "古装向": {
        "files": [
            ("genre/historical.md", "器具按时代（木杖/木义腿）／礼法与身体"),
            ("core/worldbuilding.md", "时代对残疾的解释框架"),
        ],
        "redline": "❌ 器具与医学不得超时代｜❌ 不写现代康复观念与无障碍话语",
        "pitfall": "用现代口吻写古人的身体观——「康复训练」「心理建设」这类词一出现就出戏",
    },
}


def render_text(ctx, pack, hard_layer_path, include_hard=True):
    lines = []
    lines.append("=== 本章规则包（由 query_rules.py 展开，勿凭记忆补写规则）===")
    lines.append(f"题材={ctx.get('题材大类') or '未指定'} | 类型={ctx.get('截肢类型') or '未指定'} | "
                 f"尺度档={ctx.get('亲密尺度档') or '未指定'} | 模式={ctx.get('工作流模式') or '未指定'} | "
                 f"冲突强度档={ctx.get('冲突强度档') or '未指定'} | 章型={ctx.get('chapter_kind') or '未指定'} | "
                 f"章号={ctx.get('chapter') or '未指定'}")
    lines.append("")
    lines.append("【硬约束常驻层】整段见 rules/hard-layer.md，❌ 不参与检索、不得省略；")
    lines.append("  成年闸与恢复期红线 / 回避清单与器具禁令 / 类型生理红线 / 移动与承重 / 环境归因 / 写作时点三问。")
    if include_hard and os.path.isfile(hard_layer_path):
        lines.append("")
        lines.append(read(hard_layer_path).rstrip())
    elif not include_hard:
        lines.append("  ⚠ 本包按 --no-hard-layer 生成，未附硬层全文：仅当宿主已单独整段注入硬层时可用；")
        lines.append("     未注入者须去掉该参数重新生成，否则不得开写。")
    # ── 动笔前四问（v9.4）：放在规则列表之前，因为「有没有戏」比「有没有违规」更前置。
    # 立条原因：实测一章机检全绿、段落指标全达标，读起来是清单——五件事答得出，
    # 但第 3 件填「跟着走了一圈」，第 4/5 件填「无」。规则再多也拦不住「没有事件」的稿子。
    lines.append("")
    lines.append("【动笔前四问（v9.4 · 先过这一关，再看下面的规则）】")
    lines.append("  ① 这一章她动手几次、败在哪？（「跟着走/看着/数着/照做/等着/记着」不算动手）")
    lines.append("  ② 对手今天本来想干什么？（须与她的目标冲突；答不出＝配角只有功能、没有嘴）")
    lines.append("  ③ 篇幅第一名是谁？（必须是「动手并失败的那一次」，不是搬东西/走路/收拾/等待）")
    lines.append("  ④ 她哪三处不在状态？（多余的一步/顺序错乱/中途停住/话没说完/做完发现没必要）")
    lines.append("  答不出＝这章还没有戏：改事件（加一次会失败的动手），❌ 不要用描写补。")
    lines.append("  详见 core/scene-drive.md#七；四问须落盘进章契约「★四行硬项」，gatecheck [27] 硬检。")
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
    # ── 题材专项（v9.3，BUG-044）：题材比章型上位，故排在章型之前 ──
    # 旧版只有章型会带出必读清单，题材只参与规则 scope 过滤，不产生「必读文件」——
    # 于是两条红线、三幕骨架、故事引擎全靠作者自己去读文件，这是唯一没进包的一层。
    _genre = (ctx.get("题材大类") or "").strip()
    if _genre in GENRE_EXTRA:
        _g = GENRE_EXTRA[_genre]
        lines.append("")
        lines.append(f"【本题材专项（题材={_genre}）】规则包不展开正文，按下列清单回读源文件")
        for _f, _w in _g["files"]:
            lines.append(f"  - {_f}  →  {_w}")
        lines.append("")
        lines.append(f"【本题材红线】{_g['redline']}")
        lines.append(f"【本题材最易犯的一个毛病】{_g['pitfall']}")
    elif _genre:
        lines.append("")
        lines.append(f"【本题材专项】题材「{_genre}」无专属清单；现实向／幻想向／末世生存／古装向 四类自动带出。")

    _kind = (ctx.get("chapter_kind") or "").strip()
    if _kind in KIND_EXTRA:
        lines.append("")
        lines.append(f"【本章型专项（章型={_kind}）】规则包不展开正文，按下列清单回读源文件")
        for _f, _w in KIND_EXTRA[_kind]:
            lines.append(f"  - {_f}  →  {_w}")
        if _kind in KIND_PITFALL:
            lines.append("")
            lines.append(f"【本章型最易犯的一个毛病】{KIND_PITFALL[_kind]}")
    elif _kind:
        lines.append("")
        lines.append(f"【本章型专项】章型「{_kind}」无专属清单；战斗/亲密/日常/对话/开篇/收束 六类自动带出。")
    lines.append("")
    lines.append("=== 规则包结束：本包未载的事实一律回读源文件，❌ 不得凭摘要写作 ===")
    return "\n".join(lines)


def render_compact(ctx, pack, hard_layer_path, include_hard=True):
    """紧凑档（小上下文适配）：规则 ID＋title＋一句话断言（截 60 字）。

    **默认仍附硬层全文**（--include-hard-layer 为显式同义写法）；
    仅当硬层已单独整段注入时才用 --no-hard-layer 去掉重复全文，省约 4.3 KB/章；
    代价：规则细节不在场——文末固定声明「compact 档只作索引，
    涉动作/生理/辅具写法须回读源文件」。
    """
    lines = []
    lines.append("=== 本章规则包·compact（小上下文档）===")
    lines.append(f"题材={ctx.get('题材大类') or '未指定'} | 类型={ctx.get('截肢类型') or '未指定'} | "
                 f"尺度档={ctx.get('亲密尺度档') or '未指定'} | 模式={ctx.get('工作流模式') or '未指定'} | "
                 f"章号={ctx.get('chapter') or '未指定'}")
    lines.append("")
    if include_hard:
        lines.append("【硬约束常驻层】（全文，❌ 不裁剪）")
        if os.path.isfile(hard_layer_path):
            lines.append(read(hard_layer_path).rstrip())
    else:
        lines.append("【硬约束常驻层】未附全文（--no-hard-layer）：须已单独整段注入 rules/hard-layer.md；")
        lines.append("  成年闸与恢复期红线 / 回避清单与器具禁令 / 类型生理红线 / 移动与承重 / 环境归因 / 写作时点三问。")
    for key in ("hard", "standard", "soft"):
        if pack[key]:
            lines.append("")
            lines.append(f"【{key}】{len(pack[key])} 条")
            for r in pack[key]:
                a1 = str(r.get("assertion", "") or "")[:60]
                lines.append(f"  - {r.get('id')} {r.get('title', '')}｜{a1}")
    lines.append("")
    lines.append("=== compact 档只作索引：规则细节不在场，凡涉动作/生理/辅具写法须回读源文件（权限威源见 rules.yaml）===")
    return "\n".join(lines)


def render_markdown(ctx, pack, hard_layer_path, include_hard=True):
    t = render_text(ctx, pack, hard_layer_path, include_hard)
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
    ap.add_argument("--format", default="text", choices=["text", "json", "markdown", "compact"])
    ap.add_argument("--out", default=None)
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--no-hard-layer", dest="include_hard", action="store_false",
                     help="硬层已由宿主/hook 单独整段注入时使用：规则包不再重复附 4.3 KB 全文")
    grp.add_argument("--include-hard-layer", dest="include_hard", action="store_true",
                     help="显式附带硬层全文（默认；无 shell 或仅拼这一份规则包的平台必须保留）")
    ap.set_defaults(include_hard=True)
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
               "hard_layer_included": a.include_hard,
               "counts": {k: len(pack[k]) for k in ("hard", "standard", "soft")},
               "rules": pack["all"]}
        text = json.dumps(out, ensure_ascii=False, indent=2)
    elif a.format == "markdown":
        text = render_markdown(ctx, pack, hard_path, a.include_hard)
    elif a.format == "compact":
        text = render_compact(ctx, pack, hard_path, a.include_hard)
    else:
        text = render_text(ctx, pack, hard_path, a.include_hard)

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text + "\n")
        print(f"规则包已写入 {a.out}（{len(text)} 字符；硬层全文{'已附' if a.include_hard else '未附'}；"
              f"硬 {len(pack['hard'])} / 标准 {len(pack['standard'])} / 软 {len(pack['soft'])} 条）")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
