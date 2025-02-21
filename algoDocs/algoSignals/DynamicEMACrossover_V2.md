**信号名称**：DynamicEMACrossover
**版本**：V2

**信号概述**：
在V1基础上增加异常值处理机制，提升系统鲁棒性。主要改进点：
1. 增加'vwap'极小值保护，避免除零风险
2. 新增成交量异常值过滤机制
3. 优化波动率计算公式稳定性
维持核心的成交量加权EMA交叉逻辑，适用于15秒到3分钟级别的趋势跟踪场景，预期捕获0.8%-1.5%价格波动。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  * 继续维护'fast_ema'、'slow_ema'状态变量
  * 新增'ts_std'状态变量用于动态标准差计算
  * 参数自适应机制仍保持增量计算特性

**特征提取**：
- 数据字段：'price'、'amount'、'direction'
- 特征计算：
  * 当前批次特征：
    + 'vwap' = max(Σ('price'*'amount')/Σ('amount'), 0.0001)
    + 'volatility' = ('max_price' - 'min_price')/abs('vwap') * √(max('total_ticks',1))
    + 'volume_bias' = clamp((Σ('amount' where 'direction'=1) - Σ('amount' where 'direction'=-1))/max(Σ('amount'),0.0001), -1.0, 1.0)
  * 状态变量更新：
    + 'fast_ema_window' = clamp(8 + 50*(1 - sigmoid('volatility'*100)), 5, 15)
    + 'slow_ema_window' = 2.5*'fast_ema_window'
    + 'fast_ema' = coeff_fast*'vwap' + (1 - coeff_fast)*'fast_ema_prev'
      (coeff_fast = 2/(1 + 'fast_ema_window'))
    + 'slow_ema' = coeff_slow*'vwap' + (1 - coeff_slow)*'slow_ema_prev'  
      (coeff_slow = 2/(1 + 'slow_ema_window'))
    + 'ts_std' = sqrt(exponential_ma('ts'^2, 50) - exponential_ma('ts',50)^2)
- 复杂度分析：
  * 新增3个保护函数(max/clamp/abs)额外增加O(1)开销
  * 总体仍保持O(n)线性复杂度

**信号计算**：
- 计算特点：
  * 新增波动率剪裁：'volatility' = clamp('volatility', 0.0001, 0.1)
  * 趋势强度'ts' = ('fast_ema' - 'slow_ema') / max('vwap'*0.0001, 0.000001)
  * 信号确认增加成交量验证：批次总成交量需>10*历史中位数
- 信号生成：
  * 交叉确认条件优化：连续3个批次的'ts'符号一致且|'ts'|>2*'ts_std'
  * 新增成交量异常过滤：当批次方差>5倍移动方差时跳过信号生成

**参数说明**：
- 新增保护参数：
  * 'vwap'最小值保护0.0001
  * 'volatility'范围限制[0.0001, 0.1] 
  * 'volume_bias'强制归一化[-1,1]
- 调优建议：
  * 市况平稳时适当放宽'volatility'上限
  * 可通过调整sigmoid系数改变参数灵敏度

**使用说明**：
- 推送频率：保持1秒最佳
- 新增风险控制：
  * 实时监测'vwap'有效性标记
  * 当连续3批次无法计算有效信号时触发风控
  * 建议设置最大单次亏损0.5%的止损机制
- 注意事项：
  * 新加入的clamp函数可能影响极端行情响应速度
  * 需定期校准sigmoid函数参数适应市场变迁