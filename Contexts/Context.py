from abc import ABC, abstractmethod

# Abstract Class that specifies methods common among Backtest, PaperTrade, and live Trade
# https://github.com/alpacahq/alpaca-trade-api-python

class Context(ABC):

    isPaper = False

    def __init__(self):
        return

    @abstractmethod
    def buy(self, ticker, order_type, units, limit_price=None):
        return

    @abstractmethod
    def sell(self, ticker, order_type, units, limit_price=None):
        return

    @abstractmethod
    def get_api(self):
        return

    @abstractmethod
    def get_clock(self):
        return

    @abstractmethod
    def get_account(self):
        return

    @abstractmethod
    def list_positions(self):
        return

    @abstractmethod
    def get_barset(self, symbols, timeframe, limit, start, end):
        return