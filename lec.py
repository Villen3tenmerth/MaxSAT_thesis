import random
import sys
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
from pysat.card import *
from math import exp
from lec_intervals import encode_rel

in_file = sys.argv[1]
with open(in_file, 'r') as fin:
    line = fin.readline().split()
    VARS = int(line[2])
    CLAUSES = int(line[3])
    line = fin.readline().split()
    INPUT_VARS = int(line[-1])
cnf = CNF(from_file=in_file)


def test_maxSAT(wcnf, seed):
    random.seed(seed)
    # for i in range(INPUT_VARS // 2):
    #     x = 2 * i + 1 if random.randint(0, 1) == 1 else -2 * i - 1
    #     y = 2 * i + 2 if random.randint(0, 1) == 1 else -2 * i - 2
    #     wcnf.append([x, y])
    #     wcnf.append([-x, -y])

    MAX_B = 2**INPUT_VARS - 1
    LEN = 2**POW
    lb = random.randint(0, MAX_B - LEN)
    ub = lb + LEN
    for c in encode_rel(list(range(1, INPUT_VARS + 1)), 'both', (lb, ub)):
        wcnf.append(c)

    solver = RC2(wcnf, incr=True, solver='g3')
    solver.compute()

    conf = solver.oracle.accum_stats()['conflicts']
    sec = solver.oracle_time()
    print(conf, sec)
    solver.delete()
    return conf, sec


N = 3

wcnf = WCNF()
with open('bitmask.txt', 'r') as fin:
    bitmask = [int(x) for x in fin.readline().split()]
i = 0
for cl in cnf.clauses:
    if bitmask[i] == 1:
        wcnf.append(cl, weight=1)
    else:
        wcnf.append(cl)
    i += 1

# for cl in cnf.clauses:
#     neg = 0
#     for lit in cl:
#         if lit < 0:
#             neg += 1
#     if neg > 1:
#         wcnf.append(cl, weight=1)
#     else:
#         wcnf.append(cl)

# with open('Backdoors/implications.txt', 'r') as fin:
#     units = [int(x) for x in fin.readline().split()]
#     for lit in units:
#         wcnf.append([lit])

POW = INPUT_VARS - 10
sum_conf = 0
sum_sec = 0
for x in range(N):
    seed = 19937 + 239 * x
    conf, sec = test_maxSAT(wcnf.copy(), x)
    sum_conf += conf
    sum_sec += sec
avg_conf = sum_conf / N
avg_sec = sum_sec / N
# print(avg)
print('Conflcits - ', avg_conf * 2**(INPUT_VARS-POW))
print('Seconds - ', avg_sec * 2**(INPUT_VARS-POW))
