from typing import Any, Dict, List
from fastapi import FastAPI, Header, Path, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import db
from datetime import date, datetime
import models
import requests
import main
import asyncio

import time
import threading

import uvicorn

app = FastAPI()


class BackGroundScript(threading.Thread):
    def run(self) -> None:
        main.main()


SUPPORTED_CURRENCIES = 'https://api.coingecko.com/api/v3/simple/supported_vs_currencies'
DB = db.SessionLocal()
models.Base.metadata.create_all(bind=db.engine)
app = FastAPI()

# background_tasks = BackgroundTasks
# background_tasks.add_task(self=background_tasks)
# # mainScript = main.main


def run_background_tasks(tasks: Any) -> None:
    tasks()


# @app.post("startup")
# async def startup_script():
#     print('start up.....')
#     background_tasks.add_task(self=background_tasks,main.main)
#     run_background_tasks(background_tasks)
#     return print({"message": "Notification sent in the background"})


@app.get('/')
def home() -> Dict[str, str]:
    return {"data": "test"}


@app.get('/supported_vs_currencies')
def supported_vs_currencies() -> Any:
    res = requests.get(SUPPORTED_CURRENCIES)
    return res.json()


@app.get('/getusser/{id}')
def get_usser(id: int = Path(None,)) -> Any:
    return {"data": "null"}


@app.get('/actions/{user_id}')
def getActions(user_id: str | int) -> Any:
    actions = [
        {'id': 19827489746, 'Time':  datetime.strptime('19/09/22 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'kashdoasufoausgadg', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart':  datetime.strptime('19/09/22 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end':  datetime.strptime('19/09/22 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 1.3451, 'value_of_end': 1.5431},
        {'id': 99827489746, 'Time':  datetime.strptime('19/10/22 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'kashdoasufoausgadg', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart': datetime.strptime('19/10/22 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end': datetime.strptime('19/10/22 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 2.3451, 'value_of_end': 2.5431},
        {'id': 45627489746, 'Time': datetime.strptime('19/01/23 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'kashdoasufoausgadg', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart':  datetime.strptime('19/01/23 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end':  datetime.strptime('19/01/23 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 2.4451, 'value_of_end': 1.5431},
        {'id': 87827489746, 'Time':  datetime.strptime('03/02/23 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'kashdoasufoausgadg', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart': datetime.strptime('03/02/23 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end':  datetime.strptime('03/02/23 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 1.3451, 'value_of_end': 4.5431},
        {'id': 45627489746, 'Time': datetime.strptime('19/01/23 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'sdfhgdfgudtu', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart':  datetime.strptime('19/01/23 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end':  datetime.strptime('19/01/23 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 2.4451, 'value_of_end': 1.5431},
        {'id': 87827489746, 'Time':  datetime.strptime('03/02/23 13:55:26', '%d/%m/%y %H:%M:%S'), 'UserID': 'sdfhgdfgudtu', 'CoinID': 'bitcoin', 'isOpen': False,
         'ActionType': 'buy', 'time_of_atart': datetime.strptime('03/02/23 13:56:26', '%d/%m/%y %H:%M:%S'), 'time_of_end':  datetime.strptime('03/02/23 14:56:26', '%d/%m/%y %H:%M:%S'), 'value_of_start': 1.3451, 'value_of_end': 4.5431},

    ]
    actionsNum = DB.query(models.Actions).count()
    if actionsNum == 0:
        for action in actions:
            DB.add(models.Actions(**action))
        DB.commit()
    else:
        print(f"{actionsNum} actions in db....")

    if user_id == "all":
        actions_ = DB.query(models.Actions).all()
        print(actions_)
        return actions_
    else:
        actions_ = DB.query(models.Actions).filter_by(
            UserID=user_id).all()
        return actions_


@app.get('/movments/{coin_id}')
def getMovments(coin_id: str = Path(None,)) -> Any:
    if coin_id == "all":
        movments = DB.query(models.CoinsMovments).all()
        print(movments)
        return movments
    else:
        movments = DB.query(models.CoinsMovments).filter_by(
            coin_id=coin_id).all()
        return movments


@app.get('/coins')
def getCoins() -> Any:
    coins = DB.query(models.Coins).all()
    print(coins)
    return coins

    # if __name__ == "__main__":
    #     import uvicorn
    #     uvicorn.run(app, host="0.0.0.0", port=8000,  )
if __name__ == '__main__':
    t = BackGroundScript()
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
