**信号名称**：ZArbSpot
**信号概述**：通过动态标准化波动监测统计套利价差的异常偏离，基于标的资产与对冲资产价差的动态波动特征进行逆向交易。当价差波动超过基础波动率的预定倍数时触发回归交易信号。适用于具有稳定统计关系的套利组合。

**设计模式**：
- 模式选择：有状态模式
- 选择原因：
  * 需要维护动态统计窗口（30个批次）用于计算分布的均值/方差
  * 统计分析需要中等时间窗口（15-60分钟）
  * 价差关系中频特性（1-5分钟级）适合该模式延迟容忍度

**特征提取**：
- 数据字段：price
- 特征计算：
  * 当前批次特征：相对价差 = PrimaryAsset.price / HedgeAsset.price - 1
  * 历史特征窗口：
    - 特征类型：价差波动的动态分布
    - 窗口结构：三层级窗口实现快速迭代更新
    - 具体实现：