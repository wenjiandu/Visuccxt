import datetime
import hashlib
import os
import pickle


# TODO: Compare different file formats
# https://github.com/mverleg/array_storage_benchmark
class DataSaver:

    def __init__(self, exchange, pairs, ticker_types=None, basepath="../pickle/"):
        self.basepath = basepath
        self.exchangeId = exchange.id
        if ticker_types:
            self.ticker_types = ticker_types
        else:
            self.ticker_types = ['ask', 'baseVolume', 'bid', 'high', 'low', 'last']
        self.pairs = sorted(pairs)

    # TODO: Implement hdf5 to save whole DataCollector Object
    # def save_h5py(self, DataCollector):
    #     with h5py.File(self.path + '.h5', 'w') as h5f:
    #         h5f.create_dataset('dataset_h5py', data=DataCollector)

    def save_pickle(self, DataCollector):
        exchangeId = DataCollector.exchangeId
        pairs = DataCollector.pairs
        ticker_type = DataCollector.ticker_type

        self._check_exchange_equality(exchangeId, 'save')
        self._check_pairs_equality(pairs, 'save')
        self._check_ticker_type_equality(ticker_type, 'save')

        directory = self._hash(exchangeId, pairs, ticker_type)

        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = timestamp + '.pkl'
        path = os.path.join(directory, name)

        with open(path, 'wb') as f:
            pickle.dump(DataCollector, f, pickle.HIGHEST_PROTOCOL)

    def load_pickle(self, DataCollector, filename=None):

        exchangeId = DataCollector.exchangeId
        pairs = DataCollector.pairs
        ticker_type = DataCollector.ticker_type

        self._check_exchange_equality(exchangeId, 'load')
        self._check_pairs_equality(pairs, 'load')
        self._check_ticker_type_equality(ticker_type, 'load')

        directory = self._hash(exchangeId, pairs, ticker_type)

        if os.path.exists(directory):
            if filename:
                with open(os.path.join(directory, filename), 'rb') as f:
                    data_collector = pickle.load(f)
                    print('Successfully loaded: {}'.format(filename))
                    return data_collector
            else:
                files = os.listdir(directory)
                if not files:
                    print("Couldn't load previous data. "
                          "No files available in {}".format(directory))
                    return DataCollector
                latest_pkl = sorted(files)[-1]
                with open(os.path.join(directory, latest_pkl), 'rb') as f:
                    data_collector = pickle.load(f)
                    print('Successfully loaded: {}'.format(latest_pkl))
                    return data_collector
        else:
            print("Couldn't load previous data. "
                  "Directory '{}' not available".format(directory))
            return DataCollector

    def _check_exchange_equality(self, exchangeId, status):
        if exchangeId != self.exchangeId:
            # TODO: Think of something better to avoid data loss.
            print("Error: Could not {} the DataCollector. DataCollector and "
                  "DataSaver do not refer to the same exchange."
                  .format(status))
            print("Got '{}' for DataCollector.".format(exchangeId))
            print("Got '{}' for DataSaver.".format(self.exchangeId))
            if status == 'load':
                raise FileNotFoundError
            else:
                return

    def _check_pairs_equality(self, pairs, status):
        if set(pairs) != set(self.pairs):
            print("Error: Could not {} the DataCollector. DataCollector and "
                  "DataSaver do not refer to the same pairs."
                  .format(status))
            print("Got '{}' for DataCollector.".format(pairs))
            print("Got '{}' for DataSaver.".format(self.pairs))
            if status == 'load':
                raise FileNotFoundError
            else:
                return

    def _check_ticker_type_equality(self, ticker_type, status):
        if ticker_type != self.ticker_types:
            print("Error: Could not {} the DataCollector. DataCollector and "
                  "DataSaver do not refer to the same ticker type."
                  .format(status))
            print("Got '{}' for DataCollector.".format(ticker_type))
            print("Got '{}' for DataSaver.".format(self.ticker_types))
            if status == 'load':
                raise FileNotFoundError
            else:
                return

    def _hash(self, exchangeId, pairs, ticker_type):
        to_hash = "".join(pairs) + exchangeId + ticker_type
        hex = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
        base = self.exchangeId + '_' + hex[:8]
        directory = os.path.join(self.basepath, base)
        return directory


# TODO: DataSaverManager
class DataSaverManager:

    def __init__(self):
        pass
