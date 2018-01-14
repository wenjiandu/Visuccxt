from termcolor import colored


def print_colored_percentage(pair, init, now, percentage, top=0.025, low=-0.025):
    """
    Prints the output depending of the percentage change and the given
    boundaries for the percentage value. (Positive: Green; Negative: Red)

    :param pair: the pair to print.
    :param init: the initial price (start of script) of the pair.
    :param now: the current price of the pair.
    :param percentage: the change in %.
    :param top: the upper boundary (positive %) for printing green.
    :param low: the lower boundary (negative %) for printing red.
    :return:
    """
    if percentage > top:
        p_percentage = colored("{:<+6.3%}", 'green', attrs=['bold'])
    elif percentage < low:
        p_percentage = colored("{:<+6.3%}", 'red', attrs=['bold'])
    else:
        p_percentage = colored("{:<+6.3%}", attrs=['bold'])

    print((colored("{:<8}", attrs=['bold']) +
           "  |  {:<10.8f} - {:<10.8f} -  " + p_percentage)
          .format(pair, init, now, percentage))


def print_colored_line(pair, init, now, percentage, top=0.025, low=-0.025):
    """
    Prints the output depending of the percentage change and the given
    boundaries for the complete line. (Positive: Green; Negative: Red)

    :param pair: the pair to print.
    :param init: the initial price (start of script) of the pair.
    :param now: the current price of the pair.
    :param percentage: the change in %.
    :param top: the upper boundary (positive %) for printing green.
    :param low: the lower boundary (negative %) for printing red.
    :return:
    """
    if percentage > top:
        color = 'green'
    elif percentage < low:
        color = 'red'
    else:
        color = None

    print((colored("{:<8}  |  {:<10.8f} - {:<10.8f} -  {:<+6.3%}"
                   , color, attrs=['bold']))
          .format(pair, init, now, percentage))
