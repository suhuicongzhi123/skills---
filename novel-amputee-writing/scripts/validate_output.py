#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成后校验 + 修复回路（方向③）
用法:
  python scripts/validate_output.py --project <小说项目目录> --chapter N [--repair-hint]
  python scripts/validate_output.py --project <...> --chapter N --json

职责：把「编译检查 / 账本 schema / gatecheck / 状态机」的结果汇成**一份结构化违规清单
     ＋ 回炉指令**，供宿主自动打回重写，而不是只把错误打印给人看。
     这是「生成 → 校验 → 修复」回路的校验与指令端；修复动作由上层 agent / hook 执行。

⚠ 边界（务必读）：本脚本只判**可形式化**的项（字段、枚举、编号、状态、窗口、格式）。
   它判不了「髋离断能不能主动甩残肢」这类语义事实，也判不了文笔。
   语义事实仍须靠 rules/hard-layer.md 常驻 + 冷读维度（pro/max）。
"""
import argparse
import json
import os
import subprocess
import sys

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import jsonschema  # 可选；缺失时降级为「跳过 schema 校验」并显式声明
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

try:
    import yaml
except ImportError:
    print("FAIL 需要 PyYAML：pip install pyyaml")
    sys.exit(2)


def run(cmd, cwd):
    try:
        # 子进程统一 UTF-8：子脚本输出含中文与「」等字符，
        # Windows 默认按 GBK 解码管道会 UnicodeDecodeError（读线程崩溃、结果全丢）；
        # 同时设 PYTHONIOENCODING 强制子进程用 UTF-8 写管道，两侧对齐。
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120, env=env)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return 2, f"无法执行 {cmd}: {e}"


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--project", required=True, help="小说项目目录（含 state-ledger.yaml）")
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--repair-hint", action="store_true", help="输出回炉指令")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    root = os.path.abspath(a.root)
    project = os.path.abspath(a.project)
    ledger = os.path.join(project, "state-ledger.yaml")
    findings = []
    skipped = []

    def add(kind, ok_, detail, repair):
        findings.append({"kind": kind, "pass": bool(ok_), "detail": detail, "repair": repair})

    # 1) 规则 IR 编译检查（离线；不依赖 agent）
    rc, out = run([sys.executable, os.path.join(root, "scripts", "compile_rules.py"),
                   "--root", root, "--json"], root)
    try:
        j = json.loads(out)
        add("规则编译", j.get("pass", False),
            f"errors={j.get('error_count')} warnings={j.get('warn_count')}",
            "按 compile_rules.py 的 FAIL 清单改齐口径，再重跑")
    except Exception:
        add("规则编译", False, out.strip()[:300], "检查 compile_rules.py 是否可运行")

    # 2) 账本存在 + schema 校验（可选依赖）
    if not os.path.isfile(ledger):
        add("账本存在", False, f"缺 {ledger}", "先初始化账本")
        data = {}
    else:
        add("账本存在", True, ledger, "")
        try:
            data = yaml.safe_load(read(ledger)) or {}
            add("账本可解析", True, "yaml.safe_load 通过", "")
        except Exception as e:
            data = {}
            add("账本可解析", False, str(e), "修 YAML 语法后重跑")
        schema_path = os.path.join(root, "templates", "ledger-schema.json")
        if HAS_JSONSCHEMA:
            try:
                schema = json.loads(read(schema_path))
                jsonschema.validate(data, schema)
                add("账本 schema", True, "核心字段契约通过", "")
            except jsonschema.ValidationError as e:
                add("账本 schema", False, f"{list(e.path)}: {e.message}",
                    "按 templates/ledger-schema.json 修对应字段")
            except Exception as e:
                add("账本 schema", False, str(e), "检查 schema 文件")
        else:
            skipped.append("账本 schema（缺 jsonschema 包，已显式跳过：pip install jsonschema）")

    # 3) 交付闸 gatecheck
    if os.path.isfile(ledger):
        cmd = [sys.executable, os.path.join(root, "scripts", "gatecheck.py"), project]
        if a.chapter is not None:
            cmd += ["--chapter", str(a.chapter)]
        rc, out = run(cmd, project)
        add("交付闸", rc == 0, out.strip()[:400],
            "按 gatecheck FAIL 清单逐项修复后重跑；FAIL 运行不生成交付凭证")
    else:
        add("交付闸", False, "账本缺失，未执行", "先补账本")

    # 4) 章节状态机
    if os.path.isfile(ledger):
        rc, out = run([sys.executable, os.path.join(root, "scripts", "state_machine.py"),
                       "--root", root, "--ledger", ledger, "--check"], project)
        add("章节状态机", rc == 0, out.strip()[:300],
            "按 state_machine.py 的合法转移推进；❌ 不得跳步")
    else:
        add("章节状态机", False, "账本缺失，未执行", "先补账本")

    # 5) 显式声明的未覆盖项（防「校验全绿＝内容无误」的误解）
    skipped += [
        "生理事实语义（髋离断/膝上/膝下/上肢差异）——须靠 rules/hard-layer.md 常驻 + 冷读维度",
        "文笔与声口、去 AI 化、心动句非同源——须靠 core/style.md 与 core/audience.md",
        "内容合规审核（国内平台前置/后置）——须实测目标平台，见 PLATFORM-CN.md 第 0 步",
    ]

    failed = [f for f in findings if not f["pass"]]
    result = {
        "pass": not failed,
        "chapter": a.chapter,
        "findings": findings,
        "skipped": skipped,
        "not_covered_guarantee": "本回路只保证可形式化项；语义事实与文笔不在保证范围",
    }
    if a.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(("  OK  " if f["pass"] else "  FAIL") + f" [{f['kind']}] {f['detail'][:160]}")
        for s in skipped:
            print("  SKIP", s)
        if failed and a.repair_hint:
            print("\n=== 回炉指令（不得交付，修完重跑）===")
            for f in failed:
                print(f"  - [{f['kind']}] {f['repair']}")
        print(f"\n校验回路: {'PASS' if not failed else 'FAIL'}（{len(failed)} 项不合格）")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
