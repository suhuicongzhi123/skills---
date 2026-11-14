# 维护态操作（外移自 SKILL.md 第〇/一/五节）

> 版本检查、安装注册、文件结构属安装／维护期内容，创作时不读。SKILL.md 对应章节仅保留锚点指针。

## 〇、版本与更新检查（对话首次调用时执行一次）

- 每段对话首次调用检查一次，非阻塞、不提问、提示完继续
- 有 shell：`git ls-remote --tags https://github.com/suhuicongzhi123/skills---.git`，
  取最大版本须按版本语义排序（`sort -V | tail -1`），禁取字典序末条
- 无 shell：读 GitHub tags API，按 x.y.z 三段数值比较
- 本地改过技能文件时，`git pull` 前提示用户自行处理冲突

## 一、安装后注册（非 Claude Code 平台必读）

> hook 语义单一事实源＝`host-hooks.yaml`；平台适配与降级声明权威全文在 `PLATFORM-CN.md`。

- 有 shell：`python scripts/install-host-hooks.py --platform <平台> --project-dir <项目目录> --yes`；
  未核实平台不猜测写入（exit 3 加人工注册指引）
- 任何降级必须显式写进账本 `工作流执行日志`；硬层最低补偿＝每章开写前整段重读 `rules/hard-layer.md`

## 五、文件结构与格式

> **改完必跑**：`python scripts/verify.py`（编译检查＋锚点/悬空/必填节/废止表述/孤儿/哈希）。
> 宿主 `quick_validate.py` 另验 frontmatter。两个校验器都 PASS 才算改完。

| 目录 | 职责 |
|---|---|
| `core/` | 核心规则：`scene-drive.md` 场景驱动器（有没有发生事）｜`voice.md` 人物声音｜`scene-engine.md` 场景引擎｜`intensity.md` 强度层｜`emotion.md` 情感层｜`emotion-signal.md` 情绪出口｜`psychology.md` 心理模式库｜`style.md` 词句层｜`prose-craft.md` 成文层｜`audience.md` 受众｜`character-setup.md` 设定｜`chapter-planning.md` 章级｜`structure.md` 弧线｜`workflow.md` 流程｜`cold-review.md` 冷读｜`opening.md`／`pacing.md`／`scene.md`／`short-form.md`／`physio-audit.md`／`worldbuilding.md` |
| `types/` | 截肢生理事实，按类型隔离 |
| `topics/` | 主题域专项（跨类型） |
| `genre/` | 题材适配 |
| `templates/` | 产出模板与结构化契约（含 `voice-card.md` 声音卡） |
| `rules/` | 规则 IR `rules/rules.yaml` ＋硬约束常驻层 `rules/hard-layer.md` |
| `eval/` | 离线回归评测集（不进创作上下文） |
| `scripts/` | 机检／编译／规则展开／状态机／校验回路；`verify.py` 为统一自检入口 |
| 根 | `host-hooks.yaml`、`PLATFORM-CN.md`、`MAINTENANCE.md`（维护者规范，创作时不读）、`dev/CHANGELOG.md` |

**索引格式**：带 `#锚点` 的引用一律单独成行，不写进 YAML 内联数组（逗号会被锚点解析器吃掉）。

