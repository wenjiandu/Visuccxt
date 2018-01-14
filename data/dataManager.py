import time

import ccxt

import exchange_utils.pairs
from data.dataCollectorNumpy import DataCollectorNumpy
from data.dataFetcher import TickersFetcher
from data.dataSaver import DataSaver


class DataManager:

    def __init__(self, exchanges, pairs, ticker_types=None,
                 fetch_interval=10, save_interval=500, adaptive_time=True):
        self.exchanges = exchanges
        if isinstance(exchanges, ccxt.Exchange):
            self.exchanges = [exchanges]
        self.pairs = pairs
        if ticker_types:
            self.ticker_types = ticker_types
        else:
            self.ticker_types = ['ask', 'baseVolume', 'bid',
                                 'high', 'low', 'last']
        self.fetch_interval = fetch_interval
        self.save_interval = save_interval
        self.adaptive_time = adaptive_time
        self.step_count = 0

        self.fetcher = TickersFetcher(self.exchanges, self.pairs)

        self.pairs_available = {}
        for exchange in self.exchanges:
            self.pairs_available[exchange.id] = \
                exchange_utils.pairs.get_pairs_available_at_exchange(
                    exchange, self.pairs
                )

        self.collectors = {}
        self.savers = {}
        for exchange in self.exchanges:
            pairs_available = self.pairs_available[exchange.id]
            self.collectors[exchange.id] = \
                DataCollectorNumpy(exchange, pairs_available)
            self.savers[exchange.id] = \
                DataSaver(exchange, pairs_available)

    def _fetch(self):
        self.fetcher.fetch()

    def _append(self):
        for exchange in self.exchanges:
            ticker = self.fetcher.get_tickers_for_exchange(
                exchange, self.pairs_available[exchange.id]
            )
            self.collectors[exchange.id].append(ticker)

    def step(self):
        time_pre_fetch = time.time()
        self._fetch()
        self._append()
        time_post_append = time.time()

        self.step_count += 1
        if self.step_count % 10 == 0:
            print("Steps executed: {:>5}".format(self.step_count))
        if self.step_count % self.save_interval == 0:
            self.save()
        # Delay between individual steps.
        # This is not exposed to the calling script.
        if self.adaptive_time:
            time_for_step = time_post_append - time_pre_fetch
            time.sleep(self.fetch_interval - time_for_step)
        else:
            time.sleep(self.fetch_interval)

    def save(self):
        for exchange in self.savers.keys():
            self.savers[exchange].save_pickle(
                self.collectors[exchange]
            )
        print("Successfully saved DataCollectors!")
