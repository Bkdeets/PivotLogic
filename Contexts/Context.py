from abc import ABC, abstractmethod

# Abstract Class that specifies methods common among Backtest, PaperTrade, and live Trade

class Context(ABC):

    def __init__(self):
        return

    @abstractmethod
    def buy(self, ticker, order_type, units, limit_price=None):
        return

    @abstractmethod
    def sell(self, ticker, order_type, units, limit_price=None):
        return
