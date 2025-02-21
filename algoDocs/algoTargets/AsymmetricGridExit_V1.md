**目标值名称**：AsymmetricGridExit
**版本**：V1

**目标值概述**：
本目标值构建非对称网格退出机制，在盈利方向设置多级逐步止盈位，在亏损方向设置单一严格止损位。采用斐波那契回撤比率构建网格层级，结合短期价格动能动态调整网格密度。预期在趋势行情中捕获多段利润，在震荡行情中控制下行风险。

**设计模式**：
- 模式选择：无状态
- 选择原因：单批次计算无需状态维护，满足最低延迟要求（≤0.05s），适合市价单即时成交场景

**入场确认**：
- 数据字段：price, recv_ts, direction
- 方案选择：固定价格方案(Maker)
- 确认入场：
  * 入场价格（entry_price）：取当前批次内最高买单价与最低卖单价的均值
    $entry\_price = \frac{max\_bid\_price + min\_ask\_price}{2}$
    （其中max_bid_price=entries[direction==1].price.max(), min_ask_price=entries[direction==-1].price.min()）
  * 入场时间（entry_timestamp）：首批次到达entry_price的成交时间
    $entry\_timestamp = min(entries[entries.price == entry\_price].recv\_ts)$

**特征提取**：
- 数据字段：price, recv_ts（需满足recv_ts ≥ entry_timestamp）
- 特征计算（当前批次）：
  * 斐波那契网格构建：
    $level\_1 = entry\_price \times (1 + fib\_ratio_1)$
    $level\_2 = entry\_price \times (1 + fib\_ratio_2)$
    $level\_3 = entry\_price \times (1 + fib\_ratio_3)$
    $stop\_loss = entry\_price \times (1 - stop\_loss\_ratio)$
    （fib_ratio_1=0.05, fib_ratio_2=0.08, fib_ratio_3=0.13为斐波那契扩展比率）
  * 价格穿越检测：
    $break\_up\_1 = any(price > level\_1)$
    $break\_up\_2 = any(price > level\_2)$
    $break\_up\_3 = any(price > level\_3)$
    $break\_down = any(price < stop\_loss)$

**目标值计算**：
- 数据字段：break_up_1, break_up_2, break_up_3, break_down
- 目标值生成：
  * 阶梯收益率计算：
    $target\_value = \begin{cases}
    1 + fib\_ratio_3 & \text{if } break\_up_3 \\
    1 + fib\_ratio_2 & \text{if } break\_up_2 \\
    1 + fib\_ratio_1 & \text{if } break\_up_1 \\
    1 - stop\_loss\_ratio & \text{if } break\_down \\
    \end{cases}$
  * 退出优先级：高价位突破优先于低价位止损

**参数说明**：
- fib_ratio_1（float,默认0.05）：对应23.6%斐波那契回撤的扩展比率
- fib_ratio_2（float,默认0.08）：对应38.2%斐波那契回撤的扩展比率
- fib_ratio_3（float,默认0.13）：对应61.8%斐波那契回撤的扩展比率
- stop_loss_ratio（float,默认0.10）：最大可容忍亏损比例

**使用说明**：
- 推送频率：0.05s（超高频场景）
- 应用场景：中低波动市场中的波段交易策略
- 注意事项：需同时挂出多档止盈限价单和止损单，当市场出现跳空缺口时可能存在滑点风险