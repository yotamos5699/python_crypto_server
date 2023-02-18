# from datetime import datetime  # noqa
# from typing import Optional, Union  # noqa

# import freqtrade.vendor.qtpylib.indicators as qtpylib
# # --- Do not remove these libs ---
# import numpy as np  # noqa
# import pandas as pd  # noqa
# import talib.abstract as ta
# from freqtrade.strategy import (IStrategy, IntParameter)
# from pandas import DataFrame  # noqa


# class EMABayoniStrategy(IStrategy):
#     INTERFACE_VERSION = 3
#     timeframe = '3m'
#     can_short: bool = True
#     minimal_roi = {"0": 0.0}
#     stoploss = -0.0
#     trailing_stop = False
#     process_only_new_candles = True
#     use_exit_signal = True
#     exit_profit_only = False
#     ignore_roi_if_entry_signal = False
#     startup_candle_count: int = 30
#     # buy_rsi = IntParameter(10, 40, default=30, space="buy")
#     # sell_rsi = IntParameter(60, 90, default=70, space="sell")
#     order_types = {
#         'entry': 'limit',
#         'exit': 'limit',
#         'stoploss': 'limit',
#         "force_exit": "market",
#         'stoploss_on_exchange': False
#     }
#     order_time_in_force = {
#         'entry': 'gtc',
#         'exit': 'gtc'
#     }

#     @property
#     def plot_config(self):
#         return {
#             # Main plot indicators (Moving averages, ...)
#             'main_plot': {
#                 'tema': {EMABayoniStrategy},
#                 'sar': {'color': 'white'},
#             },
#             'subplots': {
#                 # Subplots - each dict defines one additional plot
#                 "MACD": {
#                     'macd': {'color': 'blue'},
#                     'macdsignal': {'color': 'orange'},
#                 },
#                 "RSI": {
#                     'rsi': {'color': 'red'},
#                 }
#             }
#         }

#     def informative_pairs(self):
#         return [("ETH/USDT", self.timeframe)]

#     def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#         dataframe['ema7'] = ta.EMA(dataframe, timeperiod=7)
#         dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

#         return dataframe

#     def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#         dataframe.loc[
#             (
#                 qtpylib.crossed_above(dataframe['ema7'], dataframe['ema200'])
#             ),
#             'enter_long'] = 1

#         dataframe.loc[
#             (
#                 qtpylib.crossed_below(dataframe['ema7'], dataframe['ema200'])
#             ),
#             'enter_short'] = 1

#         return dataframe

#     def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#         return dataframe

#     def leverage(self, pair: str, current_time: datetime, current_rate: float,
#                  proposed_leverage: float, max_leverage: float, entry_tag: Optional[str], side: str,
#                  **kwargs) -> float:

#         return 10.0

#      # def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
#       #                      proposed_stake: float, min_stake: float, max_stake: float,
#        #                     entry_tag: Optional[str], side: str, **kwargs) -> float:

#         # return max_stake * 0.5
