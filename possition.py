

from dataclasses import asdict
from datetime import datetime
from typing import Any, NotRequired, TypedDict
from strategy import Strategy
import db
import models
import requests

from typs import Coin_T
TEST_URL = 'https://script.google.com/macros/s/AKfycbzh0Jz267JZ_HXGatrE-oJj8fwPHqXAn3G_UkVJX8EJj8m7jSStWeTwa9wHXbFTEVx1Lw/exec'


DB = db.SessionLocal()
#   __tablename__ = "actions"
#     id = Column(Integer, primary_key=True, index=True)
#     Time = Column(DATE)
#     UserID = Column(String, unique=False)
#     CoinID = Column(String, ForeignKey('coins.coin_id'))
#     ActionType = Column(String)
#     time_of_atart = Column(DATE)
#     time_of_end = Column(DATE)
#     value_of_start = Column(Float)
#     value_of_end = Column(Float)
#     isOpen = Column(Boolean)


# def returnObj(obj: Strategy) -> Any:
#     newObj = {}
#     for k, v in obj.items():
#         newObj[k] = v
#     return newObj


class Binance_T(TypedDict):
    URL: str
    TOKEN: str
    PASSWORD: str


class Test_T(TypedDict):
    URL: str
    TOKEN: str


class Tokens(TypedDict):
    EXCHANGE: str
    BINANCE: NotRequired[Binance_T]
    TEST: NotRequired[Test_T]


T_HASH = {
    "BI": "self.tokens['BINANCE']",
    "TE": "self.tokens['TEST']"
}


def callApi(POSSITION_PARAMS: Any, CRADENTIALS: Any, TYPE: str) -> Any:
    params = {**POSSITION_PARAMS}
    params['type'] = TYPE
    res = requests.get(CRADENTIALS['URL'], params=params)

    return res.json()
# time_of_atart = Column(DATE)
# "ActionType" = Column(String)
# isOpen = Column(Boolean)


class P_handler():
    def __init__(self, strat: Any, coin: Coin_T, tokens: Tokens = {"EXCHANGE": "TE", "TEST": {"URL": TEST_URL,
                                                                                              "TOKEN": "TEST"}}) -> None:
        self.strat = strat
        self.coin = coin
        self.tokens = tokens

    def open(self) -> Any:
        print('initiating save....')
        now = datetime.now()
        S: Strategy = self.strat
        C: Coin_T = self.coin

        amount = float(S.bank) * float(S.tradable_balance_ratio) * float(S.stake_amount)
        if amount > 0:
            POSSITION = {
                "time": now,
                "userid": S.userID,
                "coinid": C['coin_id'],
                "value_of_start": C['value'],
                "start_stuck_value": amount
            }
            CRADENTIALS = eval(T_HASH[self.tokens["EXCHANGE"]])
            res = callApi(POSSITION, CRADENTIALS, "open_p")
            py_data = dict.copy(res['data'])

            py_data['time_of_atart'] = datetime.fromisoformat(res['data']['time_of_atart'])
            py_data['Time'] = datetime.fromisoformat(res['data']['Time'])
            if res['isOk']:

                DB.add(models.Actions(**py_data))
                DB.commit()
                print('saved ok on user: ', S.name, ' coin_id: ', C["coin_id"])
            return res

    def close(self) -> Any:
        S: Strategy = self.strat
        C: Coin_T = self.coin
        pos = DB.query(models.Actions).filter(models.Actions.coin_id == C['coin_id'], models.Actions.UserID == S.userID).first()
        POSSITION = {}
        if (type(pos) == models.Actions):

            POSSITION = {
                "userid": S.userID,
                "coinid": C['coin_id'],
                "value_of_end": C['value'],
                "end_stuck_value": C['value']/pos.value_of_start * pos.start_stuck_value,
                "profit_lost_numeric": C['value']/pos.value_of_start * pos.start_stuck_value - pos.start_stuck_value
            }
        CRADENTIALS = eval(T_HASH[self.tokens["EXCHANGE"]])
        res = callApi(POSSITION, CRADENTIALS, "close_p")
        py_data = dict.copy(res['data'])

        py_data['time_of_atart'] = datetime.fromisoformat(res['data']['time_of_atart'])
        py_data['Time'] = datetime.fromisoformat(res['data']['Time'])
        py_data['time_of_end'] = datetime.fromisoformat(res['data']['time_of_end'])
        if res['isOk']:
            DB.query(models.Actions).filter(models.Actions.coin_id == C['coin_id'], models.Actions.UserID == S.userID).update(py_data)
            DB.commit()
        return res
