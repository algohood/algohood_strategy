**信号名称**：HFTMomentumSurge
**版本**：V1

**信号概述**：
本信号通过捕捉超高频场景下价格动量与成交量冲击的复合效应，识别闪电行情启动特征。基于市场微观结构理论中的信息扩散模型，当短时价格变化率与成交量异常同时出现时，预示知情交易者活动导致的趋势延续。预期在0.05秒窗口内捕捉5-10个基点的瞬时机会。

**设计模式**：
- 模式选择：无状态
- 选择原因：交易窗口极短（<0.05s），需要最低延迟响应；数据特征批内自洽，无需跨批次计算；符合超高频场景最低复杂度要求

**特征提取**：
- 数据字段：recv_ts, price, amount, direction
- 特征计算（当前批次）：
  * 特征1（短时动量）：
    $$
    delta\_price = (batch[-1].price - batch[0].price)/batch[0].price
    $$
    $$
    time\_window = batch[-1].recv_ts - batch[0].recv_ts
    $$
    $$
    momentum\_value = delta\_price / (time\_window + 0.001)
    $$

  * 特征2（成交量冲击）：
    $$
    buy\_amount = sum(t.amount for t in batch if t.direction == 1)
    $$
    $$
    total\_amount = sum(t.amount for t in batch)
    $$
    $$
    impact\_ratio = (buy_amount - (total_amount - buy_amount)) / total_amount
    $$

**信号计算**：
- 数据字段：momentum_value, impact_ratio
- 信号生成：
  * 特征组合：
    $$
    raw\_signal = momentum\_value \times impact\_ratio
    $$
  * 归一化处理（直接更新）：
    $$
    normalized\_signal = raw_signal / (EMA(raw_signal, 5) + 0.0001)
    $$

**方向判断**：
- 数据字段：normalized_signal
- 交易方向生成：
  * 触发条件（满足任意一条）：
    $$
    Case1: normalized_signal > Q_{80}(short_term\_momentum) \ 且 \ impact_ratio > Q_{75}(buy_impact) \Rightarrow LONG
    $$
    $$
    Case2: normalized_signal < Q_{20}(short_term\_momentum) \ 且 \ impact_ratio < Q_{25}(buy_impact) \Rightarrow SHORT
    $$

  * 频率控制：
    - 使用1秒冷却期（同一方向信号间隔不低于1秒）
    - 并行监测订单薄瞬时流动性（卖一/买一深度比>2时抑制SHORT信号）

**参数说明**：
- Q_{80}/Q_{20}: 短时动量分位数阈值（动态计算周期=5秒，默认n=100）
- Q_{75}/Q_{25}: 买方冲击分位数阈值（动态计算周期=3秒，默认n=60）
- 冷却期：固定值1秒（bool型参数，可开启/关闭）

**使用说明**：
- 推送频率：0.05秒
- 应用场景：
  1. 重大消息发布前流动行收缩期
  2. 主力合约突然放量突破阶段
  3. 跨交易所价差急速收敛初期

- 注意事项：
  1. 市场波动率＞5%时需降低仓位
  2. 执行延迟＞0.01秒时失效
  3. 现货与期货市场需采用不同参数模板