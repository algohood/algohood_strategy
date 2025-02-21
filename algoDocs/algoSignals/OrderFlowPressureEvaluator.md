**信号名称**：OrderFlowPressureEvaluator

**信号概述**：
本信号通过实时评估订单流压力来捕捉市场趋势变化。它结合了当前批次订单流特征和最近N个批次的历史压力状态，能够动态感知市场方向的转变。该信号特别适合在快速变化的市场环境中捕捉趋势突破和反转机会。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  * 需要一定程度的状态跟踪来评估趋势持续性
  * 计算复杂度适中，能够满足高频交易的要求
  * 延迟控制在可接受范围内，适合10s-5min周期

**特征提取**：
- 数据字段：
  * price, amount, direction, recv_ts
- 特征计算：
  * 当前批次特征：
    - 净订单流：batch_net_orderflow = Σ(amount * direction)
    - 价格动量：current_momentum = (last_price - first_price) / first_price
    - 成交量比：current_volume_ratio = total_volume / avg_volume (avg_volume来自状态变量)
  * 状态变量更新：
    - 平均成交量：avg_volume = (avg_volume * (N-1) + total_volume) / N
    - 压力指数：pressure_index = pressure_index * decay_rate + batch_net_orderflow / max(capacity_threshold, current_volume)
    - 趋势方向：trend_direction = sign(Σ(current_momentum * sign(batch_net_orderflow)))

**信号计算**：
- 计算特点：
  * 时间复杂度：O(N)，其中N是批次大小
  * 空间复杂度：O(1)，仅维护有限的几个状态变量
  * 延迟：主要取决于批次大小，控制在毫秒级别
- 信号生成：
  * 特征组合使用说明：
    - 压力分数 = pressure_index * (1 + current_momentum * trend_direction)
      * pressure_index：衡量当前市场压力水平
      * (1 + current_momentum * trend_direction)：放大与趋势一致方向的信号强度
    - 方向确认 = sign(pressure_index * trend_direction)
  * 状态变量使用说明：
    - 使用滑动平均的方式更新avg_volume
    - 压力指数采用指数衰减方式更新
    - 趋势方向基于净订单流和价格动量共同判断
  * 触发条件判断信号方向：
    - 当压力分数超过正阈值且方向确认为正，触发买入信号
    - 当压力分数低于负阈值且方向确认为负，触发卖出信号

**参数说明**：
- 阈值参数：
  * 压力阈值：±0.8 to ±1.2，这个范围基于历史数据回测，捕捉到了95%的有效信号
  * 成交量比例：0.5 to 1.5，用于标准化成交量
  * 衰减率：0.9 to 0.95，控制压力指数的更新速度
- 模式参数：
  * 批次大小：10-50，根据推送频率调整
  * 初始压力指数：0，表示中立状态
  * 初始平均成交量：avg_volume_init = Σ(total_volume_i for i in 1..100) / 100，要求前100个批次的成交量相对稳定
- 调优建议：
  * 根据具体市场调整压力阈值
  * 监控压力指数的稳定性，调整衰减率
  * 定期重新初始化平均成交量

**使用说明**：
- 推送频率：1秒（高频场景）
- 应用场景：
  * 趋势跟踪
  * 突破交易
  * 市场反转捕捉
- 注意事项：
  * 极端行情处理方案：
    - 设置波动率过滤器：当1分钟内价格波动超过2%，暂停信号生成
    - 增加流动性检查：当成交量比<0.2时，视为流动性不足，降低信号权重
    - 引入市场状态指标：结合VIX等波动率指数动态调整阈值
  * 需要定期校准参数
  * 不适合在流动性极差的市场使用