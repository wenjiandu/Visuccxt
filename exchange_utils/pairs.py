from exchange_utils.currencies import *


# --------- [ Pair Available ] ---------
def is_pair_available_at_exchange(exchange, pair):
    """
    Checks whether the specified trading-pair is available
    at the exchange.

    :param exchange: an exchange (as Exchange)
    :param pair: a trading-pair (as str)
    :return: a list of Boolean values
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(pair)

    if pair in exchange.symbols:
        return True
    else:
        return False


# def get_pairs_available_at_exchange(exchange, pairs):
#     check_isinstance_exchange(exchange)
#     check_isinstance_list(pairs)
#
#     mask = []
#
#     for pair in pairs:
#         mask.append(is_pair_available_at_exchange(exchange, pair))
#     return mask


def get_pairs_available_at_exchange(exchange, pairs):
    check_isinstance_exchange(exchange)
    check_isinstance_list(pairs)

    out = []
    for pair in pairs:
        if is_pair_available_at_exchange(exchange, pair):
            out.append(pair)
    return out


# --------- [ Get Pairs from Exchange ] ---------
def get_all_pairs_at_exchange(exchange):
    """Returns all symbols which are available on a exchange."""
    check_isinstance_exchange(exchange)
    return exchange.symbols


def get_all_pairs_at_exchanges(exchanges):
    """
    Returns all trading pairs that are available at the given exchanges.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_all_pairs_at_exchange(exchange))

    return pairs_s


def get_all_mutual_pairs_at_exchanges(exchanges):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)

    pairs_holder = []

    for exchange in exchanges:
        pairs_holder.append(set(get_all_pairs_at_exchange(exchange)))
    pairs_intersection = set.intersection(*pairs_holder)

    return pairs_intersection


# --------- [ Get Amount of Pairs ] ---------
def amount_pairs_at_exchange(exchange):
    return len(exchange.symbols)


def amount_pairs_at_exchanges(exchanges):
    return len(get_all_pairs_at_exchanges(exchanges))


def amount_mutual_pairs_at_exchanges(exchanges):
    return len(get_all_mutual_pairs_at_exchanges(exchanges))


# --------- [ By Base] ---------
def get_pairs_by_base_at_exchange(exchange, base):
    """
    Returns a list of all available pairs with the specified
    base at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param base: a base currency (as str)
    :return: a list of trading-pairs (as str)
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(base)
    pairs = []

    for market in exchange.markets:
        if exchange.markets[market]['base'] == base:
            pairs.append(market)

    return pairs


def get_pairs_by_bases_at_exchange(exchange, bases):
    """
    Returns a list of all available pairs with the specified
    bases at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param bases: a list of base currencies (as str)
    :return: a list of trading-pairs (as str)
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(bases)
    pairs = []

    for base in bases:
        pairs.extend(get_pairs_by_base_at_exchange(exchange, base))
    return pairs


def get_pairs_by_base_at_exchanges(exchanges, base):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified base currency.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param base: a base currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(base)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_pairs_by_base_at_exchange(exchange, base))
    return pairs_s


def get_pairs_by_bases_at_exchanges(exchanges, bases):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified base currencies.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param bases: a list of base currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(bases)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_pairs_by_bases_at_exchange(exchange, bases))
    return pairs_s


def get_all_mutual_pairs_by_base_at_exchanges(exchanges, base):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified base currency.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param base: a base currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(base)

    pairs_holder = []

    for exchange in exchanges:
        pairs_holder.append(
            set(get_pairs_by_base_at_exchange(exchange, base)))
    pairs_intersection = set.intersection(*pairs_holder)

    return pairs_intersection


def get_all_mutual_pairs_by_bases_at_exchanges(exchanges, bases):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified base currency.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param bases: a list of base currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(bases)

    pairs = []

    for base in bases:
        pairs.append(
            get_all_mutual_pairs_by_base_at_exchanges(exchanges, base))

    return pairs


# --------- [ By Quote ] ---------
def get_pairs_by_quote_at_exchange(exchange, quote):
    """
    Returns a list of all available pairs with the specified
    quote at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param quote: a base currency (as str)
    :return: a list of trading-pairs (as str)
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(quote)
    pairs = []

    for market in exchange.markets:
        if exchange.markets[market]['quote'] == quote:
            pairs.append(market)

    return pairs


def get_pairs_by_quotes_at_exchange(exchange, quotes):
    """
    Returns a list of all available pairs with the specified
    quotes at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param quotes: a list of quote currencies (as str)
    :return: a list of trading-pairs (as str)
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(quotes)
    pairs = []

    for quote in quotes:
        pairs.extend(get_pairs_by_quote_at_exchange(exchange, quote))
    return pairs


def get_pairs_by_quote_at_exchanges(exchanges, quote):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified quote currency.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param quote: a quote currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(quote)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_pairs_by_quote_at_exchange(exchange, quote))
    return pairs_s


def get_pairs_by_quotes_at_exchanges(exchanges, quotes):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified quote currencies.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param quotes: a list of quote currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(quotes)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_pairs_by_quotes_at_exchange(exchange, quotes))
    return pairs_s


def get_all_mutual_pairs_by_quote_at_exchanges(exchanges, quote):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified quote currency.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param quote: a quote currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(quote)

    pairs_holder = []

    for exchange in exchanges:
        pairs_holder.append(
            set(get_pairs_by_quote_at_exchange(exchange, quote)))
    pairs_intersection = set.intersection(*pairs_holder)

    return pairs_intersection


def get_all_mutual_pairs_by_quotes_at_exchanges(exchanges, quotes):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified quote currency.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param quotes: a list of quote currencies
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(quotes)

    pairs = []

    for quote in quotes:
        pairs.append(
            get_all_mutual_pairs_by_quote_at_exchanges(exchanges, quote))

    return pairs


# --------- [ By Currency ] ---------
def get_pairs_by_currency_at_exchange(exchange, currency):
    """
    Get all trading pairs (markets) with the specified
    currency at that exchange.
    """
    check_isinstance_string(currency)
    check_isinstance_exchange(exchange)

    if is_currency_available_at_exchange(exchange, currency):

        currency.upper()
        pairs = []

        for market in exchange.markets:
            if (exchange.markets[market]['base'] == currency) \
                    or (exchange.markets[market]['quote'] == currency):
                pairs.append(market)
        return pairs

    else:
        return []  # TODO: This seems to be a ugly solution.


def get_pairs_by_currencies_at_exchange(exchange, currencies):
    """
    Returns a list of all available pairs with the specified
    currencies at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a list of trading-pairs (as str)
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(currencies)

    pairs = []
    for currency in currencies:
        pairs.extend(get_pairs_by_currency_at_exchange(exchange, currency))
    return pairs


def get_pairs_by_currency_at_exchanges(exchanges, currency):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified currency.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param currency: a currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(currency)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(get_pairs_by_currency_at_exchange(exchange, currency))
    return pairs_s


def get_pairs_by_currencies_at_exchanges(exchanges, currencies):
    """
    Returns all trading pairs that are available at the given exchanges
    given the specified currencies.
    Notice that a pair only needs to be present at a single exchange
    to be included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(currencies)

    pairs_s = set()

    for exchange in exchanges:
        pairs_s.update(
            get_pairs_by_currencies_at_exchange(exchange, currencies))
    return pairs_s


def get_all_mutual_pairs_by_currency_at_exchanges(exchanges, currency):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified currency.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param currency: a currency (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(currency)

    pairs_holder = []

    for exchange in exchanges:
        pairs_holder.append(
            set(get_pairs_by_currency_at_exchange(exchange, currency)))
    pairs_intersection = set.intersection(*pairs_holder)

    return pairs_intersection


def get_all_mutual_pairs_by_currencies_at_exchanges(exchanges, currencies):
    """
    Returns all mutual trading pairs that are available at the
    given exchanges given the specified currencies.
    Notice that a pair needs to be present at every exchange to be
    included in the result.

    :param exchanges: a list of exchanges (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a set of pairs (as str)
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(currencies)

    pairs = []

    for currency in currencies:
        pairs.append(
            get_all_mutual_pairs_by_currency_at_exchanges(exchanges, currency))

    return pairs
