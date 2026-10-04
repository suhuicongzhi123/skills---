# 角色设定收集

> 类型无关。创作前期向用户收集以下信息（后期按需补充字段）。

## 收集流程
1. 向用户说明需要收集的设定项
2. 用户给出后，注入 `types/{type}.md` 建立生理事实基线
3. 缺项用合理默认值，并告知用户默认
4. 设定确认后进入大纲阶段

## 设定字段

```yaml
fields:
  截肢类型: hip-disarticulation | transfemoral | transtibial   # 默认 hip-disarticulation
  侧别: 左 | 右 | 双                                           # 默认 右
  截肢时间: 术前多少年 / 近期 / 先天                           # 默认 成年后数年
  年龄:
  性别:
  职业:
  性格:
  题材: realistic | fantasy                                    # 默认 realistic
  叙事视角: 第一人称 | 第三人称限知 | 第三人称全知            # 默认 第一人称（代入感强）
  是否含截肢过程: 是 | 否                                      # 默认 否（截肢后生活为主）
  devotee或W视角: devotee | wannabe | 双视角                  # 默认 devotee
  输出长度: 短篇 | 中篇 | 长篇 | 单章
```

## 默认值原则
- 代入感优先 → 默认第一人称
- 截肢后生活为主 → 默认不含截肢过程
- 髋离断为主 → 默认 hip-disarticulation