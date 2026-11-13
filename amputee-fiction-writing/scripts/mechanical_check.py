#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mechanical_check.py —— 截肢题材小说机械自查脚本

能力边界（必读）：
  本脚本基于规则表与正则匹配，不理解语义，只做辅助筛查。存在误报与漏报，
  所有报告条目必须人工研判；它是一写一审工作流的第 3 阶段工具，不替代第 4 阶段冷读稽查。

用法：
  python mechanical_check.py --config <配置.json> --chapter <章节.md> [--ledger <台账.json>]
                             [--report <输出报告.md>] [--json]

退出码：
  0 = 无错误级问题（可能仍有警告）
  1 = 存在错误级问题
  2 = 运行错误（文件缺失、配置非法、规则文件损坏）

配置 JSON schema（完整示例见 assets/机械自查配置示例.json，本说明为字段口径唯一权威）：
{
  "work": {"title": "作品名", "genre": "题材", "library_version": "vX.Y.Z"},
  "characters": [
    {
      "name": "角色名（必填）",
      "aliases": ["别名"],            # 可选，机械识别同一人用
      "amputations": [                # 必填，缺失即退出码 2
        {"code": "HD", "side": "L"}   # 键名是 code 不是 type；side 只接受 L/R/B
      ],
      "devices": ["C-01"]             # 可选，引用下方 devices[].id
    }
  ],
  "devices": [                        # 顶层扁平列表，禁止按角色嵌套成对象
    {"id": "C-01", "holder": "角色名", "type": "axillary_crutches", "count": 2}
  ],
  "exemptions": [
    {"name": "豁免名", "rules": ["规则ID"], "scenes": ["场景一"], "boundary": "边界", "cost": "代价"}
  ]
}

amputations[].code 取值（与 scripts/rules/anatomy.json 同步，共 13 个）：
  下肢 HD 髋离断 / TF 大腿截肢 / KD 膝离断 / TT 小腿截肢 / SYM 赛姆截肢 / FT 足部分截肢
  上肢 SD 肩离断 / FQ 肩胛胸廓间截肢 / TH 大臂截肢 / ED 肘离断 / TR 前臂截肢 / WD 腕离断 / PH 手部分截肢
devices[].type 取值：axillary_crutches 腋拐 / forearm_crutches 肘拐 / single_crutch 单拐 /
                    wheelchair 轮椅 / transfer_board 转移板
exemptions[].scenes 的场景名与正文分场对齐：二级标题用标题全文，* * * 分隔线依次为场景一、场景二……

高频配置错误（均以退出码 2 拒绝运行，先查这四项）：
  1. 字段写成 amputation —— 正确为 amputations 数组；
  2. 截肢项内写 "type" —— 正确键名为 code；
  3. devices 按角色嵌套成对象 —— 正确为顶层扁平列表，角色用 id 数组引用；
  4. side 写中文「左/右」 —— 只接受 L/R/B。

台账 JSON 结构（--ledger 可选）：
  {"scenes":[{"scene":"场景一","opening":{"C-01":"门边立放"},"closing":{"C-01":"手中"}}]}
"""

import argparse
import json
import re
import sys
from pathlib import Path

WINDOW = 40          # 角色归属判断窗口（字符）
CONTEXT_WINDOW = 25  # 允许上下文（辅具/代偿词）判断窗口
RULE_DIR = Path(__file__).resolve().parent / "rules"


def load_json(path, allow_missing=False):
    if path is None and allow_missing:
        return None
    p = Path(path)
    if not p.exists():
        if allow_missing:
            return None
        print(f"[运行错误] 文件不存在：{path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[运行错误] JSON 解析失败：{path}：{exc}", file=sys.stderr)
        sys.exit(2)


SCENE_DIVIDER = re.compile(r"\*[ \t]*\*[ \t]*\*")
SCENE_NUMERALS = "一二三四五六七八九十"


def scene_name(index):
    """分隔线切出的场景按顺序命名为场景一、场景二……超过十个用阿拉伯数字。"""
    return "场景" + (SCENE_NUMERALS[index - 1] if index <= 10 else str(index))


def split_scenes(text):
    """按二级标题或独占一行的 * * * 分隔线切场景，返回 [(标题, 起始行号, 正文), ...]。

    正式小说排版不使用场景二级标题：含分隔线时，分隔线之间的行文依次命名为
    场景一、场景二……，与豁免标记中的场景号对齐；无分隔线时全文按一场处理。
    二级标题切分保留，兼容改动前的章节文件。
    """
    has_divider = any(SCENE_DIVIDER.fullmatch(ln.strip()) for ln in text.splitlines())
    scenes = []
    segment = 1
    current_title = scene_name(segment) if has_divider else "全文"
    current_start = 1
    buffer = []
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if line.startswith("## "):
            if buffer:
                scenes.append((current_title, current_start, "\n".join(buffer)))
                buffer = []
            current_title = line[3:].strip()
            current_start = idx
        elif SCENE_DIVIDER.fullmatch(stripped):
            if buffer:
                scenes.append((current_title, current_start, "\n".join(buffer)))
                buffer = []
            segment += 1
            current_title = scene_name(segment)
            current_start = idx
        else:
            buffer.append(line)
    if buffer:
        scenes.append((current_title, current_start, "\n".join(buffer)))
    return scenes


def line_of(text, pos):
    return text[:pos].count("\n") + 1


def sentence_at(text, pos):
    """返回匹配点所在句子（按句末标点与换行切分）的 (起始, 结束, 文本)"""
    breaks = [0]
    for m in re.finditer(r"[。！？!?\n]", text):
        breaks.append(m.end())
    starts = [0] + breaks
    ends = breaks + [len(text)]
    for start, end in zip(starts, ends):
        if start <= pos < end:
            return start, end, text[start:end]
    return 0, len(text), text


def nearest_owner(scene_text, pos, alias_map):
    """只在匹配点所在句子内寻找角色归属，跨句不归属，防止张冠李戴"""
    _start, _end, sentence = sentence_at(scene_text, pos)
    best = None
    best_dist = WINDOW + 1
    local_offset = scene_text.find(sentence)
    for alias, owner in alias_map.items():
        for m in re.finditer(re.escape(alias), sentence):
            dist = abs((local_offset + m.start()) - pos)
            if dist < best_dist:
                best_dist = dist
                best = owner
    return best if best_dist <= WINDOW else None


def has_nearby(text, pos, words):
    seg = text[max(0, pos - CONTEXT_WINDOW): pos + CONTEXT_WINDOW]
    return any(w in seg for w in words)


def validate_config(config, anatomy):
    codes = anatomy["codes"]
    for ch in config.get("characters", []):
        if "name" not in ch or "amputations" not in ch:
            print(f"[运行错误] 角色缺少 name/amputations：{ch}", file=sys.stderr)
            sys.exit(2)
        for amp in ch["amputations"]:
            if amp.get("code") not in codes:
                print(f"[运行错误] 角色 {ch['name']} 使用了未知代码 {amp.get('code')}", file=sys.stderr)
                sys.exit(2)
            if amp.get("side") not in ("L", "R", "B"):
                print(f"[运行错误] 角色 {ch['name']} 侧别非法：{amp.get('side')}", file=sys.stderr)
                sys.exit(2)


def build_alias_map(config):
    alias_map = {}
    for ch in config["characters"]:
        alias_map[ch["name"]] = ch["name"]
        for alias in ch.get("aliases", []):
            alias_map[alias] = ch["name"]
    return alias_map


def check_side_and_level(ch, scene_title, scene_text, global_text, scene_offset, anatomy, findings):
    side_words = anatomy["side_words"]
    amps = ch["amputations"]
    aliases = [ch["name"]] + ch.get("aliases", [])
    for amp in amps:
        code, side = amp["code"], amp["side"]
        info = anatomy["codes"][code]
        # 单侧角色：相反侧别 + 截肢/残肢表述
        if side in ("L", "R"):
            opp = side_words["L"] if side == "R" else side_words["R"]
            nouns = (anatomy["lower_side_nouns"] if info["limb"] == "lower"
                     else anatomy["upper_side_nouns"])
            hint = "|".join(anatomy["amputation_hint_terms"])
            patterns = [
                rf"{opp}(?:{'|'.join(nouns)}).{{0,5}}(?:{hint})",
                rf"(?:{hint}).{{0,8}}{opp}(?:{'|'.join(nouns)})",
            ]
            for pat in patterns:
                for m in re.finditer(pat, scene_text):
                    if nearest_owner(scene_text, m.start(), {a: ch["name"] for a in aliases}):
                        findings.append(("SIDE-01", "error", scene_title,
                                         line_of(global_text, scene_offset + m.start()),
                                         m.group(0), f"{ch['name']} 登记为{side_words[side]}侧{code}，正文出现相反侧别表述"))
        negation = ["不存在", "没有", "失去", "缺失", "没了", "截去", "截掉"]
        # 平面一致性：截肢侧侧别词 + 不应存在的部件
        if side in ("L", "R") and info["absent_terms"]:
            sw = side_words[side]
            pat = rf"{sw}(?:{'|'.join(info['absent_terms'])})"
            for m in re.finditer(pat, scene_text):
                if has_nearby(scene_text, m.start(), negation):
                    continue
                if nearest_owner(scene_text, m.start(), {a: ch["name"] for a in aliases}):
                    findings.append(("LEVEL-01", "error", scene_title,
                                     line_of(global_text, scene_offset + m.start()),
                                     m.group(0), f"{ch['name']} 为{code}，{sw}侧不应存在该部件"))
        # 无残肢类型出现残肢/残端词
        if not info["has_stump"]:
            for term in anatomy["stump_terms"]:
                for m in re.finditer(term, scene_text):
                    if has_nearby(scene_text, m.start(), negation):
                        continue
                    if nearest_owner(scene_text, m.start(), {a: ch["name"] for a in aliases}):
                        findings.append(("LEVEL-02", "error", scene_title,
                                         line_of(global_text, scene_offset + m.start()),
                                         term, f"{ch['name']} 为{code}，无残肢/骨性残端，应用「截肢侧软组织」表述"))


def expand_applicable_rules(ch, anatomy, action_rules):
    codes = {a["code"] for a in ch["amputations"]}
    sides = {a["side"] for a in ch["amputations"]}
    limbs = {anatomy["codes"][a["code"]]["limb"] for a in ch["amputations"]}
    virtual = set()
    if "B" in sides and limbs == {"lower"}:
        virtual.add("BLL")
    if "B" in sides and limbs == {"upper"}:
        virtual.add("BUL")
    if limbs == {"lower", "upper"}:
        virtual.add("COMBO")
    result = []
    for rule in action_rules["rules"]:
        if not rule.get("automated", True):
            continue
        if set(rule["applies_to"]) & (codes | virtual):
            result.append(rule)
    return result


def check_actions(ch, scene_title, scene_text, global_text, scene_offset, rules,
                  alias_map, exemptions_for_scene, findings):
    owner_alias = {a: ch["name"] for a in [ch["name"]] + ch.get("aliases", [])}
    for rule in rules:
        if rule["id"] in exemptions_for_scene:
            continue
        for pat in rule["patterns"]:
            for m in re.finditer(pat, scene_text):
                owner = nearest_owner(scene_text, m.start(), owner_alias)
                if owner != ch["name"]:
                    continue
                if rule.get("allow_context") and has_nearby(scene_text, m.start(), rule["allow_context"]):
                    continue
                findings.append((rule["id"], rule["severity"], scene_title,
                                 line_of(global_text, scene_offset + m.start()),
                                 m.group(0), f"{ch['name']} 命中 {rule['description']}"))


def check_exemption_markers(text, config, findings):
    registered = {e["name"] for e in config.get("exemptions", [])}
    for m in re.finditer(r"【豁免：(.+?)｜(.+?)】", text):
        if m.group(1).strip() not in registered:
            findings.append(("EXEMPT-01", "error", "全文", line_of(text, m.start()),
                             m.group(0), "使用了未在作品设定总表登记的豁免条目"))


def check_devices(config, scene_title, scene_text, global_text, scene_offset, device_rules, findings):
    inventory = config.get("devices", [])
    inventory_categories = {d["type"] for d in inventory}
    has_crutch = bool({"axillary_crutches", "forearm_crutches", "single_crutch"} & inventory_categories)
    has_wheelchair = "wheelchair" in inventory_categories
    category_terms = {
        "crutch": ["腋拐", "肘拐", "双拐", "单拐", "拐杖", "拐"],
        "wheelchair": ["轮椅"],
        "transfer_board": ["转移板"],
    }
    # DEV-04 凭空出现
    for term in category_terms["crutch"]:
        if not has_crutch and re.search(term, scene_text):
            m = re.search(term, scene_text)
            findings.append(("DEV-04", "error", scene_title,
                             line_of(global_text, scene_offset + m.start()), term,
                             "正文出现拐杖类辅具，但配置清单未登记任何拐杖"))
            break
    for term in category_terms["wheelchair"]:
        if not has_wheelchair and term in scene_text:
            m = re.search(term, scene_text)
            findings.append(("DEV-04", "error", scene_title,
                             line_of(global_text, scene_offset + m.start()), term,
                             "正文出现轮椅，但配置清单未登记"))
    # 其余设备规则
    for rule in device_rules["rules"]:
        if not rule.get("automated", True) or rule["id"] in ("DEV-04", "DEV-05"):
            continue
        in_use = rule["crutch_in_use"]
        if rule["id"] == "DEV-01" and not has_crutch:
            continue
        if rule["id"] == "DEV-02" and "single_crutch" not in inventory_categories:
            continue
        if rule["id"] == "DEV-03" and not has_wheelchair:
            continue
        if in_use and not any(term in scene_text for term in in_use):
            continue
        for pat in rule["conflict_patterns"]:
            for m in re.finditer(pat, scene_text):
                if rule.get("suppress_context") and has_nearby(scene_text, m.start(), rule["suppress_context"]):
                    continue
                findings.append((rule["id"], rule["severity"], scene_title,
                                 line_of(global_text, scene_offset + m.start()),
                                 m.group(0), rule["description"]))


def check_ledger(ledger, findings):
    if not ledger:
        return
    prev_closing = {}
    for sc in ledger.get("scenes", []):
        opening = sc.get("opening", {})
        for dev_id, state in opening.items():
            if dev_id in prev_closing and prev_closing[dev_id] != state:
                findings.append(("DEV-05", "error", sc.get("scene", "?"), "-",
                                 f"{dev_id}: {prev_closing[dev_id]} -> {state}",
                                 "台账期初状态与上一场景期末状态不一致且无转移说明"))
        prev_closing = sc.get("closing", {})


def exemptions_in_scene(config, scene_title):
    ids = set()
    for ex in config.get("exemptions", []):
        if scene_title in ex.get("scenes", []) or any(s in scene_title for s in ex.get("scenes", [])):
            ids.update(ex.get("rules", []))
    return ids


def main():
    parser = argparse.ArgumentParser(description="截肢题材小说机械自查")
    parser.add_argument("--config", required=True)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--ledger", default=None)
    parser.add_argument("--report", default=None)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    anatomy = load_json(RULE_DIR / "anatomy.json")
    action_rules = load_json(RULE_DIR / "action_rules.json")
    device_rules = load_json(RULE_DIR / "device_rules.json")
    config = load_json(args.config)
    chapter_path = Path(args.chapter)
    if not chapter_path.exists():
        print(f"[运行错误] 章节文件不存在：{chapter_path}", file=sys.stderr)
        sys.exit(2)
    text = chapter_path.read_text(encoding="utf-8")
    ledger = load_json(args.ledger, allow_missing=True)
    validate_config(config, anatomy)

    findings = []
    check_exemption_markers(text, config, findings)
    check_ledger(ledger, findings)
    alias_map = build_alias_map(config)

    # 计算每个场景在全文中的字符偏移，用于全局行号
    scenes = split_scenes(text)
    for scene_title, _start_line, scene_text in scenes:
        scene_offset = text.find(scene_text)
        ex_scene = exemptions_in_scene(config, scene_title)
        for ch in config["characters"]:
            check_side_and_level(ch, scene_title, scene_text, text, scene_offset, anatomy, findings)
            applicable = expand_applicable_rules(ch, anatomy, action_rules)
            check_actions(ch, scene_title, scene_text, text, scene_offset, applicable,
                          alias_map, ex_scene, findings)
        check_devices(config, scene_title, scene_text, text, scene_offset, device_rules, findings)

    # 去重：同规则同行只保留首条，避免同一句被多个近义模式重复报告
    seen = set()
    dedup = []
    for item in findings:
        key = (item[0], item[2], item[3])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(item)
    errors = [f for f in dedup if f[1] == "error"]
    warnings = [f for f in dedup if f[1] == "warning"]

    if args.as_json:
        payload = [{"rule": f[0], "severity": f[1], "scene": f[2], "line": f[3],
                    "excerpt": f[4], "reason": f[5]} for f in dedup]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"机械自查报告 —— {chapter_path.name}")
        print(f"错误 {len(errors)} 项，警告 {len(warnings)} 项")
        for level, bucket in (("错误", errors), ("警告", warnings)):
            if not bucket:
                continue
            print(f"\n== {level} ==")
            for rule_id, sev, scene, line_no, excerpt, reason in bucket:
                print(f"[{rule_id}] {scene} 第{line_no}行 「{excerpt}」 —— {reason}")
        print("\n提醒：本脚本只做规则匹配，误报与漏报需人工研判，不替代冷读稽查。")

    if args.report:
        lines = [f"# 机械自查报告 —— {chapter_path.name}", "",
                 f"错误 {len(errors)} 项，警告 {len(warnings)} 项", ""]
        for rule_id, sev, scene, line_no, excerpt, reason in dedup:
            lines.append(f"- [{sev}][{rule_id}] {scene} 第{line_no}行 「{excerpt}」—— {reason}")
        Path(args.report).write_text("\n".join(lines), encoding="utf-8")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
