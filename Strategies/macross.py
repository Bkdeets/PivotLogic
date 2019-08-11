import alpaca_trade_api as tradeapi
from SDK import Utilities as util
from Contexts.Backtest import Backtest
from Contexts.LiveTrade import LiveTrade
from Contexts.PaperTrade import PaperTrade
import pandas as pd
import time
import logging
from Indicators.sma import SMA
from Strategies.strategy import Strategy
import matplotlib.pyplot as plt


class MACrossPaper(Strategy):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

        self.period = 20
        self.NY = 'America/New_York'

        # TODO: create new api key and hide it
        self.api = None


    def sort_func(self, sma_obj):
        return sma_obj.sma[-1]

    def rank(self, smas):
        return sorted(smas, key=self.sort_func)

    def checkToSell(self, sma, price):
        if sma > price:
            return True
        return False

    def checkToBuy(self, smas):
        toBuy = []
        for sma in smas:
            if sma.sma < sma.prices.iloc[-1,:].close:
                toBuy.append(sma)
        return toBuy


    def get_orders(self, context, prices_df, position_size=200, max_positions=5):

        # rank the stocks based on the indicators.
        smas = []
        symbols = set()
        for col in prices_df.columns:
            symbols.add(col[0])

        c = 0
        for symbol in symbols:
            sma = SMA(self.period, prices_df[symbol].dropna(), symbol)
            c += 1
            smas.append(sma)

        ranked = self.rank(smas)
        ranked = ranked[::-1]

        to_buy = []
        to_sell = []
        account = context.get_account()

        # now get the current positions and see what to buy,
        # what to sell to transition to today's desired portfolio.
        positions = context.list_positions()
        self.logger.info(positions)

        holdings = {p.symbol: p for p in positions}
        holding_symbols = list(holdings.keys())

        if holdings:
            to_sell = [sma.ticker for sma in smas if sma.sma[-1] > sma.prices.iloc[-1,:].close and sma.ticker in holding_symbols]

        ranked = self.checkToBuy(ranked[:max_positions])
        to_buy = [sma.ticker for sma in ranked]
        to_buy = to_buy[:len(to_sell)-1]
        orders = []

        # if a stock is in the portfolio, and not in the desired
        # portfolio, sell it
        for symbol in to_sell:
            shares = holdings[symbol].qty
            orders.append({
                'symbol': symbol,
                'qty': shares,
                'side': 'sell',
            })
            self.logger.info(f'order(sell): {symbol} for {shares}')

        # likewise, if the portfoio is missing stocks from the
        # desired portfolio, buy them. We sent a limit for the total
        # position size so that we don't end up holding too many positions.
        max_to_buy = max_positions - (len(positions) - len(to_sell))
        for symbol in to_buy:
            if max_to_buy <= 0:
                break
            shares = position_size // float(prices_df[symbol].close.values[-1])
            if shares == 0.0:
                continue
            orders.append({
                'symbol': symbol,
                'qty': shares,
                'side': 'buy',
            })
            self.logger.info(f'order(buy): {symbol} for {shares}')
            max_to_buy -= 1
        return orders


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
        for order in sells:
            try:
                self.logger.info(f'submit(sell): {order}')
                self.api.submit_order(
                    symbol=order['symbol'],
                    qty=order['qty'],
                    side='sell',
                    type='market',
                    time_in_force='day',
                )
            except Exception as e:
                self.logger.error(e)
        count = wait
        while count > 0 and len(sells) > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                self.logger.info(f'all sell orders done')
                break
            self.logger.info(f'{len(pending)} sell orders pending...')
            time.sleep(1)
            count -= 1

        # process the buy orders next
        buys = [o for o in orders if o['side'] == 'buy']
        for order in buys:
            try:
                self.logger.info(f'submit(buy): {order}')
                self.api.submit_order(
                    symbol=order['symbol'],
                    qty=order['qty'],
                    side='buy',
                    type='market',
                    time_in_force='day',
                )
            except Exception as e:
                self.logger.error(e)
        count = wait
        while count > 0 and len(buys) > 0:
            pending = self.api.list_orders()
            if len(pending) == 0:
                self.logger.info(f'all buy orders done')
                break
            self.logger.info(f'{len(pending)} buy orders pending...')
            time.sleep(1)
            count -= 1


    def getTradableAssets(self, context):
        if context.isPaper:
            return context.TEST_UNIVERSE
        assets = []
        for asset in self.api.list_assets(asset_class='us_equity', status='active'):
            asset = self.api.get_asset(asset.symbol)
            if asset.tradable:
                assets.append(asset.symbol)
        return assets


    def beginTrading(self, context):
        logging.info('start running')
        while True:
            clock = context.get_clock()
            now = clock.timestamp
            if clock.is_open:
                tradeable_assets = self.getTradableAssets(context)

                self.logger.info('Getting prices...')
                start = pd.Timestamp.now() - pd.Timedelta(days=2)
                prices_df = util.get_prices(context, tradeable_assets, timeframe='5Min', start=start)

                self.logger.info('Getting orders...')
                orders = self.get_orders(context, prices_df)

                self.logger.info(orders)
                self.trade(orders)

                self.logger.info(context.get_account())

                self.logger.info(f'done for {clock.timestamp}')

            time.sleep(60*5)


    beginTrading(PaperTrade())