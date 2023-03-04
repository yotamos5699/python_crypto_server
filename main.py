from typing import Any, List, Dict,  NotRequired,  TypedDict
import pandas as pd
import concurrent.futures
import requests
import models
import db
import time
from datetime import date, datetime, timedelta
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from possition import P_handler
from strategy import AssetsConfig, GetPrices, Strategy
from dataclasses import asdict, dataclass

import json

from typs import P_T, Coin_T, CoinTicks, GetPrices_T, MarketData_T, Move, PossitionData, Tick_
STRATS_URL = 'https://script.google.com/macros/s/AKfycbzh0Jz267JZ_HXGatrE-oJj8fwPHqXAn3G_UkVJX8EJj8m7jSStWeTwa9wHXbFTEVx1Lw/exec?type=getdata'

DB = db.SessionLocal()


def get_db() -> Any:
    db = db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


cgClient = CoinGeckoAPI()

models.Base.metadata.create_all(bind=db.engine)


def checkActions(delay: int) -> str:
    time.sleep(delay)
    return 'dont sleeping'


def getUsersData(delay: int) -> Any:
    time.sleep(delay)
    res = requests.get(STRATS_URL)
    return res.json()


def getCoinsID(coin: MarketData_T) -> str:
    return coin['id']


def getInitialData(delay: int) -> Any:
    time.sleep(delay)
    usersData = getUsersData(0)
    defaultAssetsConfig = AssetsConfig(**usersData['defaultConfig']['assets'])
    defaultStratConfig = Strategy(**usersData['defaultConfig']['algoritem'])
    marketData = cgClient.get_coins_markets(defaultAssetsConfig.pairedCoin, per_page=defaultAssetsConfig.number_assets,
                                            page=1, order=defaultAssetsConfig.sort_method, sparkline=False)
    coinsKeys = list(map(getCoinsID, marketData))
    return defaultAssetsConfig, defaultStratConfig, coinsKeys, usersData['strats']


def setInitialCounter(args: GetPrices_T) -> List[Coin_T]:
    now = datetime.now()
    print('sssssss', now)
    UPDATED_PRICES = cgClient.get_price(**args)

    newPrices: List[Coin_T] = []
    for key in args['ids']:
        newPrices.append({"coin_id": key, "value": UPDATED_PRICES[key][args['vs_currencies']], "vs": args['vs_currencies']
                         if type(args['vs_currencies']) == str else args['vs_currencies'][0], "counter": 0, "positions": 0, 'last_updated': now})
    return newPrices


def deleteCoinFromDB(coin_id: str) -> None:
    DB.query(models.Coins).filter(models.Coins.coin_id == coin_id).delete()
    DB.query(models.CoinsMovments).filter(models.CoinsMovments.coin_id == coin_id).delete()
    DB.commit()


def mergeCoinsList(oldPrices: List[Coin_T], newPrices: List[Coin_T]) -> List[Coin_T]:
    joinedList: List[Coin_T] = []
    coinsToRefetch: List[Coin_T] = []
    coinsToFetchIds: List[str] = []
    deletedIds: list[str] = []
    for newPrice in newPrices:
        isInNew = False
        for oldPrice in oldPrices:
            if oldPrice['coin_id'] == newPrice['coin_id']:
                isInNew = True

        if isInNew == False:
            if oldPrice['counter'] <= 10 or oldPrice['positions'] > 0:
                coinsToRefetch.append(oldPrice)
                coinsToFetchIds.append(oldPrice['coin_id'])
            else:
                if oldPrice['coin_id'] not in deletedIds:
                    deleteCoinFromDB(oldPrice['coin_id'])
                    deletedIds.append(oldPrice['coin_id'])
        joinedList.append(newPrice)
    refreshedPrices = cgClient.get_price(coinsToFetchIds, newPrices[0]['vs'])
    for coin in coinsToRefetch:
        newCoin = coin.copy()
        oldPrice['counter'] = oldPrice['counter'] + 1
        newCoin['value'] = refreshedPrices[coin['coin_id']][coin['vs']]
        joinedList.append(newCoin)

    return joinedList


def returnObj(obj: Coin_T) -> Any:
    newObj = {}
    for k, v in obj.items():
        newObj[k] = v
    return newObj


def update_data_base_coins(prices: List[Coin_T]) -> List[Coin_T]:
    now = datetime.now()
    returnedCoins: List[Coin_T] = []
    for coin in prices:

        coin['last_updated'] = now
        isExist = DB.query(models.Coins).filter_by(coin_id=coin['coin_id']).scalar() is not None
        if isExist:
            updatedCoin: Coin_T = {"last_updated": now, "vs": coin['vs'], "value": coin['value'], "counter": coin['counter'], "positions": coin['positions']}
            DB.query(models.Coins).filter(models.Coins.coin_id == coin['coin_id']).update(returnObj(updatedCoin))
            updatedCoin['coin_id'] = coin['coin_id']
            returnedCoins.append(updatedCoin)
        else:
            returnedCoins.append(coin)

            DB.add(models.Coins(**coin))
    DB.commit()
    return returnedCoins


gaps = [5, 15, 30]


def setTimeGaps(Moves: List[Move], newMove: Move) -> Move:
    sum = 0.0
    lenght = len(Moves)

    for count, value in enumerate(Moves):
        if count >= lenght-1:
            break
        v = value.get('value')
        sum += v if type(v) == float else 0.0
        if (count+1) == 5:
            newMove['value_5'] = sum/5
        if (count+1) == 15:
            newMove['value_15'] = sum/15
        if (count+1) == 30:
            newMove['value_30'] = sum/30
    newMove['value_60'] = sum/60

    return newMove


def update_data_base_CoinsMovments(coins: List[Coin_T]) -> None:
    now = datetime.now()
    updatedList: List[Move] = []
    for coin in coins:
        dataList: List[Move] = []
        OBJECT: Move = {"coin_id": coin['coin_id'], "time_stemp": now, "vs": coin['vs'], "value": coin['value']}
        dataList.append(OBJECT)
        coinHistory = DB.query(models.CoinsMovments).filter(models.CoinsMovments.coin_id == coin['coin_id']).order_by(models.CoinsMovments.time_stemp.desc()).limit(59).all()

        for move in coinHistory:
            dataList.append({"value": move.value, "coin_id": move.coin_id, "time_stemp": move.time_stemp, "vs": move.vs})
        updatedMovment = setTimeGaps(dataList, OBJECT)
        updatedList.append(updatedMovment)
        DB.add(models.CoinsMovments(**updatedMovment))

    DB.commit()


def formatPandasTable(MERGED_COINS: List[Coin_T] | List[Any]) -> Any:
    coinTable = []
    columns = list(MERGED_COINS[0].keys())
    for coin in MERGED_COINS:
        coinTable.append(list(coin.values()))
    return pd.DataFrame(coinTable, columns=columns)


timeSig2DbValues = {
    "1m": "value",
    "5m": "value_5",
    "15m": "value_15",
    "30m": "value_30",
    "1h": "value_60"


}


def _Sum(S: int, E: int, L: List[tuple[float, Any]]) -> float | None:
    sumed: float = 0.0
    isFloat = True
    for x in range(S, E):
        if L[x][0] == None:
            isFloat = False
            break
        sumed += L[x][0]
    return sumed if isFloat else None


def makeTicks(coinsData: List[tuple[float, Any]], strat: Strategy) -> Any:
    LONG = strat.longEmaRatio
    SHORT = strat.shortEmaRatio

    Ticks: List[Tick_] = []
    toShort = False

    if len(coinsData)-LONG-2 < 1:
        toShort = True
    # print('len status : ', toShort)

  #  print('to short !!!!', toShort)

    for i in range(1,  len(coinsData)-2 if toShort else len(coinsData)-LONG-2):
        LV = _Sum(i, (i + 2 if toShort else LONG),  coinsData)
        SV = _Sum(i, (i + 1 if toShort else SHORT), coinsData)
        if (LV == None or SV == None):
            break
        if (type(LV) == float and type(SV) == float):
            longTick: float = LV/LONG
            shortTick: float = SV/SHORT

            tick: Tick_ = {
                "time_stemp": coinsData[i][1],
                "long_ema_val": longTick,
                "short_ema_val": shortTick,
                "is_long": False if shortTick > longTick else True,
                "is_short": True if shortTick > longTick else False
            }
        else:
            break
        # print('sssssssssss', tick)
        Ticks.append(tick)
       # print(Ticks)
    return Ticks


def scaneForDeals(strats: List[Strategy], coinsKeys: List[str]) -> Any:
   # print(' in scane for deals !!!')
    coinTableData = DB.query(models.CoinsMovments)
   # print(coinTableData)
    tsd: Dict[str, tuple[str, int]] = {
        "1m": ("models.CoinsMovments.value", 300),
        "5m": ("models.CoinsMovments.value_5", 200),
        "15m": ("models.CoinsMovments.value_15", 150),
        "30m": ("models.CoinsMovments.value_30", 100),
        "1h": ("models.CoinsMovments.value_60", 72)
    }
    ticksArrays = []
    for strat in strats:
        for coinName in coinsKeys:
            coinData = coinTableData.with_entities(eval(tsd[strat.baseTimeGap][0]), models.CoinsMovments.time_stemp).filter(
                models.CoinsMovments.coin_id == coinName).order_by(models.CoinsMovments.time_stemp.desc()).limit(tsd[strat.baseTimeGap][1]).all()
            if len(coinData) > 2:
                T = makeTicks(coinData, strat)
                if len(T) > 1:
                    ticksArrays.append({
                        "user_strat": strat,
                        "coin_id": coinName,
                        "ticks": T
                    })
   # print(ticksArrays)
    return ticksArrays


def validatePossitions(strats: list[Strategy]) -> list[Strategy]:
    rList: list[Strategy] = []
    for strat in strats:
        if strat.isActive and strat.max_open_trades >= strat.current_opend:
            rList.append(strat)
    return rList


pendingRange = {
    "1m": 5,
    "5m": 2,
    "15m": 1,
    "30m": 1,
    "1h": 1
}


def checkIfCrossingUp(T: List[CoinTicks]) -> List[PossitionData] | None:
    possitionsToOpen: List[PossitionData] = []
    for ct in T:
        if len(ct['ticks']) < 2:
            return None
        if ct['ticks'][0]['is_long'] and ct['ticks'][1]['is_short']:
            print('buy signal on: ', ct['coin_id'])
            possitionsToOpen.append({"coin_id": ct['coin_id'],
                                     "strat": ct['user_strat']
                                     })
    return possitionsToOpen


def checkIfCrossingDown(T: List[CoinTicks]) -> List[PossitionData] | None:
    possitionsToClose: List[PossitionData] = []
    for ct in T:
        if len(ct['ticks']) < 2:
            return None
        if ct['ticks'][0]['is_short'] and ct['ticks'][1]['is_long']:
            print('sell signal on: ', ct['coin_id'])
            possitionsToClose.append({"coin_id": ct['coin_id'],
                                     "strat": ct['user_strat']
                                      })
    return possitionsToClose


def openPossitions(pto: List[PossitionData], MERGED_COINS: List[Coin_T]) -> List[P_T]:
    POSSITIONS: List[P_T] = []
    for P in pto:
        ActionsData = DB.query(models.Actions).filter(models.Actions.UserID == P['strat'].userID, models.Actions.isOpen == True).all()
        NOT_OPEND = True
        for action in ActionsData:
            if action.CoinID == P['coin_id']:
                NOT_OPEND = False
        if NOT_OPEND:
            COIN_DATA: Coin_T | None = None
            for COIN in MERGED_COINS:
                if COIN['coin_id'] == P['coin_id']:
                    COIN_DATA = COIN
            if (COIN_DATA):
                POSSITIONS.append({'USER_STRAT': P['strat'], 'COIN_DATA': COIN_DATA, 'IS_EXIST': True})
            else:
                POSSITIONS.append({'USER_STRAT': P['strat'], 'COIN_DATA': None, 'IS_EXIST': False})
                # print('allready deleted !!! ', P['coin_id'])
    return POSSITIONS


def validatePBeforeActions(possitionsToOpen: Any, MERGED_COINS: Any) -> List[P_T]:
    EXISTING_P: List[P_T] = []
    NOT_EXISTING_P: List[P_T] = []
    if len(possitionsToOpen) > 0:
        result: List[P_T] = openPossitions(possitionsToOpen, MERGED_COINS)
        for r in result:
            if r['IS_EXIST']:
                EXISTING_P.append(r)
            else:
                NOT_EXISTING_P.append(r)
    return EXISTING_P


def clearOldDbData(delay: int) -> None:
    time.sleep(delay)
    table = DB.query(models.CoinsMovments)
    number_of_rows = table.count()
    num_of_deleted_rows = table.filter(models.CoinsMovments.time_stemp < datetime.now()-timedelta(hours=36)).delete()
    print('num of deleted rows: ', num_of_deleted_rows, 'out of: ', number_of_rows)
    DB.commit()


def mainEventLoop(PRICES: Any, coinsKeys: Any,  defaultAssetsConfig: Any, defaultStratConfig: Any,  strats: Any, delay: int) -> Any:

    # print(PRICES, coinsKeys,  defaultAssetsConfig, defaultStratConfig,  strats, delay)
    time.sleep(delay)
    print('main event loop')
    NEW_PRICES = setInitialCounter({'ids': coinsKeys, 'vs_currencies': defaultAssetsConfig.pairedCoin, 'precision': defaultAssetsConfig.precision})
    MERGED_COINS = mergeCoinsList(PRICES, NEW_PRICES)
    PRICES = update_data_base_coins(MERGED_COINS)
    # print(formatPandasTable(PRICES))
    update_data_base_CoinsMovments(PRICES)
    VALID_STRATS = validatePossitions([Strategy(**s) for s in strats])
    T = scaneForDeals(VALID_STRATS, coinsKeys)
    possitionsToOpen = checkIfCrossingUp(T)
    possitionsToClose = checkIfCrossingDown(T)
    if possitionsToOpen:
        EXISTING_P_to_open: List[P_T] = validatePBeforeActions(possitionsToOpen, MERGED_COINS)
        for valid_P in EXISTING_P_to_open:
            if (valid_P['COIN_DATA']['coin_id']):
                P_handler(valid_P['USER_STRAT'], valid_P['COIN_DATA']).open()
            else:
                print('coin T type not found ', valid_P, "\n", "type: ", type(valid_P['COIN_DATA']))
    if possitionsToClose:
        EXISTING_P_to_close = validatePBeforeActions(possitionsToClose, MERGED_COINS)

        for valid_P in EXISTING_P_to_close:
            if (valid_P['COIN_DATA']['coin_id']):
                P_handler(valid_P['USER_STRAT'], valid_P['COIN_DATA']).close()
            else:
                print('coin T type not found ', valid_P, "\n", "type: ", type(valid_P['COIN_DATA']))
    return PRICES


def main() -> None:
    # ##print('in main script .....')

    defaultAssetsConfig, defaultStratConfig, coinsKeys, strats = getInitialData(0)
    PRICES = setInitialCounter({'ids': coinsKeys, 'vs_currencies': defaultAssetsConfig.pairedCoin, 'precision': defaultAssetsConfig.precision})
    clearOldDbData(0)
    defaultAssetsConfig.show()
    defaultStratConfig.show()
    while True:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:

                marketData = executor.submit(getInitialData, defaultAssetsConfig.refresh_time_period)
                executor.submit(clearOldDbData, 60*60*6)
                defaultAssetsConfig, defaultStratConfig, coinsKeys, strats = marketData.result()
                mainLoopRes = executor.submit(mainEventLoop, PRICES, coinsKeys,  defaultAssetsConfig, defaultStratConfig,  strats,  defaultAssetsConfig.refresh_time_period * 2)
                PRICES = mainLoopRes.result()
        except KeyboardInterrupt:
            executor.shutdown(cancel_futures=True)
