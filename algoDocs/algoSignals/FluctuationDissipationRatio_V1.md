**信号名称**：FluctuationDissipationRatio
**版本**：V1

**信号概述**：
本信号应用统计物理中的涨落耗散定理，将价格波动视为能量涨落，成交量视为能量耗散通路。当两者的动态平衡关系被打破时，市场进入非平衡状态，此时出现高概率的均值回归机会。理论依据是金融市场满足广义涨落耗散关系，参数异常反映流动性供给与价格波动的失衡。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  1. 需要持续估计波动率与成交量的动态关系
  2. 递推计算满足1秒级推送的实时性要求
  3. 固定状态变量降低内存消耗

**特征提取**：
- 数据字段：price, amount
- 特征计算（当前批次）：
  * 当前批次特征：
    - 波动幅度：$Δp = \max(price) - \min(price)$
    - 成交浓度：$C = \frac{\text{当前批次成交总量}}{\text{当前批次数据点数}}$
  * 状态变量更新：
    - 波动记忆：$EMA_Δp = α·Δp + (1-α)·EMA_Δp$
    - 量能基线：$EMA_C = α·C + (1-α)·EMA_C$
    - 波动偏离：$D_t = |Δp - EMA_Δp|$
    - 波动记忆更新：$EMA_D = α·D_t + (1-α)·EMA_D$
    - 标准差维护：$std_dev = \sqrt{EMA_D^2 - (EMA_D)^2}$

**信号计算**：
- 数据字段：Δp, C, EMA_Δp, EMA_C, std_dev
- 信号生成：
  * 特征组合：
    - 涨落耗散比：$FDRatio = \frac{Δp - EMA_Δp}{EMA_C}$
  * 归一化处理：
    - 标准化信号：$Signal = \frac{FDRatio}{std_dev + ε}$ （ε=1e-6防除零）

**方向判断**：
- 数据字段：Signal
- 交易方向生成：
  * 触发条件：
    - 做多：$Signal < -β·std_dev$ （超额耗散信号）
    - 做空：$Signal > β·std_dev$ （超额涨落信号）
    - β为波动率调整系数
  * 频率控制：
    - 冷却期：触发后冻结60秒
    - 阈值迟滞：触发后β自动提高20%
    - 状态重置：当EMA_C超过历史均值2σ时重置所有状态

**参数说明**：
- 阈值参数：
  - β=2.0（默认）：1.5-3.0可调，反映市场常态波动范围
  - α=0.05（对应半衰期≈13个周期）：控制状态变量的记忆强度
- 模式参数：
  - 冷却期长度=60s：匹配主力资金操作周期
  - 量纲保护系数ε=1e-6：维持数值稳定性

**使用说明**：
- 推送频率：1秒
- 应用场景：
  - 流动性充裕时的短期反转交易
  - 市场过热/过冷状态检测
  - 黑天鹅事件中的熔断预警
- 注意事项：
  - 需配合成交量分布过滤虚假信号
  - 极端行情下可能出现持续偏离
  - 建议与波动率通道类信号组合使用