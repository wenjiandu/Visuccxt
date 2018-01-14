import collections

import itertools


class DataCollectorDeque:

    def __init__(self, exchange, pairs, ticker_type, maxlen=100000):
        self.exchangeId = exchange.id
        self.pairs = pairs
        self.ticker_type = ticker_type
        self.values = {
            pair: collections.deque(maxlen=maxlen) for pair in self.pairs
        }
        self.value_count = 0
        self.len = maxlen

    def append(self, values):
        ctype, cdata = values
        if ctype != self.ticker_type:
            raise TypeError(
                "This DataCollector works with '{}' data. You passed "
                "'{}' data.".format(self.ticker_type, ctype)
            )
        if self.exchangeId in cdata.keys():
            for pair, value in cdata[self.exchangeId].items():
                self.values[pair].append(value)
            self.value_count += 1
        else:
            raise ValueError(
                "No data for exchange '{}' passed.".format(self.exchangeId)
            )

    def get(self, slice):
        pairs = {}
        start = self.len - slice - 1
        for pair, values in self.values.items():
            pairs[pair] = [values[i] for i in range(start, self.len - 1)]
        return pairs

    def get2(self, slice):
        pairs = {}
        start = self.len - slice - 1
        for pair, values in self.values.items():
            pairs[pair] = list(itertools.islice(values, start, None))
        return pairs
