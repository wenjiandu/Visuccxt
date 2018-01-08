from _checks import *


# --------- [ Currency ] ---------
from _checks import check_isinstance_exchange, check_isinstance_list


def is_currency_available_at_exchange(exchange, currency):
    """Checks if the currency is available at the exchange."""
    check_isinstance_exchange(exchange)
    check_isinstance_string(currency)

    currency.upper()

    for market in exchange.markets:
        if (exchange.markets[market]['base'] == currency) \
                or (exchange.markets[market]['quote'] == currency):
            return True

    return False


def are_currencies_available_at_exchange(exchange, currencies):
    """
    Checks if the specified currencies are available at the
    given exchange.

    :param exchange: an exchange (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: a list of Boolean values
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(currencies)

    mask = []

    for currency in currencies:
        mask.append(is_currency_available_at_exchange(exchange, currency))
    return mask


def get_all_supported_currencies(exchanges):
    # TODO: Docstring
    check_isinstance_list(exchanges)

    currencies = set()

    for exchange in exchanges:
        currencies.update(get_all_currencies_at_exchange(exchange))
    return currencies


def get_all_currencies_at_exchange(exchange):
    """Returns all available currencies at the exchange."""
    check_isinstance_exchange(exchange)
    return exchange.currencies


def amount_all_currencies_at_exchange(exchange):
    """Returns the amount of all currencies."""
    all = get_all_currencies_at_exchange(exchange)
    return len(all)


def get_currencies_with_deposit_fee_at_exchange(exchange):
    """
    Returns all currencies that have a fee associated with them on
    the given exchange.

    :param exchange: an exchange (as Exchange)
    :return: a list of currencies
    """
    check_isinstance_exchange(exchange)

    deposits = []

    try:
        for currency, price in exchange.fees['funding']['deposit'].items():
            if price != 0:
                deposits.append(currency)
    except (KeyError, TypeError, AttributeError) as e:
        print(exchange.id, e)
    return deposits


def get_currencies_with_deposit_fee_at_exchanges(exchanges):
    """
    Returns all currencies that have a fee associated with them on
    any of the given exchanges. This list is not exclusive.

    :param exchanges: a list of exchanges
    :return: a list of currencies
    """
    check_isinstance_list(exchanges)

    deposits = set()

    for exchange in exchanges:
        try:
            for currency, price in exchange.fees['funding']['deposit'].items():
                if price != 0:
                    deposits.update([currency])
        except (KeyError, TypeError, AttributeError) as e:
            print(exchange.id, e)
    return deposits


def get_currencies_with_withdraw_fee_at_exchange(exchange):
    """
    Returns all currencies that have a fee associated with them on
    the given exchange.

    :param exchange: an exchange (as Exchange)
    :return: a list of currencies
    """
    check_isinstance_exchange(exchange)

    withdraws = []

    try:
        for currency, price in exchange.fees['funding']['withdraw'].items():
            if price != 0:
                withdraws.append(currency)
    except (KeyError, TypeError, AttributeError) as e:
        print(exchange.id, e)
    return withdraws


def get_currencies_with_withdraw_fee_at_exchanges(exchanges):
    """
    Returns all currencies that have a fee associated with them on
    any of the given exchanges. This list is not exclusive.

    :param exchanges: a list of exchanges
    :return: a list of currencies
    """
    check_isinstance_list(exchanges)

    withdraws = set()

    for exchange in exchanges:
        try:
            for currency, price in exchange.fees['funding']['withdraw'].items():
                if price != 0:
                    withdraws.update([currency])
        except (KeyError, TypeError, AttributeError) as e:
            print(exchange.id, e)
    return withdraws
