from pprint import pprint

from exchange._checks import *
from exchange.exchange import get_all_exchange_ids


def pretty_exchange(exchange):
    """PPrints all exchange methods/properties."""
    check_isinstance_exchange(exchange)
    pprint(dir(exchange))


def pretty_exchanges():
    ex = get_all_exchange_ids()
    pprint(ex)
    print("\nNumber of exchanges available: {}".format(len(ex)))


def filter_exchange_properties(exchange, keyword):
    """Prints all exchange methods/properties matching a keyword."""
    check_isinstance_exchange(exchange)
    for prop in dir(exchange):
        if keyword.upper() in prop.upper():
            print(prop)


def pretty_market(exchange, pair):
    """PPrints all properties of a specific trading pair."""
    check_isinstance_exchange(exchange)
    check_isinstance_string(pair)
    exchange.load_markets()
    pprint(exchange.market(pair))


def pretty_markets(exchanges, pairs=None):
    """Pprints all properties of the specified trading pairs."""
    if not isinstance(exchanges, list):
        check_isinstance_exchange(exchanges)
        exchanges = [exchanges]
    if pairs is not None:
        check_isinstance_list(pairs)
    for exchange in exchanges:
        check_isinstance_exchange(exchange)
        exchange.load_markets()
        if pairs is None:
            pairs = exchange.symbols
        for pair in pairs:
            if pair in exchange.symbols:
                pprint(exchange.markets[pair])
        print("\n----------------------------\n")

def filter_market_properties(ex):
    pass
