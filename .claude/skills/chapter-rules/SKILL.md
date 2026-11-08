---
name: chapter-rules
description: 展开本章规则包（按账本坐标：题材/类型/尺度档/模式/章型/章号），每章开写前运行。产出单份规则包文本替代「AI 自己判断读哪些文件」，含硬约束常驻层。
---

# 本章规则包展开（架构层 · 方向②）

> skill 激活时下方硬层已随动态注入进入上下文（宿主预执行，AI 无法跳过）：

!`cat "${CLAUDE_PROJECT_DIR}/novel-amputee-writing/rules/hard-layer.md"`

## 执行步骤

1. 从小说项目账本（`state-ledger.yaml` 的「角色固定属性」与「章节状态」块）读取坐标：题材大类、截肢类型、亲密尺度档、工作流模式、章号。
2. 按坐标展开规则包（`--out` 写入**小说项目目录**，❌ 不得指向技能库内覆盖模板）：

```bash
python "${CLAUDE_PROJECT_DIR}/novel-amputee-writing/scripts/query_rules.py" \
  --genre <题材大类> --type <截肢类型> --tier <尺度档> --mode <模式> \
  --chapter-kind <章型> --conflict <冲突强度档> --chapter <N> \
  --format text --out <project>/chapter-rules-N.md
```

3. 展开结果即本章唯一注入的规则视图；据此填 `${CLAUDE_PROJECT_DIR}/novel-amputee-writing/templates/chapter-contract.md`。
4. 规则包未载的事实一律回读源文件，❌ 不得凭摘要写作。

## 边界

- 按 `scope` 展开，当前以题材大类为主；类型/尺度档/模式/章型/章号仅作坐标标注。
- 硬层永远整段附带、不参与检索；本 skill 已随激活注入，会话压缩后重调本 skill 补注入。