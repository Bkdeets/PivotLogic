from Contexts.Context import Context


# class to implement Context methods that execute in a backtesting environment

# TODO: Set up a mock api with same methods as trade api
# TODO: Get prices using paper trading api

class Backtest(Context):

    def __init__(self):
        super().__init__()

    def buy(self, ticker, order_type, units, limit_price=None):
        return

    def sell(self, ticker, order_type, units, limit_price=None):
        return

    def get_api(self):
        return
