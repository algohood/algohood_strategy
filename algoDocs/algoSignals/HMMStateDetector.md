**信号名称**：HMMStateDetector

**信号概述**：
隐式马尔可夫模型检测市场状态迁移，通过观测成交量相关特征构建的观测序列，识别市场处于{quiet_state}|{uptrend_state}|{downtrend_state}三种潜在状态。基于Baum-Welch算法动态更新状态转移概率矩阵，捕捉市场微观结构变化。适用于通过状态转换概率触发趋势跟随或反转策略。

**设计模式**：
- 模式选择：有状态
- 选择原因：
  * 需保留{window_length}=30分钟窗口的特征序列用于模型训练
  * 参数更新需依赖前序计算结果
  * {push_freq}=1min级推送满足模型计算时间要求

**特征提取**：
- 数据字段：amount, direction
- 特征计算：
  * 当前批次特征：
    - 方向加权成交量：{dir_weighted_volume} = sum(amount * direction)
    - 标准化成交量比率：{volume_ratio} = [sum(amount*(direction>0)) - sum(amount*(direction<0))] / sum(amount)
  * 历史特征窗口：
    - 窗口特征：[{normalized_vw}, {normalized_vr}]（使用窗口内滚动统计量进行z-score标准化）
    - 计算公式：
      * {window_mean} = mean(deque)
      * {window_std} = std(deque)
      * {normalized_value} = (current_value - {window_mean}) / ({window_std} + 1e-6)
    - 窗口结构：collections.deque(maxlen={window_size}=30)
    - 维护方式：每批次计算标准化值后右端入队，每{model_refresh_interval}=10个批次触发统计量刷新
- 复杂度分析：
  * 窗口维护：O(1)入队操作
  * 模型训练：O(TN²)时间复杂度（T={window_size}, N={n_states}=3）

**信号计算**：
- 计算特点：
  * 模型更新触发条件：满足{min_refresh_interval}=10个批次或状态转移概率变化>0.2
  * 在线Viterbi解码时延：≤80ms（满足1min级推送要求）
- 信号生成：
  * {consecutive_up_signals} = N：当Viterbi路径连续{threshold_consecutive}=3个{uptrend_state}
  * 出现{double_top_divergence}：当价格新高但{volume_ratio}下降>15%
  * 状态震荡判定：{state_stability} = ∑diag({transition_matrix}) <1.8时触发对冲
  * 确认条件：前向概率差{forward_backward_diff}=|α-β| >{prob_diff_threshold}=0.4

**参数说明**：
- 核心参数：
  * {n_states}=3（隐藏状态数，对应市场三种基本状态）
  * {n_observations}=2（观测特征维度）
  * {state_mapping} = {0:"横盘", 1:"上升", 2:"下降"}
- 动态阈值：
  * {state_transition_threshold}=主对角线元素<0.6触发警报
  * {model_retrain_condition}=σ(α)/μ(α)>{cv_threshold}=0.5
- 调优建议：
  * 通过{BIC_criteria}评估{n_states}合理性
  * {window_size}应>{state_duration}×3（典型状态持续周期）
  * {prob_diff_threshold}根据夏普率动态调整

**使用说明**：
- 推送频率：{recommended_freq}=1min（需处理延迟<100ms）
- 预热要求：最小{init_samples}=30个批次初始化数据
- 应用场景：
  * 日内{trading_phase}="趋势中继"阶段的仓位调整
  * 捕捉{price_action}与{volume_signals}的背离
  * {risk_control}场景的状态异常预警
- 注意事项：
  * 规避{low_liquidity_period}=UTC 0:00-2:00时段
  * 配合{filters}=夏普率>{sharpe_threshold}=2使用
  * 需要{gpu_acceleration}提升Viterbi解码速度