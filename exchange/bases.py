from exchange._checks import check_isinstance_exchange, check_isinstance_string, \
    check_isinstance_list


# --------- [ Base ] ---------
def is_base_available_at_exchange(exchange, base):
    """
    Checks if the specified base is available at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param base: a base currency (as str)
    :return: Boolean
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(base)

    bases = get_all_base_currencies_at_exchange(exchange)

    if base in bases:
        return True
    else:
        return False


def are_bases_available_at_exchange(exchange, bases):
    """
    Checks if the specified bases are available at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param base: a list of base currencies (as str)
    :return: Boolean
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(bases)

    mask = []

    for base in bases:
        mask.append(is_base_available_at_exchange(exchange, base))
    return mask


def get_all_base_currencies_at_exchange(exchange):
    """Returns all currencies that are available as base currency."""
    check_isinstance_exchange(exchange)

    bases = []

    for market in exchange.markets:
        currency = exchange.markets[market]['base']
        if not currency in bases:
            bases.append(currency)

    return bases


def amount_base_currencies_at_exchange(exchange):
    """Returns the amount of base currencies."""
    base = get_all_base_currencies_at_exchange(exchange)
    return len(base)
