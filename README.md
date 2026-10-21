# novel-amputee-writing 技能包

面向慕残者（devotee/wannabe）群体的截肢者题材小说写作技能。

## 版本

| 分支 | tag | 状态 |
|------|-----|------|
| `main` | `v4.5.1` | 稳定版（默认） |
| `preview` | `v4.8.4` | 测试版 |
| `v4.9.0` | `v4.9.1` | 三方审查修复 + 生成侧补强 + 受限归因判据（独立分支，未合并） |

### 安装

稳定版（默认）：
```bash
git clone https://github.com/suhuicongzhi123/skills---.git
```

测试版：
```bash
git clone -b preview https://github.com/suhuicongzhi123/skills---.git
```

v4.9.x（三方审查修复版）：
```bash
git clone -b v4.9.0 https://github.com/suhuicongzhi123/skills---.git
```

指定版本（clone 后）：
```bash
git checkout v4.9.1   # 或 v4.9.0 / v4.8.4 / v4.5.1
```

## v4.9.x 版本说明

### v4.9.1 · 受限归因判据（实测反馈修复）

v4.8.4 实测样本暴露的规则空白：受限被写成「力量性归因」（单腿力气不够），
滑向残弱叙事。本版补上「防写弱」方向：

- `topics/limitation-scenes.md` 新增「四-补、受限归因判据」：力量性 ❌ / 结构性 ✅
  对照表（支撑面/支点/合力/力矩/长度五选一）+ 快速自检钩子
- 写法模板新增「处置探索深度」：放弃前至少两轮不同策略，归因不落力量极限，
  同一放弃点题最多一次
- `core/physio-audit.md` 新增「反向违规：力量弱化」——与「不可能动作」
  互为反向的稽查维度

### v4.9.0 · 三方审查修复与生成侧补强

v4.8.4 经「机械审查 + 流程冷读 + 内容冷读」三方独立审查后的修复与补强版本，
在独立分支发布（不影响 preview 的 v4.8.4）：

- **P0 修复**：创作流程阶段顺序对撞、孤儿文件 equipment-risk.md 删除（含废止口径清除）、
  单手文件下肢模型混入、腕离断夹持解剖错误
- **口径闭环**：钩子轮转统一、招牌元素键名全称、章六要素补第六槽位、密度数值自洽、
  亲密尺度档收集字段
- **冗余瘦身**：elbow-wrist 双写删除、幻肢机制链归一（权威在 timeline.md）、
  触发三件套去互抄、SKILL.md 常驻瘦身约 30 行
- **生成侧补强**：平庸 vs 心动对照范例（7 类）、代入感通道库、性格生成轴、
  turn 三条生成路径、受限第六类「环境与他者」、沐浴与更衣专项、
  体位与接触按类型素材、空鞋意象、独门技巧库
- **工具升级**：selfcheck.py 新增悬空引用/孤儿文件检测，废止词表更新，覆盖 .yaml

详见 `novel-amputee-writing/CHANGELOG.md`。

## 技能说明

详见 `novel-amputee-writing/SKILL.md`。