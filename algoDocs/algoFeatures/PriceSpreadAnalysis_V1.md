**因子名称**：PriceSpreadAnalysis
**版本**：V1

**因子概述**：
PriceSpreadAnalysis因子用于分析市场价差（Spread）的变化情况，旨在识别市场价格异常和潜在的套利机会。该因子基于价差均值回归理论，通过维护一个滑动窗口内的价差序列，计算当前价差与历史均值的偏差，并进行标准化处理。适用于中频交易场景（5min-1h），帮助捕捉市场的异常价差波动。

---

**设计模式**：
- **模式选择**：有状态
- **选择原因**：
  - 依赖历史价差数据进行统计分析，需要维护一个滑动窗口。
  - 实时性要求适中，适用于中频交易场景。
  - 通过滑动窗口机制，保证计算复杂度可控（O(n)）。

---

**特征提取**：
- **数据字段**：
  - price：成交价格
  - amount：成交数量
  - direction：买卖方向

- **特征计算（当前批次）**：
  - **当前批次特征**：
    1. 计算当前批次内的最高价格（price_high）和最低价格（price_low）。
    2. 计算当前批次的价差：Spread = price_high - price_low。
  - **状态变量更新**：无
  - **历史特征窗口**：
    - 使用`collections.deque`维护一个滑动窗口，记录近期价差序列。
    - 窗口大小：maxlen = ⌈窗口时长/推送频率⌉（例如，1分钟推送频率下，窗口时长为30分钟，maxlen=30）。
    - 维护方式：每次计算当前批次价差后，将其加入窗口，同时移除最早的价差数据。

- **复杂度分析**：
  - 当前批次特征计算：O(n)，n为当前批次数据点数。
  - 滑动窗口维护：O(1)，使用`deque`实现高效更新。

---

**因子计算**：
- **计算特点**：
  - 基于历史价差窗口的统计分析，计算延迟适中。
  - 计算开销主要来自滑动窗口的历史数据维护。

- **因子生成**：
  - **特征组合使用说明**：
    1. 计算滑动窗口内价差的历史均值（mean_spread）和标准差（std_spread）。
    2. 计算当前价差与历史均值的标准化偏差：Z-Score = (Spread - mean_spread) / std_spread。
    3. 将Z-Score作为因子值。
  - **归一化处理**：通过Z-Score标准化，将因子值转换为标准正态分布。

---

**参数说明**：
- **阈值参数**：
  - 窗口时长（window_duration）：滑动窗口的时间长度，默认30分钟。
  - Z-Score阈值（z_threshold）：用于判断价差是否异常，默认2.0（表示价差超过2倍标准差时为异常）。
- **模式参数**：
  - maxlen：滑动窗口的最大长度，由窗口时长和推送频率决定。
- **调优建议**：
  - 根据市场波动性调整窗口时长：波动性较高时，适当缩短窗口时长以捕捉短期变化；波动性较低时，延长窗口时长以平滑噪声。
  - 根据策略需求调整Z-Score阈值：更保守的策略可使用较低阈值（如1.5），更激进的策略可使用较高阈值（如2.5）。

---

**使用说明**：
- **推送频率**：1分钟（适用于中频交易场景）。
- **应用场景**：
  - 价差异常检测：识别市场中的异常价差波动。
  - 套利机会捕捉：通过对比不同交易对的价差特征，寻找潜在套利机会。
- **注意事项**：
  - 因子依赖于历史价差数据的稳定性，在极端市场条件下可能出现误判。
  - 滑动窗口大小需根据市场特性和策略需求进行调整，过小可能导致噪声敏感，过大可能导致反应滞后。