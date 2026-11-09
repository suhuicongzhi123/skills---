#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一校验入口（v7.0.0）

用法：python scripts/verify.py [--update-baseline] [--verbose]

一次跑完两条库内校验，汇总 PASS/FAIL：
  1. scripts/compile_rules.py —— 枚举/编号/边界/锚点/计数/状态表
  2. scripts/selfcheck.py     —— 锚点落空/悬空引用/必填节/废止表述/孤儿文件/哈希基线

取代「改完要记着跑两条命令」的口头约定（漏跑是历史最贵的制度失败）。
⚠ 本入口只校验**技能库自身**；章节交付仍须单独跑
   `python scripts/gatecheck.py <小说项目目录> --chapter N`。
⚠ 子进程管道两侧统一 UTF-8（v6.0.0 E-017 教训：Windows GBK locale 会崩）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STEPS = [
    ("编译检查 compile_rules.py", "compile_rules.py", False),
    ("库内自检 selfcheck.py", "selfcheck.py", True),
]

EXTRA_OK = {"--update-baseline", "--verbose"}


def main():
    extra = [a for a in sys.argv[1:] if a in EXTRA_OK]
    unknown = [a for a in sys.argv[1:] if a not in EXTRA_OK]
    if unknown:
        print("未知参数:", " ".join(unknown))
        print("用法: python scripts/verify.py [--update-baseline] [--verbose]")
        return 2

    all_ok = True
    for label, script, pass_extra in STEPS:
        # -B ＋ PYTHONDONTWRITEBYTECODE：校验过程不产生 __pycache__ 垃圾
        cmd = [sys.executable, "-B", os.path.join(HERE, script)] + (extra if pass_extra else [])
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env={**os.environ, "PYTHONIOENCODING": "utf-8",
                                "PYTHONDONTWRITEBYTECODE": "1"})
        ok = p.returncode == 0
        all_ok = all_ok and ok
        print(f"--- {label}: {'PASS' if ok else 'FAIL'} ---")
        lines = (p.stdout or "").strip().splitlines()
        # FAIL 时打印全量输出：只截尾 6 行会掩盖「[1] 锚点落空 N」等首行明细
        for line in (lines if not ok else lines[-6:]):
            print("   ", line)
        if (p.stderr or "").strip():
            print("    stderr:", (p.stderr or "").strip()[:300])

    print("\n=== 统一校验:", "PASS" if all_ok else "FAIL", "===")
    print("提示：宿主 quick_validate.py 另验 frontmatter；章节交付闸仍须单独跑 gatecheck.py <项目目录>。")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
