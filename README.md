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

A terminal-based trading simulator for cookie ingredients with real-time profit/loss tracking.

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
git clone https://github.com/YourUsername/CookieTrading.git
cd CookieTrading
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the program:
```bash
python cookie_trader.py
```

2. Navigate the main menu:
- Position Actions:
  - 📈 Open Position: Start a new trading position
  - 📉 Close Position: Close an existing position (full or partial)
  - 🔮 Simulate Close: Test potential closing scenarios
  - 🎯 Simulate Trade: Simulate complete trades
- View Actions:
  - 📊 Show Open Positions: View current positions
  - 📜 Show Trading History: Review past trades
- Settings & Exit:
  - 👥 Update Traders Count: Modify fee calculations
  - ❌ Exit: Close the program

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
- Each trader reduces fee by 1%
- Minimum fee: 1%
- Applied to both profits and losses

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
CookieTrading/
├── src/
│   ├── models/
│   ├── views/
│   ├── controllers/
│   └── utils/
├── tests/
├── cookie_trader.py
├── requirements.txt
└── README.md
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
