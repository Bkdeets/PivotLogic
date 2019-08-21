from Tideline.Contexts.Context import Context
import alpaca_trade_api as tradeapi
import time
import logging


# class to implement Context methods that execute in a paper trading environment


class PaperTrade(Context):

    isPaper = True
    TEST_UNIVERSE = ['AAPL', 'GOOG', 'MMM', 'TSLA', 'SPWR', 'SIRI', 'F', 'RRR', 'ACN']
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.id = 1
        super().__init__()

    def buy(self, ticker, order_type, units, limit_price=None):
        return self.get_api().submit_order(
            symbol=ticker,
            qty=units,
            side='buy',
            type='market',
            time_in_force='day',
        )

    def bulkBuy(self, buys, wait=30):
        for order in buys:
            try:
                self.logger.info(f'submit(buy): {order}')
                self.buy(
                    order['symbol'],
                    'market',
                    order['qty'])
            except Exception as e:
                self.logger.error(e)
        count = wait
        while count > 0 and len(buys) > 0:
            pending = self.get_api().list_orders()
            if len(pending) == 0:
                self.logger.info(f'all buy orders done')
                break
            self.logger.info(f'{len(pending)} buy orders pending...')
            time.sleep(1)
            count -= 1

    def sell(self, ticker, order_type, units, limit_price=None):
        return self.get_api().submit_order(
            symbol=ticker,
            qty=units,
            side='sell',
            type=order_type,
            time_in_force='day',
        )

    def bulkSell(self, sells, wait=30):
        for order in sells:
            try:
                self.logger.info(f'submit(sell): {order}')
                self.sell(
                    order['symbol'],
                    'market',
                    order['qty'])

            except Exception as e:
                self.logger.error(e)
        count = wait
        while count > 0 and len(sells) > 0:
            pending = self.get_api().list_orders()
            if len(pending) == 0:
                self.logger.info(f'all sell orders done')
                break
            self.logger.info(f'{len(pending)} sell orders pending...')
            time.sleep(1)
            count -= 1

    def get_api(self):
        return tradeapi.REST(
            key_id='PKIG33U7XYR8ECVMMF4A',
            secret_key='e83t4Cn5oY07EENvlhRKwjKyTbykd8wn8Phesmze',
            base_url='https://paper-api.alpaca.markets')

    def get_clock(self):
        return self.get_api().get_clock()

    def get_account(self):
        return self.get_api().get_account()

    def list_positions(self):
        return self.get_api().list_positions()

    def get_barset(self, symbols, timeframe, limit, start, end):
        return self.get_api().get_barset(
            symbols,
            timeframe,
            limit=limit,
            start=start,
            end=end)

    def trade(self, orders, wait=30):
        '''This is where we actually submit the orders and wait for them to fill.
        Waiting is an important step since the orders aren't filled automatically,
        which means if your buys happen to come before your sells have filled,
        the buy orders will be bounced. In order to make the transition smooth,
        we sell first and wait for all the sell orders to fill before submitting
        our buy orders.
        '''

        # process the sell orders first
        sells = [o for o in orders if o['side'] == 'sell']
        self.bulkSell(sells)

        # process the buy orders next
        buys = [o for o in orders if o['side'] == 'buy']
        self.bulkBuy(buys)