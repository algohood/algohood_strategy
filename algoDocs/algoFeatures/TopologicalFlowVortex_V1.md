**因子名称**: TopologicalFlowVortex
**版本**: V1

**因子概述**：
通过微分几何方法刻画订单流的三维时空曲率特征，揭示市场流动性场的奇异点形成机制。基于Khinchin流动性场论的拓扑分析框架，识别订单流中隐含的涡旋结构。预期有效捕捉高频交易环境下的流动性异常积聚现象。

**设计模式**：
- 模式选择：无状态
- 选择原因：
  * 基于单批次即时几何特征提取
  * 避免维护复杂状态变量产生的延迟
  * 满足超高频场景的实时计算需求

**特征提取**：
- 数据字段：
  * price：成交价格
  * amount：成交数量
  * direction：买卖方向
  * recv_ts：时间戳
  
- 特征计算（当前批次）：
  1. 订单流轨迹参数化：
    \[
    \begin{cases}
    t_i = \frac{recv_ts_i - min(recv_ts)}{max(recv_ts)-min(recv_ts)} \\
    x_i = (price_i - \mu_p)/\sigma_p \\
    y_i = amount_i \times direction_i \\
    z_i = log(\Delta t_i + \epsilon)
    \end{cases}
    \]
    其中\(\mu_p,\sigma_p\)为本批次价格均值和标准差
  
  2. 曲率张量计算：
    \[
    \Gamma_{ijk} = \frac{\partial^2 u_k}{\partial x_i \partial x_j} \quad \text{(采用三次样条插值求导)}
    \]
  
  3. 拓扑特征提取：
    * 高斯曲率：
      \[
      K = \frac{R_{1212}}{det(g)} 
      \]
    * 平均曲率：
      \[
      H = \frac{1}{2}trace(g^{-1}b)
      \]
    * 挠率测度：
      \[
      \tau = \sqrt{\sum (\Gamma_{jk}^i - \Gamma_{kj}^i)^2}
      \]

**因子计算**：
- 数据字段：
  * K : 高斯曲率
  * H : 平均曲率
  * τ : 拓扑挠率
  
- 因子生成：
  1. 标准化处理：
    \[
    \widetilde{K} = \frac{K - \mu_K}{3\sigma_K}, \quad \widetilde{H} = \frac{H}{max(|H|)}, \quad \widetilde{τ} = sign(τ)\sqrt{|τ|}
    \]
  
  2. 涡旋强度合成：
    \[
    VF = \widetilde{K} \times \widetilde{H} \times e^{-\widetilde{τ}}
    \]
  
  3. 符号标准化：
    \[
    Factor = \frac{VF - median(VF)}{MAD(VF) + \epsilon}
    \]

**参数说明**：
- \( \epsilon \) (防零参数)：
  * 类型：float
  * 默认：1e-6
  * 含义：防止时间间隔为零导致的计算异常
  
- 曲率窗宽\( w \)：
  * 类型：int
  * 默认：5
  * 含义：样条插值的局部窗口点数
  
- 旋转密度阈值\( \theta \)：
  * 类型：float
  * 默认：0.7（标准差单位）
  * 含义：临界涡旋结构识别的灵敏度

**使用说明**：
- 推送频率：50ms-1s最佳（需单批次≥10笔成交）
- 应用场景：
  1. 算法交易滑点控制
  2. 流动性黑洞预警
  3. 高频套利时点识别
  
- 注意事项：
  1. 需过滤熔断机制触发的异常值
  2. 在震荡市表现优于趋势市
  3. 需配合硬件级低延迟架构使用