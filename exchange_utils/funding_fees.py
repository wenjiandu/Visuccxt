from exchange_utils._checks import check_isinstance_exchange, check_isinstance_string, \
    check_isinstance_list


# --------- [ Funding Fee ] ---------
def has_funding_fees(exchange):
    # TODO: This is not correct. Just because there is an entry doesn't mean it has fees. Could be 0...
    """Checks whether the exchange has funding fees. (via/in ccxt)"""
    check_isinstance_exchange(exchange)
    return bool(exchange.fees['funding'])


def get_exchanges_with_funding_fees(exchanges):
    # TODO: This is not correct. Just because there is an entry doesn't mean it has fees. Could be 0...
    """Returns a list of exchanges that have funding fees."""
    check_isinstance_list(exchanges)
    exchanges_with_funding_fees = []
    for exchange in exchanges:
        if has_funding_fees(exchange):
            exchanges_with_funding_fees.append(exchange)
    return exchanges_with_funding_fees


# --------- [ Deposit Fee ] ---------
def has_deposit_fee_for_currency(exchange, currency):
    """
    Checks if the given exchange supports the deposit of
    the specified currency.

    :param exchange: an exchange (as Exchange)
    :param currency: a currency (as str)
    :return: True/False
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(currency)

    if has_funding_fees(exchange):
        try:
            depo = exchange.fees['funding']['deposit']
            if currency in depo:
                if depo[currency] == 0:
                    return False
                else:
                    return True
            else:
                return False
        except:
            return False
    else:
        return False


def has_deposit_fees_for_any_given_currency(exchange, currencies):
    """
    Checks if the given exchange supports the deposit of
    the specified currencies.

    :param exchange: an exchange (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: True/False
    """

    check_isinstance_exchange(exchange)
    check_isinstance_list(currencies)

    for currency in currencies:
        if has_deposit_fee_for_currency(exchange, currency):
            return True
    return False


def has_deposit_fees_for_any_its_currencies(exchange):
    check_isinstance_exchange(exchange)

    if has_funding_fees(exchange):
        try:
            depo = exchange.fees['funding']['deposit']
            for price in depo.values():
                if price != 0:
                    return True
        except (KeyError, TypeError, AttributeError) as e:
            print(e)
    return False


# TODO:
def get_deposit_fee_for_currency_at_exchange():
    pass


# TODO:
def get_deposit_fee_fee_for_currency_at_exchanges():
    pass


# TODO:
def get_deposit_fees_for_currencies_at_exchange():
    pass


# TODO:
def get_deposit_fees_for_currencies_at_exchanges():
    pass


# --------- [ Withdraw Fee ] ---------
def has_withdraw_fee_for_currency(exchange, currency):
    """
    Checks if the given exchange supports the withdraw of
    the specified currency.

    :param exchange: an exchange (as Exchange)
    :param currency: a currency (as str)
    :return: True/False
    """
    check_isinstance_exchange(exchange)
    check_isinstance_string(currency)

    if has_funding_fees(exchange):
        try:
            depo = exchange.fees['funding']['withdraw']
            if currency in depo:
                if depo[currency] == 0:
                    return False
                else:
                    return True
            else:
                return False
        except:
            return False
    else:
        return False


def has_withdraw_fees_for_any_given_currency(exchange, currencies):
    """
    Checks if the given exchange supports the withdraw of
    the specified currencies.

    :param exchange: an exchange (as Exchange)
    :param currencies: a list of currencies (as str)
    :return: True/False
    """

    check_isinstance_exchange(exchange)
    check_isinstance_list(currencies)

    for currency in currencies:
        if has_withdraw_fee_for_currency(exchange, currency):
            return True
    return False


def has_withdraw_fees_for_any_its_currencies(exchange):
    check_isinstance_exchange(exchange)

    if has_funding_fees(exchange):
        try:
            depo = exchange.fees['funding']['withdraw']
            for price in depo.values():
                if price != 0:
                    return True
        except (KeyError, TypeError, AttributeError) as e:
            print(e)

    return False


# TODO:
def get_withdraw_fee_for_currency_at_exchange():
    pass


# TODO:
def get_withdraw_fee_fee_for_currency_at_exchanges():
    pass


# TODO:
def get_withdraw_fees_for_currencies_at_exchange():
    pass


# TODO:
def get_withdraw_fees_for_currencies_at_exchanges():
    pass
