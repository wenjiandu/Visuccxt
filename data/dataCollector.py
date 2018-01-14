import collections

import sys


class DataCollector:

    def __init__(self, pairs, windows):
        self.pairs = pairs
        if any(window == 0 for window in windows):
            print("No window size '0' allowed! Please try again.")
            sys.exit()
        self.windows = windows
        self.values = {pair: collections.deque() for pair in pairs}
        self.value_count = 0

        self.means = self._init_queue()
        self.diffs = self._init_queue()
        self.diffs_percent = self._init_queue()
        self.diff_to_means = self._init_queue()
        self.diff_to_means_percent = self._init_queue()
        self.highs = self._init_queue()
        self.lows = self._init_queue()

        self.container = {'means': self.means,
                          'diffs': self.diffs,
                          'diffs_percent': self.diffs_percent,
                          'diff_to_means': self.diff_to_means,
                          'diff_to_means_percent': self.diff_to_means_percent,
                          'highs': self.highs,
                          'lows': self.lows}

    def _init_queue(self):
        return {pair: {window: collections.deque()
                           for window in self.windows}
                    for pair in self.pairs}

    def append_value(self, values):
        for pair, value in values.items():
            self.values[pair].append(value)
        self.value_count += 1
        self._update_means()
        self._update_diffs()
        self._update_diffs_percent()
        # self._update_diffs_both()
        self._update_diff_to_means()
        self._update_diff_to_means_percent()
        self._update_highs()
        self._update_lows()

    # ---------- [ Getter ] ----------
    def get_latest(self, deque_name=None):
        if deque_name is None:
            out = {}
            for key, deque in self.container.items():
                out[key] = {pair: {window: values[-1] for window, values in
                                   deque[pair].items()}
                            for pair in self.pairs}
            return out
        else:
            deque = self.container[deque_name]
            out = {pair: {window: values[-1] for window, values in
                          deque[pair].items()}
                   for pair in self.pairs}
            return out

    def get_values(self, deque_name=None):
        if deque_name is None:
            return self.container
        else:
            return self.container[deque_name]

    # ---------- [ Updates ] ----------
    def _update_means(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = None
                else:
                    to_append = self._calculate_mean(window, pair)
                self.means[pair][window].append(to_append)

    def _update_diffs(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = None
                else:
                    to_append = self._calculate_diffs(window, pair)
                self.diffs[pair][window].append(to_append)

    def _update_diffs_percent(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = 0.0
                else:
                    to_append = self._calculate_diffs_percent(window, pair)
                self.diffs_percent[pair][window].append(to_append)

    # def _update_diffs_both(self):
    #     for window in self.windows:
    #         for pair in self.pairs:
    #             if window > self.value_count:
    #                 num_to_append = None
    #                 perc_to_append = None
    #             else:
    #                 num_to_append, perc_to_append = self._calculate_diffs_both(
    #                     window, pair)
    #             self.diffs[pair][window].append(num_to_append)
    #             self.diffs_percent[pair][window].append(perc_to_append)

    def _update_diff_to_means(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = None
                else:
                    to_append = self._calculate_diff_to_means(window, pair)
                self.diff_to_means[pair][window].append(to_append)

    def _update_diff_to_means_percent(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = 0.0
                else:
                    to_append = self._calculate_diff_to_means_percent(window,
                                                                      pair)
                self.diff_to_means_percent[pair][window].append(to_append)

    def _update_highs(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = self._calculate_highs(self.value_count, pair)
                else:
                    to_append = self._calculate_highs(window, pair)
                self.highs[pair][window].append(to_append)

    def _update_lows(self):
        for window in self.windows:
            for pair in self.pairs:
                if window > self.value_count:
                    to_append = self._calculate_lows(self.value_count, pair)
                else:
                    to_append = self._calculate_lows(window, pair)
                self.lows[pair][window].append(to_append)

    # ---------- [ Calculations ] ----------
    def _calculate_mean(self, window, pair):
        # Deque allows no slice access.
        length = len(self.values[pair]) - 1
        deque_slice = range(length - window, length)
        mean = float(sum([self.values[pair][i] for i in deque_slice]) / window)
        return mean

    def _calculate_diffs(self, window, pair):
        diff = self.values[pair][-1] - self.values[pair][-window]
        return diff

    def _calculate_diffs_percent(self, window, pair):
        try:
            diff_percent = (self.values[pair][-1] /
                            self.values[pair][-window]) - 1.0
        except ZeroDivisionError:
            diff_percent = 0.0
        return diff_percent

    # def _calculate_diffs_both(self, window, pair):
    #     diff = self.values[pair][-1] - self.values[pair][-window]
    #     perc = diff / self.values[pair][-1]
    #     return diff, perc

    def _calculate_diff_to_means(self, window, pair):
        # TODO: should the mean selection be -2? without the updated value?
        diff_to_mean = self.values[pair][-1] - \
                       self.means[pair][window][-1]
        return diff_to_mean

    def _calculate_diff_to_means_percent(self, window, pair):
        try:
            diff_to_mean_percent = (self.values[pair][-1] / \
                                    self.means[pair][window][-1]) - 1.0
        except ZeroDivisionError:
            diff_to_mean_percent = 0.0
        return diff_to_mean_percent

    def _calculate_highs(self, window, pair):
        length = len(self.values[pair]) - 1
        deque_slice = range(length - window, length)
        high = max([self.values[pair][i] for i in deque_slice])
        return high

    def _calculate_lows(self, window, pair):
        length = len(self.values[pair]) - 1
        deque_slice = range(length - window, length)
        low = min([self.values[pair][i] for i in deque_slice])
        return low
