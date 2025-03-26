"""Constants used throughout the application."""

# Trading ingredients with their emojis
INGREDIENTS = {
    'CRL': 'Cereal 🌾',
    'CHC': 'Chocolate 🍫',
    'BTR': 'Butter 🧈',
    'SUC': 'Sugar 🧂',
    'NOI': 'Walnut 🥜',
    'SEL': 'Salt 🧂',
    'VNL': 'Vanilla 🍶',
    'OEUF': 'Eggs 🥚'
}

# Trade status emojis
TRADE_EMOJIS = {
    'profit': '📈',
    'loss': '📉',
    'neutral': '➡️'
}

# Fee system constants
BASE_FEE = 20  # Base fee percentage
FEE_REDUCTION_PER_TRADER = 1  # Fee reduction percentage per trader

# Database constants
DB_PATH = 'trading.db'

# UI constants
MAX_COMMENT_LENGTH = 500 