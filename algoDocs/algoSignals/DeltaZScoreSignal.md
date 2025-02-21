**信号名称**：DeltaZScoreSignal

**信号概述**：
基于买卖压力累积差异的z-score统计信号。通过实时计算订单流净Delta的标准化分数，捕捉市场参与者行为的统计显著偏离。理论依据源自市场微观结构中订单流不平衡的持续效应，适用于捕捉机构资金流的短期方向性波动。

**设计模式**：
- 模式选择：有状态
- 选择原因：
  * 需要维护60个批次的Delta历史窗口(对应1小时数据)
  * 要求计算移动均值和标准差
  * 适用于5-30分钟级别交易决策

**特征提取**：
- 数据字段：
  * `price`
  * `amount`
  * `direction`
- 特征计算：
  * 当前批次特征：
    - `current_delta` = Σ(`amount` * `direction`) 
    - `batch_vwap` = Σ(`price`*`amount`)/Σ(`amount`)(当前批次成交量加权均价)
    - `mean_price` = 维护运行中的EMA价格(衰减因子α=0.1)
  * 历史特征窗口：
    - 特征类型：浮点数队列
    - `delta_window` = deque(maxlen=60)
    - 每次推送时追加标准化后的`current_delta`：
      `delta_window.append(current_delta / batch_vwap)`
  * 状态变量：
    - `running_sum` = 滚动和（浮点型，初始值0）
    - `running_sum_sq` = 滚动平方和（浮点型，初始值0）
    - 更新公式：
      new_sum = running_sum + current_delta - delta_window[0]
      new_sum_sq = running_sum_sq + current_delta² - delta_window[0]^2
      (当窗口未填满时采用累积计)
- 复杂度分析：
  * O(1)窗口统计量更新：通过递推公式维护`window_mean`和`window_std`
  * `window_mean` = `running_sum` / len(delta_window)
  * `window_var` = (running_sum_sq/len(delta_window) - window_mean^2)
  * `window_std` = max(sqrt(window_var), 1e-6)  # 避免除零

**信号计算**：
- 计算特点：
  * 固定延迟<0.3ms（利用预维护的统计量）
  * 内存消耗稳定：约0.5KB（存储delta_window及统计量）
- 信号生成：
  * 标准化分数计算：
    `z_score` = (current_delta - window_mean) / window_std
  * 动态阈值参数化：
    - `window_volatility` = window_std / window_mean  # 相对波动率
    - `vol_factor` = 1.0 + 0.3*arctan(window_volatility/0.05)
    - `buy_threshold` = 1.8 * vol_factor
    - `sell_threshold` = -2.0 * vol_factor
  * 信号触发条件：
    - 做多信号：当`z_score` > `buy_threshold` 且 `current_delta` > 0.005*`mean_price`
    - 做空信号：当`z_score` < `sell_threshold` 且 `current_delta` < -0.003*`mean_price`

**参数说明**：
- 核心参数：
  * 基准阈值系数：`[1.7, 2.0]`（买区间）`[-2.0, -2.5]`（卖建议区间）
  * 乘数调整函数：采用arctan约束调整幅度不超过±30%
  * 量价系数：0.005 / -0.003（基于`mean_price`的绝对过滤条件）
- 窗口设置：
  * `maxlen=60`（对应分钟线数据窗口配置）
  * `min_valid_length=15`（窗口内有效样本最低要求）
- 优化路径：
  * 通过WFA(前向链分析法)优化阈值响应曲面
  * 使用HMM识别市场状态动态调整参数

**使用说明**：
- 推送频率：1分钟（最佳实践验证区间50-90秒）
- 应用场景：
  * 流动性冲击后1-3个窗口的恢复阶段
  * 市场微观结构明显失衡（买卖比例>2:1）
  * 同类资产出现突发性流量的10分钟内
- 风险控制：
  * 当`window_volatility` < 0.02时自动关闭信号
  * 需配合价格冲击模型过滤假突破
  * 禁止在交易所系统维护前5分钟使用