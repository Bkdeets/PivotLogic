import alpaca_trade_api as tradeapi
from SDK import Utilities as util
from Contexts.Backtest import Backtest
from Contexts.LiveTrade import LiveTrade
from Contexts.PaperTrade import PaperTrade
import pandas as pd
import time
import logging
from Indicators.rsi import RSI
import matplotlib.pyplot as plt



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

period = 20
NY = 'America/New_York'

# TODO: create new api key and hide it
api = None


def sort_func(rsi_obj):
    return rsi_obj.RSI[-1]
def rank(RSIs):
    return sorted(RSIs, key=sort_func)
def checkToSell(RSI):
    if RSI < 70:
        return True
    return False


def get_orders(api, prices_df, position_size=200, max_positions=5):

    # rank the stocks based on the indicators.
    RSIs = []
    symbols = set()
    for col in prices_df.columns:
        symbols.add(col[0])

    c = 0
    for symbol in symbols:
        rsi = RSI(period, prices_df[symbol].dropna(), symbol)
        #print(symbol, rsi.RSI[-1], c)
        c += 1
        RSIs.append(rsi)

    ranked = rank(RSIs)
    ranked = ranked[::-1]

    to_buy = []
    to_sell = []
    account = api.get_account()

    # now get the current positions and see what to buy,
    # what to sell to transition to today's desired portfolio.
    positions = api.list_positions()
    logger.info(positions)

    holdings = {p.symbol: p for p in positions}
    holding_symbols = list(holdings.keys())

    if holdings:
        to_sell = [RSI.ticker for RSI in RSIs if RSI.RSI[-1] < 70 and RSI.ticker in holding_symbols]

    to_buy = [RSI.ticker for RSI in ranked[:max_positions]]
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
        logger.info(f'order(sell): {symbol} for {shares}')

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
        logger.info(f'order(buy): {symbol} for {shares}')
        max_to_buy -= 1
    return orders


def trade(orders, wait=30):
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
            logger.info(f'submit(sell): {order}')
            api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='sell',
                type='market',
                time_in_force='day',
            )
        except Exception as e:
            logger.error(e)
    count = wait
    while count > 0 and len(sells) > 0:
        pending = api.list_orders()
        if len(pending) == 0:
            logger.info(f'all sell orders done')
            break
        logger.info(f'{len(pending)} sell orders pending...')
        time.sleep(1)
        count -= 1

    # process the buy orders next
    buys = [o for o in orders if o['side'] == 'buy']
    for order in buys:
        try:
            logger.info(f'submit(buy): {order}')
            api.submit_order(
                symbol=order['symbol'],
                qty=order['qty'],
                side='buy',
                type='market',
                time_in_force='day',
            )
        except Exception as e:
            logger.error(e)
    count = wait
    while count > 0 and len(buys) > 0:
        pending = api.list_orders()
        if len(pending) == 0:
            logger.info(f'all buy orders done')
            break
        logger.info(f'{len(pending)} buy orders pending...')
        time.sleep(1)
        count -= 1


def getTradableAssets(context):
    if context.isPaper():
        return context.TEST_UNIVERSE
    assets = []
    for asset in api.list_assets(asset_class='us_equity', status='active'):
        asset = api.get_asset(asset.symbol)
        if asset.tradable:
            assets.append(asset.symbol)
    return assets


def beginTrading(context):
    logging.info('start running')
    while True:
        clock = context.get_clock()
        now = clock.timestamp
        if clock.is_open:
            tradeable_assets = getTradableAssets(context)

            logger.info('Getting prices...')
            prices_df = util.get_prices(tradeable_assets)

            logger.info('Getting orders...')
            orders = get_orders(context, prices_df)

            logger.info(orders)
            trade(orders)

            logger.info(context.get_account())

            logger.info(f'done for {clock.timestamp}')

        time.sleep(60*5)


beginTrading(PaperTrade)