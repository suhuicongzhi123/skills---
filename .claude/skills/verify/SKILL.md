---
name: verify
description: novel-amputee-writing 交付闸机检。写章交付前与每次 git commit 前运行：selfcheck、compile_rules、state_machine、gatecheck 四项，任一 FAIL 即不得交付或提交。用户要求验证章节、检查交付、commit 前检查时使用。
---

# 交付闸机检（架构层 · 方向③）

> 本 skill 是技能库 gatecheck 体系的宿主入口：Claude Code 会话中每次 commit 前自动被指示运行（verify 命名约定）。
> 强制力来自宿主指示 + 本 skill 的 FAIL 即阻断约定，不依赖 AI 自觉。

## 运行步骤（按序，全部跑完再判定）

技能库位于 `${CLAUDE_PROJECT_DIR}/novel-amputee-writing/`（下称 `<skill>`）；小说项目目录从对话上下文确认（含 `state-ledger.yaml` 的目录，下称 `<project>`）。

1. 库完整性（任何场景必跑）：

```bash
python <skill>/scripts/selfcheck.py
python <skill>/scripts/compile_rules.py
```

2. 章节交付闸（写作/交付场景，`<project>` 存在时）：

```bash
python <skill>/scripts/state_machine.py --ledger <project>/state-ledger.yaml --check
python <skill>/scripts/gatecheck.py <project> --chapter N
```

3. 汇总校验回路（可选，输出结构化违规清单与回炉指令）：

```bash
python <skill>/scripts/validate_output.py --project <project> --chapter N --repair-hint
```

## 判定与处置

- 任一命令退出码非 0（FAIL）：**不得交付、不得 commit**。
- 按 FAIL 清单逐项修复后重跑，直至全 PASS。
- ❌ 禁止跳过失败项继续提交；❌ 禁止只跑部分命令就宣称通过。
- 机检边界如实声明：本闸只覆盖可形式化项；生理事实语义、文笔、心动句非同源仍须冷读 + 人工校对（机检全绿 ≠ 内容无误）。