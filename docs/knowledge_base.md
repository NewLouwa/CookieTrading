# Cookie Trading System Knowledge Base

## System Overview
The Cookie Trading System is a terminal-based trading simulation application for managing trading positions of various cookie ingredients. It features real-time profit/loss calculation, position tracking, and a dynamic fee system based on the number of traders.

## Core Components

### Database Structure
- **traders**: Stores number of traders and last update time
- **positions**: Tracks open and closed trading positions
- **trading_history**: Records completed trades with P/L information
- **portfolio**: Maintains current holdings of each ingredient

### Trading Features
1. **Position Management**
   - Open new positions
   - Close existing positions
   - Simulate position closes
   - Simulate complete trades

2. **Analysis Tools**
   - View portfolio
   - Trading history
   - Order records
   - Real-time dashboard

3. **System Features**
   - Dynamic fee calculation
   - Trader count management
   - Database reset capability
   - Portfolio synchronization

### Ingredient Codes
- CRL: Cereal 🌾
- CHC: Chocolate 🍫
- BTR: Butter 🧈
- SUC: Sugar 🧂
- NOI: Walnut 🥜
- SEL: Salt 🧂
- VNL: Vanilla 🍶
- OEUF: Eggs 🥚

### Fee System
- Base fee: 20%
- Fee reduction: 1% per trader
- Minimum fee: 0%

## User Interface

### Main Menu Structure
1. **Position Management**
   - Open New Position
   - Close Position
   - Simulate Position Close
   - Simulate Complete Trade

2. **Analysis Tools**
   - View Portfolio
   - Trading History
   - View Order Records

3. **Settings & System**
   - Update Traders Count
   - Reset Database
   - Exit Program

### Dashboard Information
- Current trader count and fee
- Number of open positions
- Total profit/loss
- Total completed trades

## Database Operations

### Portfolio Synchronization
- Automatically syncs portfolio with positions
- Updates total quantities and average prices
- Maintains data consistency

### Position Management
- Tracks entry and exit prices
- Records trade comments
- Maintains position status
- Calculates profit/loss

### History Tracking
- Records all completed trades
- Stores fee information
- Maintains trade timestamps
- Links positions to history

## Safety Features

### Database Reset
- Requires "I AGREE" confirmation
- 5-second wait period
- Complete data deletion
- Table recreation
- Error handling

### Input Validation
- Price format checking
- Quantity limits
- Ingredient code validation
- Comment length limits

## Technical Details

### Dependencies
- sqlite3: Database management
- rich: Terminal UI
- datetime: Timestamp handling
- emoji: Emoji support

### File Structure
- cookie_trader.py: Main application
- trading.db: SQLite database
- src/utils/: Utility functions

### Error Handling
- Database connection errors
- Input validation errors
- Operation cancellation
- Invalid data handling

## Best Practices

### Trading
- Monitor portfolio regularly
- Use simulation tools before trading
- Keep track of trading history
- Maintain proper position sizing

### System Usage
- Regular portfolio synchronization
- Proper database backups
- Careful use of reset function
- Monitor fee changes

## Future Considerations

### Potential Improvements
- Advanced analytics
- Risk management tools
- Performance optimization
- Additional trading features
- Enhanced reporting

### Known Limitations
- Single database instance
- Basic fee structure
- Limited position types
- Terminal-only interface

## Status: Final
This knowledge base represents the final state of the Cookie Trading System. All core features are implemented and tested. The system is ready for production use. 