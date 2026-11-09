#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则 IR 编译期一致性检查（方向①）
用法: python scripts/compile_rules.py [--root <技能目录>] [--json]

职责：把 rules/rules.yaml 当作唯一事实源，检查「散文副本」是否与它一致。
     这是**离线**检查，不依赖任何 agent 运行时；可挂 pre-commit / CI。
     与 selfcheck.py 的分工：selfcheck 查锚点/悬空/孤儿/废止词/哈希；
     本脚本查**枚举冲突、编号重复、边界值差一档、计数漂移、scope 完整性**。

退出码：0 通过 / 1 有问题（--json 时输出结构化结果，便于上层适配层消费）
"""
import argparse
import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("FAIL 需要 PyYAML：pip install pyyaml")
    sys.exit(2)

BANNED_MARKERS = ("已废止", "❌", "不写", "禁止", "反例", "禁用字面量")


def norm(s):
    return re.sub(r"[\s★、（）()：:/·\-]+", "", s)


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    os.chdir(root)

    errors = []
    warnings = []
    checks = []

    def fail(code, msg):
        errors.append(f"[{code}] {msg}")

    def warn(code, msg):
        warnings.append(f"[{code}] {msg}")

    def ok(code, msg):
        checks.append(f"[{code}] {msg}")

    _last_ok = [0]

    def section(code, msg):
        """汇总行：仅当本段未新增 error 才报 OK，避免同一段同时出现 FAIL 与 OK。"""
        if len(errors) == _last_ok[0]:
            ok(code, msg)
        _last_ok[0] = len(errors)

    # ── 1. IR 存在且可解析 ─────────────────────────────────
    ir_path = os.path.join("rules", "rules.yaml")
    if not os.path.isfile(ir_path):
        fail("IR-01", f"缺 {ir_path}")
        return emit(a.as_json, errors, warnings, checks)
    try:
        ir = yaml.safe_load(read(ir_path)) or {}
    except Exception as e:
        fail("IR-02", f"rules.yaml 解析失败: {e}")
        return emit(a.as_json, errors, warnings, checks)
    ok("IR-01", "rules.yaml 解析通过")

    # ── 2. 必填块与 schema 版本 ────────────────────────────
    for key in ("schema_version", "enumerations", "invariants", "rules",
                "chapter_states", "consistency_checks"):
        if key not in ir:
            fail("IR-03", f"rules.yaml 缺必填块 {key}")
    section("IR-03", "必填块齐全")

    # ── 3. 规则 id 唯一 / layer / severity 合法 ─────────────
    ids = [r.get("id") for r in (ir.get("rules") or []) if isinstance(r, dict)]
    dup = sorted({x for x in ids if x and ids.count(x) > 1})
    if dup:
        fail("IR-04", f"规则 id 重复: {dup}")
    else:
        ok("IR-04", f"规则 id 唯一（{len(ids)} 条）")
    for r in (ir.get("rules") or []):
        if not isinstance(r, dict):
            continue
        if r.get("layer") not in ("hard", "standard", "soft"):
            fail("IR-05", f"{r.get('id')} layer 非法: {r.get('layer')}")
        if r.get("severity") not in ("hard", "soft"):
            fail("IR-05", f"{r.get('id')} severity 非法: {r.get('severity')}")
        if not r.get("assertion"):
            fail("IR-06", f"{r.get('id')} 缺 assertion")
        src = str(r.get("source", ""))
        # 通配路径只验证前缀目录存在；具体文件验证存在
        if src and not src.startswith("{"):
            p = src.split("#")[0]
            if "{" not in p and os.path.sep in p and not os.path.isfile(p):
                fail("IR-07", f"{r.get('id')} source 文件不存在: {p}")
    section("IR-05", "layer / severity / assertion / source 校验完成")

    # ── 4. 硬层必须存在且体量受控 ──────────────────────────
    hard_rules = [r for r in (ir.get("rules") or []) if isinstance(r, dict) and r.get("layer") == "hard"]
    if len(hard_rules) < 5:
        fail("IR-08", f"硬层规则仅 {len(hard_rules)} 条，疑似漏登记（应 ≥5）")
    else:
        ok("IR-08", f"硬层规则 {len(hard_rules)} 条")
    hard_file = os.path.join("rules", "hard-layer.md")
    if not os.path.isfile(hard_file):
        fail("IR-09", "缺 rules/hard-layer.md（硬约束常驻层）")
    else:
        size = os.path.getsize(hard_file)
        if size > 12 * 1024:
            warn("IR-09", f"hard-layer.md 达 {size} 字节，超过 12 KB 建议上限（常驻成本）")
        else:
            ok("IR-09", f"hard-layer.md 存在，{size} 字节")

    # ── 5. 枚举一致性：禁用字面量不得在正文裸用 ─────────────
    cc = ir.get("consistency_checks") or {}
    for item in (cc.get("enum_sources") or []):
        for lit in (item.get("forbidden_literals") or []):
            for pat in (item.get("files") or []):
                for f in glob.glob(pat):
                    if not os.path.isfile(f):
                        continue
                    for i, line in enumerate(read(f).split("\n"), 1):
                        if lit in line and not any(m in line for m in BANNED_MARKERS):
                            fail("ENUM-01", f"{f}:{i} 禁用字面量「{lit}」裸用（对应枚举 {item.get('enum')}）")
    section("ENUM-01", "禁用字面量扫描完成")

    # ── 5b. 题材枚举与账本权威源 / Schema 三者一致（防「另立取值」复发）──
    # 历史实证：初版 IR 另立「末世·丧尸·生存」，而账本权威源是「末世生存」，
    # 导致末世专属规则按账本值展开不到、且合法账本被 Schema 拒收；内部 scope 覆盖检查查不出。
    ir_genres = [str(x).strip() for x in ((ir.get("enumerations") or {}).get("题材大类") or [])]
    setup_p = os.path.join("core", "character-setup.md")
    auth_genres = []
    if os.path.isfile(setup_p):
        m = re.search(r"^\s*题材大类:\s*([^#\n]+)", read(setup_p), re.M)
        if m:
            auth_genres = [x.strip() for x in m.group(1).split("|") if x.strip()]
        else:
            fail("ENUM-02", f"{setup_p} 未找到「题材大类: …」权威定义行")
    else:
        fail("ENUM-02", f"缺账本字段权威源 {setup_p}")
    schema_p = os.path.join("templates", "ledger-schema.json")
    schema_genres = []
    if os.path.isfile(schema_p):
        try:
            schema_genres = (json.loads(read(schema_p))["properties"]["角色固定属性"]
                             ["properties"]["题材大类"]["enum"])
        except Exception as e:
            fail("ENUM-02", f"{schema_p} 题材大类 enum 读取失败: {e}")
    else:
        fail("ENUM-02", f"缺结构化契约 {schema_p}")
    if auth_genres and ir_genres != auth_genres:
        fail("ENUM-02", f"IR 题材枚举 {ir_genres} 与账本权威源 {auth_genres} 不一致（❌ 不得另立取值）")
    if schema_genres and ir_genres != schema_genres:
        fail("ENUM-02", f"IR 题材枚举 {ir_genres} 与 ledger-schema.json enum {schema_genres} 不一致")
    aliases = (ir.get("enumerations") or {}).get("题材别名") or {}
    for k, v in aliases.items():
        if v not in ir_genres:
            fail("ENUM-02", f"题材别名「{k}」→「{v}」不在合法枚举内")
    section("ENUM-02", "题材枚举与账本权威源 / Schema / 别名一致")

    # ── 6. 边界值一致性（规则文字 vs 代码，防差一档）────────
    for pair in (cc.get("boundary_pairs") or []):
        f = pair.get("file")
        expr = pair.get("code_expr", "")
        if not f or not os.path.isfile(f):
            fail("BND-01", f"边界检查目标文件不存在: {f}")
            continue
        body = read(f)
        if expr.startswith("cur_ch - last_rec"):
            m = re.search(r"cur_ch\s*-\s*last_rec\s*(>=|>|==|<=|<)\s*(\d+)", body)
            if not m:
                fail("BND-02", f"{f} 未找到资源账窗口比较表达式")
            else:
                op, num = m.group(1), int(m.group(2))
                if not (op == ">=" and num == 3):
                    fail("BND-03", f"{f} 边界为 `{op} {num}`，规则文字「{pair.get('rule_text')}」要求 `>= 3`")
                else:
                    ok("BND-03", f"{f} 窗口边界 `>= 3` 与规则文字一致")
        elif expr and expr not in body:
            warn("BND-04", f"{f} 未找到标记「{expr}」（人工确认是否为软口径）")
    section("BND-01", "边界值检查完成")

    # ── 7. 机检编号唯一（一个编号只能指向一个机检项）────────
    gate_ids = (ir.get("enumerations") or {}).get("交付闸机检编号") or []
    gbody = read(os.path.join("scripts", "gatecheck.py"))
    for gid in gate_ids:
        n = len(re.findall(r"^\s*" + re.escape(gid), gbody, re.M))
        if n != 1:
            warn("NUM-01", f"gatecheck.py 中 {gid} 作为 docstring 条目出现 {n} 次（期望 1）")
    for gid in ("[15]", "[16]", "[17]"):
        if gid not in gbody:
            fail("NUM-02", f"gatecheck.py 缺 {gid} 机检项")
    section("NUM-02", "机检编号 [15]/[16]/[17] 均在 gatecheck.py 中出现")

    # ── 8. 锚点存在性 ─────────────────────────────────────
    for item in (cc.get("anchor_sources") or []):
        f = item.get("file")
        if not f or not os.path.isfile(f):
            fail("ANC-01", f"锚点源不存在: {f}")
            continue
        body = read(f)
        heads = [norm(x) for x in re.findall(r"^#{1,6}\s*(.+)$", body, re.M)]
        keys = [norm(x) for x in re.findall(r"^\s*-?\s*([^\s#:]+)\s*:", body, re.M)]
        pool = heads + keys
        for anc in (item.get("anchors") or []):
            na = norm(anc)
            if not any(na in h for h in pool):
                fail("ANC-02", f"{f} 缺锚点「{anc}」")
    section("ANC-02", "锚点源检查完成")

    # ── 9. 计数不漂移 ─────────────────────────────────────
    for item in (cc.get("count_checks") or []):
        exp = str(item.get("expected", ""))
        for f in (item.get("files") or []):
            if not os.path.isfile(f):
                fail("CNT-01", f"计数检查目标不存在: {f}")
                continue
            if exp not in read(f):
                warn("CNT-02", f"{f} 未出现「{exp}」（{item.get('what')}）；人工确认是否为该文件的职责范围")
    section("CNT-01", "计数检查完成")

    # ── 10. 状态机自洽 ────────────────────────────────────
    cs = ir.get("chapter_states") or {}
    allowed = cs.get("allowed") or []
    trans = cs.get("transitions") or {}
    for src, dsts in trans.items():
        if src not in allowed:
            fail("FSM-01", f"转移起点「{src}」不在 allowed")
        for d in (dsts or []):
            if d not in allowed:
                fail("FSM-02", f"转移目标「{d}」不在 allowed（起点 {src}）")
    for jump in (cs.get("forbidden_jumps") or []):
        if "→" not in jump:
            fail("FSM-03", f"forbidden_jumps 格式错: {jump}")
    section("FSM-01", f"状态机自洽（{len(allowed)} 态 / {len(trans)} 组转移）")

    # ── 10b. IR 状态表 vs gatecheck [17] 内嵌表（防两个副本漂移）──
    gpath = os.path.join("scripts", "gatecheck.py")
    if os.path.isfile(gpath):
        gbody = read(gpath)
        import ast
        try:
            tree = ast.parse(gbody)
            gallowed, gtrans = None, None
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name) and t.id == "FSM_ALLOWED":
                            gallowed = ast.literal_eval(node.value)
                        if isinstance(t, ast.Name) and t.id == "FSM_TRANS":
                            gtrans = ast.literal_eval(node.value)
            if gallowed is None or gtrans is None:
                fail("FSM-04", "gatecheck.py 缺 FSM_ALLOWED / FSM_TRANS 内嵌表（[17] 未落地？）")
            else:
                if list(gallowed) != list(allowed):
                    fail("FSM-05", f"状态枚举不一致：rules.yaml={allowed} / gatecheck={gallowed}")
                elif {k: list(v) for k, v in gtrans.items()} != {k: list(v) for k, v in trans.items()}:
                    fail("FSM-06", "转移表不一致：rules.yaml 与 gatecheck [17] 须逐字同步")
                else:
                    ok("FSM-06", "IR 状态表与 gatecheck [17] 内嵌表一致")
        except Exception as e:
            fail("FSM-07", f"gatecheck.py 状态表解析失败: {e}")
    else:
        fail("FSM-04", "缺 scripts/gatecheck.py")

    # ── 11. 题材 scope 覆盖（新增题材包不得漏声明）──────────
    genres = (ir.get("enumerations") or {}).get("题材大类") or []
    for g in genres:
        hit = any(
            isinstance(r, dict) and (r.get("scope") or {}).get("题材大类")
            and g in (r.get("scope") or {}).get("题材大类")
            for r in (ir.get("rules") or [])
        )
        if not hit:
            fail("SCP-01", f"题材「{g}」在规则 IR 中无专属规则（scope 覆盖缺口）")
    section("SCP-01", f"题材 scope 覆盖检查完成（{len(genres)} 类）")

    return emit(a.as_json, errors, warnings, checks)


def emit(as_json, errors, warnings, checks):
    result = {"pass": not errors, "errors": errors, "warnings": warnings,
              "checks": checks, "error_count": len(errors), "warn_count": len(warnings)}
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for c in checks:
            print("  OK", c)
        for w in warnings:
            print("  WARN", w)
        for e in errors:
            print("  FAIL", e)
        print(f"编译检查: {'PASS' if not errors else 'FAIL'}"
              f"（{len(checks)} 项通过 / {len(warnings)} 警告 / {len(errors)} 错误）")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
