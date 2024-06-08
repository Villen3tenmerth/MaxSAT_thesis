import random
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from concurrent.futures import ProcessPoolExecutor
import time
import sys


def add_xor_wcnf(wcnf, xs, fl):
    if fl == 0:
        xs[-1] = -xs[-1]
    k = len(xs)
    for mask in range(1 << k):
        sum = 0
        for i in range(k):
            sum += ((mask >> i) & 1)
        if sum % 2 == 0:
            cl = []
            for i in range(k):
                cl.append(xs[i] if ((mask >> i) & 1) == 0 else -xs[i])
            wcnf.append(cl)


def test_maxSAT(wcnf):
    INPUT_VARS = 60

    STEP = 5
    for i in range(0, INPUT_VARS, STEP):
        fl = random.randint(0, 1)
        add_xor_wcnf(wcnf, list(range(i + 1, i + STEP + 1)), fl)
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


def calc(bitmask, pow):
    wcnf = WCNF()
    for i in range(len(bitmask)):
        if bitmask[i] == 1:
            wcnf.append(cnf.clauses[i], weight=1)
        else:
            wcnf.append(cnf.clauses[i])
    conf = 0

    with ProcessPoolExecutor() as pool:
        futures = []
        for x in range(N):
            futures.append(pool.submit(test_maxSAT, wcnf.copy()))
        for f in futures:
            conf += f.result()

    return conf / N * 2 ** pow


if __name__ == '__main__':
    # in_file = sys.argv[1]
    in_file = 'Factorizations/fact_C_32_32.cnf'
    with open(in_file, 'r') as fin:
        line = fin.readline().split()
        VARS = int(line[2])
        CLAUSES = int(line[3])
    cnf = CNF(from_file=in_file)
    INPUT_VARS = 64

    with open('bitmask.txt', 'r') as fin:
        bitmask = [int(x) for x in fin.readline().split()]
    assert(len(bitmask) == CLAUSES)

    N = 15
    POW = 12
    res = calc(bitmask, POW)
    print('Start - ', res)
    for e_step in range(100000):
        new_mask = mutate(bitmask)
        new_res = calc(new_mask, POW)
        if new_res < res:
            res = new_res
            bitmask = new_mask
            with open('bitmask.txt', 'w') as fout:
                print(*bitmask, file=fout)
            print('Found: ', res, 'on step', e_step)
        if e_step % 100 == 0:
            print('Done iterations - ', e_step)
