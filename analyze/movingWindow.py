import abc

import numpy as np

from ohlcv.reader import OHLCVReader


class MovingWindow(abc.ABC):

    @abc.abstractmethod
    def init_windows(self):
        """Calculates the moving windows."""
        pass

    @staticmethod
    def rolling_window(a, window):
        """
        Make an ndarray with a rolling window of the last dimension

        [1] https://www.mail-archive.com/numpy-discussion@scipy.org/msg29450.html
        [2] https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.lib.stride_tricks.as_strided.html
        [3] https://stackoverflow.com/questions/4923617/efficient-numpy-2d-array-construction-from-1d-array
        [4] https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.strides.html

        Parameters
        ----------
        a : array_like
            Array to add rolling window to
        window : int
            Size of rolling window

        Returns
        -------
        Array that is a view of the original array with a added dimension
        of size w.

        Examples
        --------
        >> x=np.arange(10).reshape((2,5))
        >> rolling_window(x, 3)
        array([[[0, 1, 2], [1, 2, 3], [2, 3, 4]],
               [[5, 6, 7], [6, 7, 8], [7, 8, 9]]])

        Calculate rolling mean of last dimension:
        >> np.mean(rolling_window(x, 3), -1)
        array([[ 1.,  2.,  3.],
               [ 6.,  7.,  8.]])

        """
        if window < 1:
            raise ValueError("`window` must be at least 1.")
        if window > a.shape[-1]:
            raise ValueError("`window` is too long.")
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides,
                                               writeable=False)


class OHLCVTypeMovingWindow(MovingWindow):
    """
    Handles Moving Window operations of a single type of an OHLCV data-set.
    Thereby, type refers to one of ['open', 'high', 'low', 'close', 'volume'].
    This is usually invoked by OHLCVMovingWindow.
    """

    def __init__(self, window_size, data, ohlcv_type, exchangeId, symbol,
                 timeframe):
        """
        Initializes the Moving Window of specified size for the given
        ohlcv type (and exchange, symbol, timeframe).

        :param window_size: the window size of the moving window.
        :param data: the data of the specified ohlcv type.
        :param ohlcv_type: the type in question of the ohlcv.
        :param exchangeId: the id of the exchange.
        :param symbol: the symbol in question.
        :param timeframe: the ohlcv's timeframe.
        """
        self.window_size = window_size
        self.data_source = data
        self.data_windowed = None  # will hold the data via self.init_windows().

        # ---- [ Not in use yet ] --------
        self.ohlcv_type = ohlcv_type
        self.exchangeId = exchangeId
        self.symbol = symbol
        self.timeframe = timeframe
        self.len = len(data) - window_size + 1

    def init_windows(self):
        """Initializes the moving window for the given ohlcv type"""
        self.data_windowed = self.rolling_window(self.data_source,
                                                 self.window_size)

    def get_data(self, func):
        """
        Returns the window-values calculated by the provided function.
        The 'func'tion needs to calculate the values based on a numpy-array structure:
            --> [[window1],[window2],[window3], ... , [windown]]

        :param func: function that process the numpy-windows (e.g. np.mean(windowed_data, -1)
        :return: the return value of that function.
        """
        return func(self.data_windowed)


class OHLCVMovingWindow(MovingWindow):
    """
    This class holds the MovingWindows for one set of ohlcv_data. (OHLCVTypeMovingWindow)
    This is usually defined by exchange, symbol and timeframe.
    """

    def __init__(self, window_size, data_mappings, exchangeId, symbol,
                 timeframe):
        """
        Initializes the moving window structure of one set of OHLCV
        timeseries data.

        :param window_size: the size of the moving window.
        :param data_mappings: mapping between the ohlcv_type and the data:
                        {'open': data_open,
                         'high': data_high,
                         'low': data_low,
                         'close': data_close,
                         'volume': data_volume,
                         'timestamp': data_timestamp}
        :param exchangeId: the id of the corresponding exchange.
        :param symbol: the corresponding symbol.
        :param timeframe: the corresponding timeframe.
        """
        self.window_size = window_size
        self.data_mappings = data_mappings

        self.exchangeId = exchangeId
        self.symbol = symbol
        self.timeframe = timeframe

        self.timestamps = None  # Will be assigned in the loop below.
        self.windows = {}  # Will hold the OHLCVTypeMovingWindow object.
        for ohlcv_type, data in self.data_mappings.items():
            if ohlcv_type == 'timestamp':
                self.timestamps = data
            else:
                self.windows[ohlcv_type] = OHLCVTypeMovingWindow(
                    window_size, data, ohlcv_type, exchangeId, symbol, timeframe
                )

        self.len = len(self.timestamps)
        self.base_point = window_size - 1  # at which timeseries point the window starts

    def init_windows(self):
        """Initializes the MovingWindows for all ohlcv_types"""
        for moving_window in self.windows.values():
            moving_window.init_windows()

    def get_data(self, func):
        """
        Processes the windowed data of each ohlcv_type according to the given 'func'tion.
        This is usually something like mean, max, min and so on.

        :param func: the function that gets applied on the windowed data.
        :return: the windowed data of the OHLCV that has been transformed by the 'func'tion.
        """
        data = {}
        for ohlcv_type, moving_window in self.windows.items():
            data[ohlcv_type] = moving_window.get_data(func)
        return data

    def get_timestamps(self):
        """Returns the timestamps of the OHLCV data."""
        return self.timestamps


class MovingWindowManager(abc.ABC):
    pass


class OHLCVMovingWindowManager(MovingWindowManager):
    """
    The ohlcv_types that are used in the MovingWindows are defined here.
    """

    def __init__(self, mappings, ohlcv_path, ohlcv_types=None):
        """
        Initializes the OHLCVMovingWindowManager according to the specified mapping:

        :param mappings: {exchanges: {symbols: {timeframes: [window_sizes]}}}

        Example:
        --------
        mappings: {'binance': {'ENG/ETH': {'1m': [5, 10, 40],
                                           '1h': [5, 10, 40],
                                           '1d': [5, 10, 40]    },
                               'ETH/BTC': {'1m': [5, 10, 40],
                                           '1h': [5, 10, 40]    }
                               }
                   'bittrex': {'ENG/ETH': {'1m': [5, 10, 40, 80, 160],
                                           '1d': [5, 10, 40]    },
                               'XRP/BTC': {'1m': [10, 40],
                                           '1d': [10, 40]    }
                               }
                   }

        """
        self.mappings = mappings
        self.ohlcv_path = ohlcv_path
        self.reader = OHLCVReader(self.ohlcv_path)
        if ohlcv_types is None:
            self.ohlcv_types = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
        else:
            self.ohlcv_types = ohlcv_types

        # ---------- [ Setup Access Composition ] ---------------
        self.exchanges = set()
        self.symbols = set()
        self.timeframes = set()
        self.window_sizes = set()

        for exchange, symbols in mappings.items():
            self.exchanges.add(exchange)
            for symbol, timeframes in symbols.items():
                self.symbols.add(symbol)
                for timeframe, windows in timeframes.items():
                    self.timeframes.add(timeframe)
                    for window in windows:
                        self.window_sizes.add(window)

        # This is the original OHLCV source data.
        self.data = {}  # will be filled with self.load_ohlcv_data()
        # self.data: {exchanges: {symbols: {timeframes: {ohlcv_types: data}}}}

        # This holds the access to the MovingWindow objects.
        self.moving_windows = {}  # will be filled with self.init_windows()
        # self.moving_windows: {exchanges: {symbols: {timeframes: {windows: OHLCVMovingWindow}}}}

        # ---------- [ Container for computed data ] ---------------
        self.timestamps = {}
        self.data_mean = {}
        self.data_min = {}
        self.data_max = {}

    def load_ohlcv_data(self):
        """
        Loads the ohlcv data of all initially given mappings.
        The structure holding the data looks as follows:
        self.data: {exchanges: {symbols: {timeframes: {ohlcv_types: data}}}}

        The data itself is organized as a numpy array.
        """
        for exchange, symbols in self.mappings.items():
            self.data[exchange] = {}
            for symbol, timeframes in symbols.items():
                self.data[exchange][symbol] = {}
                for timeframe in timeframes:
                    self.data[exchange][symbol][timeframe] = \
                        self.reader.load_ohlcv(exchange, symbol, timeframe, self.ohlcv_types)

    def init_windows(self):
        """
        Initializes all MovingWindows and sets a reference accordingly:
        self.moving_windows: {exchanges: {symbols: {timeframes: {windows: OHLCVMovingWindow}}}}

        Each OHLCVMovingWindow itself holds access to an OHLCV type (e.g. 'open' or 'high')
        """
        for exchange, symbols in self.mappings.items():
            self.moving_windows[exchange] = {}
            for symbol, timeframes in symbols.items():
                self.moving_windows[exchange][symbol] = {}
                for timeframe, windows in timeframes.items():
                    self.moving_windows[exchange][symbol][timeframe] = {}

                    # Build data mappings.
                    data_mapping = {}
                    for ohlcv_type in self.ohlcv_types:
                        data_mapping[ohlcv_type] = self.data[exchange][symbol][timeframe][
                            ohlcv_type]

                    for window in windows:
                        self.moving_windows[exchange][symbol][timeframe][window] = \
                            OHLCVMovingWindow(window, data_mapping, exchange, symbol, timeframe)
                        self.moving_windows[exchange][symbol][timeframe][window].init_windows()

    # -------------------- [ Getter ] ----------------------------
    def get(self, func, data_holder, exchanges=None, symbols=None, timeframes=None,
            windows=None):
        """
        Calls the the 'func'tion on the windowed data of every movingWindow specified
        in the parameters (or, if None, all available combinations).

        While the structure holding the data is returned, it is also kept as reference
        in the class instance through the data_holder parameter which corresponds to
        a property (e.g. self.data_mean).

        :param func: the function that should be computed on top of the windowed data.
        :param data_holder: structure holding the computed results.
        :param exchanges: the exchanges in question.
        :param symbols: the symbols in question.
        :param timeframes: the timeframes in question.
        :param windows: the window sizes in question.
        :return: the data structure holding the data computed by the funcition for all
                 specified ohlcv windows.
        """
        if isinstance(exchanges, str):
            raise ValueError("{} needs to be of type list.".format(exchanges))
        if isinstance(symbols, str):
            raise ValueError("{} needs to be of type list.".format(symbols))
        if isinstance(timeframes, str):
            raise ValueError("{} needs to be of type list.".format(timeframes))
        if isinstance(windows, str):
            raise ValueError("{} needs to be of type list.".format(windows))

        exchanges = exchanges if exchanges else self.exchanges
        symbols = symbols if symbols else self.symbols
        timeframes = timeframes if timeframes else self.timeframes
        windows = windows if windows else self.window_sizes

        for exchange in exchanges:
            data_holder[exchange] = {}
            for symbol in symbols:
                data_holder[exchange][symbol] = {}
                for timeframe in timeframes:
                    data_holder[exchange][symbol][timeframe] = {}
                    for window in windows:
                        data_holder[exchange][symbol][timeframe][window] = \
                            self.moving_windows[exchange][symbol][timeframe][window].get_data(
                                func)
        return data_holder

    def get_timestamps(self):
        """Returns and caches the timestamps of all OHLCV data."""
        for exchange in self.exchanges:
            self.timestamps[exchange] = {}
            for symbol in self.symbols:
                self.timestamps[exchange][symbol] = {}
                for timeframe in self.timeframes:
                    self.timestamps[exchange][symbol][timeframe] = {}
                    for window_size in self.window_sizes:
                        if __name__ == '__main__':
                            timestamps = self.moving_windows[exchange][symbol][timeframe][window_size].get_timestamps()
                            self.timestamps[exchange][symbol][timeframe][window_size] = \
                                timestamps
        return timestamps


    def get_mean(self, exchanges=None, symbols=None, timeframes=None, windows=None):
        """
        Returns the mean of each window of the specified combination of exchanges,
        symbols, timeframes and windows.
        All parameters are optional and, when left out, correspond to all available
        parameters specified in the class instance.

        :param exchanges: a list of exchanges.
        :param symbols: a list of symbols.
        :param timeframes: a list of timeframes.
        :param windows: a list of window sizes.
        :return: the data structure holding the mean for all specified ohlcv windows.
        """
        tmp = self.get(
            self.compute_mean, self.data_mean, exchanges, symbols, timeframes, windows
        )
        return tmp

    def get_min(self, exchanges=None, symbols=None, timeframes=None, windows=None):
        """
        Returns the minimum of each window of the specified combination of exchanges,
        symbols, timeframes and windows.
        All parameters are optional and, when left out, correspond to all available
        parameters specified in the class instance.

        :param exchanges: a list of exchanges.
        :param symbols: a list of symbols.
        :param timeframes: a list of timeframes.
        :param windows: a list of window sizes.
        :return: the data structure holding the minimum for all specified ohlcv windows.
        """
        tmp = self.get(
            self.compute_min, self.data_min, exchanges, symbols, timeframes, windows
        )
        return tmp

    def get_max(self, exchanges=None, symbols=None, timeframes=None, windows=None):
        """
        Returns the maximum of each window of the specified combination of exchanges,
        symbols, timeframes and windows.
        All parameters are optional and, when left out, correspond to all available
        parameters specified in the class instance.

        :param exchanges: a list of exchanges.
        :param symbols: a list of symbols.
        :param timeframes: a list of timeframes.
        :param windows: a list of window sizes.
        :return: the data structure holding the maximum for all specified ohlcv windows.
        """
        tmp = self.get(
            self.compute_max, self.data_max, exchanges, symbols, timeframes, windows
        )
        return tmp

    # -------------------- [ Calculations ] ----------------------------
    @staticmethod
    def compute_mean(x):
        """Computes the mean of each window."""
        return np.mean(x, -1)

    @staticmethod
    def compute_max(x):
        """Computes the max of each window."""
        return np.max(x, -1)

    @staticmethod
    def compute_min(x):
        """Computes the min of each window."""
        return np.min(x, -1)
