import random
import sys
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.card import *

in_file = sys.argv[1]
with open(in_file, 'r') as fin:
    line = fin.readline().split()
    VARS = int(line[2])
    CLAUSES = int(line[3])
    line = fin.readline().split()
    INPUT_VARS = int(line[-1])
cnf = CNF(from_file=in_file)


def test_maxSAT(wcnf, mask):
    for i in range(INPUT_VARS // 2):
        x = 2 * i + 1
        y = 2 * i + 2 if (mask >> i) == 1 else -2 * i - 2
        wcnf.append([x, y])
        wcnf.append([-x, -y])

    solver = RC2(wcnf, incr=True, solver='g3')
    solver.compute()

    conf = solver.oracle.accum_stats()['conflicts']
    sec = solver.oracle_time()
    print(conf, sec)
    solver.delete()
    return conf, sec


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


sum_conf = 0
sum_sec = 0
POW = INPUT_VARS // 2
for mask in range(1 << POW):
    conf, sec = test_maxSAT(wcnf.copy(), mask)
    sum_conf += conf
    sum_sec += sec
print('Conflcits - ', sum_conf)
print('Seconds - ', sum_sec)
