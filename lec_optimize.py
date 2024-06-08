import random
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
from pysat.card import *
from math import exp

cnf = CNF(from_file="Multipliers/lec_CvK_12.cnf")
bitset = [0] * len(cnf.clauses)


temp = 1
step = 0.999
def chance(ans1, ans2):
    return exp((ans1 - ans2) / temp)
def gen_rand():
    x = random.randint(1, 100000000)
    y = random.randint(1, 100000000)
    x %= y
    return x / y


def mutate(bitset, seed):
    random.seed(seed)
    for i in range(len(bitset)):
        if random.randint(1, 100) == 100:
            bitset[i] ^= 1
    return bitset


def get_wcnf(bitset):
    wcnf = WCNF()
    for i in range(len(bitset)):
        if bitset[i] == 1:
            wcnf.append(cnf.clauses[i], weight=1)
        else:
            wcnf.append(cnf.clauses[i])
    for i in range(4):
        wcnf.append([-i - 1])
        wcnf.append([-i - 13])
    return wcnf


def test_maxSAT(wcnf, seed):
    random.seed(seed)
    for i in [2, 3, 4, 5, 8, 9, 10, 11]:
        x = 2 * i + 1 if random.randint(0, 1) == 1 else -2 * i - 1
        y = 2 * i + 2 if random.randint(0, 1) == 1 else -2 * i - 2
        wcnf.append([x, y])
    solver = RC2(wcnf, incr=True, solver='g3')
    solver.compute()

    ret = solver.oracle.accum_stats()['conflicts']
    solver.delete()
    return ret


def test_SAT(seed):
    random.seed(seed)
    solver = Solver(name='g3', use_timer=True, bootstrap_with=cnf.clauses)
    for i in [2, 3, 4, 5, 8, 9, 10, 11]:
        x = 2 * i + 1 if random.randint(0, 1) == 1 else -2 * i - 1
        y = 2 * i + 2 if random.randint(0, 1) == 1 else -2 * i - 2
        solver.add_clause([x, y])

    if solver.solve():
        print('!!!!')

    print(solver.time(), end=' ')
    ret = solver.accum_stats()['conflicts']
    print(ret)
    solver.delete()
    return ret


N = 5
opt = 10 ** 9
cur = 10 ** 9
cool_seed = 0
for x in range(10000):
    seed = 19937 + 239 * x
    old_b = bitset.copy()
    bitset = mutate(bitset.copy(), seed)
    wcnf = get_wcnf(bitset)

    conf = 0
    for i in range(0, 2 * N, 2):
        res = test_maxSAT(wcnf.copy(), i)
        conf += res
    conf /= N
    print(conf)

    if conf < cur or chance(cur, conf) < gen_rand():
        cur = conf
    else:
        bitset = old_b

    if cur < opt:
        opt = cur
        cool_seed = seed
        print(opt, 'seed=', cool_seed)
    temp *= step

print('Optimal conflicts - ', opt)
print('Cool seed - ', cool_seed)

