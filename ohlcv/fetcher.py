import datetime
import math
import pprint
import time

import ccxt
import os

import pickle

import tqdm


class OHLCVFetcher:

    def __init__(self, exchange, symbols, basepath=None, since=None,
                 timeframes=None):

        if isinstance(exchange, ccxt.Exchange):
            self.exchange = exchange
            self.exchangeId = exchange.id
        else:
            self.exchange = getattr(ccxt, exchange)()
            self.exchangeId = exchange
        exchange.load_markets()

        if not self.exchange.hasFetchOHLCV:
            raise NoOHLCVSupportError(
                "The exchange '{}' has no OHLCV support.".format(
                    self.exchangeId)
            )

        self.basepath = basepath
        if isinstance(symbols, str):
            symbols = [symbols]
        self.symbols = symbols

        if timeframes is None:
            self.timeframes = ['1m', '1h', '1d', '1M', '1y']
        else:
            if isinstance(timeframes, str):
                timeframes = [timeframes]
            self.timeframes = timeframes

        self.ohlcv_types = ['timestamp', 'open', 'high', 'low', 'close',
                            'volume']

        if since is None:
            self.since = 1
        else:
            self.since = since
        self.previous_fetch = None

        self.latest_timestamp = None  # for live fetches

        self.estimators = {}
        self.tmp_values = {}
        self.values = {}
        self.counter = {}
        for symbol in self.symbols:
            self.estimators[symbol] = {}
            self.tmp_values[symbol] = {}
            self.counter[symbol] = {}
            self.values[symbol] = {}
            for timeframe in self.timeframes:
                self.estimators[symbol][timeframe] = None
                self.tmp_values[symbol][timeframe] = []
                self.counter[symbol][timeframe] = 0
                self.values[symbol][timeframe] = {}
                for ohlc_type in self.ohlcv_types:
                    self.values[symbol][timeframe][ohlc_type] = None

    def fetch(self):

        pass

    def fetch_latest(self):

        pass

    def fetch_since(self):

        for symbol in self.symbols:
            for timeframe in self.timeframes:
                try:
                    time.sleep(0.2)
                    current_timestamp = self.since
                    if self.estimators[symbol][timeframe]:
                        tqdm_bar = tqdm.trange(self.estimators[symbol][timeframe]['fetches'], desc='{} | {}'.format(symbol, timeframe))
                    while True:
                        start = time.time()
                        ohlcv = self.exchange.fetch_ohlcv(
                            symbol, timeframe, current_timestamp
                        )
                        new_timestamp = self.get_last_timestamp(ohlcv)
                        if new_timestamp == current_timestamp:
                            break
                        else:
                            current_timestamp = new_timestamp
                        self.tmp_values[symbol][timeframe].append(ohlcv)
                        self.counter[symbol][timeframe] += 1

                        # ----- [ Print; take out later ] ------------
                        # self.print_pretty_ohlcv(ohlcv)
                        # print("{:>3} {}".format(self.counter[symbol][timeframe],
                        #                         "-" * 132))
                        pre_sleep = time.time()
                        time_to_sleep = \
                            (self.exchange.rateLimit / 1000) - (pre_sleep - start)
                        if time_to_sleep > 0:  # allows us to fetch at rateLimit
                            time.sleep(time_to_sleep)
                        if self.estimators[symbol][timeframe]:
                            tqdm_bar.update(1)
                    if self.estimators[symbol][timeframe]:
                        tqdm_bar.set_postfix_str('Download finished!')
                        tqdm_bar.close()
                    self.save_ohlcv(self.tmp_values[symbol][timeframe],
                                    symbol, timeframe)
                    print("Finish fetching: {}/{}".format(symbol, timeframe))
                    time.sleep(0.1)
                except:
                    continue

    def estimate_fetch_time(self):

        total = {
            'steps': 0, 'fetches': 0, 'seconds': 0.0, 'minutes': 0.0,
            'hours': 0.0
        }
        total_timeframe = {}
        for timeframe in self.timeframes:
            total_timeframe[timeframe] = {
                'steps': 0, 'fetches': 0, 'seconds': 0.0, 'minutes': 0.0,
                'hours': 0.0}
        total_symbol = {}
        for symbol in self.symbols:
            total_symbol[symbol] = {
                'steps': 0, 'fetches': 0, 'seconds': 0.0, 'minutes': 0.0,
                'hours': 0.0}

        for symbol in self.symbols:
            for timeframe in self.timeframes:
                try:
                    start = time.time()
                    ohlcv_start = self.exchange.fetch_ohlcv(
                        symbol, timeframe, self.since
                    )
                    end = time.time()
                    time_to_sleep = (self.exchange.rateLimit / 1000) - (
                            end - start)
                    if time_to_sleep > 0:
                        time.sleep(time_to_sleep)

                    start = time.time()
                    ohlcv_end = self.exchange.fetch_ohlcv(
                        symbol, timeframe
                    )

                    ohlcv_len = len(ohlcv_start)
                    step_with = ohlcv_start[1][0] - ohlcv_start[0][0]
                    span = ohlcv_end[-1][0] - ohlcv_start[0][0]
                    steps = math.ceil(span / step_with)
                    time_s = math.ceil(
                        (steps * (self.exchange.rateLimit / 1000)) / ohlcv_len
                    )
                    time_m = time_s / 60
                    time_h = time_s / 3600
                    fetches = math.ceil(steps / ohlcv_len)

                    values = {'steps': steps,
                              'fetches': fetches,
                              'seconds': time_s,
                              'minutes': time_m,
                              'hours': time_h}
                    self.estimators[symbol][timeframe] = values

                    print("Symbol: {:8} - Timeframe: {}  |  Steps: {:>8}  |  "
                          "Fetches: {:>7}  |  "
                          "Time: {:>7} s  / {:>6.1f} m  / {:>5.2f} h"
                          .format(symbol, timeframe, steps, fetches,
                                  time_s, time_m, time_h))
                    end = time.time()
                    time_to_sleep = (self.exchange.rateLimit / 1000) - (
                            end - start)
                    if time_to_sleep > 0:
                        time.sleep(time_to_sleep)
                    for k, v in values.items():
                        total_timeframe[timeframe][k] += v
                        total_symbol[symbol][k] += v
                        total[k] += v
                except:
                    continue

            print("-" * 116)

        print("Total:  # Symbol: {}  |  # Timeframe: {}  |  "
              "Total Steps: {}  |  "
              "Total Fetches: {}  |  "
              "Total Time: {} s / {:.1f} m / {:.2f} h".format(
            len(self.symbols), len(self.timeframes), total['steps'],
            total['fetches'], total['seconds'], total['minutes'], total['hours'])
        )
        print("-" * 121)

    def get_last_timestamp(self, ohlcv):
        return ohlcv[-1][0]

    def print_pretty_ohlcv(self, ohlcvs):
        for ohlcv in ohlcvs:
            utc_time_ms = ohlcv[0]  # UTC in milliseconds
            open = ohlcv[1]
            high = ohlcv[2]
            low = ohlcv[3]
            close = ohlcv[4]
            volume = ohlcv[5]
            utc_time = datetime.datetime.fromtimestamp(
                int(utc_time_ms / 1000)).strftime('%Y-%m-%d %H:%M:%S')
            items = [utc_time, open, high, low, close, volume, utc_time_ms]
            print(
                "{} | Open: {:<10f} | High: {:<10f} | "
                "Low {:10f} | Close {:10f} | Volume {:>10}  | ms: {:>15}"
                    .format(*items)
            )

    def save_ohlcv(self, ohlcv, symbol, timeframe, basepath=None):
        if self.basepath is None and basepath is None:
            raise NoBasePathGivenError("Please provide a basepath.")
        if basepath:
            path = basepath
        else:
            path = self.basepath
        symbol = symbol.replace('/', '-')
        dir_path = os.path.join(path, 'ohlcv', self.exchangeId, symbol)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_name = 'ohlcv_' + timeframe + '.pkl'
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'wb', pickle.HIGHEST_PROTOCOL) as f:
            pickle.dump(ohlcv, f)
            print("Successfully saved ohlcv to: {}".format(file_path))



class NoOHLCVSupportError(Exception):
    pass

class NoBasePathGivenError(Exception):
    pass
