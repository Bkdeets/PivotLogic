from abc import ABC, abstractmethod, abstractproperty
import alpaca_trade_api as tradeapi
from SDK import Utilities as util
from Contexts.Backtest import Backtest
from Contexts.LiveTrade import LiveTrade
from Contexts.PaperTrade import PaperTrade
import pandas as pd
import time
import logging
from Indicators.sma import SMA
import matplotlib.pyplot as plt

# Abstract Class that specifies methods common among Backtest, PaperTrade, and live Trade
# https://github.com/alpacahq/alpaca-trade-api-python

class Strategy(ABC):

    def __init__(self):
        return

    @property
    @abstractmethod
    def params(self):
        return

    @abstractmethod
    def sort_func(self, indicator_obj):
        return

    @abstractmethod
    def rank(self, aList):
        return

    @abstractmethod
    def checkToBuy(self, smas):
        return

    @abstractmethod
    def checkToSell(self, indicator, price):
        return

    @abstractmethod
    def get_orders(self, context, prices_df, position_size, max_positions):
        return



