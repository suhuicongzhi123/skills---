# 按需注入索引（外移自 SKILL.md 第八节）

> 权威全文。SKILL.md 第八节仅保留锚点指针。按阶段读取，❌ 不整体加载；硬层 `rules/hard-layer.md` 整段常驻优先于一切按需注入。

## 八、按需注入索引

> 按阶段读取，不主动全量加载。硬层 `rules/hard-layer.md` 整段常驻优先于一切按需注入。
> `types/{type}.md` 与 `genre/{题材}.md` 为通配，覆盖目录内全部文件。

```yaml
injection:
  常驻: [rules/hard-layer.md]
  触发启动: [core/workflow.md, core/style.md, core/audience.md, core/voice.md]
  角色设定:
    - core/character-setup.md
    - core/psychology.md         # 心理模式库 M1–M31：按人物取向取模式；呈现技法见 emotion/emotion-signal
    - core/voice.md            # 第二节四要素 + 第四节温度矩阵，配合 templates/voice-card.md
    - templates/voice-card.md
    - topics/timeline.md
    - types/{type}.md
  类型未登记兜底:                     # 用户要求的类型不在第六节清单内
    - 向用户确认截断平面（保留哪段骨骼／有无残端／残端可否承重）
    - 复制 types/_template.md 建立新文件并登记到第六节
    - 未确认前禁止静默套用最近邻类型
  侧别为双（叠加层）: [types/bilateral.md]        # 冲突处以本文件为准（无健腿）
  上肢低位分支: [types/elbow-wrist.md, topics/one-handed-daily.md]
  ★上下肢复合注入规则:
    - SKILL.md#★上下肢复合（并行注入 · 按域分工）
  大纲/弧线规划:
    - core/structure.md
    - core/prose-craft.md            # 大纲期取文风契约四项＋意象母题 1–3 个并落账本
    - core/worldbuilding.md
    - core/chapter-planning.md
    - core/opening.md
    - templates/outline.md
    - templates/chapter-outline.md
  章级规划（每章开写前，先于正文）:
    - core/scene-drive.md            # ★生成层：做事≠动手 / 假戏六型 / 详略差 / 配角驱动器 / 出状态
    - core/scene-engine.md           # 一场戏五件事 / 材料三问 / 场景与概述交替
    - core/intensity.md              # ★强度层：峰值段 / 战斗回合 / 动作密度 / 对话博弈 / 段落卫生
    - core/emotion.md                # ★情感层：情感被平均分配 / 在乎的对象 / 压着的动作 / 漏出来的一处
    - core/emotion-signal.md         # ★情绪出口：三层信号 / 可观察vs可命名 / 签名动作 / 紧张时的语言失控
    - core/chapter-planning.md
    - topics/limitation-scenes.md
    - types/{type}.md#受限清单
    - templates/chapter-contract.md
    # ⚠ 本阶段只产出「本章写作卡」（含★四行硬项，gatecheck [27] 硬检）。
    #    ❌ 不打开 templates/chapter.md（那是审读时点的表）
  开写前必做:
    - core/voice.md#三、开写前三句试音
  用户指定剧情/要求提前呈现:
    - SKILL.md#★用户指令优先（剧情变更的最高优先级）
    - core/chapter-planning.md#十、用户指定剧情的插入与提前
  开篇阶段: [core/opening.md, genre/{题材}.md]
  上肢截肢分支(肩离断等):
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md, topics/daily-actions.md]
    例外: 上下肢复合时本分支「不注入」全部失效，按 ★上下肢复合注入规则 并行注入
    改注入:
      - topics/one-handed-daily.md
      - types/{type}.md#日常动作差异
      - types/{type}.md#假肢使用差异
      - types/{type}.md#身体细节
      - types/{type}.md#幻肢感
      - types/{type}.md#服装
  一切移动相关(下肢, 必读): [topics/mobility-modes.md]
  写到拐杖场景(下肢):
    - topics/crutch-spec.yaml
    - topics/crutch-usage.md
    - types/{type}.md#拐杖使用差异
  无辅具分支(辅具类型=无(单腿跳)):
    必读: [topics/mobility-modes.md, topics/limitation-scenes.md]
    不注入: [topics/crutch-spec.yaml, topics/crutch-usage.md, topics/hands-occupied.md]
    战斗场景另读: topics/combat-mechanics.md#二、类型分型总表（十一型）
  写到假肢:
    - topics/prosthesis.md
    - topics/fetish.md             # 恋物素材 F3/F4/F29：假肢脱卸/接受腔/穿脱仪式动作链
    - types/{type}.md#假肢使用差异
  写到日常动作(下肢):
    - topics/daily-actions.md
    - types/{type}.md#日常动作差异
  写到高频私密/公共场景: [topics/daily-scenes.md]
  写到双手与移动并存场景(下肢):
    - topics/hands-occupied.md
    - types/{type}.md#拐杖使用差异
  写到场景构建: [core/scene-drive.md, core/scene-engine.md, core/scene.md]
  写到对白/人物声音: [core/voice.md]
  写到服装/衣装场景:
    - topics/clothing.md
    - topics/fetish.md             # 恋物素材 F0/F1/F2/F14/F16/F24/F32/F36/F37：丝袜/高跟/连裤袜/空袜管/手丝/全身袜
    - types/{type}.md#服装
  写到身体细节或幻肢感:
    - topics/body-details.md
    - topics/fetish.md             # 恋物素材 F17/F19/F20/F21/F22/F25/F26/F28/F30/F40：残肢触感/乳房/骨盆/空管/髋离断比喻
    - types/{type}.md#身体细节
  写到亲密关系:
    - topics/intimacy.md
    - core/voice.md                  # 亲密戏用词与回避方式仍按声音卡，不能换一个人
    - topics/fetish.md               # 恋物素材 F5/F7/F11/F12/F13/F15/F23/F31/F33/F34/F38/F39：残肢互动/性工具/人偶化/踩踏
    - topics/intimacy-explicit.md    # 条件注入：账本 亲密尺度档 = B 或 C 时唯一执行层
    - topics/intimacy-genre.md       # 条件注入（B/C 档）：四题材 × 六栏
  写到亲密关系·C 成人档:
    - topics/intimacy-explicit.md    # 全量注入；须用户显式声明 C
    - topics/intimacy-genre.md
  写到W视角: [topics/wannabe.md]
  写到对抗/冲突场景: [topics/conflict-scenes.md]
  写到战斗/追逐/围堵: [topics/combat-mechanics.md, topics/conflict-scenes.md]
  写到超自然战斗(高武/高魔/神话):
    - topics/combat-magic.md         # 条件注入：档位 E1–E3／A·B 两组红线／六类豁免／M01–M08
    - genre/fantasy.md               # 幻想向战斗章必读：第十节受限豁免／第十一节真实战斗冲突（R-032/R-033 唯一权威）
    # ⚠ 现实向、古装低武、无超自然能力的末世战斗章整节不读，仍过 K01–K13
  写到受限场景: [topics/limitation-scenes.md]
  写到节奏/张力场景: [core/pacing.md]
  写到文风/氛围/跨章一致性: [core/prose-craft.md, core/style.md]
  短篇/单章(计划章数≤10): [core/short-form.md]
  题材适配: [genre/realistic.md, genre/fantasy.md, genre/postapocalyptic.md, genre/historical.md]
  产出模板:
    - templates/voice-card.md
    - templates/chapter-contract.md
    - templates/character-card.md
    - templates/outline.md
    - templates/chapter-outline.md
    - templates/state-ledger.yaml
    - templates/ledger-schema.json
  审读时点(初稿之后才读):
    - templates/chapter.md           # 必过 12 组 + 文学自评 4 问 + 比对表
    - core/cold-review.md            # 读感七问 + 必判 13 维（定义共 22 维）
    - templates/reviewer-brief.md
    - templates/redteam-brief.md
  架构层(维护期):
    - rules/rules.yaml
    - rules/hard-layer.md
    - MAINTENANCE.md
    - PLATFORM-CN.md
    - host-hooks.yaml
    - scripts/compile_rules.py
    - scripts/query_rules.py
    - scripts/state_machine.py
    - scripts/validate_output.py
    - scripts/install-host-hooks.py
    - scripts/gatecheck.py
    - scripts/ledger_lint.py
    - scripts/optimize_prompts.py
    - scripts/selfcheck.py
    - scripts/verify.py
    - eval/eval-set.yaml
  章末必过审查:                        # G01–G12；执行清单见 templates/chapter.md
    G01_严重错误六类: SKILL.md#三、严重错误分级              # S18–S23
    G02_回避与边界: core/audience.md#★器具损耗与更换禁令        # S17、S32–S34、S40
    G03_动作与移动可行性: core/physio-audit.md                  # S25–S31；类型禁止项见 types/{type}.md#不可能动作
    G04_幻肢档位: topics/timeline.md                            # S35、S36
    G05_招牌元素限频: core/audience.md#★招牌元素密度与疲劳控制   # S37、S38
    G06_受限供给: core/audience.md#★受限清单                    # S14–S16
    G07_剧情结构: core/chapter-planning.md#一、章八要素          # S01–S04、S06–S08、S13
    G08_章末钩子与张力: core/chapter-planning.md#五、章末钩子类型库  # S05、S09–S12
    G09_大纲溯源与开篇: templates/outline.md#★主题材契约         # S24、S39
    G10_人声与语气: core/voice.md#十一、自查三问（每章写完必答，写进章末自评）  # S50 · 声口可辨
    G11_文笔形状: core/style.md#标点与句式三禁（叙述层）         # S41–S43、S46
    G12_交付手续: core/workflow.md#一、执行完整性硬卡口        # S44–S49
  新规审查落点（挂既有组与维度，不新增 S／G／维度编号）:
    - R-032 / R-033: genre/fantasy.md     # 章末 G01/G02/G07/G08、冷读 6/9/13/19/21、机检 [30][31]、双简报第三节
    - R-034: core/character-setup.md      # 章末 G10、冷读读感问 4、机检 [31]、双简报第三节
  推荐流程:
    - core/workflow.md#八、状态核查流水账
    - core/cold-review.md
```

