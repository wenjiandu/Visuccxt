import numpy as np


class AnalyzeMovingWindowOnline:

    def __init__(self, data_collector, window_sizes, analysis_types):

        self.data_collector = data_collector
        self.exchange = data_collector.exchange
        self.exchangeId = data_collector.exchangeId
        self.pairs = data_collector.pairs
        self.ticker_types = data_collector.ticker_types
        self.entry_count = data_collector.entry_count
        self.len = 100  # data_collector.len
        self.timestamps = data_collector.timestamps

        self.window_sizes = window_sizes
        self.analysis_types = analysis_types
        self.analysis_methods = {}

        for analysis_type in self.analysis_types:
            self.analysis_methods[analysis_type] = getattr(self, analysis_type)

        self.pointer = -1

        self.values = {}
        for pair in self.pairs:
            self.values[pair] = {}
            for ticker_type in self.ticker_types:
                self.values[pair][ticker_type] = {}
                for analysis in self.analysis_types:
                    self.values[pair][ticker_type][analysis] = {}
                    analysis = self.values[pair][ticker_type][analysis]
                    for window_size in self.window_sizes:
                        analysis[window_size] = \
                            np.empty(self.len, dtype=np.float32)

    def initial_calculation(self):
        pass

    def refresh_calculation(self):
        pass

    def refresh_pointer(self):
        if self.pointer == self.len - 1:
            self.pointer = 0
            # TODO: call to save routine
        else:
            self.pointer += 1

    def step(self, data_collector):

        self.refresh_pointer()
        self.entry_count = data_collector.entry_count
        self.timestamps[self.pointer] = data_collector.timestamps[0]
        print(self.entry_count)

        window_data = {}
        slice = sorted(self.window_sizes)[-1]
        for pair, ticker_types in data_collector.values.items():
            window_data[pair] = {}
            for ticker_type, values in ticker_types.items():
                window_data[pair][ticker_type] = values[:slice - 1]

        for pair, ticker_types in self.values.items():
            for ticker_type, analysis_types in ticker_types.items():
                for analysis_type, windows in analysis_types.items():
                    func = self.analysis_methods[analysis_type]
                    for window, values in windows.items():
                        if window > self.entry_count:
                            values[self.pointer] = 0.0
                        else:
                            c_values = window_data[pair][ticker_type]
                            values[self.pointer] = func(c_values[:window - 1])


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

    @staticmethod
    def mean_window(rolled_windows):
        return np.mean(rolled_windows, -1)
