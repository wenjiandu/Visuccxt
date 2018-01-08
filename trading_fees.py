import ccxt
from _checks import *


# TODO: Docstring all functions.
# --------- [ Maker Fees ] ---------
from _checks import check_isinstance_list


# --------- [ Maker Fees ] ---------
def has_maker_fee(exchange):

    check_isinstance_exchange(exchange)

    if 'maker' in exchange.fees['trading']:
        return True
    else:
        return False


def get_maker_fee_from_exchange(exchange):

    check_isinstance_exchange(exchange)

    if has_maker_fee(exchange):
        return exchange.fees['trading']['maker']


def get_maker_fee_from_exchanges(exchanges):

    check_isinstance_list(exchanges)

    fees = {}

    for exchange in exchanges:
        fee = get_maker_fee_from_exchange(exchange)
        fees[exchange.id] = fee
    return fees


def get_maker_fee_from_exchanges_deep(exchanges):

    check_isinstance_list(exchanges)

    exchanges = get_exchanges_with_maker_fee(exchanges)

    ex_tier = get_exchanges_with_tier_based_fees(exchanges)
    ex_normal = get_exchanges_without_tier_based_fees(exchanges)

    fees_tier = get_tier_based_maker_fees_from_exchanges(ex_tier)
    fees_normal = get_maker_fee_from_exchanges(ex_normal)

    fees_out = {**fees_tier, **fees_normal}
    return fees_out


def get_exchanges_with_maker_fee(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if has_maker_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


def get_exchanges_without_maker_fee(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if not has_maker_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


# --------- [ Taker Fees ] ---------
def has_taker_fee(exchange):

    check_isinstance_exchange(exchange)

    if 'taker' in exchange.fees['trading']:
        return True
    else:
        return False


def get_taker_fee_from_exchange(exchange):

    check_isinstance_exchange(exchange)

    if has_taker_fee(exchange):
        return exchange.fees['trading']['taker']


def get_taker_fee_from_exchanges(exchanges):

    check_isinstance_list(exchanges)

    fees = {}

    for exchange in exchanges:
        fee = get_taker_fee_from_exchange(exchange)
        fees[exchange.id] = fee
    return fees


def get_taker_fee_from_exchanges_deep(exchanges):

    check_isinstance_list(exchanges)

    exchanges = get_exchanges_with_taker_fee(exchanges)

    ex_tier = get_exchanges_with_tier_based_fees(exchanges)
    ex_normal = get_exchanges_without_tier_based_fees(exchanges)

    fees_tier = get_tier_based_taker_fees_from_exchanges(ex_tier)
    fees_normal = get_taker_fee_from_exchanges(ex_normal)

    fees_out = {**fees_tier, **fees_normal}
    return fees_out


def get_exchanges_with_taker_fee(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if has_taker_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


def get_exchanges_without_taker_fee(exchanges):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if not has_taker_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


# --------- [ Percentage Fees ] ---------
def has_percentage_fee(exchange):

    check_isinstance_exchange(exchange)

    if 'percentage' in exchange.fees['trading']:
        return True
    else:
        return False


def get_exchanges_with_percentage_fee(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if has_percentage_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


def get_exchanges_without_percentage_fee(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if not has_percentage_fee(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


# --------- [ Tier-Based Fees ] ---------
def fee_is_tier_based(exchange):

    check_isinstance_exchange(exchange)

    base = exchange.fees['trading']
    if all (k in base for k in ('tierBased', 'tiers')):
        if exchange.fees['trading']['tierBased']:
            return True
    return False


def get_tier_based_maker_fees_from_exchange(exchange):

    check_isinstance_exchange(exchange)

    if fee_is_tier_based(exchange):
        fee = exchange.fees['trading']['tiers']['maker']
        return fee
    else:
        return None


def get_tier_based_taker_fees_from_exchange(exchange):

    check_isinstance_exchange(exchange)

    if fee_is_tier_based(exchange):
        fee = exchange.fees['trading']['tiers']['taker']
        return fee
    else:
        return None


def get_tier_based_maker_fees_from_exchanges(exchanges):

    check_isinstance_list(exchanges)

    fees_out = {}

    for exchange in exchanges:
        fee = get_tier_based_maker_fees_from_exchange(exchange)
        if fee:
            fees_out[exchange.id] = fee
    return fees_out


def get_tier_based_taker_fees_from_exchanges(exchanges):

    check_isinstance_list(exchanges)

    fees_out = {}

    for exchange in exchanges:
        fee = get_tier_based_taker_fees_from_exchange(exchange)
        if fee:
            fees_out[exchange.id] = fee
    return fees_out


def get_exchanges_with_tier_based_fees(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if fee_is_tier_based(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


def get_exchanges_without_tier_based_fees(exchanges, as_str=False):

    check_isinstance_list(exchanges)

    ex_out = []

    for exchange in exchanges:
        if not fee_is_tier_based(exchange):
            ex_out.append(exchange)

    if as_str:
        ex_str_out = []
        for exchange in ex_out:
            ex_str_out.append(exchange.id)
        return ex_str_out

    return ex_out


# --------- [ General Trading ] ---------
def get_exchanges_with_trading_fees(exchanges):

    check_isinstance_list(exchanges)

    maker = set(get_exchanges_with_maker_fee(exchanges))
    taker = set(get_exchanges_with_taker_fee(exchanges))

    if maker == taker:
        return maker
    else:
        diff = taker - maker
        maker.update(diff)
        return maker
