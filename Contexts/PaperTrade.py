from Contexts.Context import Context
import alpaca_trade_api as tradeapi


# class to implement Context methods that execute in a paper trading environment


class PaperTrade(Context):

    TEST_UNIVERSE = ['AAPL', 'GOOG', 'MMM', 'TSLA', 'SPWR', 'SIRI', 'F', 'RRR', 'ACN']

    def __init__(self):
        super().__init__()

    def buy(self, ticker, order_type, units, limit_price=None):
        return

    def sell(self, ticker, order_type, units, limit_price=None):
        return

    def get_api(self):
        return tradeapi.REST(
            key_id='PKIG33U7XYR8ECVMMF4A',
            secret_key='e83t4Cn5oY07EENvlhRKwjKyTbykd8wn8Phesmze',
            base_url='https://paper-api.alpaca.markets')

    def get_clock(self):
        return self.get_api().get_clock()

    def get_account(self):
        return self.get_api().get_account()