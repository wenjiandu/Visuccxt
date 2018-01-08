from _checks import check_isinstance_list, check_isinstance_string
from funding_fees import has_deposit_fee_for_currency, \
    has_deposit_fees_for_any_its_currencies, \
    has_deposit_fees_for_any_given_currency, \
    has_withdraw_fee_for_currency, \
    has_withdraw_fees_for_any_its_currencies, \
    has_withdraw_fees_for_any_given_currency
from pairs import *

import pickle
import time
from fuzzywuzzy import fuzz
from multiprocessing import Pool


# --------- [ Exchange IDs ] ---------
from quote import is_quote_available_at_exchange


def get_all_exchange_ids(exchanges=None):
    """Returns all available exchange-ids."""
    if exchanges is None:
        return ccxt.exchanges
    else:
        ids = []
        for exchange in exchanges:
            ids.append(exchange.id)
        return ids


def get_exchange_by_id(id):
    """Returns the exchange based on the id-string."""
    check_isinstance_string(id)

    exchange = getattr(ccxt, id)()
    return exchange


def get_exchanges_by_id(ids):
    # TODO: make a check that the ids actually correspond to exchanges.
    """
    Returns a list of exchange based on the id-strings.

    :param ids: list of exchange-ids (as str)
    :return: list of exchanges (as Exchange)
    """
    check_isinstance_list(ids)
    ids_out = []

    for id in ids:
        ids_out.append(get_exchange_by_id(id))
    return ids_out


def exchange_in_ccxt(exchange_str, extended_search=False, number_results=5):
    """
    Tries to find the given exchange in ccxt. If it has an exact match, this
    one will be returned, otherwise fuzzy search through all possibilities
    will be made.

    :param exchange_str: the exchange which should be searched.
    :param extended_search: use fuzzy search.
    :param number_results: number of printed results of fuzzy search.
    """
    check_isinstance_string(exchange_str)

    exchanges = get_all_exchange_ids()

    if not extended_search and (exchange_str in exchanges):
        print("Found exact match: {}".format(exchange_str))
    else:
        accuracies = {}
        for exchange in exchanges:
            accuracy = fuzz.ratio(exchange_str, exchange)
            accuracies[exchange] = accuracy

        accuracies = list(reversed(sorted(
            accuracies.items(), key=lambda x:x[1])))

        print("\nThe best matching results for {}:"
              "\n--------------------------".format(exchange_str))
        for result in accuracies[:number_results]:
            print("{:3d}: {}".format(result[1], result[0]))


def exchanges_in_ccxt(exchange_list, extended_search=False, number_results=5):
    """
    Tries to find the given exchanges in ccxt. If it has an exact match, this
    one will be returned, otherwise fuzzy search through all possibilities
    will be made.

    :param exchange_list: list of given exchange-names.
    :param extended_search: use fuzzy search.
    :param number_results: number of printed results of fuzzy search.
    """
    check_isinstance_list(exchange_list)

    for exchange in exchange_list:
        exchange_in_ccxt(exchange,
                         extended_search=extended_search,
                         number_results=number_results)


# --------- [ Exchange Objects ] ---------
def get_all_exchanges_as_dict():
    """Returns a dictionary of exchange-id: Exchange-object
    of every exchange."""
    exchanges = {}
    for exchange in ccxt.exchanges:
        exchanges[exchange] = getattr(ccxt, exchange)()
    return exchanges


def get_all_exchanges_as_list(debug=True):
    """Returns all available exchanges as a list."""
    if debug:
        exchanges = load_exchanges_from_pickle('markets.pkl')
    else:
        exchanges = []
        for exchange in ccxt.exchanges:
            exchanges.append(getattr(ccxt, exchange)())
    return exchanges


def get_exchanges_as_list(exchanges_ids):
    """Returns the specified exchanges as a list."""
    check_isinstance_list(exchanges_ids)
    exchanges = []
    for exchange in exchanges_ids:
        exchanges.append(getattr(ccxt, exchange)())
    return exchanges


# --------- [ Initializing Markets ] ---------
def __load_markets_sub(exchange):
    """Subroutine for load_markets_threaded."""
    try:
        exchange.load_markets()
        return exchange
    except:
        print("Couldn't load market: {}".format(exchange.id))


def load_markets_threaded(exchanges, nr_Threads=20,
                          debug=False, pkl_path="markets.pkl"):
    """
    To interact with an exchange, its markets need to be loaded first.
    Since the i/o times of various exchanges differ drastically (in worst
    case a request may take up to 30 seconds), the request are split
    into a number of threads to get the data in parallel (up to 10x
    speed increase).

    :param exchanges: a list of exchanges (as Exchange)
    :param debug: loads exchanges from disk for quicker development.
    :param pkl_path: the path to the pkl-file.
    :return: the exchanges
    """
    # TODO: remove debug arg
    if debug:
        return load_exchanges_from_pickle(pkl_path)


    check_isinstance_list(exchanges)

    start = time.time()
    print("Starting threaded polling.")

    if nr_Threads > len(exchanges):
        nr_Threads = len(exchanges)

    pool = Pool(nr_Threads)
    exchanges = pool.map(__load_markets_sub, exchanges)

    end = time.time()
    print("{} Threads required {:2}s for {} exchanges.".format(
        nr_Threads, (end - start), len(exchanges)))

    # Remove NoneType-Exchanges (where no data could be pulled)
    exchanges_clean = [x for x in exchanges if x != None]
    print("{} exchanges were not able to provide data and where removed"
          .format((len(exchanges)-len(exchanges_clean))))

    return exchanges_clean


def safe_exchanges_to_pickle(pickle_file, exchanges=None):
    """
    Saves the passed exchanges as a pickle file to the specified
    location. This should ease development since the average time
    for loading all markets is ~15 seconds.
    If no exchanges are specified, all exchanges are pulled and saved.

    :param pickle_file: path to the pickle file.
    :param exchanges: a list of exchanges (no ids)
    :return: the list of exchanges that have been saved.
    """
    if exchanges is None:  # quick save of all exchanges
        exchanges = load_markets_threaded()
    with open(pickle_file, 'wb') as f:
        pickle.dump(exchanges, f,)
        print("Saved '{}' successfully.".format(pickle_file))
    return exchanges


def load_exchanges_from_pickle(pickle_file):
    """
    Loads the previously saved list of exchanges.

    :param pickle_file: path to the pickle file
    :return: list of exchanges
    """
    with open(pickle_file, 'rb') as f:
        exchanges = pickle.load(f)
        print("Loaded '{}' successfully.".format(pickle_file))
    return exchanges


# --------- [ Get Exchanges by currency ] ---------
def get_exchanges_supporting_currency(exchanges, currency):
    """
    Returns the exchanges that support a given currency.

    :param exchanges: the exchanges that should be reviewed
    :param currency: a currency (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_string(currency)

    exchanges_out = []
    # TODO: This is not the best solution ... improve this.
    try:
        is_currency_available_at_exchange(exchanges[0], currency)
    except:
        exchanges = load_markets_threaded(exchanges)
    for exchange in exchanges:
        try:
            if is_currency_available_at_exchange(exchange, currency):
                exchanges_out.append(exchange)
        except:
            print("Exchange not loadable: {}".format(exchange))

    return exchanges_out


def get_exchanges_supporting_currencies(exchanges, currencies):
    """
    Returns the exchanges that support any of the given currencies.

    :param exchanges: the exchanges that should be reviewed
    :param currencies: a list of currencies (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(currencies)
    check_isinstance_list(exchanges)

    exchange_ids_holder = set()
    exchanges_holder = []

    for currency in currencies:
        exchanges_support = get_exchanges_supporting_currency(exchanges, currency)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchanges_holder.append(exchange)

        exchange_ids_holder.update(get_all_exchange_ids(exchanges_support))

    return exchanges_holder


def get_exchanges_supporting_mutual_currencies(exchanges, currencies):
    """
    Returns the exchanges that mutually support the given currencies.

    :param exchanges: a list of exchanges (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_list(currencies)

    exchange_ids_holder = []
    exchange_holder = {}

    for currency in currencies:
        exchanges_support = get_exchanges_supporting_currency(exchanges, currency)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchange_holder[exchange.id] = exchange

        exchange_ids_holder.append(
            set(get_all_exchange_ids(exchanges_support)))
    currencies_intersection = set.intersection(*exchange_ids_holder)

    exchanges_out = []
    for exchange_id in currencies_intersection:
        exchanges_out.append(exchange_holder[exchange_id])

    return exchanges_out


# --------- [ Get Exchanges by base ] ---------
def get_exchanges_supporting_base(exchanges, base):
    """
    Returns the exchanges that support a given base.

    :param exchanges: the exchanges that should be reviewed
    :param base: a base currency (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_string(base)

    exchanges_out = []

    try:
        is_base_available_at_exchange(exchanges[0], base)
    except:
        exchanges = load_markets_threaded(exchanges)
    for exchange in exchanges:
        try:
            if is_base_available_at_exchange(exchange, base):
                exchanges_out.append(exchange)
        except:
            print("Exchange not loadable: {}".format(exchange))

    return exchanges_out


def get_exchnages_supporting_bases(exchanges, bases):
    """
    Returns the exchanges that support any of the given base currencies.

    :param exchanges: a list of exchanges (as Exchange)
    :param bases: a list of base currencies (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(bases)
    check_isinstance_list(exchanges)

    exchange_ids_holder = set()
    exchanges_holder = []

    for base in bases:
        exchanges_support = get_exchanges_supporting_base(exchanges, base)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchanges_holder.append(exchange)

        exchange_ids_holder.update(get_all_exchange_ids(exchanges_support))

    return exchanges_holder


def get_exchnages_supporting_mutual_bases(exchanges, bases):
    """
    Returns the exchanges that mutually support the given base currencies.

    :param exchanges: a list of exchanges (as Exchange)
    :param bases: a list of base currencies (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_list(bases)

    exchange_ids_holder = []
    exchange_holder = {}

    for base in bases:
        exchanges_support = get_exchanges_supporting_base(exchanges, base)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchange_holder[exchange.id] = exchange

        exchange_ids_holder.append(
            set(get_all_exchange_ids(exchanges_support)))
    bases_intersection = set.intersection(*exchange_ids_holder)

    exchanges_out = []
    for exchange_id in bases_intersection:
        exchanges_out.append(exchange_holder[exchange_id])

    return exchanges_out


# --------- [ Get Exchanges by quote ] ---------
def get_exchanges_supporting_quote(exchanges, quote):
    """
    Returns the exchanges that support a given quote currency.

    :param exchanges: the exchanges that should be reviewed
    :param quote: a quote (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_string(quote)

    exchanges_out = []

    try:
        is_quote_available_at_exchange(exchanges[0], quote)
    except:
        exchanges = load_markets_threaded(exchanges)
    for exchange in exchanges:
        try:
            if is_quote_available_at_exchange(exchange, quote):
                exchanges_out.append(exchange)
        except:
            print("Exchange not loadable: {}".format(exchange))

    return exchanges_out


def get_exchanges_supporting_quotes(exchanges, quotes):
    """
    Returns the exchanges that support any of the given quote currencies.

    :param exchanges: the exchanges that should be reviewed
    :param quotes: a list of quote currencies (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(quotes)
    check_isinstance_list(exchanges)

    exchange_ids_holder = set()
    exchanges_holder = []

    for quote in quotes:
        exchanges_support = get_exchanges_supporting_quote(exchanges, quote)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchanges_holder.append(exchange)

        exchange_ids_holder.update(get_all_exchange_ids(exchanges_support))

    return exchanges_holder


def get_exchanges_supporting_mutual_quotes(exchanges, quotes):
    """
    Returns the exchanges that mutually support the given quote currencies.

    :param exchanges: a list of exchanges (as Exchange)
    :param quotes: a list of quote currencies (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_list(quotes)

    exchange_ids_holder = []
    exchange_holder = {}

    for quote in quotes:
        exchanges_support = get_exchanges_supporting_quote(exchanges, quote)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchange_holder[exchange.id] = exchange

        exchange_ids_holder.append(
            set(get_all_exchange_ids(exchanges_support)))
    quotes_intersection = set.intersection(*exchange_ids_holder)

    exchanges_out = []
    for exchange_id in quotes_intersection:
        exchanges_out.append(exchange_holder[exchange_id])

    return exchanges_out


# --------- [ Get Exchanges by pairs ] ---------
def get_exchanges_supporting_pair(exchanges, pair):
    """
    Returns the exchanges that support a given pair.

    :param exchanges: the exchanges that should be reviewed
    :param pair: a pair (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_string(pair)
    exchanges_out = []

    try:
        is_pair_available_at_exchange(exchanges[0], pair)
    except:
        exchanges = load_markets_threaded(exchanges)
    for exchange in exchanges:
        try:
            if is_pair_available_at_exchange(exchange, pair):
                exchanges_out.append(exchange)
        except:
            print("Exchange not loadable: {}".format(exchange))

    return exchanges_out


def get_exchanges_supporting_pairs(exchanges, pairs):
    """
    Returns the exchanges that support any of the given pairs.

    :param exchanges: the exchanges that should be reviewed
    :param pairs: a list of pairs (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(pairs)
    check_isinstance_list(exchanges)

    exchange_ids_holder = set()
    exchanges_holder = []

    for pair in pairs:
        exchanges_support = get_exchanges_supporting_pair(exchanges, pair)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchanges_holder.append(exchange)

        exchange_ids_holder.update(get_all_exchange_ids(exchanges_support))

    return exchanges_holder


def get_exchanges_supporting_mutual_pairs(exchanges, pairs):
    """
    Returns the exchanges that mutually support the given pairs.

    :param exchanges: a list of exchanges (as Exchange)
    :param pairs: a list of pairs (as str)
    :return: a list of exchanges
    """

    check_isinstance_list(exchanges)
    check_isinstance_list(pairs)

    exchange_ids_holder = []
    exchange_holder = {}

    for pair in pairs:
        exchanges_support = get_exchanges_supporting_pair(exchanges, pair)
        for exchange in exchanges_support:
            if not (exchange.id in exchange_ids_holder):
                exchange_holder[exchange.id] = exchange

        exchange_ids_holder.append(
            set(get_all_exchange_ids(exchanges_support)))
    pairs_intersection = set.intersection(*exchange_ids_holder)

    exchanges_out = []
    for exchange_id in pairs_intersection:
        exchanges_out.append(exchange_holder[exchange_id])

    return exchanges_out


# --------- [ Exchanges with Deposit Fees ] ---------
def get_exchanges_with_currency_deposit_fee(exchanges, currency):
    """
    Returns the exchanges that support the deposit of the
    specified currency.

    :param exchanges: a list of exchanges (as Exchange)
    :param currency: a currency (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(currency)

    exchange_out = []

    for exchange in exchanges:
        if has_deposit_fee_for_currency(exchange, currency):
            exchange_out.append(exchange)
    return exchange_out


def get_exchanges_with_currencies_deposit_fees(exchanges, currencies):
    """
    Returns a list of exchanges that support any of the given
    currencies. This is not an exclusive operation!

    :param exchanges: a list of exchanges (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(currencies)

    exchange_out = []

    for exchange in exchanges:
        for currency in currencies:
            if has_deposit_fee_for_currency(exchange, currency):
                exchange_out.append(exchange)
                break
    return exchange_out


# --------- [ Exchanges - Deposit Fee Pairs ] ---------
def get_exchange_deposit_currency_fees_pairs(exchanges, currencies=None):
    """
    Returns a nested dictionary (exchange: currency: fee) of all given
    exchanges and currencies (or all possible currencies).

    :param exchanges: a list of exchanges
    :param currencies: a list of currencies
    :return: nested dictionary (exchange: currency)
    """
    check_isinstance_list(exchanges)

    pairs = {}

    if currencies is None:
        has_currencies = has_deposit_fees_for_any_its_currencies
    else:
        has_currencies = has_deposit_fees_for_any_given_currency

    for exchange in exchanges:
        currencies_out = {}
        if has_currencies(exchange):
            deposit = exchange.fees['funding']['deposit']
            for currency, price in deposit.items():
                if price != 0:
                    currencies_out[currency] = price
            pairs[exchange.id] = currencies_out

    return pairs


def get_currency_deposit_fee_exchanges_pairs(exchanges, currencies=None):
    """
    Returns a nested dictionary (currency: exchange: fee) of all given
    exchanges and currencies (or all possible currencies).

    :param exchanges: a list of exchanges
    :param currencies: a list of currencies
    :return: nested dictionary (currency: exchange)
    """
    check_isinstance_list(exchanges)

    pairs = {}

    if currencies is None:
        has_currencies = has_deposit_fees_for_any_its_currencies
        for exchange in exchanges:
            if has_currencies(exchange):
                deposit = exchange.fees['funding']['deposit']
                for currency, price in deposit.items():
                    if price != 0:
                        pairs.setdefault(currency, {})[exchange.id] = price
    else:
        has_currencies = has_deposit_fees_for_any_given_currency
        for exchange in exchanges:
            if has_currencies(exchange, currencies):
                deposit = exchange.fees['funding']['deposit']
                for currency, price in deposit.items():
                    if price != 0:
                        pairs.setdefault(currency, {})[exchange.id] = price

    return pairs


# --------- [ Exchanges with Withdraw Fees ] ---------
def get_exchanges_with_currency_withdraw_fee(exchanges, currency):
    """
    Returns the exchanges that support the withdraw of the
    specified currency.

    :param exchanges: a list of exchanges (as Exchange)
    :param currency: a currency (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(exchanges)
    check_isinstance_string(currency)

    exchange_out = []

    for exchange in exchanges:
        if has_withdraw_fee_for_currency(exchange, currency):
            exchange_out.append(exchange)
    return exchange_out


def get_exchanges_with_currencies_withdraw_fees(exchanges, currencies):
    """
    Returns a list of exchanges that support any of the given
    currencies. This is not an exclusive operation!

    :param exchanges: a list of exchanges (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a list of exchanges
    """
    check_isinstance_list(exchanges)
    check_isinstance_list(currencies)

    exchange_out = []

    for exchange in exchanges:
        for currency in currencies:
            if has_withdraw_fee_for_currency(exchange, currency):
                exchange_out.append(exchange)
                break
    return exchange_out


# --------- [ Exchanges - Withdraw Fee Pairs ] ---------
def get_exchange_withdraw_currency_fees_pairs(exchanges, currencies=None):
    """
    Returns a nested dictionary (exchange: currency: fee) of all given
    exchanges and currencies (or all possible currencies).

    :param exchanges: a list of exchanges
    :param currencies: a list of currencies
    :return: nested dictionary (exchange: currency)
    """
    check_isinstance_list(exchanges)

    pairs = {}

    if currencies is None:
        has_currencies = has_withdraw_fees_for_any_its_currencies
        for exchange in exchanges:
            currencies_out = {}
            if has_currencies(exchange):
                withdraw = exchange.fees['funding']['withdraw']
                for currency, price in withdraw.items():
                    if price != 0:
                        currencies_out[currency] = price
                pairs[exchange.id] = currencies_out
    else:
        has_currencies = has_withdraw_fees_for_any_given_currency
        for exchange in exchanges:
            currencies_out = {}
            if has_currencies(exchange, currencies):
                withdraw = exchange.fees['funding']['withdraw']
                for currency, price in withdraw.items():
                    if price != 0:
                        currencies_out[currency] = price
                pairs[exchange.id] = currencies_out


    return pairs


def get_currency_withdraw_fee_exchanges_pairs(exchanges, currencies=None):
    """
    Returns a nested dictionary (currency: exchange: fee) of all given
    exchanges and currencies (or all possible currencies).

    :param exchanges: a list of exchanges
    :param currencies: a list of currencies
    :return: nested dictionary (currency: exchange)
    """
    check_isinstance_list(exchanges)

    pairs = {}

    if currencies is None:
        has_currencies = has_withdraw_fees_for_any_its_currencies
        for exchange in exchanges:
            if has_currencies(exchange):
                withdraw = exchange.fees['funding']['withdraw']
                for currency, price in withdraw.items():
                    if price != 0:
                        pairs.setdefault(currency, {})[exchange.id] = price

    else:
        has_currencies = has_withdraw_fees_for_any_given_currency
        for exchange in exchanges:
            if has_currencies(exchange, currencies):
                withdraw = exchange.fees['funding']['withdraw']
                for currency, price in withdraw.items():
                    if price != 0:
                        pairs.setdefault(currency, {})[exchange.id] = price

    return pairs
