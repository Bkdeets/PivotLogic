import logging
import pandas as pd
from SDK import Utilities as util
import time


'''
This will be a lambda function that hits a 'Fargate' thing which handles the long-running 
trade thread...

The trade thread stops eod (4:00 eastern) and the state is saved then queued
for execution whenever the market opens tomorrow
'''
def beginTrading(self, context, strategy_instance):
    logging.info('start running')
    timeframe_map = {
        '1Min': 1,
        '5Min': 5,
        'day' : 5
    }

    sleep = timeframe_map.get(strategy_instance.params.timeframe)

    # This user notation is just for demo purposes,
    # we will have to call backend to see if strategy for user is active
    user = User()
    while user.hasStrategyActive(strategy_instance.id):
        clock = context.get_clock()
        now = clock.timestamp
        if clock.is_open:
            tradeable_assets = strategy_instance.params.assets

            strategy_instance.logger.info('Getting prices...')
            start = pd.Timestamp.now() - pd.Timedelta(days=2)
            prices_df = util.get_prices(
                context,
                tradeable_assets,
                timeframe=strategy_instance.params.timeframe,
                start=start)

            strategy_instance.logger.info('Getting orders...')
            orders = strategy_instance.get_orders(context, prices_df)

            strategy_instance.logger.info(orders)
            strategy_instance.trade(orders)
            strategy_instance.logger.info(context.get_account())
            strategy_instance.logger.info(f'done for {clock.timestamp}')

        time.sleep(60 * sleep)

# Dummy user class for now
class User:
    def hasStrategyActive(self, id):
        return True