import math
import time

import ccxt
import numpy as np
import tqdm

from ohlcv.errors import NoOHLCVSupportError


class OHLCVFetcher:

    def __init__(self, exchange, ohlcv_reader, ohlcv_transformer,
                 symbols=None, since=None, timeframes=None):

        self.exchange = None
        self.exchangeId = None
        self._symbols = None
        self.symbols = None
        self._timeframes = ['1m', '1h', '1d', '1M', '1y']
        self.timeframes = None
        self.ohlcv_types = ['timestamp', 'open', 'high', 'low', 'close',
                            'volume']
        self.since = since if since else 1
        self.estimators = {}
        self.values = {}
        self.downloads_completed = {}

        self.ohlcv_reader = ohlcv_reader
        self.ohlcv_transformer = ohlcv_transformer

        # -------- [ Setup Exchange ] --------
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

        # -------- [ Setup Symbols ] --------
        self._symbols = self.exchange.symbols
        if symbols is None:
            self.symbols = self.exchange.symbols
        else:
            if isinstance(symbols, str):
                symbols = [symbols]
            self.symbols = symbols

        # -------- [ Setup Timeframes ] --------
        if timeframes is None:
            self.timeframes = self._timeframes
        else:
            if isinstance(timeframes, str):
                timeframes = [timeframes]
            self.timeframes = timeframes

        # -------- [ Setup Datastructures ] --------
        for symbol in self.symbols:
            self.values[symbol] = {}
            for timeframe in self.timeframes:
                self.values[symbol][timeframe] = []

    # -------- [ Fetch ] --------
    def fetch(self, symbol, timeframe, since, estimate=False):
        """
        Fetches the ohlcv-data of the specified symbol and timeframe
        beginning at a timestamp 'since'.

        :param symbol: The symbol whose ohlcv should be fetched.
        :param timeframe: The ohlcv timeframe.
        :param since: The starting timestamp of the ohlcv-data.
        :param estimate: Whether the required time should be displayed.
        :return:
        """
        current_timestamp = since
        if timeframe == '1m':
            # estimates = self.estimate()
            # ---------------------------------------------------------------
            start = time.time()
            ohlcv_start = \
                self.exchange.fetch_ohlcv(symbol, timeframe, self.since)
            end = time.time()
            time_to_sleep = (self.exchange.rateLimit / 1000) - (end - start)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)

            ohlcv_end = self.exchange.fetch_ohlcv(symbol, timeframe)

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

            # print(
            #     "Symbol: {:8} - Timeframe: {}  |  Steps: {:>8}  |  "
            #     "Fetches: {:>7}  |  "
            #     "Time: {:>7} s  / {:>6.1f} m  / {:>5.2f} h"
            #         .format(symbol, timeframe, steps, fetches,
            #                 time_s, time_m, time_h))
            # ---------------------------------------------------------------

            estimate = True
            tqdm_bar = tqdm.trange(
                fetches, desc='{} | {}'.format(symbol, timeframe)
            )
        while True:
            start_step = time.time()  # Track fetch time for rateLimit adaption
            # -------- [ Fetch ohlcv data ] --------
            try:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, timeframe, current_timestamp
                )
            except:
                # print("Couldn't fetch ohlcv for: {} {} {}".format(
                #     symbol, timeframe, current_timestamp
                # ))
                time.sleep(0.5)
                break  # not possible
            # -------- [ Adapt since-timestamp ] --------
            new_timestamp = self._get_last_timestamp(ohlcv)
            if new_timestamp == current_timestamp:
                break  # Fetched all data
            else:
                current_timestamp = new_timestamp

            # -------- [ Rearrange and append ohlcv data ] --------
            self._append_ohlcvs(ohlcv, symbol, timeframe)

            # -------- [ Wait for rateLimit to pass ] --------
            end_step = time.time()
            time_to_sleep = \
                (self.exchange.rateLimit / 1000) - (end_step - start_step)
            if time_to_sleep > 0:  # allows us to fetch at rateLimit
                time.sleep(time_to_sleep)

            if estimate:
                tqdm_bar.update(1)
        if estimate:
            tqdm_bar.set_postfix_str('Download finished!')
            tqdm_bar.close()
        return self.values[symbol][timeframe]

    def fetch_and_save_all(self, since=None):
        since = since if since else self.since
        for symbol in tqdm.tqdm(self.symbols, desc="Fetching data:"):
            # for symbol in self.symbols:
            # for timeframe in tqdm.tqdm(self.timeframes, desc="# Timeframes:"):
            for timeframe in self.timeframes:
                value = self.fetch(symbol, timeframe, since)
                value_transformed = \
                    self.ohlcv_transformer.transform_value_to_numpy_online(
                        value)
                self._save_ohlcv(value_transformed, symbol, timeframe)
                self._reset_value(symbol, timeframe)
        info = self.create_meta_info()
        self.ohlcv_reader.save_ohlcv_info(info, self.exchangeId)

    def fetch_and_save_latest(self):
        """
        Fetches the latest ohlcv data of the ohlcvs that had been fetched
        before. This function reads the contents of info.json to extract
        the timestamp from the last download.

        :return: the newly fetched values for each symbol/timeframe.
        """
        # -------- [ Load info.json file ] --------
        meta_data = self.ohlcv_reader.load_ohlcv_info(self.exchangeId)

        # -------- [ Get latest timestamp and fetch new Values ] --------
        for symbol, timeframes in tqdm.tqdm(meta_data.items(),
                                            desc="Fetching data."):
            for timeframe, values in timeframes.items():
                since = values['last_timestamp'] + 1
                self.fetch(symbol, timeframe, since, False)

        for symbol, timeframes in tqdm.tqdm(values.items(),
                                            desc="Transforming OHLCV."):
            for timeframe, ohlcv_types in timeframes.items():
                for ohlcv_type, new_data in ohlcv_types.items():
                    old_data = self.ohlcv_reader.load_ohlcv_type(
                        self.exchangeId, symbol, timeframe, ohlcv_type
                    )
                    merged_data = np.append(old_data, new_data)
                    self.ohlcv_reader.save_ohlcv_type(
                        merged_data, self.exchangeId, symbol, timeframe,
                        ohlcv_type
                    )

        meta_info = self.create_meta_info()
        self.ohlcv_reader.save_ohlcv_info(meta_info, self.exchangeId)
        self._reset_values()

    # TODO:
    def step(self):
        pass

    # -------- [ Meta Info ] --------
    def create_meta_info(self):

        meta_info = {}
        for symbol in self.symbols:
            meta_info[symbol] = {}
            for timeframe in self.timeframes:
                meta_info[symbol][timeframe] = {}
                meta_short = meta_info[symbol][timeframe]
                try:
                    data = self.ohlcv_reader.read_ohlcv_timestamp(
                        self.exchangeId, symbol, timeframe
                    )
                except FileNotFoundError:
                    continue
                meta_short['first_timestamp'] = data[0].item()
                meta_short['last_timestamp'] = data[-1].item()
                meta_short['entry_count'] = len(data)
        return meta_info

    # TODO: Still necessary?
    def update_meta_info(self, symbol, timeframe, ohlcv_transformed):
        info = self.ohlcv_reader.load_ohlcv_info(self.exchangeId)
        info[symbol][timeframe]['last_timestamp'] = \
            ohlcv_transformed['timestamp'][-1]

    # -------- [ Helper functions ] --------
    def _get_last_timestamp(self, ohlcv):
        return ohlcv[-1][0]

    def _append_ohlcvs(self, ohlcvs, symbol, timeframe):
        for ohlcv in ohlcvs:
            self.values[symbol][timeframe].append(ohlcv)

    def _reset_value(self, symbol, timeframe):
        self.values[symbol][timeframe] = {}

    def _reset_values(self):
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                self._reset_value(symbol, timeframe)

    def _save_ohlcv(self, values, symbol, timeframe):
        for ohlcv_type, value in values.items():
            self.ohlcv_reader.save_ohlcv_type(
                value, self.exchangeId, symbol, timeframe, ohlcv_type
            )

    # TODO:c
    def Scheck_new_data_available(self):
        pass
