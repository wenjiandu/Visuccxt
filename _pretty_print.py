import ccxt
from ccxt.base.exchange import Exchange
from _checks import *
from exchange import *

from pprint import pprint


def pretty_exchanges():
    ex = get_all_exchange_ids()
    pprint(ex)
    print("\nNumber of exchanges available: {}".format(len(ex)))


def pretty_exchange(exchange):
    """PPrints all exchange methods/properties."""
    check_isinstance_exchange(exchange)
    pprint(dir(exchange))


def search_exchange_properties(exchange, keyword):
    """Prints all exchange methods/properties matching a keyword."""
    check_isinstance_exchange(exchange)
    for prop in dir(exchange):
        if keyword.upper() in prop.upper():
            print(prop)


def pretty_market(exchange, market):
    """PPrints all properties of a specific trading pair."""
    check_isinstance_exchange(exchange)
    check_isinstance_string(market)

    pprint(exchange.market(market))


def pretty_markets(exchange, markets):
    """Pprints all properties of the specified trading pairs."""
    check_isinstance_exchange(exchange)
    check_isinstance_list(markets)

    for market in markets:
        pprint(exchange.markets[market])
        print("\n----------------------------\n")
