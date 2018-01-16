import os
import pickle

import ccxt
import numpy as np
from tqdm import tqdm


class OHLCVTransformer:

    def __init__(self, ohlcv_path, exchange, symbols=None, timeframes=None):

        self.ohlcv_path = ohlcv_path

        if isinstance(exchange, ccxt.Exchange):
            self.exchangeId = exchange.id
            self.exchange = exchange
        else:
            self.exchangeId = exchange
            self.exchange = getattr(ccxt, exchange)()
        self.exchange.load_markets()

        self._symbols = exchange.symbols
        if symbols is None:
            self.symbols = self._symbols
        else:
            if isinstance(symbols, str):
                symbols = [symbols]
            self.symbols = symbols

        self._timeframes = ['1m', '1h', '1d', '1M', '1y']
        if timeframes is None:
            self.timeframes = self._timeframes
        else:
            if isinstance(timeframes, str):
                timeframes = [timeframes]
            self.timeframes = timeframes

        self.ohlcv_types = ['timestamp', 'open', 'high', 'low', 'close',
                            'volume']

        self.paths = {}
        for symbol in self.symbols:
            self.paths[symbol] = {}
            for timeframe in self.timeframes:
                self.paths[symbol][timeframe] = \
                    self.path_builder_load(symbol, timeframe)

    def transform_all_to_numpy(self):
        for symbol in tqdm(self.symbols):
            for timeframe in self.timeframes:
                self.transform_to_numpy(symbol, timeframe)

    def transform_to_numpy(self, symbol, timeframe):
        try:
            path = self.paths[symbol][timeframe]
            ohlcvs = self.load_ohlcv(path)
            length = 0
            for fetch in ohlcvs:
                length += len(fetch)

            # TODO: 'Temp Fix' (lol) for wrong saves.
            # Appended a new fetche, not itsindividual contents.
            # ohlcv_np = {ohlcv_type: np.empty(len(ohlcvs[0]), np.float32)
            #             for ohlcv_type in self.ohlcv_types}
            ohlcv_np = {
                'timestamp': np.empty(length, dtype=np.int32),
                'open': np.empty(length, dtype=np.float32),
                'high': np.empty(length, dtype=np.float32),
                'low': np.empty(length, dtype=np.float32),
                'close': np.empty(length, dtype=np.float32),
                'volume': np.empty(length, dtype=np.float32),
            }

            # TODO: Remove outer loop and all js.
            i_increment = 0
            for fetch in ohlcvs:
                for i, ohlcv in enumerate(fetch):
                    pointer = i + i_increment
                    # TODO: Important! Division by 1000 to get rid of ms part
                    ohlcv_np['timestamp'][pointer] = int(ohlcv[0] / 1000)
                    ohlcv_np['open'][pointer] = ohlcv[1]
                    ohlcv_np['high'][pointer] = ohlcv[2]
                    ohlcv_np['low'][pointer] = ohlcv[3]
                    ohlcv_np['close'][pointer] = ohlcv[4]
                    ohlcv_np['volume'][pointer] = ohlcv[5]
                i_increment += len(fetch)

            for ohlcv_type, values in ohlcv_np.items():
                self.save_ohlcv_as_numpy(values, ohlcv_type, symbol, timeframe)
        except:
            pass

    def load_ohlcv(self, ohlcv_path):

        with open(ohlcv_path, 'rb') as f:
            return pickle.load(f)

    def save_ohlcv_as_numpy(self, numpy_array, ohlcv_type, symbol, timeframe):

        path = self.path_builder_save(symbol, timeframe, ohlcv_type)
        directories = os.path.dirname(path)
        if not os.path.exists(directories):
            os.makedirs(directories)
        with open(path, 'wb') as f:
            pickle.dump(numpy_array, f, pickle.HIGHEST_PROTOCOL)

    def path_builder_load(self, symbol, timeframe):
        symbol = symbol.replace('/', '-')
        return os.path.join(
            self.ohlcv_path, self.exchangeId, symbol,
            'ohlcv_' + timeframe + '.pkl'
        )

    def path_builder_save(self, symbol, timeframe, ohlcv_type, dtype='numpy'):
        symbol = symbol.replace('/', '-')
        part = self.exchangeId + '_' + dtype
        return os.path.join(
            self.ohlcv_path, part, symbol, timeframe,
            'ohlcv_' + ohlcv_type + '.pkl'
        )
