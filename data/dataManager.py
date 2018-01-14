import pprint
import time

import ccxt

import pairs
from data.dataCollectorNumpy import DataCollectorNumpy
from data.dataFetcher import TickersFetcher
from data.dataSaver import DataSaver


class DataManager:

    def __init__(self, exchanges, pairs_, ticker_types=None,
                 fetch_interval=10):
        self.exchanges = exchanges
        if isinstance(exchanges, ccxt.Exchange):
            self.exchanges = [exchanges]
        self.pairs = pairs_
        if ticker_types:
            self.ticker_types = ticker_types
        else:
            self.ticker_types = ['ask', 'baseVolume', 'bid', 'high', 'low', 'last']
        self.fetch_interval = fetch_interval
        self.step_count = 0

        self.fetcher = TickersFetcher(self.exchanges, self.pairs)

        self.pairs_available = {}
        for exchange in self.exchanges:
            self.pairs_available[exchange.id] = \
                pairs.get_pairs_available_at_exchange(exchange, self.pairs)

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
        self._fetch()
        self._append()
        self.step_count += 1
        if self.step_count % 2 == 0:
            print("Steps executed: {:>5}".format(self.step_count))
            pprint.pprint(self.collectors['binance'].values)
        if self.step_count % 500 == 0:
            self.save()
        time.sleep(self.fetch_interval)

    def save(self):
        for exchange in self.savers.keys():
            self.savers[exchange].save_pickle(
                self.collectors[exchange]
            )
        print("Successfully saved DataCollectors!")
