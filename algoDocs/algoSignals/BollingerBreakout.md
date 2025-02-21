信号名称：BollingerBreakout  
信号概述：该信号基于布林带上下轨的突破行为，结合历史波动率判断趋势延续或反转。通过分析价格在布林带外的停留时间和波动性，捕捉市场突破机会。适用于中频交易场景，特点是稳健性强，能有效过滤噪音。

设计模式：
- 模式选择：有状态
- 选择原因：需要维护历史价格和波动率数据，适合中频交易场景，延迟和复杂度在允许范围内。

数据字段：
- price: 成交价格
- amount: 成交数量
- recv_ts: 接收时间戳

特征提取：
- 当前批次特征：
  * 当前价格加权均值：current_batch_mean_price = sum(price * amount) / sum(amount)
  * 当前价格加权标准差：current_batch_std_price = sqrt(sum((price - current_batch_mean_price)^2 * amount) / sum(amount))
- 历史特征窗口：
  * 窗口结构：collections.deque，maxlen = ceil(窗口时长 / 推送频率)
    - 推送频率为1min时，窗口时长为20min，maxlen = 20
    - 推送频率为5min时，窗口时长为100min，maxlen = 20
    - 推送频率为10min时，窗口时长为200min，maxlen = 20
    - 说明：窗口时长固定为20个单位时间（20min、100min、200min等），maxlen根据推送频率动态调整。
  * 维护方式：deque中存储完整的特征值（包括current_batch_mean_price和current_batch_std_price）。每次新批次数据到来时，计算current_batch_mean_price和current_batch_std_price，并将元组(current_batch_mean_price, current_batch_std_price)加入deque。旧数据会自动移除。
  * 布林带计算：
    - 中轨（MA）：ma = sum([x[0] for x in deque]) / len(deque)
    - 上轨（UB）：ub = ma + 2 * sum([x[1] for x in deque]) / len(deque)
    - 下轨（LB）：lb = ma - 2 * sum([x[1] for x in deque]) / len(deque)

信号计算：
- 计算特点：基于历史价格窗口分析，复杂度较高，但延迟在可接受范围内。
- 信号生成：
  * 特征组合使用说明：
    - 判断当前价格是否突破上轨或下轨：is_breakout = (current_batch_mean_price > ub) or (current_batch_mean_price < lb)
    - 突破持续时间更新规则：
      * 每次新批次数据到来时，若is_breakout为True，duration += 1；否则，duration = 0
    - 结合波动率判断信号方向：
      * 波动率计算：volatility = sum([x[1] for x in deque]) / len(deque)
      * 波动率阈值：threshold_volatility = 动态波动率均值 * 0.5
        - 动态波动率均值：根据历史波动率的滚动均值计算，窗口大小与deque相同
        - 根据市场波动性动态调整，默认系数为0.5，可根据策略表现优化
      * 信号方向判断：
        * 若current_batch_mean_price > ub且duration >= 2且volatility > threshold_volatility则生成买入信号
        * 若current_batch_mean_price < lb且duration >= 2且volatility > threshold_volatility则生成卖出信号
  * 触发条件判断信号方向：
    - 买入信号：当前价格持续突破上轨且波动率较高
    - 卖出信号：当前价格持续突破下轨且波动率较高

参数说明：
- 布林带参数：n=20（窗口大小），k=2（标准差倍数）
- 突破持续时间阈值：duration >= 2（持续2个单位时间突破）
- 波动率阈值：threshold_volatility = 动态波动率均值 * 0.5
  * 调优建议：根据市场波动性优化默认系数（0.5），或采用自适应机制动态调整
- 调优建议：根据市场波动性调整n、k和threshold_volatility，优化突破持续时间阈值。

使用说明：
- 推送频率：1min（推荐），5min，10min
- 应用场景：中频交易（5min-1h），适合趋势跟踪和突破交易
- 注意事项：在高波动性市场中可能出现假突破，需结合其他指标过滤信号。