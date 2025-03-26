# 🍪 Cookie Trading Manager

## Table of Contents
- [🍪 Cookie Trading Manager](#-cookie-trading-manager)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
    - [Use Case](#use-case)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Available Ingredients](#available-ingredients)
  - [Fee System](#fee-system)
  - [Data Persistence](#data-persistence)
  - [Project Structure](#project-structure)
  - [Development](#development)
    - [Setting Up Development Environment](#setting-up-development-environment)
    - [Running Tests](#running-tests)
    - [Test Structure](#test-structure)
  - [Contributing](#contributing)
  - [License](#license)
  - [Trading Tips](#trading-tips)

A terminal-based trading manager for Cookie Clicker's market minigame that helps players track and analyze their trading positions.

## About

Cookie Trading Manager is designed specifically for Cookie Clicker's market minigame, where players can trade various ingredients used in cookie production. The market features dynamic prices that change based on supply and demand, making it crucial to track positions and calculate profits accurately.

### Use Case

In Cookie Clicker's market minigame:
- Players can buy and sell ingredients like Butter, Sugar, and Eggs
- Prices fluctuate based on market conditions and trader count
- Each trade incurs a fee that reduces with more traders
- Success requires careful tracking of entry/exit prices and timing

This tool helps players by:
- Tracking multiple positions across different ingredients
- Calculating accurate profit/loss including fees
- Simulating potential trades before execution
- Maintaining a complete history of trading activity
- Providing real-time insights into current positions

## Features

- 📊 Real-time trading dashboard with current positions and P/L
- 📈 Position tracking with entry/exit prices and timestamps
- 💰 Profit/loss calculation with dynamic fee system
- 📝 Optional comments for positions and trades
- 📅 Complete trading history with detailed records
- 🎨 Beautiful terminal UI with colors and emojis
- 💾 Persistent data storage using SQLite
- ✅ Comprehensive test suite with 100% coverage
- 🔄 Automatic database schema management
- 🎯 Precise financial calculations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cookie-trading.git
cd cookie-trading
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the program:
```bash
python main.py
```

2. Main Menu Options:
   - `1. 📈 Add Position`: Open a new trading position
   - `2. 📉 Close Position`: Close an existing position
   - `3. 🔮 Simulate Close`: Test potential position closure
   - `4. 📊 Show Open Positions`: View current positions
   - `5. 📜 Show Trading History`: View past trades
   - `6. 👥 Update Traders Count`: Modify trader count
   - `7. ❌ Exit`: Close the program

3. Adding a Position:
   - Select option 1
   - Choose ingredient code (e.g., BTR for Butter)
   - Enter quantity
   - Enter entry price (e.g., $575.21)
   - Add optional comment (max 500 characters)

4. Closing a Position:
   - Select option 2
   - Enter position ID
   - Enter exit price
   - Add optional comment (max 500 characters)

5. Simulating a Close:
   - Select option 3
   - Enter position ID
   - Enter hypothetical exit price
   - View projected profit/loss and fees

## Available Ingredients

| Code | Ingredient | Emoji | Description |
|------|------------|-------|-------------|
| CRL  | Cereal     | 🌾    | Used in basic cookie recipes |
| CHC  | Chocolate  | 🍫    | Premium ingredient for special cookies |
| BTR  | Butter     | 🧈    | Common ingredient in most recipes |
| SUC  | Sugar      | 🧂    | Essential for all cookie types |
| NOI  | Walnut     | 🥜    | Adds crunch to cookies |
| SEL  | Salt       | 🧂    | Enhances cookie flavor |
| VNL  | Vanilla    | 🍶    | Premium flavoring ingredient |
| OEUF | Eggs       | 🥚    | Binding agent for cookie dough |

## Fee System

- Base fee: 20%
- Reduction: -1% per trader
- Example: With 5 traders, fee = 15%
- Fees are calculated on the absolute value of profit/loss
- All calculations are rounded to 2 decimal places for precision

## Data Persistence

All data is stored in `trading.db`:
- Open positions with entry prices and timestamps
- Trading history with exit prices and P/L
- Trader count and fee settings
- Position and trade comments
- Last updated timestamps
- Automatic schema versioning

## Project Structure

```
cookie-trading/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── src/
│   ├── models/         # Data models
│   │   ├── __init__.py
│   │   ├── position.py  # Position model
│   │   └── trade.py     # Trade model
│   ├── views/          # UI components
│   │   ├── __init__.py
│   │   ├── dashboard.py # Dashboard view
│   │   └── tables.py    # Table views
│   ├── controllers/    # Business logic
│   │   ├── __init__.py
│   │   └── trader.py    # Trader controller
│   └── utils/          # Helper functions
│       ├── __init__.py
│       ├── constants.py # Game constants
│       ├── database.py  # Database utilities
│       └── formatting.py # Formatting utilities
├── tests/              # Test files
│   ├── __init__.py
│   ├── conftest.py     # Test configuration
│   ├── test_position.py
│   ├── test_trade.py
│   ├── test_trader.py
│   ├── test_formatting.py
│   └── test_database.py
└── .cursor/           # Development documentation
    └── rules/         # Project rules and patterns
        ├── patterns/  # Code patterns
        └── tasks/     # Task guidelines
```

## Development

### Setting Up Development Environment

1. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

1. Run all tests:
```bash
python -m pytest tests/
```

2. Run tests with coverage report:
```bash
python -m pytest tests/ --cov=src
```

3. Run specific test file:
```bash
python -m pytest tests/test_position.py
```

4. Run tests with verbose output:
```bash
python -m pytest tests/ -v
```

### Test Structure

The test suite includes:
- `test_position.py`: Tests for position management
- `test_trade.py`: Tests for trade history
- `test_trader.py`: Tests for trader controller
- `test_formatting.py`: Tests for utility functions
- `test_database.py`: Tests for database operations
- `conftest.py`: Common test fixtures

Test features:
- Isolated test database
- Automatic schema setup
- Comprehensive test coverage
- Non-interactive testing support
- Floating-point precision handling
- Database transaction testing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Trading Tips

1. **Market Timing**:
   - Watch for price trends before entering positions
   - Consider trader count impact on fees
   - Use the simulate feature to test potential trades

2. **Position Management**:
   - Start with small positions to test the market
   - Use comments to track your trading strategy
   - Monitor multiple ingredients for opportunities

3. **Fee Optimization**:
   - Increase trader count to reduce fees
   - Consider fee impact on small trades
   - Use simulation to calculate net profit after fees
