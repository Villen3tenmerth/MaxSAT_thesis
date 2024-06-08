import random
import sys

from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
from wcnf_utils import *

SOFT_LAYERS = 5   # initial soft/hard split
N = 6      # number of tests for fitness function
STEPS = 10 ** 6

in_file = sys.argv[1]
cnf = readCNF(in_file)
bitmask = readWcnfLayers(in_file, SOFT_LAYERS)


def test_maxSAT(wcnf, rnd):
    idx = 0
    for i in range(14):
        x = 2 * i + 1 if rnd[idx] == 1 else -2 * i - 1
        y = 2 * i + 2 if rnd[idx + 1] == 1 else -2 * i - 2
        idx += 2
        wcnf.append([x, y])
    solver = RC2(wcnf, incr=True, solver='g3')
    solver.compute()

    ret = solver.oracle.accum_stats()['conflicts']
    solver.delete()
    return ret


def mutate(mask):
    new_mask = []
    sz = len(mask)
    for b in mask:
        if random.randint(1, sz) == 1:
            new_mask.append(1 - b)
        else:
            new_mask.append(b)
    return new_mask


def calc(bitmask):
    wcnf = WCNF()
    for i in range(len(bitmask)):
        if bitmask[i] == 1:
            wcnf.append(cnf.clauses[i], weight=1)
        else:
            wcnf.append(cnf.clauses[i])
    conf = 0
    for x in range(N):
        conf += test_maxSAT(wcnf.copy(), rnd_seq[x])
    return conf / N


rnd_seq = []
for i in range(N):
    random.seed(19937 + 239 * i)
    seq = []
    for j in range(28):
        seq.append(random.randint(0, 1))
    rnd_seq.append(seq)


res = calc(bitmask)
print(res)
for e_step in range(STEPS):
    new_mask = mutate(bitmask)
    new_res = calc(new_mask)
    if new_res < res:
        res = new_res
        bitmask = new_mask
        print(res)
