import timeit

from functools import partial


# https://stackoverflow.com/questions/8220801/how-to-use-timeit-module
class CompareExecutionTime(timeit.Timer):

    def __init__(self, functions_to_compare):
        super().__init__()
        self.functions = functions_to_compare

    def time(self, message=None, repeat=3, number=1000, micro=None):
        if message:
            print(message)
            print("-" * len(message))
        for func_name, func in self.functions.items():
            times = timeit.Timer(partial(func)).repeat(repeat, number)
            time = min(times) / 1000
            if micro:
                print("{:>30}: {:>12.3f} micros".
                      format(func_name, (time * 1000000)))
            else:
                if time > 1:
                    print("{:>30}: {:>9f} s".format(func_name, time))
                elif (time * 1000) > 1:
                    print("{:>30}: {:>9.3f} millis".
                          format(func_name, (time * 1000)))
                else:
                    print("{:>30}: {:>9.3f} micros".
                          format(func_name, (time * 1000000)))

