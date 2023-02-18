from typing import Any, Generator, List, Dict, NewType, NotRequired, TypeVar, TypedDict, Unpack
import pandas as pd
import concurrent.futures
import requests
import models
import db
import time
from datetime import date, datetime
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from strategy import AssetsConfig, GetPrices, Strategy
from dataclasses import asdict, dataclass
import json
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


class Coin_T(TypedDict):
    coin_id: NotRequired[str]
    last_updated: datetime
    vs: str
    value: float
    counter: NotRequired[int]
    positions: NotRequired[int]


class MarketData_T(TypedDict):
    id: str


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
    return defaultAssetsConfig, defaultStratConfig, coinsKeys


class GetPrices_T(TypedDict):
    ids: list[str]
    vs_currencies:  list[str] | str
    precision: NotRequired[int]
    include_market_cap: NotRequired[bool]
    include_24hr_vol: NotRequired[bool]
    include_24hr_change: NotRequired[bool]
    include_last_updated_at: NotRequired[bool]
    last_updated: NotRequired[bool]


ARGS = {'ids': ['tether', 'bitcoin', 'binance-usd', 'ethereum', 'usd-coin', 'weth', 'ripple', 'blur', 'dogecoin', 'binancecoin', 'matic-network', 'litecoin', 'solana', 'fantom', 'cardano', 'shiba-inu', 'tron',
                'the-graph', 'optimism', 'aptos', 'polkadot', 'chainlink', 'oasis-network', 'the-sandbox', 'dydx', 'singularitynet', 'lido-dao', 'avalanche-2', 'hashflow', 'mina-protocol'], 'vs_currencies': 'usd', 'precision': 4}
PRICESUU = {'aptos': {'usd': 14.7739}, 'avalanche-2': {'usd': 18.5493}, 'binancecoin': {'usd': 302.7306}, 'binance-usd': {'usd': 1.0004}, 'bitcoin': {'usd': 22799.0969}, 'blur': {'usd': 0.9297}, 'cardano': {'usd': 0.3892}, 'chainlink': {'usd': 6.9096}, 'dogecoin': {'usd': 0.0861}, 'dydx': {'usd': 2.8351}, 'ethereum': {'usd': 1578.5287}, 'fantom': {'usd': 0.5376}, 'hashflow': {'usd': 0.6956}, 'lido-dao': {'usd': 2.7553}, 'litecoin': {'usd': 97.2818}, 'matic-network': {'usd': 1.2707}, 'mina-protocol': {'usd': 1.1334}, 'oasis-network': {'usd': 0.0816}, 'optimism': {'usd': 2.5448}, 'polkadot': {'usd': 6.2944}, 'ripple': {'usd': 0.386}, 'shiba-inu': {'usd': 0.0}, 'singularitynet': {'usd': 0.4267}, 'solana': {'usd': 22.3211}, 'tether': {'usd': 1.0005}, 'the-graph': {'usd': 0.1789},
            'the-sandbox': {'usd': 0.7175}, 'tron': {'usd': 0.0694}, 'usd-coin': {'usd': 1.0004}, 'weth': {'usd': 1578.9557}}


def setInitialCounter(args: GetPrices_T) -> List[Coin_T]:
    now = datetime.now()
   # #print(args)
    UPDATED_PRICES = cgClient.get_price(**args)
   # #print(UPDATED_PRICES)
    newPrices: List[Coin_T] = []
    for key in args['ids']:
        newPrices.append({"coin_id": key, "value": UPDATED_PRICES[key][args['vs_currencies']], "vs": args['vs_currencies']
                         if type(args['vs_currencies']) == str else args['vs_currencies'][0], "counter": 0, "positions": 0, 'last_updated': now})
    return newPrices


def deleteCoinFromDB(coin_id: str, coin: Any) -> None:
    print('deleting coins data !!!!  ', coin_id)
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
        # f = {'coin_id': 'wrapped-bitcoin', 'value': 24532.00871566, 'vs': 'usd', 'counter': 0, 'positions': 0, 'last_updated': datetime.datetime(2023, 2, 18, 16, 34, 2, 774525)}
        # print(isInNew == False, oldPrice['counter'] <= 10, oldPrice['positions'] > 0)
        # print(isInNew == False and (oldPrice['counter'] <= 10 or oldPrice['positions'] > 0))
        if isInNew == False:
            if oldPrice['counter'] <= 10 or oldPrice['positions'] > 0:
                print('in coin to refresh !!!')
                coinsToRefetch.append(oldPrice)
                coinsToFetchIds.append(oldPrice['coin_id'])
            else:
                if oldPrice['coin_id'] not in deletedIds:
                    deleteCoinFromDB(oldPrice['coin_id'], oldPrice)
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
            print('else new coin !!!!!', coin)
            returnedCoins.append(coin)

            DB.add(models.Coins(**coin))
    DB.commit()
    return returnedCoins


gaps = [5, 15, 30]


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


# s = [{'coin_id': 'tether', 'time_stemp': datetime.datetime(2023, 2, 16, 17, 8, 54, 666946), 'vs': 'usd', 'value': 0.99950526}, < models.CoinsMovments object at 0x000002B46347C1D0 > , < models.CoinsMovments object at 0x000002B46347E6D0 > ] {'coin_id': 'tether', 'time_stemp': datetime.datetime(2023, 2, 16, 17, 8, 54, 666946), 'vs': 'usd', 'value': 0.99950526}


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

    print(formatPandasTable(updatedList))
    DB.commit()


def formatPandasTable(MERGED_COINS: List[Coin_T] | List[Any]) -> Any:
    coinTable = []
    columns = list(MERGED_COINS[0].keys())
    for coin in MERGED_COINS:
        coinTable.append(list(coin.values()))
    return pd.DataFrame(coinTable, columns=columns)


def main() -> None:
    # print('in main script .....')

    defaultAssetsConfig, defaultStratConfig, coinsKeys = getInitialData(0)
    PRICES = setInitialCounter({'ids': coinsKeys, 'vs_currencies': defaultAssetsConfig.pairedCoin, 'precision': defaultAssetsConfig.precision})

    # #print(coinsKeys)
    defaultAssetsConfig.show()
    defaultStratConfig.show()
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                marketData = executor.submit(getInitialData, defaultAssetsConfig.refresh_time_period)
                defaultAssetsConfig, defaultStratConfig, coinsKeys = marketData.result()
            except KeyboardInterrupt:
                print('error i n while loop ', ValueError)
            NEW_PRICES = setInitialCounter({'ids': coinsKeys, 'vs_currencies': defaultAssetsConfig.pairedCoin, 'precision': defaultAssetsConfig.precision})

            MERGED_COINS = mergeCoinsList(PRICES, NEW_PRICES)
            # print('**************************MERGED COINS !!!!!************************\n', formatPandasTable(MERGED_COINS))
            PRICES = update_data_base_coins(MERGED_COINS)
            # print(PRICES)
            update_data_base_CoinsMovments(PRICES)
            print(formatPandasTable(MERGED_COINS))

    #  #print(users_data.result())


# main()
