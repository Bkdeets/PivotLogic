from abc import ABC, abstractmethod


# Abstract Class that specifies methods common among Backtest, PaperTrade, and live Trade
# https://github.com/alpacahq/alpaca-trade-api-python

class Strategy(ABC):

    def __init__(self):
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



