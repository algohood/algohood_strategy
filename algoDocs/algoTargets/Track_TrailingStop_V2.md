**目标值名称**：跟踪止盈延迟止损
**版本**：V2

**目标值概述**：
本目标值设计用于在价格趋势中动态跟踪止盈，以及在价格回撤时延迟止损。该目标值结合了趋势跟踪和延迟止损的逻辑，旨在捕捉趋势中的收益机会，同时避免因短期波动导致的过早止损。通过设置回撤百分比和延迟时间参数，该目标值能够在不同市场环境下灵活应用，提升交易策略的稳定性和收益风险比。

**设计模式**：
- 模式选择：半无状态
- 选择原因：由于需要维护趋势状态和延迟时间，半无状态模式能够满足实时性要求，同时保持较低的计算复杂度。

**入场确认**：
- 方案选择：执行价格方案（Taker）
- 入场价格确认：
  * 计算方法：基于最近N笔成交的VWAP计算入场价格。VWAP（Volume Weighted Average Price）计算公式为：
    \[
    \text{VWAP} = \frac{\sum_{i=1}^{N} (\text{price}_i \times \text{amount}_i)}{\sum_{i=1}^{N} \text{amount}_i}
    \]
    其中，\(\text{price}_i\)和\(\text{amount}_i\)分别为第i笔成交的价格和数量。
  * 确认流程：在获取到entry_timestamp时，立即计算并确认入场价格。
- 入场时间确认：
  * 记录方法：记录入场确认时的系统时间戳。entry_timestamp为确认入场价格时的时间戳。
  * 确认流程：在入场价格确认成功后，记录当前时间戳作为entry_timestamp。
- 返回结果：
  * 确认成功：{entry_price, entry_timestamp}
  * 确认失败：{target_name: None}

**特征提取**：
- 数据字段：price, amount, direction, recv_ts
- 特征计算（当前批次）：
  * 当前批次特征：计算当前批次内的最高价、最低价和平均价格。
  * 状态变量更新：维护历史最高价和最低价，并在每个批次中更新。
  * 历史特征窗口：无
- 复杂度分析：计算复杂度为O(n)，能够在实时性要求下高效完成。

**目标值计算**：
- 计算特点：低延迟，适合高频交易场景。
- 目标值生成：
  * 特征组合使用说明：基于当前价格和历史最高价计算回撤百分比，判断是否触发止盈；基于当前价格和历史最低价，判断是否达到止损条件。
    - 回撤百分比计算公式为：
      \[
      \text{回撤百分比} = \frac{\text{历史最高价} - \text{当前价格}}{\text{历史最高价}} \times 100\%
      \]
    - 延迟时间判断：如果当前价格低于止损价格且从确认入场时间开始已经过了预设的延迟时间N秒，则触发止损。
  * 状态变量使用说明：使用状态变量记录历史最高价和最低价，并在每个批次中更新。
  * 计算逻辑：如果当前价格回撤超过预设百分比（如回撤x%），则触发止盈；如果当前价格低于止损价格且延迟时间已过，则触发止损。
  * 输出结果格式：{stop_loss: bool, take_profit: bool}，其中stop_loss和take_profit为布尔值，表示是否触发止损或止盈。

**参数说明**：
- 阈值参数：回撤百分比（x%），延迟时间（N秒）。
- 模式参数：无
- 调优建议：根据市场波动性调整回撤百分比和延迟时间，以提高策略的适应性和稳定性。

**使用说明**：
- 推送频率：1s
- 应用场景：适用于高频交易场景，捕捉短期趋势中的收益机会。
- 注意事项：在高波动市场中，需谨慎设置回撤百分比和延迟时间，以避免频繁触发止损。