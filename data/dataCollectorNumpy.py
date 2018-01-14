import numpy as np
import time


class DataCollectorNumpy:
    """
    This class is responsible for keeping track of fetched exchange data.
    It comprises all given pairs/symbols (e.g. 'ETH/BTC') and what
    information is provided by the ticker (e.g. 'ask', 'bid') through
    ticker_type.
    """
    def __init__(self, exchange, pairs, ticker_types=None,
                 dtype=np.float32, maxlen=10000):
        """

        :param exchange: the exchange whose data should be tracked.
        :param pairs: the pairs that should be tracked.
        :param ticker_types: the ticker types; defaults to all available ones.
        :param dtype: data type that should be used for the collector.
        :param maxlen: the max length of the numpy array.
        """
        self.exchangeId = exchange.id
        self.pairs = pairs
        if ticker_types:
            self.ticker_types = ticker_types
        else:
            self.ticker_types = ['ask', 'baseVolume', 'bid', 'high', 'low', 'last']
        self.values = {
            pair: {
                ticker_type: np.empty(maxlen, dtype=dtype)
                for ticker_type in self.ticker_types
            }
            for pair in self.pairs
        }
        self.timestamps = np.empty(maxlen)
        self.entry_count = 0
        self.len = maxlen

    # TODO: implement a variant with a temp array that only
    # gets append every 1000 iterations
    def append(self, tickers):

        self.timestamps = np.roll(self.timestamps, 1)
        self.timestamps[0] = int(time.time() * 10)  # 1e-1 seconds
        for pair, values in tickers.items():
            for ticker_type, value in values.items():
                self.values[pair][ticker_type] = \
                    np.roll(self.values[pair][ticker_type], 1)
                self.values[pair][ticker_type][0] = value
        self.entry_count += 1

    def get(self, amount):
        """Returns the specified amount of latest items."""
        pairs = {}
        to_slice = amount - 1
        for pair, ticker_types in self.values.items():
            pairs[pair] = {}
            for ticker_type, values in ticker_types.items():
                if to_slice > 0:  # Return the specified slice
                    pairs[pair][ticker_type] = values[:to_slice]
                else:  # Return only the last element.
                    pairs[pair][ticker_type] = [values[0]]
        return pairs
