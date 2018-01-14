from exchange._checks import check_isinstance_exchange, check_isinstance_string, \
    check_isinstance_list


# --------- [ Quote ] ---------
def is_quote_available_at_exchange(exchange, quote):
    """
    Checks if the specified quote is available at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param quote: a quote currency (as str)
    :return: Boolean
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(quote)

    quotes = get_all_quote_currencies_at_exchange(exchange)

    if quote in quotes:
        return True
    else:
        return False


def are_quotes_available_at_exchange(exchange, quotes):
    """
    Checks if the specified quotes are available at the given exchange.

    :param exchange: an exchange (as Exchange)
    :param quote: a list of quote currencies (as str)
    :return: Boolean
    """
    check_isinstance_exchange(exchange)
    check_isinstance_list(quotes)

    mask = []

    for quote in quotes:
        mask.append(is_quote_available_at_exchange(exchange, quote))
    return mask


def get_all_quote_currencies_at_exchange(exchange):
    """Returns all currencies that are available as quote currency."""
    check_isinstance_exchange(exchange)

    quotes = []

    for market in exchange.markets:
        currency = exchange.markets[market]['quote']
        if not currency in quotes:
            quotes.append(currency)

    return quotes


def amount_quote_currencies_at_exchange(exchange):
    """Returns the amount of quote currencies."""
    quote = get_all_quote_currencies_at_exchange(exchange)
    return len(quote)
