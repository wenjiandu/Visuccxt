import ccxt
from ccxt.base.exchange import Exchange


def check_isinstance_exchange(exchange):
    if not isinstance(exchange, Exchange):
        raise TypeError("'exchange' needs to be of type 'Exchange'.")


def check_isinstance_string(string):
    if not isinstance(string, str):
        raise TypeError("'{}' needs to be of type 'str'.".format(string))


def check_isinstance_list(list_):
    if not isinstance(list_, list):
        raise TypeError("'{}' needs to be of type 'list'.".format(list_))
