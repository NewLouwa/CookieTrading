# Cookie Trading Manager 🍪

A user-friendly Python script to manage trading positions in Cookie Clicker's market minigame. Track and analyze your ingredient trading with persistent storage and fee calculations.

## Features 🌟

- Interactive command-line interface with colors and emojis
- Persistent storage using SQLite database
- Support for all 8 trading ingredients:
  - Cereal (CRL)
  - Chocolate (CHC)
  - Butter (BTR)
  - Sugar (SCR)
  - Walnut (NOI)
  - Salt (SEL)
  - Vanilla (VNL)
  - Eggs (OEUF)
- Multi-share trading support
- Position management (open, close, simulate)
- Automatic fee calculation based on number of traders
- Real-time profit/loss tracking

## Installation 🔧

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage 🎮

Run the script:
```bash
python cookie_trader.py
```

## Database Schema 📊

The SQLite database maintains:
- Active positions
- Trading history
- Trader count
- Fee calculations

## License 📝

See [LICENSE](LICENSE) file for details.
