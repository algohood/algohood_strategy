**信号名称**：EntropyAccelerator

**信号概述**：
本信号通过量化市场信息熵的动态演变预测金融资产的相变临界点。运用香农熵度量市场信息的秩序程度，结合Tsallis非广延熵捕捉长程相关性特征。通过两类熵值的时变发散度识别微观结构的非线性变化，配合双曲正切速度饱和函数（tanh）实现相变预警。预期可提前1-3个数据批次检测到波动率异动，捕捉暴涨暴跌前的市场状态转换。

**设计模式**：
- 模式选择：半无状态
- 选择原因：
  1. 需要在批处理中保持熵指标的动态特征
  2. 维持最新5个周期的熵发散度移动均值状态
  3. 计算复杂度介于O(n)到O(n logn)之间
  4. 适用于高频恶劣环境下的低延迟响应

**特征提取**：
- 数据字段：amount, direction
- 特征计算：
  * 当前批次特征：
    1. 买卖量香农熵：H_S = -Σ(p_i log2 p_i)，p_i为买方/卖方成交量占比
    2. Tsallis熵：H_T = (1 - Σp_i^q)/(q - 1)，q=1.7为非广延参数
    3. 熵发散度：ΔH = |H_S - H_T| / max(H_S, H_T)
  * 状态变量更新：
    1. 滑动均值μ(ΔH)：维护长度为N=5的环形缓冲区，μ_t = μ_{t-1} + (ΔH_t - ΔH_{t-N})/N
    2. 发散加速度α：α = tanh( (ΔH_t - μ_t)/σ_t )，σ_t为滚动标准差
    初始化：首次运行时用前5个批次计算μ和σ
- 复杂度分析：
  特征计算O(n) + 状态更新O(1)，可支持1秒级处理

**信号计算**：
- 计算特点：引入崖山系数（临界指数）的Logistic回归变形
- 信号生成：
  * 特征组合：信号强度S = α × ln(1 + ΔH/μ)
  * 状态变量触发：当S > λ_s 且 α > λ_α 时产生买入信号，当S < -λ_s 且 α < -λ_α 时产生卖出信号
  * 速度约束：连续触发需满足 |dS/dt| > η（速率阈值）
  触发条件：S的极值点位于前向差分的三次样条插值曲线拐点

**参数说明**：
- 阈值参数：
  1. λ_s=0.618（黄金比例截断）
  2. λ_α=tanh(0.5)≈0.462（标准化非线性阈值）
  3. η=0.05Δt^{-1}（速率敏感性，Δt为数据间隔）
- 模式参数：
  1. N=5（经验最优滚动窗口）
  2. q=1.7（最优非广延性参数）
- 调优建议：
  q值增加增强对小概率事件的敏感性
  N加大降低噪声但延迟上升
  速率η需要与标的波动率正相关

**使用说明**：
- 推送频率：适用于1秒级高频场景（最佳实践62秒周期）
- 应用场景：黑色天鹅事件前的波动率突破预警
- 注意事项：
  1. 需配合市场波动率状态过滤器使用
  2. 在流动性极度匮乏时可能失效
  3. 重大消息发布期间需要人工干预