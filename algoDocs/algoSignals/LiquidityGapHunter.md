**信号名称**：LiquidityGapHunter

**信号概述**：
本信号通过监测买卖价差的统计分布特征，结合生存分析中的故障时间预测模型，识别流动性突然枯竭前的预警信号。基于cox比例风险模型构建动态风险评分，当市场流动性处于临界状态时提前发出警示。适用于防范黑天鹅事件引发的流动性真空，在极端行情中保护头寸。

**设计模式**：
- 模式选择：有状态
- 选择原因：
  * 需要维护5分钟级别的价差分布特征
  * 生存分析需累积足够统计样本
  * 突变检测依赖时序模式识别

**特征提取**：
- 数据字段：
  * `price`, `recv_ts`, `amount`
- 特征计算：
  * 当前批次特征：
    - `middle_price` = (max(`price`[bid]) + min(`price`[ask]))/2
    - `bid_ask_spread` = (min(`price`[ask]) - max(`price`[bid])) / `middle_price`
  * 历史特征窗口：
    - `spread_deque` = collections.deque(maxlen=30) // 保留30期价差（对应30分钟）
    - 异步更新线程处理窗口：每次推送后将`bid_ask_spread`加入队列
    - 维护滑动生存时间索引：`time_index` = [0.01,0.02,...,30.0] // 带时间戳的观测序列
- 复杂度分析：
  * O(n)特征计算 + O(k²)生存模型计算（k=窗口长度）
  * 通过异步更新将计算延迟降低35%

**信号计算**：
- 计算特点：
  * 实时计算线程与特征更新线程分离
  * 基于部分似然的近似快速解法
- 信号生成： 
  * 标准化特征值：
    `spread_z` = (`bid_ask_spread` - mean(`spread_deque`)) / std(`spread_deque`)
  * 动态风险函数：
    `hazard_ratio` = exp(0.5 * `spread_z` + 0.3 * lag(`spread_z`))
  * 生存曲线计算：
    `baseline_survival` = exp(-0.01 * `time_index`**1.5)
    `survival_prob` = `baseline_survival` ** `hazard_ratio`
  * 突变条件：
    if gradient(`survival_prob`) < -3 * ewma(gradient(`survival_prob`)):
        trigger = SHORT_SIGNAL
    elif 风险衰减加速：
        trigger = LIQUIDITY_WARNING

**参数说明**：
- 阈值参数：
  * `risk_multiplier` = dynamic(1.8σ~2.5σ) 根据vol_regime动态调整
  * `survival_decay` = 0.95±0.03 需与市场波动率负相关
  * `critical_gradient` = [-5.0, -3.0] 分位数阈值区间
- 模式参数：
  * `maxlen` ∈ [20,50] 分钟粒度可调窗口
  * 异步更新延迟容忍度=10ms
- 调优建议：
  * 使用C-index指标评估模型判别力
  * 通过网格搜索优化exp()内的系数权重

**使用说明**：
- 推送频率：1分钟级别
- 应用场景：
  * 指数期货与现货市场联动监控
  * 跨交易所流动性套利保护
  * 大宗交易市场冲击预警
- 注意事项：
  * 需配合L1/L2数据交叉验证
  * 建议与`VolatilityClustering`信号组合使用
  * 每8小时做一次窗口重置防止记忆效应