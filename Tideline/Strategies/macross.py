import logging
from Tideline.Indicators import SMA
from Tideline.Strategies import Strategy


class MACrossPaper(Strategy):

    def __init__(self, params):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

        self.NY = 'America/New_York'
        self.id = 1

        # TODO: create new api key and hide it
        self.api = None
        self.params = params


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
            sma = SMA(self.params.period, prices_df[symbol].dropna(), symbol)
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
