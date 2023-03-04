
from typing import Any, List, NotRequired, TypedDict
from strategy import Strategy
from datetime import datetime


class Coin_T(TypedDict):
    coin_id: NotRequired[str]
    last_updated: datetime
    vs: str
    value: float
    counter: NotRequired[int]
    positions: NotRequired[int]


class P_T(TypedDict):
    IS_EXIST: bool
    USER_STRAT: Strategy
    COIN_DATA: Coin_T | Any


class Tick_(TypedDict):
    time_stemp: datetime
    long_ema_val: float
    short_ema_val: float
    is_long: bool
    is_short: bool


class CoinTicks(TypedDict):
    user_strat: Strategy
    coin_id: str
    ticks: List[Tick_]


class PossitionData(TypedDict):
    coin_id: str
    strat: Strategy


class Move(TypedDict):
    movment_id: NotRequired[int]
    coin_id: str | Any
    time_stemp: datetime | Any
    vs:   str | Any
    value: float | Any
    value_5: NotRequired[float]
    value_15: NotRequired[float]
    value_30: NotRequired[float]
    value_60: NotRequired[float]


class MarketData_T(TypedDict):
    id: str


class GetPrices_T(TypedDict):
    ids: list[str]
    vs_currencies:  list[str] | str
    precision: NotRequired[int]
    include_market_cap: NotRequired[bool]
    include_24hr_vol: NotRequired[bool]
    include_24hr_change: NotRequired[bool]
    include_last_updated_at: NotRequired[bool]
    last_updated: NotRequired[bool]
