---
name: novel-amputee-writing
version: 4.6.2
author: 溯洄从之
description: 面向慕残者(devotee/wannabe)群体的截肢者题材小说写作技能。主角为截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断，含肘离断/腕离断）。覆盖拐杖、假肢、日常动作、高频生活场景、身体细节、幻肢感、亲密关系、W视角等主要方面，含剧情节奏/弧线/场景结构/长篇连续性通用写作技法，支持现实向、幻想向、末世、古装四类题材。触发条件：用户要求写截肢者/残障者题材小说、续写、大纲、人物设定、章节，或提到"慕残""截肢""残肢""拐杖""假肢""髋离断""幻肢""独臂""肩离断""肘离断""腕离断""单臂"等；或明确要求本技能。不触发：非截肢题材普通小说、纯医学/康复专业内容、猎奇式苦难叙事。
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
      改按下方下肢分支注入拐杖与日常动作专项
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
  写到器具风险/丢失/损坏场景:
    - topics/equipment-risk.md
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
  章末必过审查:
    生理事实兜底: core/physio-audit.md
    类型不可能动作: types/{type}.md#不可能动作
    幻肢频率对档位: topics/timeline.md
    招牌元素未连续重复: core/audience.md#招牌元素密度与疲劳控制
    setup/payoff跟踪: templates/state-ledger.yaml#open_setups
    本章beat与钩子: core/chapter-planning.md#一、章五要素
    章级质量落点:                        # 上四项的执行点，缺一即不可查
      章五要素勾选: templates/chapter.md#章末核查清单
      账本登记: templates/state-ledger.yaml#本章登记
      钩子不重复: templates/state-ledger.yaml#章末钩子类型
      密度可查: templates/state-ledger.yaml#distribution.元素上次出现章
  推荐流程:
    状态核查流水账: core/workflow.md#6-状态核查流水账
    冷读稽查(创作前询问用户): core/cold-review.md
```

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

> 各类型的**运动能力**与**体位与动态**小节为必填（见 `types/_template.md`），
> 缺失该两节时不得登记为新类型。

## 七、专项完善状态

- `topics/timeline.md`：✅ 已新增（截肢时长分档：先天/近期/多年 + 幻肢感频率锚点）
- `core/audience.md`：✅ 已补（受众身份定位、devotee/wannabe 入戏约束、★招牌元素密度与疲劳控制）
- `types/*#服装` 与 `topics/clothing.md`：✅ 已修正（患侧**裁剪位置**：髋离断=大腿根部/裆线，
  膝上=残端下缘，膝下=残端下缘，肩离断=肩峰下缘；髋离断无"空裤管"，常服在裆线处结束）
- `topics/crutch-spec.yaml` + `topics/crutch-usage.md`：✅ 已完善
- `types/hip-disarticulation.md`：✅ 已完善
- `topics/hands-occupied.md`、`topics/clothing.md`、`topics/equipment-risk.md`：✅ 已完善
- `genre/postapocalyptic.md`：✅ 已新增
- `core/cold-review.md`、`templates/state-ledger.yaml`、`core/physio-audit.md`：✅ 已新增
- `types/shoulder-disarticulation.md`、`topics/one-handed-daily.md`：✅ 已新增（上肢截肢支持）
- `core/pacing.md`、`core/structure.md`、`core/scene.md`：✅ 已新增（通用写作技法，借鉴自 creative-writing-skills）
- `core/opening.md`：✅ 已新增（开篇切入方式库 + 多样性约束，解决开篇套路化）
- `core/*`、`topics/*`、`types/*`、`genre/*`、`templates/*`：✅ 已完善初版

> **4.6.2 增补（术语消歧）**：`core/audience.md` 招牌元素清单第 ⑤ 类统一为
> 「辅助器具特写」，并加**统摄限定**——清单 7 类均须与截肢身体/辅助器具直接相关，
> 剧情道具（信物/武器/文书/钥匙/照片等）不属招牌元素、不占密度预算；
> 同步 `templates/state-ledger.yaml` 的 distribution 元素枚举键名
> **4.6.1 增补（补漏）**：`topics/daily-scenes.md` 床高与床边转移两条去掉轮椅表述（与 v4.5.0 裁定一致）
> **4.6.0 增补（审查整改：受众方向同步 + 覆盖缺口补全）**
> **A. 受众方向**
> ① 清理「空裤管 / 裤管空垂 / 扁瘪」跨文件残留 8 处（`core/opening.md`、`topics/daily-actions.md`、
> `topics/body-details.md`、`topics/clothing.md`、`templates/state-ledger.yaml`、
> `types/hip-disarticulation.md` 穿裤行），统一为「髋离断＝裆线收口 + 空椅面；
> 膝上/膝下＝残端下缘以下空」。**保留** `hip-disarticulation.md` 未裁剪公用裤的合法例外，
> **保留** `core/audience.md` 招牌元素清单第 ④ 类「空」并加类型限定
> ② 8 处裸「多写 / 写细」收紧为「写细，分布服从 `core/audience.md` 密度规则与 `topics/timeline.md` 档位」
> ③ 补仲裁：`topics/timeline.md` B 档（近期）频率上限优先于「不连续两章」，B 档取「每 2 章」为常态
> ④ 主体性修正：「韧性」3 处（crutch-usage / equipment-risk / postapocalyptic）改动作智慧与主动权；
> 「无助」「最脆弱」2 处改处置顺序与判断
> ⑤ 可消除性修正：`core/opening.md` 维度 I 加「环境不作受限来源」限定，A/H 维度加苦难边界
> **B. 规则落点（让规则可执行）**
> ⑥ 重写 `templates/state-ledger.yaml`：固定属性补辅具类型 / 叙事视角 / 训练程度 / 视角身份定位 / 密度档；
> distribution 改 7 类枚举 +「元素→上次出现章」映射 + 首章 beat 数 + 已覆盖类别；
> 新增 `本章登记`（beat/turn/新信息/章节功能/stakes/章末钩子类型）；
> 拐杖状态枚举补齐（挂肘/交他人）；核查记录加滚动窗口（近 5 章，历史归档）
> ⑦ `templates/chapter.md` 补章级质量勾选（beat/turn/新信息/stakes/钩子/功能）
> ⑧ `core/cold-review.md`：读取清单加 `templates/outline.md` 与 `core/audience.md`；稽查维度加密度与频率；
> 明确「子代理只报、主代理只改」；四-bis/四-ter 标注仅供全书改稿模式
> ⑨ 三点步态定义统一为「本技能不适用，勿写」
> ⑩ wannabe 主角路径：`topics/timeline.md` 全书锁定加跃迁豁免，`core/character-setup.md` 补
> 「受众视角 × 叙事视角」组合说明（第一人称下"我"的身体状态）
> ⑪ 章末钩子与开篇维度联动：`core/opening.md` 加四-补节，`core/chapter-planning.md` 加轮转硬约束
> **C. 覆盖缺口与规范**
> ⑫ 新增 `types/bilateral.md`（双侧叠加层）、`types/elbow-wrist.md`（肘离断/腕离断）、
> `genre/historical.md`（古装向，含古代器具表）、`topics/daily-scenes.md`（高频日常场景，按节注入）
> ⑬ `core/physio-audit.md` 加「题材豁免」节（幻想/科幻可豁免条目 + 豁免后仍须保留的受限 + 三条硬底线）
> ⑭ `genre/realistic.md` 加 6 个细分题材的最小规则；`genre/fantasy.md` 加物理规则豁免边界
> ⑮ 注入索引加「类型未登记兜底」分支与「上下肢复合」例外；类型清单登记 elbow-wrist 与 bilateral；
> `types/_template.md` 补「运动能力」「体位与动态」两节为必填
> ⑯ 版本记录补 4.0.x 基线与 4.1.0；`templates/character-card.md` 注释改 HTML 注释；补 5 处标题前空行
> **4.5.1 增补（补漏）**：`types/shoulder-disarticulation.md`「止点改变」→「止点失去」（与 hip 文件同类修正对齐）
> **4.5.0 增补（剧情与大纲体系）**：新增 `core/worldbuilding.md`（世界观建立，
>   含无障碍水平/社会态度/器具可得性，锁定跨章一致性）与 `core/chapter-planning.md`
>   （章五要素/章末钩子类型库/功能配比/章间连接）；
>   扩充 `templates/outline.md`（世界观区块、弧线编排表、招牌元素全书分布计划表）
>   与 `templates/state-ledger.yaml`（时间线/关系状态/信息状态/角色弧状态）；
>   联动更新注入索引、`core/workflow.md` 大纲阶段（加大纲质量闸）、
>   `templates/chapter.md` 核查清单（加剧情项）、`core/cold-review.md`（加剧情结构稽查维度）；
>   修正「无障碍水平」相关表述——**受限来源是身体结构，环境只放大难度**
> **4.4.2 增补（残留清理二）**：`body-details.md` 坐姿条加髋离断限定（写空椅面）；`hip-disarticulation.md` 服装节空行清理
> **4.4.1 增补（残留清理）**：删除 `hip-disarticulation.md` 中与「三层模型」矛盾的「裤管扁瘪」残留
> （日常动作表坐行、身体细节坐姿条）；坐姿改用已确立的「空椅面」意象；服装节空行清理
> **4.4.0 增补（髋离断修订同步）**：髋离断形态改为「三层模型」（骨骼/外形/功能）；新增运动能力四级、
> 体位与动态、颤动幅度上限；修正假肢节的主动控制表述；
> 「蹲」改为分级——双腿蹲不可能、健腿单腿蹲可能（扶物半蹲/无支撑半蹲/全蹲上限），
> 并在 `physio-audit.md` 补单腿蹲豁免；
> 同步 `clothing.md` 与 `body-details.md` 的髋离断相关句
> **4.3.0 增补（受众驱动校准）**：
> ① `core/audience.md` 明确"本技能为受众驱动、不是写实记录"——当"医学上更常见"与"读者更爱看"冲突时取后者；
> 确立 **devotee 默认为读者身份**（非角色），devotee/wannabe 可入戏但须从属主线、不得改变 central question；
> 新增 **★招牌元素密度与疲劳控制**硬约束（同一元素不连续两章出现、每 2–3 章 1 个、全书在清单内轮转，
> 不得只盯 2–3 个元素反复写）。
> ② 新增 `topics/timeline.md`：**幻肢感频率与截肢时长匹配**（先天=默认不写／近期=每 1–2 章／多年=每 3–5 章），
> 档位全书锁定并写入角色卡与 state-ledger；`character-setup.md` 的"截肢时间"改为"截肢时长档位"。
> ③ 修正患侧**裁剪位置**：髋离断=**大腿根部（裆线/腹股沟）**（原写"裁剪至骨盆处"，骨盆非成衣基准线，且髋离断无空裤管）；
> 膝上/膝下=残端下缘；肩离断上装=肩峰下缘。`topics/clothing.md` 新增"类型差异：裁剪位置"对照表与常见错误。
> ④ 用户裁定记录：**轮椅不设为单腿截肢角色的常用辅具，维持拐杖为主**（受众偏好优先于写实常见度）；
> **不设未成年人硬约束**（由 Agent 自行判断）。
> ⑤ 顺带修正两处硬事实错误：`types/shoulder-disarticulation.md` 肩离断肌电假肢表述、
> `topics/crutch-usage.md` 三点步态与摆至步重复。
> **4.2.0 增补**：新增 `core/opening.md` 开篇切入方式库（10 维度）+ 多样性硬约束 + 烂开篇反例清单 + 题材→推荐开篇映射；`core/workflow.md` 加逐章创作硬性要求（禁止一次生成整篇）+ 大纲阶段选开篇 + 构思阶段询问用户是否开启冷读稽查；`core/scene.md` 例外条款加限制；`templates/outline.md` 第一章行改为分布池选 1–2 个 + 强制首章含钩子；`core/style.md` 重点内容降级为全书密度目标 + 新增声口多样性；`core/character-setup.md` 加多样性自检 + 设定摇号表；`genre/*.md` 各加推荐开篇类型；`templates/chapter.md` 核查清单加开篇雷同检查；`templates/state-ledger.yaml` 加 distribution 字段。
> **4.1.1 增补**：髋离断假肢上下楼梯规则（`types/hip-disarticulation.md` + `topics/prosthesis.md`）；假肢为常用辅具时空裤腿默认折叠塞裤腰不裁剪（`topics/clothing.md`）。
> **4.1.0 增补**（据仓库提交记录补记）：新增剧情节奏/弧线/场景结构通用写作技法
> （`core/pacing.md`、`core/structure.md`、`core/scene.md`）+ 肩离断上肢支持 + 生理事实审查
> （`core/physio-audit.md`）+ 去AI化润色深化
> **4.0.x 基线**（据仓库提交记录补记，4.0.1 / 4.0.2）：技能创建，确立
> `core/` `types/` `topics/` `genre/` `templates/` 五层结构与按需注入机制、受众驱动的定位基调

## 八、通用说明

- 所有专项已完善初版内容，后续按实际创作反馈迭代。
- **推荐流程**：状态核查流水账（章末自查，零成本）+ 冷读子代理稽查（创作前询问用户是否开启）。
- 本总纲第七节为无版本号的状态清单；版本变更一律记入下方的版本记录，并保持两处不冲突。