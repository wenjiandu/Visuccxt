import abc

import numpy as np


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
        :param timeframe: the ohlcv's timeframe
        """
        self.window_size = window_size
        self.data_source = data
        self.data_windowed = None
        self.ohlcv_type = ohlcv_type
        self.exchangeId = exchangeId
        self.symbol = symbol
        self.timeframe = timeframe
        self.len = len(data) - window_size + 1

    def init_windows(self):
        """Initializes the moving window for the given ohlcv type"""
        self.data_windowed = self.rolling_window(self.data_source,
                                                 self.window_size)


class OHLCVMovingWindow(MovingWindow):
    """
    This class holds the MovingWindows for one set of ohlcv_data.
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
        self.timestamps = None

        self.windows = {}
        for type, data in self.data_mappings.items():
            if type == 'timestamp':
                self.timestamps = data
            else:
                self.windows[type] = OHLCVTypeMovingWindow(
                    window_size, data, type, exchangeId, symbol, timeframe
                )
        self.len = len(self.timestamps)
        self.base_point = window_size - 1  # at which timeseries point the window starts

    def init_windows(self):
        """Initializes the MovingWindows for all ohlcv_types"""
        for moving_window in self.windows.values():
            moving_window.init_windows()
