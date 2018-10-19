import logging
import time

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def get_now(pair):
    """
    Return last info for crypto currency pair
    :param pair:
    :return:
    """
    url_key = "t" + pair
    return requests.get(('https://api.bitfinex.com/v2/ticker/' + url_key)).json()


def get_past(pair, period, days_history=30):
    """
    Return historical charts data from poloniex.com
    :param pair:
    :param period: 1m, 5m, 15m, 30m, 1h, 4h, 1D, 1M
    :param days_history:
    :return:
    """
    periods_dict = {300: '5m', 900: '15m', 1800: '30m', 7200: None, 14400: '4h', 86400: '1D'}

    url_key = '/trade:' + periods_dict[period] + ':' + 't' + pair + '/hist'
    end = int(time.time()) * 1000
    start = end - (24 * 60 * 60 * days_history * 1000)
    params = {'end': end, 'start': start}
    response = requests.get(('https://api.bitfinex.com/v2/candles' + url_key), params=params)

    return response.json()


def convert_pair_bitfinex(pair):
    converted = "{0}{1}".format(*pair.split('_'))
    logger.warning('Warning: Pair was converted to ' + converted)
    return converted


def load_dataframe(pair, period, days_history=30):
    """
    Return historical charts data from poloniex.com
    :param pair: ex:'BTCUSD'
    :param period: 1m, 5m, 15m, 30m, 1h, 4h, 1D,
    :param days_history:
    :param timeframe:
    :return:
    """

    try:
        data = get_past(convert_pair_bitfinex(pair), period, days_history)
    except Exception as ex:
        raise ex

    if 'error' in data:
        raise Exception("Bad response: {}".format(data['error']))

    df = pd.DataFrame(data, columns=('date', 'open',
                                     'hight', 'low',
                                     'close', 'volume'))
    df = df.iloc[::-1]
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df = df.set_index(['date'])
    df = df[['close', 'hight', 'low', 'open', 'volume']]

    return df
