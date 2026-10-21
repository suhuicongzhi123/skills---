---
name: novel-amputee-writing
version: 4.8.4
author: 溯洄从之
description: 面向慕残者(devotee/wannabe)群体的截肢者题材小说写作技能。主角为截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断，含肘离断/腕离断）。覆盖拐杖、假肢、日常动作、高频生活场景、身体细节、幻肢感、亲密关系、W视角等主要方面，含剧情节奏/弧线/场景结构/长篇连续性通用写作技法，支持现实向、幻想向、末世、古装四类题材。触发条件：用户要求写截肢者/残障者题材小说、续写、大纲、人物设定、章节，或提到"慕残""截肢""残肢""拐杖""假肢""髋离断""幻肢""独臂""肩离断""肘离断""腕离断""单臂"等；或明确要求本技能。不触发：非截肢题材普通小说、纯医学/康复专业内容、猎奇式苦难叙事。
---

# novel-amputee-writing Skill

面向慕残者群体的截肢者题材小说写作技能。全平台通用，不针对某平台特殊处理。

> **强制约束**：角色设定确认后，Agent 不再就流程分支向用户询问下一步操作或决策确认，所有流程分支由 Agent 依据本文档规则决定。
> **两项例外**：① **章级推进节奏的确认**（写完一章后是否进入下一章，见 `core/workflow.md`）；
> ② **创作前是否开启冷读稽查**（见 `core/cold-review.md`）。
> 创作前期需向用户收集角色设定（见 `core/character-setup.md`）。

---

## 一、受众与内容定位

- **受众**：慕残者（devotee）+ W视角（wannabe），详见 `core/audience.md`
- **主角**：截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断），默认女性
- **内容偏好**（重点→次重点）：受限与不便、幻肢感（非幻肢痛）、裸露场景（洗澡/更衣/睡觉/亲密）残肢与剩余部分细节 ＞ 剩余部分颤动、代入感 ＞ 日常样态（次重点，作背景）
- **回避**：苦难叙事（幻肢痛、健腿劳损、伤口处理）、医学临床化、猎奇渲染、励志二元叙事
- **W视角**：可含求截肢行为，但主剧情以截肢后生活为主
- **题材**：现实向（主）+ 幻想向 / 末世生存 / 古装向（辅，符合截肢设定事实，按需加入高科技/魔法元素）

## 二、文件结构与格式

> **改完必跑自检**：`python scripts/selfcheck.py` —— 查注入锚点落空 / 类型必填节 /
> 已废止表述复发三项。跨版本残留是本包历史上所有冲突的来源，改口径后务必跑。

| 目录 | 格式 | 职责 |
|------|------|------|
| `core/` | md | 类型无关核心规则（工作流/风格/受众/角色设定/节奏/弧线/场景/开篇） |
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

详见 `core/workflow.md`。概要：构思→大纲→人物设定→章节写作→润色。每阶段按需注入对应专项。**逐章创作，禁止一次生成整篇**。

## 五、按需注入索引

Agent 按以下规则读取专项（不主动全量加载）：

```yaml
injection:
  命名说明:                       # 账本两种写法同指一物，避免"引用了不存在的文件"误判
    源模板: templates/state-ledger.yaml
    运行时: 开书时复制到小说项目工作区，称 state-ledger.yaml
  触发启动:
    - core/workflow.md
    - core/style.md
    - core/audience.md
  角色设定阶段:
    - core/character-setup.md
    - topics/timeline.md
    - types/{type}.md
  类型未登记兜底:                 # 用户要求的类型不在第六节清单内时走此分支
    条件: 该类型未在 types/ 登记
    步骤:
      - 向用户确认截断平面（保留哪段骨骼、有无残端、残端可否承重）
      - 复制 types/_template.md 建立新文件并登记到第六节
      - 未确认前禁止静默套用最近邻类型的事实条目
      - 尤其禁止移植：有无残端、可否主动带动、可否用肌电假肢
  侧别为双:                       # 叠加层，与 types/{type}.md 同时注入
    - types/bilateral.md          # 冲突处以本文件为准（无健腿）
  上肢低位分支:                    # 肘离断 / 腕离断
    - types/elbow-wrist.md
    - topics/one-handed-daily.md
  ★上下肢复合注入规则:             # 截肢部位=上下肢复合 时必读
    - SKILL.md#★上下肢复合（并行注入 · 按域分工）
  大纲/弧线规划阶段:
    - core/structure.md
    - core/worldbuilding.md
    - core/chapter-planning.md
    - core/opening.md
  开篇阶段:
    - core/opening.md
    - genre/{题材}.md#推荐开篇类型
  上肢截肢分支(肩离断等):
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md, topics/daily-actions.md]
    例外: 上下肢复合截肢时（截肢部位=上下肢复合），本分支的"不注入"全部失效，
      按下方「★上下肢复合注入规则」并行注入
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
  写到高频私密/公共场景:          # 按场景查对应小节，不全文加载
    - topics/daily-scenes.md      # 一 如厕 / 二 床上起卧与床边转移 / 三 公共交通 /
      # 四 长距离行走 / 五 负重与楼梯 / 六 厨房与家务 / 七 照护与更衣 /
      # 八 其他高频（电梯困住·雨雪·运动·门诊·职场·校园）
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
  章级规划受限beat:               # 每章开写前选 1 个
    - topics/limitation-scenes.md
    - types/{type}.md#受限清单
  写到受限场景(冲突/追赶/双手占用/对立):
    - topics/limitation-scenes.md  # 能力丧失 / 器具剥夺 / 双手占用 / 速度劣势 / 对立挑衅
  写到节奏/张力场景:
    - core/pacing.md
  题材适配:
    现实向: genre/realistic.md
    幻想向: genre/fantasy.md
    末世/丧尸/生存: genre/postapocalyptic.md
    古装向: genre/historical.md           # 含古代器具表（crutch-spec.yaml 仅覆盖现代，本题材不适用）
  产出模板:
    大纲: templates/outline.md
    人物卡: templates/character-card.md
    章节: templates/chapter.md
    状态账本: templates/state-ledger.yaml
  章末必过审查:                        # 本节 8 项为「必过子集」；完整勾选清单见 templates/chapter.md
    生理事实兜底: core/physio-audit.md
    类型不可能动作: types/{type}.md#不可能动作
    幻肢频率对档位: topics/timeline.md
    招牌元素未连续重复: core/audience.md#招牌元素密度与疲劳控制
    setup/payoff跟踪: templates/state-ledger.yaml#open_setups
    本章beat与钩子: core/chapter-planning.md#一、章六要素
    受限beat≥1且不重复: core/audience.md#★受限清单（章级必备，与上方招牌清单并行）
    幻肢档位真实度: topics/timeline.md#幻肢档位总表（频率 × 触发 × 意图 × 残肢 × 后果）
    章级质量落点:                        # 上八项的执行点，缺一即不可查
      章六要素勾选: templates/chapter.md#章末核查清单
      账本登记: templates/state-ledger.yaml#本章登记
      钩子不重复: templates/state-ledger.yaml#章末钩子类型
      密度可查: templates/state-ledger.yaml#distribution.元素上次出现章
  推荐流程:
    状态核查流水账: core/workflow.md#6-状态核查流水账
    冷读稽查(创作前询问用户): core/cold-review.md
```

## 五-补、★上下肢复合（并行注入 · 按域分工）

> 触发：`截肢部位: 上下肢复合`（上下肢**均有**截肢，如髋离断 + 肩离断）。

`{type}` **取两份 `types/{type}.md` 并行注入**（上肢一份、下肢一份），
❌ **不是二选一**——冲突按**域**裁决：

| 域 | 归属 |
|---|---|
| 移动 / 体位与动态 / 步态 / 辅具（拐杖·轮椅）/ 受限清单 | **下肢为准** |
| 手部操作 / 袖管 / 上肢假肢 / 上身体态 / 单手日常 | **上肢为准** |
| 招牌元素（身体细节 / 幻肢感 / 空 / 被看见 / 亲密中的身体） | **两侧分别取象，都写** |
| 不可能动作 | **两份并集**（任一侧的不可能动作都成立） |
| 幻肢感档位 | **同一角色统一档位**，按 `topics/timeline.md`——**不按侧别分档** |

**示例**：髋离断 + 肩离断
- 移动按髋离断：单腿跳 / 双拐 / 单腿蹲（正式豁免）；受限走髋离断清单
- 操作按肩离断：单手，双手协同任务做不到；上肢假肢按肩离断
- 招牌元素④「空」**两侧都写**：空椅面（下）+ 空袖管（上）
- 不可能动作取并集：患侧蹲/跪、双腿蹲（下）+ 双臂环抱、双手提物（上）都成立

> ❌ 易错：把复合当成"随便挑一份"，或让上肢去决定移动样态。
> 移动是章级主干，**永远看下肢体**。

## 六、截肢类型清单

```yaml
types:
  hip-disarticulation: 髋离断（下肢，主）
  transfemoral: 膝上截肢（下肢，辅）
  transtibial: 膝下截肢（下肢，辅）
  shoulder-disarticulation: 肩离断（上肢，辅）
  elbow-wrist: 肘离断/腕离断（上肢低位，见 types/elbow-wrist.md）
  bilateral: 双侧截肢（叠加层，见 types/bilateral.md；与上述下肢类型叠加使用）
  # 新增类型：复制 types/_template.md，在 types/ 加文件并在此登记
  # 未登记类型的兜底规则见第五节注入索引「类型未登记兜底」
```

> **必填节闸门（两级）**
> - **独立类型**（`hip-disarticulation` / `transfemoral` / `transtibial` / `shoulder-disarticulation` /
>   `elbow-wrist`）：`types/_template.md` 的 11 节**全部必填，缺失不得登记为新类型**。
>   其中**运动能力**与**体位与动态**为实质要求（须写清可/不可）；
>   其余 9 节可写短节（"见第 X 节 / 本类型不适用"），但**小节名必须在**，否则注入锚点落空。
> - **叠加层**（`bilateral`——须与单侧类型并行注入，**不单独成立**）：按最小集——
>   适用范围 / 失效条目 / 移动样态 / 身体细节 / 幻肢感 / 受限清单。
>   ❌ 不要求 11 节，不因其缺节而判定违规。

## 七、专项完善状态

> 历史变更记录已迁出，见 **`CHANGELOG.md`**（本文件不再承载变更史，以控制常驻上下文体积）。
> 当前版本见 frontmatter `version`。

## 八、通用说明

- 所有专项已完善初版内容，后续按实际创作反馈迭代。
- **推荐流程**：状态核查流水账（章末自查，零成本）+ 冷读子代理稽查（创作前询问用户是否开启）。
- **版本变更一律记入 `CHANGELOG.md`**，本总纲不再承载变更史（v4.8.0 迁出）。