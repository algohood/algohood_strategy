# AlgoHood Strategy Framework

The AlgoHood Strategy Framework is a quantitative trading system strategy repository for implementing core components. It adopts standardized interface definitions and realizes next-generation strategy development through conversational AI programming.

## Development Philosophy

This framework revolutionizes traditional development through AI-assisted programming:

> **Core Belief**: When AI fails to implement a feature, it's usually not due to AI limitations but rather unclear human requirements and logic. In AI collaboration, we must shift focus to requirement clarity and logical integrity.

1. **Conversational Development**
   - Developers transition from coding to guiding AI through natural dialogue
   - Most code generated via AI conversations, minimizing direct coding
   - Humans focus on high-level design and strategic decisions

2. **AI-Driven Efficiency**
   - Standardized prompt templates in `algoAgent/prompts/` guide AI to generate consistent, high-quality code
   - Deep integration with Cursor IDE enables seamless AI assistance
   - Significant time savings through human-AI collaboration

3. **Role Evolution**
   - Developers evolve from coders to strategy directors
   - Focus shifts to system design and strategy optimization
   - AI handles routine coding, humans ensure quality and innovation

## Core Features

### 1. Strategy Logic Storage
- **Signal Strategies**: `algoSignals/` - Signal generation implementations
- **Feature Engineering**: `algoIntercepts/` - Feature calculation implementations
- **Performance Calculation**: `algoPerformances/` - Generate time-series returns for filtered signals
- **Metric Evaluation**: `algoAbstracts/` - Cross-sectional analysis of time-series data
- **Strategy Optimization**: `algoOptimizers/` - Strategy selection and elimination mechanisms
- **Risk Management**: `algoRisks/` - Risk control strategies
- **Capital Allocation**: `algoLiquidities/` - Liquidity-based capital allocation

### 2. AI-Driven Development
- **Standardized Prompts**: `algoAgent/prompts/` - Template prompts for AI code generation
- **Code Generation**: AI-automated strategy code with interface compliance
- **Logic Optimization**: AI-assisted strategy optimization

### 3. Interface Standards
- **Unified Interfaces**: All strategies inherit base classes from `algoUtils`
- **Standardized I/O**: Consistent data structures and formats
- **Type Constraints**: Strict type hints and checks

## Project Structure
```
algohood_strategy/
├── algoAgent/
│   └── prompts/         # AI agent prompt templates
│       ├── signals.md   # Signal generation prompts
│       ├── features.md  # Feature engineering prompts
│       ├── models.md    # Model training prompts
│       └── intercept.md # Signal interception prompts
├── algoStrategy/
│   ├── algoSignals/     # Signal generation strategies
│   ├── algoIntercepts/  # Feature engineering
│   ├── algoPerformances/# Time-series returns
│   ├── algoAbstracts/   # Cross-sectional metrics
│   ├── algoOptimizers/  # Strategy optimization
│   ├── algoRisks/      # Risk management
│   └── algoLiquidities/ # Liquidity allocation
├── algoBroker/         # Core orchestration
│   └── brokerMgr.py    # Broker manager
├── algoConfig/         # Configuration
│   ├── execConfig.py   # Execution config
│   ├── redisConfig.py  # Redis config
│   └── zmqConfig.py    # ZMQ config
├── algoStart/          # Launch scripts
│   ├── signalStart.py  # Signal module
│   ├── execStart.py    # Execution module
│   └── monitorStart.py # Monitoring
└── tests/              # Test cases
```

### Directory Structure

1. **Core Components**
   - `algoBroker/`: Core orchestration for task management
   - `algoConfig/`: System configuration
   - `algoStart/`: Module launch scripts

2. **Strategy Components**
   - `algoStrategy/`: Strategy implementations
     - `algoSignals/`: Signal generation
     - `algoIntercepts/`: Feature engineering
     - `algoPerformances/`: Return calculation
     - `algoAbstracts/`: Metric analysis
     - `algoOptimizers/`: Strategy selection and elimination
     - `algoRisks/`: Risk control
     - `algoLiquidities/`: Capital allocation

3. **AI Components**
   - `algoAgent/`: AI agent implementation
     - `prompts/`: Standardized prompts
       - `signals.md`: Signal generation
       - `features.md`: Feature engineering
       - `models.md`: Model training
       - `intercept.md`: Signal interception

4. **Configuration**
   - `execConfig.py`: Execution parameters (latency, fees)
   - `redisConfig.py`: Redis connections
   - `zmqConfig.py`: ZMQ communication

5. **Launch Scripts**
   - `signalStart.py`: Signal module
   - `execStart.py`: Execution module
   - `monitorStart.py`: Monitoring

## Development Standards

### 1. Naming Conventions
- Parameter names with leading underscore (e.g., `_param_name`)
- Snake case for variables (e.g., `price_data`)
- Lower camel case for filenames (e.g., `activeMarket.py`)

### 2. Performance Requirements
- Vectorized operations with numpy
- Avoid pandas for performance-critical code
- Implement caching mechanisms
- Optimize memory usage

### 3. Code Standards
- Detailed function comments
- Type hints
- PEP 8 compliance
- Unit tests

## Dependencies
- Python >= 3.10
- algoSignal
- algoUtils

## Installation
```bash
python -m venv .venv
# Windows   
source .venv/Scripts/activate
# Linux
source .venv/bin/activate
git clone https://github.com/algohood/algohood_strategy.git
cd algohood_strategy
pip install -e .
```

## System Requirements

Python 3.10+ and dependencies in `pyproject.toml`

## Environment Setup

### Redis Configuration

1. **Install Redis Stack Server**
   - Get latest version from [Redis Stack GitHub](https://github.com/redis-stack/redis-stack)
   - Includes required TimeSeries module
   - OS-specific installation instructions available

2. **Start Redis Instances**
   - Config instance (port 6379): Stores configurations
   - Node instance (port 9001): Stores actual data
   ```bash
   mkdir --parents ~/redis_file/config ~/redis_file/node
   screen -dmS config bash -c 'redis-stack-server --port 6379 --dir ~/redis_file/config'
   screen -dmS node bash -c 'redis-stack-server --port 9001 --dir ~/redis_file/node'
   ```

3. **Run Initialization Script**
   ```bash
   cd algoStart
   python init_redis.py  # Edit script for symbols/time ranges
   ```

   > **Note**: Script creates `algoLog` directory at project root for logs. Run from `algoStart` directory.

### Common Issues

1. Redis Connection Issues
   - Verify Redis service status
   - Check port configurations
   - Review firewall settings

2. Data Sync Problems
   - Ensure stable network
   - Check disk space
   - Review log files

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## License

Proprietary License (Contact AlgoHood for licensing details)
