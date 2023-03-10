from typing import Any, Dict
from sqlalchemy import Column, DateTime,  Integer, Float, String, DATE, Boolean, ForeignKey
from sqlalchemy.orm import relationship


from db import Base
Base = Base


class Actions(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Time = Column(DateTime)
    UserID = Column(String, unique=False)
    CoinID = Column(String, ForeignKey('coins.coin_id'))
    ActionType = Column(String)
    time_of_atart = Column(DateTime)
    time_of_end = Column(DateTime, nullable=True)
    value_of_start = Column(Float)
    value_of_end = Column(Float, nullable=True)
    start_stuck_value = Column(Float, nullable=True)
    end_stuck_value = Column(Float, nullable=True)
    profit_lost_numeric = Column(Float, nullable=True)
    normelized_commission = Column(Float, nullable=True)
    isOpen = Column(Boolean)


class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    Time = Column(DATE)
    UserID = Column(String)
    CoinID = Column(String)
    HashKey = Column(String)


class Coins(Base):
    __tablename__ = "coins"
    coin_id = Column(String, primary_key=True, index=True)
    last_updated = Column(DateTime)
    vs = Column(String)
    value = Column(Float)
    counter = Column(Integer)
    positions = Column(Integer)
    coins_movments = relationship('CoinsMovments', backref='author')
    actions = relationship('Actions', backref='author')


class CoinsMovments(Base):
    __tablename__ = "coins_movments"
    movment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coin_id = Column(String, ForeignKey('coins.coin_id'), index=True)
    time_stemp = Column(DateTime)
    vs = Column(String)
    value = Column(Float)
    value_5 = Column(Float, nullable=True)
    value_15 = Column(Float, nullable=True)
    value_30 = Column(Float, nullable=True)
    value_60 = Column(Float, nullable=True)

    # def __init__(self, movment_id, coin_id, time_stemp, vs, value, value_5, value_15, value_30, value_60) -> None:
    #     self.movment_id = movment_id
    #     self.coin_id = coin_id
    #     self.time_stemp = time_stemp
    #     self.vs = vs
    #     self.value = value
    #     self.value_5 = value_5
    #     self.value_15 = value_15
    #     self.value_30 = value_30
    #     self.value_60 = value_60

    def __repr__(self) -> str:
        x = "movment_id:", self.movment_id, "coin_id:", self.coin_id,
        "time_stemp:",  self.time_stemp,
        "vs:", self.vs,
        "value:",  self.value,
        "value_5:",  self.value_5,
        "value_15:",   self.value_15,
        "value_30:",  self.value_30,
        "value_60:",  self.value_60
        return str(x)
