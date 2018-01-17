from multiprocessing.pool import Pool
from time import sleep

import ccxt


class TickersFetcher:

    def __init__(self, exchanges, symbols=None):
        if isinstance(exchanges, ccxt.Exchange):  # only one exchange passed
            self.exchanges = [exchanges]
        else:
            self.exchanges = exchanges

        if symbols is None:
            self.symbols = symbols
        elif isinstance(symbols, str):  # only one symbol passed
            self.symbols = [symbols]
        else:
            self.symbols = symbols

        self.tickers = {}
        self.number_exchanges = len(self.exchanges)
        self.ticker_types = ['ask', 'baseVolume', 'bid', 'high', 'low', 'last']

    def fetch(self):
        """Fetches the tickers for all exchanges."""
        self.tickers = {}
        # [1] If we don't have enough exchanges to query (Thread overhead).
        if self.number_exchanges < 5:
            tickers = []
            for exchange in self.exchanges:
                tickers.append(
                    (exchange.id, self._fetch_single_ticker(exchange))
                )
        # [2] Connection Overhead > Thread Overhead
        else:
            # Threading init causes a 1.4s overhead?
            pool = Pool(self.number_exchanges)
            tickers = pool.map(self._fetch_tickers_threaded, self.exchanges)

            # Closing the Pool is extremely important!
            # Do not change this, otherwise it will eat your memory in no time!
            pool.terminate()
            pool.join()
            for worker in pool._pool:
                assert not worker.is_alive()

        # Symbol Filtering
        for ticker in tickers:
            exchange = ticker[0]
            data = ticker[1]
            if self.symbols is None:
                self.tickers[exchange] = data
            else:
                self.tickers[exchange] = {}
                for symbol, values in data.items():
                    if symbol in self.symbols:
                        self.tickers[exchange][symbol] = values

    def _fetch_single_ticker(self, exchange):
        try:
            return exchange.fetch_tickers(self.symbols)
        except:
            sleep(0.5)
            print("There is an issue loading the tickers from '{}'."
                  .format(exchange))
            self._fetch_single_ticker(exchange)


    def _fetch_tickers_threaded(self, exchange):
        """Threaded subroutine for fetching tickers."""
        try:
            ticker = exchange.fetch_tickers(self.symbols)
            return exchange.id, ticker
        except:
            sleep(0.5)
            print("There is an issue loading the tickers from '{}'."
                  .format(exchange))
            self._fetch_tickers_threaded(exchange)

    def get_tickers_for_all_exchanges(self, symbols=None):
        """
        Returns the values from the previously fetched tickers for all
        exchanges. This can either happen for all available symbols or a
        selection of passed symbols.

        Structure of the returned object:
        dict(exchange) -> dict(pairs)  -> dict(ticker_types) -> ticker_values

        :param symbols: a selection of symbols; if None: all symbols are used.
        :return: the selection of tickers according to the symbols.
        """
        tickers = {}
        for exchange, pairs in self.tickers.items():
            tickers[exchange] = {}
            for pair, parameters in pairs.items():
                tickers[exchange][pair] = {}
                # [1] Get the value for all symbols.
                if symbols is None:
                    for ticker_type in self.ticker_types:
                        tickers[exchange][pair][ticker_type] = \
                            parameters[ticker_type]
                    continue
                # If only one symbol gets passed.
                if not isinstance(symbols, list):
                    symbols = [symbols]
                # [2] The usual case when the symbols are specified.
                if pair in symbols:
                    for ticker_type in self.ticker_types:
                        tickers[exchange][pair][ticker_type] = \
                            parameters[ticker_type]
        return tickers

    def get_tickers_for_exchange(self, exchange, symbols=None):
        """
        Returns the values from the previously fetched tickers for the
        specified exchanges. This can either happen for all available symbols
        or a selection of passed symbols.

        Structure of the returned object:
        dict(pairs)  -> dict(ticker_types) -> ticker_values

        :param exchange: the specified exchange
        :param symbols: a selection of symbols; if None: all symbols are used.
        :return: the selection of tickers according to the symbols.
        """
        tickers = {}
        for pair, parameters in self.tickers[exchange.id].items():
            tickers[pair] = {}
            # [1] Get the value for all symbols.
            if symbols is None:
                for ticker_type in self.ticker_types:
                    tickers[pair][ticker_type] = parameters[ticker_type]
                continue
            # If only one symbol gets passed.
            if not isinstance(symbols, list):
                symbols = [symbols]
            # [2] The usual case when the symbols are specified.
            if pair in symbols:
                for ticker_type in self.ticker_types:
                    tickers[pair][ticker_type] = parameters[ticker_type]
        return tickers
