**因子名称**: SpreadConvergenceMeasure
**版本**: V1

**因子概述**：
用于实时衡量买卖价差收敛效率，评估市场深度恢复能力的动态指标。基于Foucault订单簿动态模型，通过价格离散度变化速率分析市场自稳定能力。预期反映市场参与者主动修复流动性的意愿强度。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  * 延迟要求：需要维持当前价差状态但无需完整历史数据
  * 复杂度：通过EMA方式降低高频噪声影响
  * 适用性：适配1s-1min级别的高频策略需求

**特征提取**：
- 数据字段：
  * price：成交价格
  * amount：成交数量
  * direction：买卖方向
  
- 特征计算（当前批次）：
  1. 价差动态：
    当前批次最高成交价（MaxPrice）与最低成交价（MinPrice）之比的自然对数：
    \[ Spread_t = \ln(\frac{MaxPrice}{MinPrice}) \]
    
  2. 量能权重：
    当前批次成交量加权方向：
    \[ FlowWeight = \frac{\sum (amount \times direction)}{\sum amount} \]
    
- 状态变量更新：
  1. 指数移动平均价差（EMS_price）：
    \[ EMS_t = \alpha \times Spread_t + (1-\alpha) \times EMS_{t-1} \]
    其中\(\alpha = 0.2\)（衰减参数）
    
  2. Gamma调节参数：
    \[ Gamma = \beta \times |FlowWeight| \]
    其中\(\beta = 0.8\)（敏感度系数）

**因子计算**：
- 数据字段：
  * 当前批次Spread_t
  * 状态变量EMS_{t-1}
  * FlowWeight
  
- 因子生成：
  1. 基础指标：
    \[ RawFactor = \frac{Spread_t}{EMS_{t-1}} \times Gamma \]
    
  2. 归一化处理：
    采用指数衰减标准化：
    \[ Factor_{t} = \lambda \times RawFactor + (1-\lambda) \times Factor_{t-1} \]
    其中\(\lambda = 0.3\)（冲击衰减率）

**参数说明**：
- \(\alpha\)（EMA参数）：
  * 类型：float
  * 默认：0.2
  * 含义：窗口长度约5个周期，控制价差均值响应速度
  
- \(\beta\)（敏感系数）：
  * 类型：float
  * 默认：0.8
  * 含义：流动性方向对价差收敛的放大效应比率
  
- \(\lambda\)（冲击衰减）：
  * 类型：float
  * 默认：0.3
  * 含义：日内高频冲击的遗忘速率

**使用说明**：
- 推送频率：3-300秒最优（需保证单批次有3笔以上成交）
- 应用场景：
  1. 做市商动态价差调整
  2. 日内流动性风险预警
  3. 冲击成本实时监控
  
- 注意事项：
  1. 单笔大额交易可能造成短期信号失真
  2. 震荡行情需配合其他因子过滤
  3. 不宜直接用于10秒以下超高频策略