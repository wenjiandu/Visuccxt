import json
import os
import pickle


class OHLCVReader:

    def __init__(self, ohlcv_path):
        self.ohlcv_path = ohlcv_path
        self.ohlcv_types = ['open', 'high', 'low', 'close', 'volume', 'timestamp']

    def load_ohlcv(self, exchangeId, symbol, timeframe, basepath=None):
        ohlcv = {}
        for ohlcv_type in self.ohlcv_types:
            ohlcv[ohlcv_type] = \
                self.load_ohlcv_type(exchangeId, symbol, timeframe, ohlcv_type, basepath)
        return ohlcv

    # ------- [ OHLCV Type ] ----------------
    def save_ohlcv_type(self, ohlcv, exchangeId, symbol, timeframe, ohlcv_type, basepath=None):
        dir_path, file_path = self._build_ohlcv_type_path(
            exchangeId, symbol, timeframe, ohlcv_type, basepath
        )
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(file_path, 'wb', pickle.HIGHEST_PROTOCOL) as f:
            pickle.dump(ohlcv, f)

    def load_ohlcv_type(self, exchangeId, symbol, timeframe, ohlcv_type, basepath=None):
        _, file_path = self._build_ohlcv_type_path(
            exchangeId, symbol, timeframe, ohlcv_type, basepath
        )

        with open(file_path, 'rb') as f:
            ohlcv = pickle.load(f)
        return ohlcv

    def _build_ohlcv_type_path(self, exchangeId, symbol, timeframe, ohlcv_type, basepath=None):
        path = basepath if basepath else self.ohlcv_path
        symbol = symbol.replace('/', '-')

        file_name = 'ohlcv_' + ohlcv_type + '.pkl'
        dir_path = os.path.join(path, exchangeId, symbol, timeframe)
        file_path = os.path.join(dir_path, file_name)
        return dir_path, file_path

    # ------- [ OHLCV Info ] ----------------
    def save_ohlcv_info(self, info, exchangeId, basepath=None):
        path = basepath if basepath else self.ohlcv_path
        file_path = os.path.join(path, exchangeId, 'info.json')
        with open(file_path, 'w') as f:
            json.dump(info, f)

    def load_ohlcv_info(self, exchangeId, basepath=None):
        path = basepath if basepath else self.ohlcv_path
        file_path = os.path.join(path, exchangeId, 'info.json')
        with open(file_path, 'r') as f:
            info_data = json.load(f)
        return info_data

    def read_ohlcv_timestamp(self, exchangeId, symbol, timeframe, basepath=None):
        path = basepath if basepath else self.ohlcv_path
        symbol = symbol.replace('/', '-')

        filename = 'ohlcv_timestamp.pkl'
        file_path = os.path.join(path, exchangeId, symbol, timeframe, filename)
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
