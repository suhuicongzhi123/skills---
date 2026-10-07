---
name: novel-amputee-writing
version: 4.1.0
author: 溯洄从之
description: 面向慕残者(devotee/wannabe)群体的截肢者题材小说写作技能。主角为截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断）。涵盖截肢者日常生活方方面面（拐杖、假肢、日常动作、身体细节、幻肢感、亲密关系、W视角等），含剧情节奏/弧线/场景结构通用写作技法，覆盖几乎所有小说题材（现实向为主、幻想向为辅）。触发条件：用户要求写截肢者/残障者题材小说、续写、大纲、人物设定、章节，或提到"慕残""截肢""残肢""拐杖""假肢""髋离断""幻肢""独臂""肩离断""单臂"等；或明确要求本技能。不触发：非截肢题材普通小说、纯医学/康复专业内容、猎奇式苦难叙事。
---

# novel-amputee-writing Skill

面向慕残者群体的截肢者题材小说写作技能。全平台通用，不针对某平台特殊处理。

> **强制约束**：角色设定确认后，Agent 不再就流程分支向用户询问下一步操作或决策确认，所有流程分支由 Agent 依据本文档规则决定。创作前期需向用户收集角色设定（见 `core/character-setup.md`）。

---

## 一、受众与内容定位

- **受众**：慕残者（devotee）+ W视角（wannabe），详见 `core/audience.md`
- **主角**：截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断），默认女性
- **内容偏好**（重点→次重点）：受限与不便、幻肢感（非幻肢痛）、裸露场景（洗澡/更衣/睡觉/亲密）残肢与剩余部分细节 ＞ 剩余部分颤动、代入感 ＞ 日常样态（次重点，作背景）
- **回避**：苦难叙事（幻肢痛、健腿劳损、伤口处理）、医学临床化、猎奇渲染、励志二元叙事
- **W视角**：可含求截肢行为，但主剧情以截肢后生活为主
- **题材**：现实向（主）+ 幻想向（辅，符合截肢设定事实，按需加入高科技/魔法元素）

## 二、文件结构与格式

| 目录 | 格式 | 职责 |
|------|------|------|
| `core/` | md | 类型无关核心规则（工作流/风格/受众/角色设定/节奏/弧线/场景） |
| `types/` | md | 截肢生理事实，按类型隔离（易扩展） |
| `topics/` | md + yaml | 主题域专项（跨类型） |
| `genre/` | md | 题材适配 |
| `templates/` | md | 产出模板 |

**格式选择原理**：
- **md**：规则/叙述/指导，注入即指令，支持小节锚点按需引用
- **yaml**：纯结构化数据（属性-值/枚举），紧凑可解析易扩展
- **不用 json**：冗长无注释，人工维护不如 yaml

## 三、拆分原理

1. **类型无关/相关分离**：`core/`+`topics/` 跨类型复用，`types/` 放类型差异。新增截肢类型只在 `types/` 加一文件，不动其余。
2. **主题域解耦类型差异**：`topics/` 下各主题文件写通用规则，类型特有差异在 `types/{type}.md` 对应小节。
3. **按需注入**：本总纲放注入索引，Agent 按需读取专项，省上下文与创作成本。

## 四、创作工作流

详见 `core/workflow.md`。概要：构思→大纲→人物设定→章节写作→润色。每阶段按需注入对应专项。

## 五、按需注入索引

Agent 按以下规则读取专项（不主动全量加载）：

```yaml
injection:
  触发启动:
    - core/workflow.md
    - core/style.md
    - core/audience.md
  角色设定阶段:
    - core/character-setup.md
    - types/{type}.md
  大纲/弧线规划阶段:
    - core/structure.md
  上肢截肢分支(肩离断等):
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md, topics/daily-actions.md]
    改注入:
      单手日常: topics/one-handed-daily.md
      日常动作差异: types/{type}.md#日常动作差异
      假肢: types/{type}.md#假肢使用差异
      身体细节: types/{type}.md#身体细节
      幻肢感: types/{type}.md#幻肢感
      服装: types/{type}.md#服装
  写到拐杖场景(下肢):
    - topics/crutch-spec.yaml
    - topics/crutch-usage.md
    - types/{type}.md#拐杖使用差异
  写到假肢:
    - topics/prosthesis.md
    - types/{type}.md#假肢使用差异
  写到日常动作(下肢):
    - topics/daily-actions.md
    - types/{type}.md#日常动作差异
  写到双手与移动并存场景(下肢):
    - topics/hands-occupied.md
    - types/{type}.md#拐杖使用差异
  写到场景构建:
    - core/scene.md
  写到服装/衣装场景:
    - topics/clothing.md
    - types/{type}.md#服装
  写到身体细节或幻肢感:
    - topics/body-details.md
    - types/{type}.md#身体细节
  写到亲密关系:
    - topics/intimacy.md
  写到W视角:
    - topics/wannabe.md
  写到器具风险/丢失/损坏场景:
    - topics/equipment-risk.md
  写到节奏/张力场景:
    - core/pacing.md
  题材适配:
    现实向: genre/realistic.md
    幻想向: genre/fantasy.md
    末世/丧尸/生存: genre/postapocalyptic.md
  产出模板:
    大纲: templates/outline.md
    人物卡: templates/character-card.md
    章节: templates/chapter.md
    状态账本: templates/state-ledger.yaml
  章末必过审查:
    生理事实兜底: core/physio-audit.md
    类型不可能动作: types/{type}.md#不可能动作
    setup/payoff跟踪: templates/state-ledger.yaml#open_setups
  推荐流程:
    状态核查流水账: core/workflow.md#6-状态核查流水账
    冷读稽查(可选): core/cold-review.md
```

## 六、截肢类型清单

```yaml
types:
  hip-disarticulation: 髋离断（下肢，主）
  transfemoral: 膝上截肢（下肢，辅）
  transtibial: 膝下截肢（下肢，辅）
  shoulder-disarticulation: 肩离断（上肢，辅）
  # 新增类型：复制 types/_template.md，在 types/ 加文件并在此登记
```

## 七、专项完善状态

- `topics/crutch-spec.yaml` + `topics/crutch-usage.md`：✅ 已完善
- `types/hip-disarticulation.md`：✅ 已完善
- `topics/hands-occupied.md`、`topics/clothing.md`、`topics/equipment-risk.md`：✅ 已完善
- `genre/postapocalyptic.md`：✅ 已新增
- `core/cold-review.md`、`templates/state-ledger.yaml`、`core/physio-audit.md`：✅ 已新增
- `types/shoulder-disarticulation.md`、`topics/one-handed-daily.md`：✅ 已新增（上肢截肢支持）
- `core/pacing.md`、`core/structure.md`、`core/scene.md`：✅ 已新增（通用写作技法，借鉴自 creative-writing-skills）
- `core/*`、`topics/*`、`types/*`、`genre/*`、`templates/*`：✅ 已完善初版

> 所有专项已完善初版内容，后续按实际创作反馈迭代。
> **推荐流程**：状态核查流水账（章末自查，零成本）+ 冷读子代理稽查（可选，测试后定是否启用）。