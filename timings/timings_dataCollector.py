"""
Those Timings were calculated with beneath code.
While there is some initialization and appending drawback, numpy outperform
both deque approach by a huge margin. Especially when the the slices need
to be very large.

                  Numpy create:        2.990 micros
                  Deque create:        0.603 micros

                  Numpy append:        1.932 micros
                  Deque append:        0.290 micros

                   Numpy get 1:        0.315 micros
       (List Comp) Deque get 1:        2.855 micros
      (Iter slice) Deque get 1:      488.306 micros

                   Numpy get 5:        0.311 micros
       (List Comp) Deque get 5:        0.969 micros
      (Iter slice) Deque get 5:      509.149 micros

                  Numpy get 10:        0.321 micros
      (List Comp) Deque get 10:        1.306 micros
     (Iter slice) Deque get 10:      497.096 micros

                  Numpy get 50:        0.359 micros
      (List Comp) Deque get 50:        3.294 micros
     (Iter slice) Deque get 50:      502.389 micros

                 Numpy get 100:        0.320 micros
     (List Comp) Deque get 100:        5.888 micros
    (Iter slice) Deque get 100:      500.680 micros

                 Numpy get 250:        0.320 micros
     (List Comp) Deque get 250:      14.017 micros
    (Iter slice) Deque get 250:      497.639 micros

                 Numpy get 500:        0.331 micros
     (List Comp) Deque get 500:       26.615 micros
    (Iter slice) Deque get 500:      497.205 micros

                Numpy get 1000:        0.326 micros
    (List Comp) Deque get 1000:       56.327 micros
   (Iter slice) Deque get 1000:      504.340 micros

                Numpy get 5000:        0.319 micros
    (List Comp) Deque get 5000:      767.399 micros
   (Iter slice) Deque get 5000:      521.793 micros

               Numpy get 10000:        0.321 micros
   (List Comp) Deque get 10000:     3450.182 micros
  (Iter slice) Deque get 10000:      585.676 micros

               Numpy get 50000:        0.321 micros
   (List Comp) Deque get 50000:   115701.343 micros
  (Iter slice) Deque get 50000:      922.717 micros
"""


from data.dataCollectorDeque import DataCollectorDeque
from data.dataCollectorNumpy import DataCollectorNumpy
from timings.compareExecutionTime import CompareExecutionTime

pairs = ['ABC', 'DEF', 'GHD', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZ']
values = dict.fromkeys(pairs, 0)


def numpy_create():
    return DataCollectorNumpy(pairs)


def deque_create():
    return DataCollectorDeque(pairs)


dcn = numpy_create()
dcq = deque_create()

for i in range(100000):
    dcq.append(values)

def numpy_append():
    dcn.append(values)


def deque_append():
    dcq.append(values)


def numpy_get1(num=1): return dcn.get(num)
def numpy_get5(num=5): return dcn.get(num)
def numpy_get10(num=10): return dcn.get(num)
def numpy_get50(num=50): return dcn.get(num)
def numpy_get100(num=100): return dcn.get(num)
def numpy_get250(num=250): return dcn.get(num)
def numpy_get500(num=500): return dcn.get(num)
def numpy_get1000(num=1000): return dcn.get(num)
def numpy_get5000(num=5000): return dcn.get(num)
def numpy_get10000(num=10000): return dcn.get(num)
def numpy_get50000(num=50000): return dcn.get(num)

def deque_get1(num=1): return dcq.get(num)
def deque_get5(num=5): return dcq.get(num)
def deque_get10(num=10): return dcq.get(num)
def deque_get50(num=50): return dcq.get(num)
def deque_get100(num=100): return dcq.get(num)
def deque_get250(num=250): return dcq.get(num)
def deque_get500(num=500): return dcq.get(num)
def deque_get1000(num=1000): return dcq.get(num)
def deque_get5000(num=5000): return dcq.get(num)
def deque_get10000(num=10000): return dcq.get(num)
def deque_get50000(num=50000): return dcq.get(num)

def deque_get21(num=1): return dcq.get2(num)
def deque_get25(num=5): return dcq.get2(num)
def deque_get210(num=10): return dcq.get2(num)
def deque_get2250(num=50): return dcq.get2(num)
def deque_get2100(num=100): return dcq.get2(num)
def deque_get2250(num=250): return dcq.get2(num)
def deque_get2500(num=500): return dcq.get2(num)
def deque_get21000(num=1000): return dcq.get2(num)
def deque_get25000(num=5000): return dcq.get2(num)
def deque_get210000(num=10000): return dcq.get2(num)
def deque_get250000(num=50000): return dcq.get2(num)


# print(numpy_get10())
# print(deque_get10())
# print(deque_get210())

functions_to_time = {'Numpy create': numpy_create,
                     'Deque create': deque_create,
                     'Numpy append': numpy_append,
                     'Deque append': deque_append,
                     'Numpy get 1': numpy_get1,
                     '(List Comp) Deque get 1': deque_get1,
                     '(Iter slice) Deque get 1': deque_get21,
                     'Numpy get 5': numpy_get5,
                     '(List Comp) Deque get 5': deque_get5,
                     '(Iter slice) Deque get 5': deque_get25,
                     'Numpy get 10': numpy_get10,
                     '(List Comp) Deque get 10': deque_get10,
                     '(Iter slice) Deque get 10': deque_get210,
                     'Numpy get 50': numpy_get50,
                     '(List Comp) Deque get 50': deque_get50,
                     '(Iter slice) Deque get 50': deque_get250,
                     'Numpy get 100': numpy_get100,
                     '(List Comp) Deque get 100': deque_get100,
                     '(Iter slice) Deque get 100': deque_get2100,
                     'Numpy get 250': numpy_get250,
                     '(List Comp) Deque get 250': deque_get250,
                     '(Iter slice) Deque get 250': deque_get2250,
                     'Numpy get 500': numpy_get500,
                     '(List Comp) Deque get 500': deque_get500,
                     '(Iter slice) Deque get 500': deque_get2500,
                     'Numpy get 1000': numpy_get1000,
                     '(List Comp) Deque get 1000': deque_get1000,
                     '(Iter slice) Deque get 1000': deque_get21000,
                     'Numpy get 5000': numpy_get5000,
                     '(List Comp) Deque get 5000': deque_get5000,
                     '(Iter slice) Deque get 5000': deque_get25000,
                     'Numpy get 10000': numpy_get10000,
                     '(List Comp) Deque get 10000': deque_get10000,
                     '(Iter slice) Deque get 10000': deque_get210000,
                     'Numpy get 50000': numpy_get50000,
                     '(List Comp) Deque get 50000': deque_get50000,
                     '(Iter slice) Deque get 50000': deque_get250000
                     }

CompareExecutionTime(functions_to_time).time(repeat=3, number=100, micro=True)

# for i in [1, 5, 10, 50, 100, 250, 500, 1000, 5000, 10000, 50000]:
#     print("def numpy_get{}(num={}): return dcn.get(num)".format(i, i))
#
# for i in [1, 5, 10, 50, 100, 250, 500, 1000, 5000, 10000, 50000]:
#     print("def deque_get{}(num={}): return dcq.get(num)".format(i, i))
#
# for i in [1, 5, 10, 50, 100, 250, 500, 1000, 5000, 10000, 50000]:
#     print("def deque_get2{}(num={}): return dcq.get2(num)".format(i, i))

# for i in [1, 5, 10, 50, 100, 250, 500, 1000, 5000, 10000, 50000]:
#     print("'Numpy get {}': numpy_get{},".format(i, i))
#     print("'Deque get {}': deque_get{},".format(i, i))
#     print("'Deque get2 {}': deque_get2{},".format(i, i))
