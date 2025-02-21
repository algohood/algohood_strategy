**信号名称**：CointegrationZscore
**版本**：V1

**信号概述**：
本信号基于协整关系的统计套利策略，适用于具有长期均衡关系的资产对（ETH/BTC）。通过在线维护价格比率窗口，实时计算线性回归残差的标准化分数（Z-score）。当Z-score超过理论阈值时，认为价差出现统计异常，触发对冲交易。信号兼具统计套利的严谨性和在线更新的实时性。

**设计模式**：
- 模式选择：有状态
- 选择原因：
  1. 需要维护500周期价格比窗口进行协整分析
  2. 允许每分钟级别的在线更新复杂度
  3. 持仓周期适合中频交易策略

**特征提取**：
- 数据字段：symbol字段关联"eth_btc"交易对
- 特征计算（当前批次）：
  * 价格比率：
```python
price_ratio = eth_price / btc_price
```
  * 历史特征窗口：
```python
from collections import deque
window = deque(maxlen=500)  # 假定推送频率为1min时对应8.3小时窗口
window.extend(price_ratio)
```

**信号计算**：
- 数据字段：window队列中的历史price_ratio
- 信号生成：
  1. 在线线性回归：
```python
# 时间序列作为自变量
n = len(window)
sum_x = n*(n-1)/2
sum_y = sum(window)
sum_xy = sum(i*y for i,y in enumerate(window))
beta = (n*sum_xy - sum_x*sum_y)/(n*sum_x**2 - sum_x**2)
alpha = (sum_y - beta*sum_x)/n

# 残差计算
residuals = [y - (alpha + beta*i) for i,y in enumerate(window)]
sigma = np.std(residuals)
z_score = (window[-1] - (alpha + beta*(n-1)))/sigma
```

  2. 归一化处理（指数衰减）：
```python
half_life = 3600  # 1小时半衰期
lambda_factor = 1 - np.exp(np.log(0.5)/half_life)
smoothed_z = lambda_factor*z_score + (1-lambda_factor)*prev_smoothed_z
```

**方向判断**：
- 数据字段：smoothed_z
- 交易方向生成：
  * 触发条件：
```python
buy_cond = smoothed_z < -2.0  # 价格比率低于均值2个标准差
sell_cond = smoothed_z > 2.0   # 价格比率高于均值2个标准差
```
  经济含义：95%置信区间外的波动可视为统计显著偏离
  * 频率控制：
```python
min_interval = 300  # 两次信号间隔≥5分钟
last_signal_ts = 0
if current_ts - last_signal_ts > min_interval:
    触发信号并更新last_signal_ts
```

**参数说明**：
- 窗口长度（window_size）：
  - 类型：int
  - 默认：500
  - 经济含义：覆盖约1个交易日的分钟级数据周期
- 标准差阈值（z_threshold）：
  - 类型：float
  - 默认：2.0
  - 经济含义：对应95%置信区间
- 半衰期（half_life）：
  - 类型：int
  - 默认：3600
  - 经济含义：平衡信号灵敏度和抗噪能力

**使用说明**：
- 推送频率：1分钟
- 应用场景：
  1. 加密货币市场ETH/BTC交易对
  2. 资产间存在稳定协整关系时段
  3. 市场未出现重大基本面冲击
- 注意事项：
  1. 需定期检验协整关系稳定性
  2. 重大市场事件期间停用
  3. 建议组合保证金率≥30%