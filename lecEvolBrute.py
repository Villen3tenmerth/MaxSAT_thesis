import random
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from concurrent.futures import ProcessPoolExecutor
import time
import sys


def test_maxSAT(wcnf):
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
    return test_maxSAT(wcnf)


def getStartingMask(cnf):
    # HARD_START = int(sys.argv[2])
    HARD_START = 250
    return ([0] * HARD_START) + ([1] * (len(cnf.clauses) - HARD_START))


if __name__ == '__main__':
    # in_file = sys.argv[1]
    in_file = 'tests/Small/ram_k3_n10.ra1.wcnf'
    cnf = WCNF(from_file=in_file).unweighted()

    bitmask = getStartingMask(cnf)
    assert len(bitmask) == len(cnf.clauses)
    res = calc(bitmask)
    print('Start - ', res)
    for e_step in range(100000):
        new_mask = mutate(bitmask)
        new_res = calc(new_mask)
        if new_res < res:
            res = new_res
            bitmask = new_mask
            with open('bitmask.txt', 'w') as fout:
                print(*bitmask, file=fout)
            print('Found: ', res, 'on step', e_step)
        if e_step % 100 == 0:
            print('Done iterations - ', e_step)
