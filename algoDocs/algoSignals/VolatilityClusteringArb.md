**信号名称**：VolatilityClusteringArb

**信号概述**：
本信号基于波动率聚集效应和市场过度反应理论设计。通过维护15分钟价格波动率特征窗口，识别短期波动率突破长期波动通道的异常状态。当波动率偏离超过统计合理范围时触发逆向交易，捕捉波动均值回归的收益机会。融合GARCH模型思想优化条件判断，预期在低流动性时段获得显著alpha。

**设计模式**：
- 模式选择：有状态
- 选择原因：
  * 需要维护60分钟窗口的历史波动率统计量
  * 涉及多时间尺度波动特征联合计算
  * 统计套利策略要求建立合理基准波动区间

**特征提取**：
- 数据字段：`price`, `amount`
- 特征计算：
  * 当前批次特征：
    - 计算单批次内价格对数收益率：`r_t = ln(price_t/price_{t-1})`
    - 批次短期波动率：`batch_vol = std(r_t)`（取绝对值处理）
    - 当前VWAP：`current_vwap = sum(price*amount)/sum(amount)`
  * 历史特征窗口：
    - 短期波动率窗口：`numpy.ndarray`维护最近⌈900/推送间隔⌉个批次的`batch_vol`值，滚动更新
    - 长期统计窗口：
      * `long_term_mean_window`: 保存60分钟窗口的15分钟波动率均值，形状为(4,1)
      * `long_term_std_window`: 保存60分钟窗口的15分钟波动率标准差，形状为(4,1)
    - 窗口更新规则：每15分钟触发统计量重计算，移除最早时段的统计值
- 复杂度分析：
  * 批次特征计算：O(n) + O(1)滚动更新
  * 窗口操作：O(1)索引访问 + O(m)空间复杂度
  * 总体适合1分钟级低频场景

**信号计算**：
- 计算特点：
  * 使用滑动窗口批量更新替代逐笔更新
  * 增加波动率标准化处理
- 信号生成：
  * 波动通道计算：
    - 长期基准波动率：`ma_vol = numpy.median(long_term_mean_window)`
    - 波动离散度：`adaptive_width = numpy.percentile(long_term_std_window, 75)`
    - 动态通道上轨：`upper_band = ma_vol + channel_multiplier*adaptive_width`
    - 动态通道下轨：`lower_band = ma_vol - channel_multiplier*adaptive_width`
  * 触发策略：
    - 买入条件：
      1. `current_volatility < lower_band`
      2. `price_delta = (current_vwap - numpy.min(last_10_vwap)) / current_vwap`
      3. `price_delta > mean_reversion_threshold`
    - 卖出条件：
      1. `current_volatility > upper_band`
      2. `price_delta = (current_vwap - numpy.max(last_10_vwap)) / current_vwap`
      3. `price_delta < -mean_reversion_threshold`

**参数说明**：
- 核心参数：
  * `channel_multiplier`: 动态通道倍数（BTC/USDT: 2.0-3.0，传统资产: 1.5-2.0）
  * `mean_reversion_threshold`: 价格回归阈值（0.5%-1.2%）
- 优化参数：
  * `volatility_lookback`: 波动率观测窗口长度（默认900秒）
  * `price_confirm_window`: VWAP确认窗口（默认10周期）
- 调优建议：
  * 根据标的资产流动性调整阈值步长（流动性差的放大30%阈值）
  * 日内不同时段设置差异化参数（亚洲时段/欧美时段）

**使用说明**：
- 推送频率：1分钟（需确保时间戳精确对齐）
- 适用品种：
  * 加密货币：BTC/USDT, ETH/USDT等主流交易对
  * 传统资产：ES期货、外汇主要货币对
  * 跨市场：交易所间相同标的溢价套利
- 风险控制：
  * 必须配合波动率止损（跟踪波幅的2倍ATR止损）
  * 禁止在重大经济数据发布前后30分钟内使用
  * 单次交易最大回撤控制在0.5%以内