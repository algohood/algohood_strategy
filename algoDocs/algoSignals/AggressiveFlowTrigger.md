**信号名称**：AggressiveFlowTrigger

**信号概述**：
该信号捕捉订单流的短期激进买入行为。通过维护主动买单占比的累积指标及其极值统计，结合动态波动阈值判断买方资金流入异常。理论基础是市场微观结构中大单主动买入往往领先短期价格上涨，在1秒级别的推送频率下能捕捉资金集结特征。预期在趋势启动初期产生有效信号。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  * 需维护5秒窗口的累积队列和极值统计
  * 状态变量数量固定且更新规则明确
  * 在计算复杂度和时效性之间取得平衡

**特征提取**：
- 数据字段：amount, direction
- 特征计算：
  * 当前批次特征：
    - 主动买单量：buy_vol = sum(amount where direction==1)
    - 总成交量：total_vol = sum(amount)
    - 主动买单占比：buy_ratio = buy_vol / (total_vol + 1e-6)
  * 状态变量更新：
    - 累积值队列：ratio_deque = collections.deque(maxlen=5)
    - 极值统计：
      * 最大累积值：max_cumulative = max(ratio_deque) if len(ratio_deque)>0 else 0
      * 最小累积值：min_cumulative = min(ratio_deque) if len(ratio_deque)>0 else 0
    - 更新流程：
      1. 将当前buy_ratio压入ratio_deque（自动维护长度）
      2. 计算新累积值current_cum = sum(ratio_deque)
      3. 更新极值：
         - max_cumulative = max(current_cum, max_cumulative)
         - min_cumulative = min(current_cum, min_cumulative)
  * 历史特征窗口：无
- 复杂度分析：
  * 当前特征O(n)遍历计算
  * 极值更新O(1)
  * 队列操作O(1)

**信号计算**：
- 计算特点：状态变量内存占用量约64字节（5个float+2个float）
- 信号生成：
  * 动态阈值计算：
    - 基准值 = 0.5 * (max_cumulative + min_cumulative)
    - 波动带 = 1.5 * (max_cumulative - min_cumulative)
    - 买入阈值 = 基准值 + 0.3*波动带
  * 触发条件判断：
    - 多头信号：current_cum > 买入阈值 且 current_cum > 基准值
    - 空头信号：current_cum < (基准值 - 0.3*波动带) 且 current_cum < 基准值
    - 信号强度：与(current_cum - 基准值)/波动带成正比

**参数说明**：
- 极值更新机制：
  * 采用running max/min模式（永久记忆）
  * 可选重置条件：当(max_cumulative - min_cumulative)超过3倍ATR时重置历史极值
- 动态系数调整：
  * 基准系数：根据市场波动状态动态调整（牛市中增加空头敏感性）
  * 波动带系数：当市场处于趋势行情时降低至1.2，震荡行情提升至1.8
- 初始设置：
  * 前5个周期仅收集数据不产生信号
  * max_cumulative初始为负无穷
  * min_cumulative初始为正无穷

**使用说明**：
- 极值维护：需持久化保存max_cumulative和min_cumulative
- 特殊处理：
  * 当单批次数据缺失时，用前值buy_ratio填充队列
  * 极值统计遇到零成交时暂停更新
  * 遇到系统重启时从最近20个周期重新初始化极值