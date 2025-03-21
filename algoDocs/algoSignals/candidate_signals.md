**候选方案1**
- 信号名称：OrderFlowImbalanceDetector
- 信号模式：无状态
- 核心逻辑：计算当前批次成交量净差与总量比，超过阈值即触发信号
- 适用场景：高频做市（0.05s级推送）
- 主要特点：
  * 实时计算买卖单量失衡程度
  * 配合价格变化验证有效性
  * 采用动态校准的阈值参数

**候选方案2**
- 信号名称：VolatilitySurgeCapture
- 信号模式：无状态
- 核心逻辑：基于当前批次价差计算波动率异常百分位
- 适用场景：突发行情捕捉（1s级推送）
- 主要特点：
  * 使用极差法计算瞬时波动率
  * 异常值检测采用分位数机制
  * 波动率回归跟踪机制

**候选方案3**
- 信号名称：DynamicSpreadArbitrage
- 信号模式：半无状态
- 核心逻辑：跟踪动态价差基线，捕捉偏离交易机会
- 适用场景：跨期套利（1min推送）
- 主要特点：
  * 维护动态价差基线EMA
  * 偏差计算结合标准差通道
  * 自适应的基线更新机制

**候选方案4**
- 信号名称：HMMStateDetector
- 信号模式：有状态
- 核心逻辑：隐式马尔可夫模型识别市场状态迁移
- 适用场景：状态转换交易（1min推送）
- 主要特点：
  * 三状态模型（横盘/上升/下降）
  * 基于成交量特征构建观测序列
  * 状态转移概率动态更新

**候选方案5**
- 信号名称：LiquidityVortex
- 信号模式：有状态
- 核心逻辑：流动性漩涡效应跟踪多维度指标
- 适用场景：大宗交易预测（10min推送）
- 主要特点：
  * 结合交易深度变化速率
  * 量价分布偏离度检测
  * 市场冲击成本预测模型