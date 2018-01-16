import numpy as np


class OHLCVTransformer:

    def __init__(self):
        pass

    def transform_values_to_numpy_online(self, values):
        values_transformed = {}
        for symbol, timeframes in values.times():
            values_transformed[symbol] = {}
            for timeframe, ohlcv in timeframes.items():
                ohlcv_tmp = self.transform_value_to_numpy_online(ohlcv)
                values_transformed[symbol][timeframe] = ohlcv_tmp
        return values_transformed

    def transform_value_to_numpy_online(self, value):
        length = len(value)
        ohlcv_tmp = {
            'timestamp': np.empty(length, dtype=np.int64),
            'open': np.empty(length, dtype=np.float32),
            'high': np.empty(length, dtype=np.float32),
            'low': np.empty(length, dtype=np.float32),
            'close': np.empty(length, dtype=np.float32),
            'volume': np.empty(length, dtype=np.float32),
        }
        # -------- [ Transform the data ] --------
        for i, ohlcv in enumerate(value):
            # TODO: Fix this with the timing issue
            ohlcv_tmp['timestamp'][i] = int(ohlcv[0])
            ohlcv_tmp['open'][i] = ohlcv[1]
            ohlcv_tmp['high'][i] = ohlcv[2]
            ohlcv_tmp['low'][i] = ohlcv[3]
            ohlcv_tmp['close'][i] = ohlcv[4]
            ohlcv_tmp['volume'][i] = ohlcv[5]
        return ohlcv_tmp
