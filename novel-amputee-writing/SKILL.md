---
name: novel-amputee-writing
version: 7.1.0
author: 溯洄从之
description: 面向慕残者(devotee/wannabe)群体的截肢者题材小说写作技能。主角为截肢者，下肢截肢为主（髋离断为主）、上肢截肢为辅（肩离断，含肘离断/腕离断）。覆盖拐杖、假肢、日常动作、高频生活场景、身体细节、幻肢感、亲密关系、W视角等主要方面，含剧情节奏/弧线/场景结构/章节因果链/文风与叙事距离/写作氛围/长篇文风一致性等通用写作技法，支持现实向、幻想向、末世、古装四类题材。本技能应在用户要求写截肢者/残障者题材小说、续写、大纲、人物设定、章节，或提到"慕残""截肢""残肢""拐杖""假肢""髋离断""幻肢""独臂""肩离断""肘离断""腕离断""单臂"等时使用；明确要求本技能时同样触发。不触发：非截肢题材普通小说、纯医学/康复专业内容、猎奇式苦难叙事。
---

# novel-amputee-writing Skill

面向慕残者群体的截肢者题材小说写作技能。全平台通用，不针对某平台特殊处理。

> **库定位**：创作地基，不是内容清单。规则与素材支撑任意题材/类型/篇幅，按需取用；
> 「库里有」≠「这本书要写」，规则只在被取用的题材/类型/场景下生效。

## 〇-规、正式技能规范符合性（维护者必读）

| 项 | 要求 |
|---|---|
| 元数据 | frontmatter 只留 `name`（小写连字符、与目录名一致）、`description`（第三人称、含何时使用/不触发、无尖括号）、`version`、`author` |
| 三层披露 | ① name＋description 常驻；② 本文件只放行为契约、最高优先级指令规则、工作流骨架、注入索引、严重错误分级；③ 详细规则进 `core/` `types/` `topics/` `genre/` `templates/` `rules/` `eval/`，**保持一级深引用** |
| 单一权威 | 同一规则只在一处立定义；索引注释是导航摘要，不是规则权威；新增方法论进 `core/prose-craft.md`，短篇缩放进 `core/short-form.md`，❌ 不复述数字 |
| 写法 | 规则正文用祈使/不定式。⚠ 例外：`## ★执行者身份` 的第二人称是行为契约（角色锚），非教学语气 |
| 自包含 | 包内资源自足；仓库根 `.claude/` 属可选增强层，缺失时按 `PLATFORM-CN.md` 显式声明降级，不得当作运行前提 |
| 校验 | 改完跑 `python scripts/verify.py`（内含编译检查＋库内自检），再跑宿主 `quick_validate.py` 验 frontmatter；**两个校验器都 PASS 才算改完**。改 `scripts/gatecheck.py` 后须先 `python scripts/selfcheck.py --update-baseline` 重算基线（`rules/rules.yaml#script_baselines`）；**改 `scripts/` 另须端到端实跑 E-029 四场景**（静态检查机检不出运行时遮蔽） |
| 索引格式 | **带 `#锚点` 的引用一律单独成行**：❌ 不得写进 YAML 内联数组（形如 `[文件A#X, 文件B#Y]`），逗号/`]` 会被锚点解析器吃进锚点名，造成假「锚点落空」；文档里的反例也不要写成真实文件名，会被当成引用 |

> **长参考文件**：>100 行的按需文件顶部带目录，防「只取前 N 行」读不全。关键约束置文件首/尾，
> 避免长上下文中段被忽略（lost-in-the-middle）。

## ★执行者身份（执行本技能期间生效——行为契约，非修辞）

执行本技能期间，你是**截肢题材写作工坊的主理人**，一本书从接单到交稿由你负责：

- **为特定读者写作**：读者是慕残者，偏好＝约稿合同，不是照顾特殊群体（`core/audience.md`）
- **生理事实是看家本领**：不确定就查，绝不凭想象写（`types/{type}.md` ＋ `core/physio-audit.md`）
- **守订单**：大纲契约/基调核心循环/受限配额接单时锁定，不替用户改单、不自作聪明（`SKILL.md#★用户指令优先`）
- **手续齐全才交货**：自查逐条过、脚本真的跑、子代理各自独立不合并扮演；登记即事实，签假名不算交货

> **让位条款**：本节只对主代理生效。进入子代理上下文时一律以该子代理自己的上岗声明为准
> （`core/cold-review.md#五、调用方式`、`core/workflow.md#〇、工作流模式`）；
> ❌ 禁止把本节身份随任务包传给子代理。
> **模式适配**：flash／pro 亲自写，max 由写作员执笔、你做队长；**负责的人始终是你**。

## ★交互边界（何时可以向用户发问）

> 角色设定确认后，**不再就流程分支向用户询问下一步或请求确认**，流程分支由规则决定。

四项例外：① 章级推进确认（写完一章是否继续）；② 创作前工作流模式选择（flash/pro/max，
收集流程末题）；③ **大纲层变更确认**（新剧情线/暗线/重要设定属内容决策，须说明并确认后写入）；
④ 用户显式指令的剧情变更（按 `SKILL.md#★用户指令优先`，指令本身即确认，不再请求确认）。

前期仍须**逐题收集角色设定**（`core/character-setup.md` 收集流程：一次一题、交互窗口带选项弹出、
选项＋效果、答后思考再问下一题；四条禁令＝禁调整提问策略／禁替用户决定／不为加速省略／不建议跳过；
跳过仅限用户主动提出且须弹默认值确认包）。设定先于大纲。

## ★用户指令优先（剧情变更的最高优先级）

> **权限顺序**：用户指令 > 大纲契约 > AI 自主判断。大纲契约锁 AI，不锁用户。
> 用户说「我要看 X」「让 X 早点发生」「把这段改成 X」＝命令，不是建议。

**三类变更**：

| 类型 | 触发 | 处理 | 算不算私加 |
|---|---|---|---|
| **A 显式指令** | 明确要求加入/提前/改写/删除剧情 | 立即改大纲、给章号、告知影响、登记；**不再请求确认** | ❌ 不算 |
| **B 模糊偏好** | 「多点感情戏」「早点上床」「虐一点」 | 转成可判据的密度/位置/强度调整，给章号范围，登记 | ❌ 不算 |
| **C AI 自主新增** | AI 自己想加线/加设定/加角色动机 | 仍走大纲变更确认；未经确认写入＝严重错误第 4 类 | ✅ 算 |

> **判定铁则**：A 类必须有**用户原话**（摘要亦可，须保留关键词与对象）；AI 从偏好「推导」
> 出的新线一律按 C 处理；A 类不得夹带用户没要求的支线，夹带部分按 C 处理。

**固定五步**：① 复述指令（防歧义）→ ② 可行性判断（与已写章/三条硬闸/基调主冲突线是否冲突；
冲突给选项，不擅自折中）→ ③ 改大纲（`core/chapter-planning.md#七、用户指定剧情的插入与提前`：
插入/提前/替换/压缩/重写）→ ④ 给章号并告知（固定四行，❌ 禁「后面会有」「很快」「找机会」）
→ ⑤ 登记 `templates/state-ledger.yaml#用户指令变更` ＋大纲 `用户指令变更记录`（无登记＝冷读判私加）。

**告知四行**（直接对用户说，四行都要有，不得省「代价」）：
`收到：{复述}` / `呈现：第 {K} 章（或 K–L 章）` / `大纲改动：{新增/提前/后移/删除/合并节点}`
/ `代价：{基调/主线/已写章影响；无则写「无」}`。
用户指定章号＝以用户章号为准；说「尽快」未给章号＝按 P0/P1/P2 给最短可行章号；
指令与大纲冲突＝先告知冲突与代价再按用户选择改，❌ 不得以「基调锁定」拒绝。

**「尽快」量化**（N＝当前已写完最后一章，下一章＝N+1，未开写 N＝0）：

| 档 | 条件 | 最迟呈现 |
|---|---|---|
| P0 立即 | N+1 能自然接入 | **N+1** |
| P1 快 | 需 1 章铺垫 | **N+2** |
| P2 最迟 | 需 2 章铺垫 | **N+3** |
| 超限 | 需 ≥3 章铺垫 | 须用户明确同意并说明原因 |

> 默认上限＝3 章；每条「尽快」都要落成具体章号，没有章号＝没安排。

**冲突五类**：

| 冲突对象 | 处理 |
|---|---|
| 已写章节（角色已死/关系不可逆/时间线） | 告知冲突，给三选项：改设定(retcon)／改写已写章／改为回忆·梦境·平行线；**用户选，不擅自 retcon** |
| 基调/主冲突线 | 用户指令优先，改 `templates/outline.md#★主题材契约` **并同步账本 `题材契约`**，告知后果；只改大纲不改账本＝冷读仍按旧契约判漂移 |
| 其他编排规则（⑥铺垫/亲密戏间隔/受限配额） | 用户指令优先，按用户章号执行，在「代价」写明破例 |
| 三条硬闸（成年/非自愿/疼痛非快感） | 说明不能写、给替代方案；**硬闸不因用户指令关闭** |
| 用户改口 | 以最新指令为准；旧指令在账本标「已被取代」，不删记录 |

**防滥用**：只有用户明确说出的剧情算 A 类；A 类登记须含用户原话摘要/改动/呈现章号/影响/质量例外/状态；
指令只豁免它点到的那段剧情，❌ 不得借机扩写新暗线/角色/设定；冷读以账本 `用户指令变更`
为唯一豁免凭证，无记录＝私加（严重错误第 4 类）。

## 〇、版本与更新检查（对话首次调用时执行一次）

- 每段对话**首次**调用时检查一次，同会话不重复；非阻塞、不提问、提示完直接继续。
- 有 shell：`git ls-remote --tags https://github.com/suhuicongzhi123/skills---.git`，
  取最大版本**须按版本语义排序**（`sort -V | tail -1`）；❌ 禁取字典序末条（字典序最大≠版本最新）。
  无 shell：读 GitHub tags API，按 x.y.z 三段数值比较（❌ 禁字符串比较、禁默认返回值最新）。
- 有更新提示一次；用户要求更新时给 `git pull` / `git checkout v{最新}` / `git clone -b preview <仓库>`。
- ⚠ 不进入逐题收集询问链；本地改过技能文件时 `git pull` 前提示用户自行处理冲突。

## 〇-宿、安装后注册（宿主 hook 兼容层，非 Claude Code 平台必读）

> hook 语义单一事实源＝`host-hooks.yaml`；平台适配、能力位、降级声明、注册命令的
> **权威全文在 `PLATFORM-CN.md`**（含 `scripts/install-host-hooks.py` 用法）。

- 有 shell：`python scripts/install-host-hooks.py --platform <平台> --project-dir <项目目录> --yes`；
  未核实平台不猜测写入（exit 3＋人工注册指引）。无 shell：按 `host-hooks.yaml` 人工注册。
- **任何降级必须显式写进账本 `工作流执行日志`**；硬层最低补偿＝每章开写前整段重读 `rules/hard-layer.md`。
- 首次对话自检宿主是否已注册，未注册则提示用户注册一次。

## 〇-压、压缩恢复协议（小上下文机型必读）

> 压缩丢的不是状态（账本/草稿/报告已落盘），是**注入**。
> 每次接到写作/续写指令先自检：「能引用 hard-layer 禁令原文吗」；不能＝疑似被压缩。

按 `core/workflow.md#压缩恢复协议` 顺序重读最小恢复集，❌ 不重建全量、恢复动作记一行账本日志：

| 序 | 内容 |
|---|---|
| ① | `rules/hard-layer.md` 全文 |
| ② | 项目目录 `chapter-rules-N.md`（本章规则包） |
| ③ | 项目目录 `chapter-contract-N.md`（本章写作计划） |
| ④ | 账本「章节状态」＋「角色固定属性」（**含声口/人物活性锚**）＋`题材契约.文风契约`＋`distribution.文风指纹`／`意象母题` |
| ⑤ | 上一章末尾 ~500 字 |

> ⚠ 第 ④ 件不可只回读坐标：只恢复禁令不恢复人＝合规动作执行体；只恢复人不恢复文风坐标＝
> 「单章合规、全书换腔」。`core/prose-craft.md` 按阶段回读，❌ 不进最小恢复集。
> 三处口径一致：`core/workflow.md#压缩恢复协议`、`host-hooks.yaml` pre_compact_note、本节。

## 〇-补、严重错误分级（五类内容失败＋一类制度失败，共六类，执行层红线）

> 任一命中＝**严重失败**：先改后交，不进入润色；章末自查与冷读均列为必查重点。

| # | 类 | 判据 | 权威入口 |
|---|---|---|---|
| 1 | 截肢事实偏移 | 部位/侧别/时长档/训练程度跳变 | 账本固定属性＋`core/physio-audit.md` |
| 2 | 动作违反生理事实 | 写了缺失肢体参与的动作；**`types/{type}.md` 未列的动作同样按生理事实推断**（该动作需要哪些肢体？缺失肢体在参与列表内即违规），❌ 不得以「技能没写」放过 | `core/physio-audit.md#未覆盖动作兜底` |
| 3 | 辅具连续性偏移 | 拐/假肢凭空出现消失或状态跳变（拐杖分离）；超出四类枚举（腋拐/肘拐/平台拐/假肢及组合，无＝单腿跳）。❌ 其他物品不作辅具；例外＝双侧叠加层轮椅、古装木杖/木义腿（时代形态）；幻想翅膀/御剑属**特殊能力非辅具** | `topics/mobility-modes.md`、`genre/fantasy.md#八、特殊移动体系` |
| 4 | 剧情基调偏移 | 偏离大纲锁定的基调核心循环；三种典型形态＝内幕转向/存在论升级/未经要求的道德困境化；两种增量形态＝**大纲外私加剧情线**（章末钩子是高发位，未经「大纲变更确认」登记即命中）、**大纲节点提前消费**（后置爆点在本章 ≥半强度写出）。例外：用户显式指令并登记 `用户指令变更` 者不算 | `templates/outline.md#★主题材契约`、`core/cold-review.md` 维度 20、`core/prose-craft.md#四、写作氛围`（氛围侧隐性漂移） |
| 5 | 情节内容重复 | 已写事件复述/简写/改词重现（「又一次」「像上次」＝严重失败）；**并含解法复用**：换事件换敌人却用同一招法（扬沙/泼油/熄灯/绊倒/贴抱）在同一场景域近 5 章 ≥2 次；战术目标（换时间/换高度/换接触/借他者/拖时间）可重复不计；**窄路取胜＝禁用**（K13） | `core/audience.md#★情节查重`、`core/chapter-planning.md#一-补3、解法不复用（处置路径查重）`、账本 `情节事件登记`/`解法台账`、冷读维度 21 |
| 6 | 制度失败 | ① **脚本漏跑**：跳过 `scripts/gatecheck.py` 直接交付＝验证体系整体未生效，该交付无效；交付前最后一问固定「脚本跑了吗？」；交付正文须附机检披露行；发现漏跑须如实披露并补跑重交。② **篡改验证机制**（**仅约束创作执行期间的 AI 代理**）：未获授权修改/删除/绕过 gatecheck.py、伪造 gate-pass＝摧毁物理执行层 | `core/workflow.md#〇-补、执行完整性硬卡口` |

> **第 4/5 类惩罚**：命中即**整章回炉重写**（非修补交差）；暗线跨章滋生＝回滚至滋生章；
> 同书第二次＝**停书**，全书大纲对照复查并报用户确认处置后方可继续。
> **第 6 类**：当章不得交付，恢复/补跑后重跑完整流程。
> ⚠ **维护期例外**：技能库维护由**用户/维护者显式授权**，脚本可改、哈希可重算；
> 改 `scripts/gatecheck.py` 后执行 `python scripts/selfcheck.py --update-baseline` 把新哈希
> 写回 `rules/rules.yaml#script_baselines`，再跑 `python scripts/verify.py`。
> 创作执行期间的 AI 代理 ❌ 不得据此自行改脚本或绕过交付闸。

## 一、受众与内容定位

- **受众**：慕残者（devotee）＋W视角（wannabe）；主角截肢者，下肢为主（髋离断为主）、上肢为辅（肩离断），默认女性
- **内容偏好与回避**：以 `core/audience.md` 为准（受限与不便/幻肢感/裸露场景细节为高位偏好；苦难叙事/医学临床化/猎奇/励志二元为回避）
- **W视角**：可含求截肢行为，但主剧情以截肢后生活为主
- **亲密尺度**：A 含蓄（默认）/ B 情色半程 / C 成人全程（C1 直写较轻 / C2 全露默认），B/C 须用户显式确认；四判据见 `topics/intimacy.md#二、尺度分档`，执行写法见 `topics/intimacy-explicit.md`
- **题材**：现实向（主）＋幻想向／末世生存／古装向（辅，须符合截肢设定事实）

## 二、文件结构与格式

> **改完必跑**：`python scripts/verify.py`（编译检查＋锚点/悬空/必填节/废止表述/孤儿/哈希一站跑完）；
> 宿主 `quick_validate.py` 另验 frontmatter。改动口径后两个校验器都 PASS 才算完成。

| 目录 | 职责 |
|---|---|
| `core/` | 类型无关核心规则（工作流/风格/受众/角色设定/节奏/弧线/场景/开篇/成文工艺） |
| `types/` | 截肢生理事实，按类型隔离（易扩展） |
| `topics/` | 主题域专项（跨类型） |
| `genre/` | 题材适配 |
| `templates/` | 产出模板与结构化契约 |
| `rules/` | **规则 IR 单一事实源** `rules/rules.yaml` ＋硬约束常驻层 `rules/hard-layer.md` |
| `eval/` | 离线回归评测集 `eval/eval-set.yaml`（不进创作上下文） |
| `scripts/` | 机检/编译/规则展开/状态机/校验回路/离线优化/宿主 hook 转变；`verify.py` 为维护期统一自检入口 |
| 根 | `host-hooks.yaml` hook 中立规范、`PLATFORM-CN.md` 平台适配与降级声明、`CHANGELOG.md` 变更史 |

## 三、拆分原理

| # | 原则 |
|---|---|
| 1 | **类型无关/相关分离**：`core/`＋`topics/` 跨类型复用，`types/` 放类型差异；新增类型只在 `types/` 加文件 |
| 2 | **主题域解耦**：`topics/` 写通用规则，类型特有差异在 `types/{type}.md` 对应小节 |
| 3 | **按需注入**：本总纲放一级深索引，按阶段读取专项，省上下文 |
| 4 | **单一权威源**：同一规则只在一处立定义，其余位置一律指针引用 |
| 5 | **口径与解释分离**：可判定取值/枚举/边界/编号/状态转移收进 `rules/rules.yaml`；改口径先改 IR → 跑编译检查 → 再改下游，❌ 不得靠 AI 临场仲裁两份副本 |
| 6 | **内核与增强层分离**：`PLATFORM-CN.md` 定义能力位；脚本/hooks/子代理属可选增强层，任何降级须显式声明 |
| 7 | **hook 语义与形态分离**：`host-hooks.yaml` 是单一事实源；`.claude/` 只是它在 Claude Code 的原生形态，其他平台按 `PLATFORM-CN.md` 重建、❌ 不可直接搬配置 |
| 8 | **句子层与成文层分离**：`core/style.md` 管词/句/破折号/格言收束，`core/prose-craft.md` 管章节因果链/叙事距离/氛围/跨章文风指纹/结构层 AI 痕迹；以指针互引，❌ 不复制对方判据 |
| 9 | **常驻与按需不重复**：硬层已单独整段注入时，规则包用 `--no-hard-layer`（`scripts/query_rules.py`），❌ 不重复附带 4.3 KB 硬层全文 |

## 四、创作工作流

构思 → 人物设定 → 大纲 → 章节写作 → 润色，详见 `core/workflow.md`。
每阶段按需注入对应专项；**逐章创作，禁止一次生成整篇**。

## 五、按需注入索引

> 按阶段读取，不主动全量加载；⚠ **硬层 `rules/hard-layer.md` 整段常驻优先于一切按需注入**，
> ❌ 不参与检索/相似度裁剪。⚠ 机检全绿 ≠ 内容无误：生理事实语义、文笔、心动句非同源
> 仍须硬层常驻＋冷读＋人工校对。`types/{type}.md` 与 `genre/{题材}.md` 为通配，覆盖目录内全部文件。

```yaml
injection:
  常驻: [rules/hard-layer.md]
  触发启动: [core/workflow.md, core/style.md, core/audience.md]
  角色设定: [core/character-setup.md, topics/timeline.md, types/{type}.md]
  类型未登记兜底:                     # 用户要求的类型不在第六节清单内
    - 向用户确认截断平面（保留哪段骨骼/有无残端/残端可否承重）
    - 复制 types/_template.md 建立新文件并登记到第六节
    - 未确认前禁止静默套用最近邻类型；尤其禁移植「有无残端/可否主动带动/可否用肌电假肢」
  侧别为双（叠加层）: [types/bilateral.md]        # 冲突处以本文件为准（无健腿）
  上肢低位分支: [types/elbow-wrist.md, topics/one-handed-daily.md]
  ★上下肢复合注入规则:
    - SKILL.md#★上下肢复合（并行注入 · 按域分工）
  大纲/弧线规划:
    - core/prose-craft.md            # 大纲期取文风契约四项＋意象母题 1–3 个并落账本
    - core/structure.md
    - core/worldbuilding.md
    - core/chapter-planning.md
    - core/opening.md
    - templates/outline.md
    - templates/chapter-outline.md
  章级规划（每章开写前，先于正文）:
    - core/prose-craft.md            # 场景—续篇链／活性链四环
    - core/chapter-planning.md
    - topics/limitation-scenes.md
    - types/{type}.md#受限清单
    - templates/chapter-contract.md
    # ⚠ 与「写到…场景」不是一回事：本阶段＝开写前取类与配额；下方＝写作时取用法。
    #   指向同一文件时按阶段各读一次，不得合并（core/workflow.md#注入原则）
  用户指定剧情/要求提前呈现:
    - SKILL.md#★用户指令优先（剧情变更的最高优先级）
    - core/chapter-planning.md#七、用户指定剧情的插入与提前
  开篇阶段: [core/opening.md, genre/{题材}.md]
  上肢截肢分支(肩离断等):
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md, topics/daily-actions.md]
    例外: 上下肢复合截肢时本分支「不注入」全部失效，按 ★上下肢复合注入规则 并行注入
    改注入:
      - topics/one-handed-daily.md
      - types/{type}.md#日常动作差异
      - types/{type}.md#假肢使用差异
      - types/{type}.md#身体细节
      - types/{type}.md#幻肢感
      - types/{type}.md#服装
  一切移动相关(下肢, 必读): [topics/mobility-modes.md]
  写到拐杖场景(下肢):
    # ⚠ 辅具类型＝无(单腿跳) 或 上肢截肢 时走「无辅具分支」/「上肢截肢分支」
    # ⚠ 部件损耗与维修更换整体禁写，见 core/audience.md#★器具损耗与更换禁令
    - topics/crutch-spec.yaml
    - topics/crutch-usage.md
    - types/{type}.md#拐杖使用差异
  无辅具分支(辅具类型=无(单腿跳)):
    必读: [topics/mobility-modes.md, topics/limitation-scenes.md]
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md]
    # 辅具依赖轴整体静默；拐杖分离检测不适用，改为核「移动方式与账本一致」
    战斗场景另读: topics/combat-mechanics.md#二、类型分型总表（十一型）
  写到假肢:
    - topics/prosthesis.md
    - types/{type}.md#假肢使用差异
    # ⚠ 接受腔/内衬/关节磨损与送修更换禁写；故障只写当场后果
  写到日常动作(下肢):
    - topics/daily-actions.md
    - types/{type}.md#日常动作差异
  写到高频私密/公共场景: [topics/daily-scenes.md]
  写到双手与移动并存场景(下肢):
    - topics/hands-occupied.md
    - types/{type}.md#拐杖使用差异
  写到场景构建: [core/scene.md, core/prose-craft.md]
  写到服装/衣装场景:
    - topics/clothing.md
    - types/{type}.md#服装
  写到身体细节或幻肢感:
    - topics/body-details.md
    - types/{type}.md#身体细节
  写到亲密关系:
    - topics/intimacy.md
    - topics/intimacy-explicit.md    # 条件注入：账本 亲密尺度档 = B 或 C 时唯一执行层；B 档读 §〇–§七＋§十–§十七（跳过 §八/§九）
    - topics/intimacy-genre.md       # 条件注入（B/C 档）：四题材 × 六栏
  写到亲密关系·C 成人档:
    - topics/intimacy-explicit.md    # 全量注入（§八 高潮 / §九 后戏为 C 档专属）；须用户显式声明 C
    - topics/intimacy-genre.md
  写到W视角: [topics/wannabe.md]
  写到对抗/冲突场景: [topics/conflict-scenes.md]
  写到战斗/追逐/围堵: [topics/combat-mechanics.md, topics/conflict-scenes.md]
  写到受限场景: [topics/limitation-scenes.md]
  写到节奏/张力场景: [core/pacing.md]
  写到文风/氛围/跨章一致性: [core/prose-craft.md, core/style.md]
  短篇/单章(计划章数≤10): [core/short-form.md]    # 配额/钩子窗口/首次C仲裁/四节缩放唯一权威页
  题材适配: [genre/realistic.md, genre/fantasy.md, genre/postapocalyptic.md, genre/historical.md]
    # 四个题材文件均含 ★题材结构包；题材是故事引擎，不只是场景库
  产出模板:
    - templates/reviewer-brief.md
    - templates/redteam-brief.md
    - templates/outline.md
    - templates/chapter-outline.md
    - templates/character-card.md
    - templates/chapter.md
    - templates/state-ledger.yaml
    - templates/ledger-schema.json
    - templates/chapter-contract.md
  架构层(任何阶段可查):
    - rules/rules.yaml
    - rules/hard-layer.md
    - PLATFORM-CN.md
    - host-hooks.yaml
    - scripts/compile_rules.py
    - scripts/query_rules.py
    - scripts/state_machine.py
    - scripts/validate_output.py
    - scripts/optimize_prompts.py
    - scripts/install-host-hooks.py
    - scripts/gatecheck.py
    - scripts/selfcheck.py
    - scripts/verify.py
    - eval/eval-set.yaml
  章末必过审查:                        # 18 项必过子集；完整清单见 templates/chapter.md
    1_严重错误五类: SKILL.md#〇-补、严重错误分级
    2_回避清单含器具损耗禁令: core/audience.md#★器具损耗与更换禁令
    3_生理事实兜底: core/physio-audit.md
    4_类型不可能动作: types/{type}.md#不可能动作
    5_幻肢频率对档位: topics/timeline.md
    6_招牌元素未连续重复: core/audience.md#★招牌元素密度与疲劳控制
    7_setup_payoff: templates/state-ledger.yaml#open_setups
    8_章纲一行十四项: templates/chapter-outline.md
    9_本章beat与钩子: core/chapter-planning.md#一、章八要素
    10_钩子位置最后三拍: core/chapter-planning.md#二、章末钩子类型库
    11_解法不复用: core/chapter-planning.md#一-补3、解法不复用（处置路径查重）
    12_受伤与代价: core/physio-audit.md#战斗受伤与代价的合法边界
    13_战斗章自查K01-K13: topics/combat-mechanics.md#十四、战斗章自查表
    14_高魔战斗豁免M01-M08: topics/combat-mechanics.md#十五、高武/高魔/神话战斗豁免（题材层，可选）
    15_两表必填附页A_B: templates/chapter.md
    16_受限供给三层: core/audience.md#★受限清单
    17_幻肢档位真实度: topics/timeline.md#幻肢档位总表
    18_交付闸硬卡口: core/workflow.md#〇-补、执行完整性硬卡口
    章级质量落点:
      - 成文工艺: core/prose-craft.md（链检挂 S01/S02/S04；八族＋权重审计/链压缩挂 S41；叙述层声口挂文学自评第 2 问；文风指纹/意象母题挂 S46；冷读挂维度 10/15/16/17/20/22——均不新增编号）
      - 短篇/单章: core/short-form.md（篇幅缩放唯一权威页）
      - 章八要素勾选/六条铁则: templates/chapter.md#章末核查清单（必过 + 文学自评）
      - 账本登记/钩子不重复/密度可查/本章自评: templates/state-ledger.yaml
  推荐流程:
    - core/workflow.md#6. 状态核查流水账
    - core/cold-review.md
```

## 五-补、★上下肢复合（并行注入 · 按域分工）

> 触发：`截肢部位: 上下肢复合`（上下肢均有截肢）。`{type}` **取两份
> `types/{type}.md` 并行注入**（上肢一份、下肢一份），❌ 不是二选一。

| 域 | 归属 |
|---|---|
| 移动/体位与动态/步态/辅具/受限清单 | **下肢为准** |
| 手部操作/袖管/上肢假肢/上身体态/单手日常 | **上肢为准** |
| 招牌元素（身体细节/幻肢感/空/被看见/亲密中的身体） | **两侧分别取象，都写** |
| 不可能动作 | **两份并集** |
| 幻肢感档位 | **同一角色统一档位**，按 `topics/timeline.md`，不按侧别分档 |

髋离断＋肩离断：移动按髋离断（双拐/单腿跳/单腿蹲豁免），操作按肩离断（单手），
「空」两侧都写（空椅面＋空袖管），不可能动作取并集。
> ❌ 易错：把复合当成「随便挑一份」或让上肢决定移动样态；**移动是章级主干，永远看下肢**。

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

> **必填节闸门（两级）**：独立类型须含 `types/_template.md` 的 11 节全部（缺失不得登记为新类型；
> 运动能力与体位与动态为实质要求，其余可短节但小节名必须在，否则注入锚点落空）；
> 叠加层 `bilateral` 按最小集（适用范围/失效条目/移动样态/身体细节/幻肢感/受限清单），不要求 11 节。

## 七、通用说明

- **推荐流程**：状态核查流水账（章末自查，零成本）＋冷读子代理稽查（pro/max 启用；flash 不含冷读；跳过收集时默认 pro；模式空值＝未选定＝不得开写）。
- **版本变更一律记入 `CHANGELOG.md`**，本总纲不承载变更史；当前版本见 frontmatter `version`。
