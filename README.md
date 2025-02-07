# AlgoHood Strategy Framework

AlgoHood Strategy Framework is a strategy repository for quantitative trading systems, designed to store implementations of core components. The repository adopts standardized interface definitions and embraces a new paradigm of AI-driven development through conversation.

## Development Philosophy

The framework revolutionizes traditional development approaches by leveraging AI-assisted programming:

> **Core Belief**: Given the current capabilities of AI, if AI fails to implement a feature, it's usually not due to AI's limitations but rather because humans haven't clearly defined the requirements and logic. When collaborating with AI, we need to shift our mindset to focus on clarity of requirements and completeness of logic.

1. **Conversation-First Development**
   - Developers transition from writing code to directing AI through natural conversations
   - Most code is generated through dialogue with AI, minimizing direct coding
   - Humans focus on high-level design and strategic decisions

2. **AI-Powered Efficiency**
   - Standardized prompts in `algoAgent/prompts/` guide AI to generate consistent, high-quality code
   - Integration with Cursor IDE enables seamless AI assistance
   - Development time is significantly reduced through AI-human collaboration

3. **Role Evolution**
   - Developers evolve from code executors to strategy directors
   - Focus shifts to system design and optimization strategies
   - AI handles routine coding tasks while humans ensure quality and innovation

## Core Features

### 1. Strategy Logic Storage
- **Signal Strategy**: `algoSignals/` - Implementation of signal generation
- **Feature Engineering**: `algoIntercepts/` - Implementation of feature calculation
- **Performance Calculation**: `algoPerformances/` - Calculate time-series returns from filtered signals
- **Metric Evaluation**: `algoAbstracts/` - Cross-sectional statistical analysis of time-series data
- **Strategy Optimization**: `algoOptimizers/` - Strategy selection and elimination mechanisms
- **Risk Control**: `algoRisks/` - Risk control strategy implementation
- **Capital Allocation**: `algoLiquidities/` - Liquidity-based capital allocation

### 2. AI-Driven Development
- **Standardized Prompts**: `algoAgent/prompts/` - Standard prompt templates for AI code generation
- **Code Generation**: Support for AI-generated code following interface specifications
- **Logic Optimization**: Support for AI optimization of existing strategy logic

### 3. Interface Specifications
- **Unified Interfaces**: All strategy logic must inherit from base classes in `algoUtils`
- **Standardized I/O**: Unified data structure and format definitions
- **Type Constraints**: Strict type hints and checking

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
│   ├── algoIntercepts/  # Feature engineering implementations
│   ├── algoPerformances/# Time-series return calculations
│   ├── algoAbstracts/   # Cross-sectional statistics
│   ├── algoOptimizers/  # Strategy selection and elimination
│   ├── algoRisks/      # Risk control strategies
│   └── algoLiquidities/ # Liquidity-based capital allocation
├── algoBroker/         # Core scheduling component
│   └── brokerMgr.py    # Broker manager implementation
├── algoConfig/         # Configuration directory
│   ├── execConfig.py   # Execution configuration
│   ├── redisConfig.py  # Redis configuration
│   └── zmqConfig.py    # ZMQ configuration
├── algoStart/          # Startup scripts directory
│   ├── signalStart.py  # Signal module startup
│   ├── execStart.py    # Execution module startup
│   └── monitorStart.py # Monitoring module startup
└── tests/              # Test cases
```

### Directory Description

1. **Core Components**
   - `algoBroker/`: Core scheduling component for task distribution and management
   - `algoConfig/`: System configuration files with various parameter settings
   - `algoStart/`: Module startup scripts for system initialization

2. **Strategy Components**
   - `algoStrategy/`: Strategy implementations
     - `algoSignals/`: Signal generation strategies
     - `algoIntercepts/`: Feature engineering implementations
     - `algoPerformances/`: Time-series return calculations
     - `algoAbstracts/`: Cross-sectional statistics
     - `algoOptimizers/`: Strategy selection and elimination
     - `algoRisks/`: Risk control strategies
     - `algoLiquidities/`: Liquidity-based capital allocation

3. **AI Components**
   - `algoAgent/`: AI agent implementations
     - `prompts/`: Standardized templates
       - `signals.md`: Signal generation prompts
       - `features.md`: Feature engineering prompts
       - `models.md`: Model training prompts
       - `intercept.md`: Signal interception prompts

4. **Configuration Files**
   - `execConfig.py`: Execution configuration (delays, fees, etc.)
   - `redisConfig.py`: Redis connection configuration
   - `zmqConfig.py`: ZMQ communication configuration

5. **Startup Scripts**
   - `signalStart.py`: Signal module startup script
   - `execStart.py`: Execution module startup script
   - `monitorStart.py`: Monitoring module startup script

## Development Standards

### 1. Naming Conventions
- Use leading underscore for parameters (e.g., `_param_name`)
- Use snake_case (e.g., `price_data` instead of `priceData`)
- Use camelCase for filenames (e.g., `activeMarket.py`)

### 2. Performance Requirements
- Use numpy for vectorized operations
- Avoid performance-intensive libraries like pandas
- Implement proper caching mechanisms
- Optimize memory usage

### 3. Code Standards
- Provide detailed function documentation
- Use type hints
- Follow PEP 8 guidelines
- Write unit tests

## Dependencies
- Python >= 3.10
- algoSignal
- algoUtils

## Installation
```bash
pip install git+https://github.com/algohood/algohood_strategy.git@master
```

## System Requirements

Python 3.10+ and dependencies listed in `pyproject.toml`

## Environment Setup

### Redis Installation and Configuration

1. **Install Redis Stack Server**
   - Visit [Redis Stack GitHub](https://github.com/redis-stack/redis-stack) for the latest installation package
   - Redis Stack includes the required TimeSeries module
   - Choose installation method based on your operating system

2. **Start Redis Instances**
   - config instance (port 6379): for storing configurations and data states
   - node instance (port 9001): for storing actual data

3. **Run Initialization Script**
   ```bash
   # Switch to algoStart directory to run
   cd algoStart
   python init_redis.py  # You can edit the symbols and time range for data download
   ```

   > **Note**: The script will automatically create an `algoLog` folder in the project root directory for storing logs. To ensure correct log file placement, make sure to run the script from the `algoStart` directory.

### Common Issues

1. Redis Connection Issues
   - Check if Redis service is running properly
   - Verify port configurations
   - Check firewall settings

2. Data Synchronization Issues
   - Ensure stable network connection
   - Check available disk space
   - Review log files for troubleshooting

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## License

Proprietary License (Contact AlgoHood for licensing details)
