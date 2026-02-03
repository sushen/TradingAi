from subscription.subscription_manager import SubscriptionManager
from bot.trading_bot import TradingBot
import sys

sub = SubscriptionManager(app_name="TradingBotX")

if not sub.is_allowed():
    print("❌ ACCESS DENIED")
    print(sub.lock_reason())
    sys.exit(1)

bot = TradingBot()
bot.run_trading_bot()
