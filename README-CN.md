# AlgoHood Strategy Framework

AlgoHood Strategy Framework是量化交易系统的策略仓库，用于存放各个核心组件的具体实现逻辑。该仓库采用标准化的接口定义，通过对话式AI开发实现新一代的策略开发范式。

## 开发理念

本框架通过AI辅助编程彻底革新了传统的开发方式：

> **核心信念**：以当前AI的能力水平，如果AI无法实现某个功能，往往不是AI能力不足，而是人类没有想清楚需求和逻辑。在与AI协作时，我们需要转变思维方式，将重点放在需求的明确性和逻辑的完整性上。

1. **对话式开发**
   - 开发者从编写代码转变为通过自然对话指导AI
   - 大部分代码通过与AI的对话生成，最小化直接编码工作
   - 人类专注于高层设计和战略决策

2. **AI驱动效率**
   - `algoAgent/prompts/`中的标准化提示模板指导AI生成一致、高质量的代码
   - 与Cursor IDE的深度集成实现无缝AI辅助
   - 通过AI-人类协作显著减少开发时间

3. **角色进化**
   - 开发者从代码执行者进化为策略指导者
   - 工作重心转向系统设计和优化策略
   - AI处理常规编码任务，人类确保质量和创新

## 核心功能

### 1. 策略逻辑存储
- **信号策略**：`algoSignals/` - 存放信号生成的具体实现
- **特征工程**：`algoIntercepts/` - 存放特征计算的具体实现
- **性能计算**：`algoPerformances/` - 对过滤后的信号计算粗略收益，生成时序数据
- **指标评估**：`algoAbstracts/` - 对时序数据进行截面统计分析，计算相关评估指标
- **策略优化**：`algoOptimizers/` - 实现策略筛选和淘汰机制
- **风控策略**：`algoRisks/` - 实现风险控制相关策略
- **资金配置**：`algoLiquidities/` - 实现基于流动性的资金配置策略

### 2. AI驱动开发
- **标准化Prompt**：`algoAgent/prompts/` - 用于AI生成各类策略代码的标准提示模板
- **代码生成**：支持通过AI自动生成符合接口规范的策略代码
- **逻辑优化**：支持通过AI优化现有策略逻辑

### 3. 接口规范
- **统一接口**：所有策略逻辑必须继承自`algoUtils`中定义的基类
- **标准化输入输出**：统一的数据结构和格式定义
- **类型约束**：严格的类型提示和检查

## 项目结构
```
algohood_strategy/
├── algoAgent/
│   └── prompts/         # AI代理提示模板
│       ├── signals.md   # 信号生成提示
│       ├── features.md  # 特征工程提示
│       ├── models.md    # 模型训练提示
│       └── intercept.md # 信号拦截提示
├── algoStrategy/
│   ├── algoSignals/     # 信号生成策略
│   ├── algoIntercepts/  # 特征工程实现
│   ├── algoPerformances/# 时序收益计算
│   ├── algoAbstracts/   # 截面指标统计
│   ├── algoOptimizers/  # 策略筛选淘汰
│   ├── algoRisks/      # 风险控制策略
│   └── algoLiquidities/ # 流动性资金配置
├── algoBroker/         # 核心调度组件
│   └── brokerMgr.py    # Broker管理器实现
├── algoConfig/         # 配置文件目录
│   ├── execConfig.py   # 执行配置
│   ├── redisConfig.py  # Redis配置
│   └── zmqConfig.py    # ZMQ配置
├── algoStart/          # 启动脚本目录
│   ├── signalStart.py  # 信号模块启动
│   ├── execStart.py    # 执行模块启动
│   └── monitorStart.py # 监控模块启动
└── tests/              # 测试用例
```

### 目录说明

1. **核心组件**
   - `algoBroker/`: 核心调度组件，负责任务分发和管理
   - `algoConfig/`: 系统配置文件，包含各类参数设置
   - `algoStart/`: 各模块启动脚本，管理系统启动流程

2. **策略组件**
   - `algoStrategy/`: 策略相关实现
     - `algoSignals/`: 信号生成策略
     - `algoIntercepts/`: 特征工程实现
     - `algoPerformances/`: 时序收益计算
     - `algoAbstracts/`: 截面指标统计
     - `algoOptimizers/`: 策略筛选淘汰
     - `algoRisks/`: 风险控制策略
     - `algoLiquidities/`: 流动性资金配置

3. **AI组件**
   - `algoAgent/`: AI代理相关实现
     - `prompts/`: 标准化提示模板
       - `signals.md`: 信号生成提示
       - `features.md`: 特征工程提示
       - `models.md`: 模型训练提示
       - `intercept.md`: 信号拦截提示

4. **配置文件**
   - `execConfig.py`: 执行相关配置（延迟、费率等）
   - `redisConfig.py`: Redis连接配置
   - `zmqConfig.py`: ZMQ通信配置

5. **启动脚本**
   - `signalStart.py`: 信号模块启动脚本
   - `execStart.py`: 执行模块启动脚本
   - `monitorStart.py`: 监控模块启动脚本

## 开发规范

### 1. 命名规范
- 参数命名使用前导下划线（如`_param_name`）
- 使用蛇形命名法（如`price_data`而非`priceData`）
- 文件名使用小驼峰命名（如`activeMarket.py`）

### 2. 性能要求
- 使用numpy进行向量化运算
- 避免使用pandas等性能较差的库
- 合理使用缓存机制
- 注意内存使用效率

### 3. 代码规范
- 提供详细的函数注释
- 使用类型提示
- 遵循PEP 8规范
- 编写单元测试

## 依赖要求
- Python >= 3.10
- algoSignal
- algoUtils

## 安装方法
```bash
python -m venv .venv
# windows   
source .venv/Scripts/activate
# linux
source .venv/bin/activate
git clone https://github.com/algohood/algohood_strategy.git
cd algohood_strategy
pip install -e .
```

## 系统要求

Python 3.10+ 及`pyproject.toml`中列出的依赖

## 环境配置

### Redis安装与配置

1. **安装Redis Stack Server**
   - 访问 [Redis Stack GitHub](https://github.com/redis-stack/redis-stack) 获取最新安装包
   - Redis Stack包含了必需的TimeSeries模块
   - 根据操作系统选择对应的安装方式：

2. **启动Redis实例**
   - config实例（端口6379）：用于保存配置和数据状态，端口可自定义，但需要与配置文件中的端口号一致
   - node实例（端口9001）：用于存储实际数据，端口可自定义，但需要与配置文件中的端口号一致
   ```bash
   mkdir --parents ~/redis_file/config ~/redis_file/node
   screen -dmS config bash -c 'redis-stack-server --port 6379 --dir ~/redis_file/config'
   screen -dmS node bash -c 'redis-stack-server --port 9001 --dir ~/redis_file/node'
   ```

3. **运行初始化脚本**
   ```bash
   # 切换到algoStart目录运行
   cd algoStart
   python init_redis.py  #根据网络情况，可编辑下载数据得标的和时间范围
   ```

   > **注意**：脚本运行后会自动在项目根目录创建`algoLog`文件夹用于存放日志。为确保日志文件位置正确，请务必在`algoStart`目录下运行脚本。

### 常见问题

1. Redis连接失败
   - 检查Redis服务是否正常运行
   - 确认端口号配置正确
   - 检查防火墙设置

2. 数据同步问题
   - 确保网络连接稳定
   - 检查磁盘空间是否充足
   - 查看日志文件排查错误

## 贡献指南

欢迎贡献代码！请遵循以下流程：
1. Fork代码仓库
2. 创建特性分支
3. 提交Pull Request

## 许可证

专有许可证（具体授权细节请联系AlgoHood） 