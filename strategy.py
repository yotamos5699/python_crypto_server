from typing import List, Dict
from dataclasses import dataclass
timeValue = {
    "5s": 5,
    "30s": 30,
    "1m": 60,
    "3m": 180,
    "5m": 300
}

# https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true&precision=8


@dataclass(order=True)
class GetPrices:
    # def __init__(self,  ids: List[str], vs_currencies: List[str], include_market_cap: bool, include_24hr_vol: bool, include_24hr_change: bool, include_last_updated_at: bool, precision: int):
    ids: List[str] | str
    vs_currencies: List[str] | str = 'usd'
    precision: int = 6
    include_market_cap: bool = False
    include_24hr_vol: bool = False
    include_24hr_change: bool = False
    include_last_updated_at: bool = True


class AssetsConfig:
    def __init__(self,  number_assets: int, sort_method: str, min_value: float, refresh_time_period: str, pairedCoin: str, precision: int):

        self.number_assets = number_assets
        self.sort_method = sort_method
        self.min_value = min_value
        self.refresh_time_period = timeValue[refresh_time_period]
        self.pairedCoin = pairedCoin
        self.precision = precision

    def show(self) -> None:
        print('number_assets: ', self.number_assets,
              'sort_method: ', self.sort_method,
              'min_value: ',   self.min_value,
              'refresh_time_period: ',  self.refresh_time_period,
              'pairedCoin: ', self.pairedCoin)


class Strategy:
    def __init__(self, id: str, userID: str, max_open_trades: int, stake_amount: int, tradable_balance_ratio: float, entryTimeOut: int, exitTimeOut: int, timeout_count: int, baseTimeGap: str, shortEmaRatio: int, longEmaRatio: int) -> None:
        self.id = id
        self.userID = userID
        self.max_open_trades = max_open_trades
        self.stake_amount = stake_amount
        self.baseTimeGap = baseTimeGap
        self.shortEmaRatio = shortEmaRatio
        self.longEmaRatio = longEmaRatio

        self.stake_currency = "USDT"
        # Amount of crypto-currency your bot will use for each trade

        # Ratio of the total account balance the bot is allowed to trade.
        self.tradable_balance_ratio = tradable_balance_ratio
        self.fiat_display_currency = "USD"
        self.dry_run = True,
        self.cancel_open_orders_on_exit = True
        self.trading_mode = "futures"
        self.margin_mode = "isolated"
        self.unfilledtimeout = {
            "entry": entryTimeOut,
            "exit": exitTimeOut,
            "exit_timeout_count": timeout_count,
            "unit": "minutes"
        }
        self.entry_pricing = {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1,
            "price_last_balance": 0.0,
            "check_depth_of_market": {
                "enabled": False,
                "bids_to_ask_delta": 1
            }
        },
        self.exit_pricing = {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1
        }

    def show(self) -> None:
        print('id: ', self.id,
              'userID: ', self.userID,
              'max_open_trades: ',   self.max_open_trades,
              'stake_amount: ',  self.stake_amount,
              'baseTimeGap: ', self.baseTimeGap,
              'shortEmaRatio: ', self.shortEmaRatio,
              'longEmaRatio: ', self.longEmaRatio,
              'stake_currency: ',   self.stake_currency,
              'tradable_balance_ratio: ',  self.tradable_balance_ratio,
              'fiat_display_currency: ', self.fiat_display_currency,
              'dry_run: ', self.dry_run,
              'cancel_open_orders_on_exit: ', self.cancel_open_orders_on_exit,
              'trading_mode: ',   self.trading_mode,
              'margin_mode: ',  self.margin_mode,
              'unfilledtimeout: ', self.unfilledtimeout,
              'entry_pricing: ',   self.entry_pricing,
              'exit_pricing: ',  self.exit_pricing,
              'unfilledtimeout: ', self.unfilledtimeout)

    # "edge": {
    #     "enabled": false,
    #     "process_throttle_secs": 3600,
    #     "calculate_since_number_of_days": 7,
    #     "allowed_risk": 0.01,
    #     "stoploss_range_min": -0.01,
    #     "stoploss_range_max": -0.1,
    #     "stoploss_range_step": -0.01,
    #     "minimum_winrate": 0.60,
    #     "minimum_expectancy": 0.20,
    #     "min_trade_number": 10,
    #     "max_trade_duration_minute": 1440,
    #     "remove_pumps": false
    # },

    # self.available_capital = 1.23154 , # Available starting capital for the bot. Useful when running multiple bots on the same exchange

    # "exchange": {
    #     "name": "binance",
    #     "key": "",
    #     "secret": "",
    #     "ccxt_config": {},
    #     "ccxt_async_config": {},
    #     "pair_whitelist": [],
    #     "pair_blacklist": []
    # },
#  // "telegram": {
#         // "enabled": false,
#         // "token": "5980455910:AAGmXrBTzerKvQCzJM-J4oaHp_N1luhTTjg",
#         // "chat_id": ""
#         //},

#   "api_server": {
#         "enabled": false,
#         "listen_ip_address": "127.0.0.1",
#         "listen_port": 8080,
#         "verbosity": "error",
#         "enable_openapi": false,
#         "jwt_secret_key": "32b788e388405bc3f1dbb6a909380d6b49ea6d4421d7a30495b335b3cd8a09f9",
#         "CORS_origins": [],
#         "username": "",
#         "password": ""
#     },
#     "bot_name": "freqtrade",
#     "initial_state": "running",
#     "force_entry_enable": false,
#     "internals": {
#         "process_throttle_secs": 5
#     }
