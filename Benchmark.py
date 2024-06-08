from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
from concurrent.futures import ProcessPoolExecutor
import numpy


def test_sat(cnf, solver_name):
    solver = Solver(name=solver_name, bootstrap_with=cnf.clauses, use_timer=True)
    if solver.solve():
        raise RuntimeError("Solution was found")
    conf = solver.accum_stats()['conflicts']
    sec = solver.time()
    solver.delete()
    return conf, sec


def test_max_sat(wcnf):
    solver = RC2(wcnf, incr=True, solver='g3')
    solver.compute()
    conf = solver.oracle.accum_stats()['conflicts']
    sec = solver.oracle_time()
    solver.delete()
    return conf, sec


def test_mask(cnf, solver_name, mask_size, mask):
    new_cnf = cnf.copy()
    for i in range(0, mask_size):
        x = i * 2 + 1
        y = i * 2 + 2
        if (mask >> i) == 0:
            new_cnf.append([-x, y])
            new_cnf.append([x, -y])
        else:
            new_cnf.append([x, y])
            new_cnf.append([-x, -y])
    return test_sat(new_cnf, solver_name)


def test_maxsat_mask(cnf, mask_size, mask):
    wcnf = WCNF()
    for c in cnf.clauses:
        wcnf.append(c, 1)
    for i in range(0, mask_size):
        x = i * 2 + 1
        y = i * 2 + 2
        if (mask >> i) == 0:
            wcnf.append([-x, y])
            wcnf.append([x, -y])
        else:
            wcnf.append([x, y])
            wcnf.append([-x, -y])
    return test_max_sat(wcnf)


def task(solver_name, cnf_file, mask_size, beg, end):
    cnf = CNF(from_file=cnf_file)
    conf = []
    sec = []
    for mask in range(beg, end):
        if solver_name == 'rc2':
            c, s = test_maxsat_mask(cnf, mask_size, mask)
        else:
            c, s = test_mask(cnf, solver_name, mask_size, mask)
        conf.append(c)
        sec.append(s)
    return conf, sec


def print_stats(arr):
    print(numpy.min(arr), end=', ')
    print(numpy.max(arr), end=', ')
    print("%.3f" % numpy.average(arr), end=', ')
    print("%.3f" % numpy.std(arr), end='; ')


def main(solver_name, cnf_file, mask_size):
    masks = 1 << mask_size
    threads = 32
    batch = masks // threads
    conf = []
    sec = []

    futures = []
    with ProcessPoolExecutor() as pool:
        for i in range(threads):
            futures.append(pool.submit(task, solver_name, cnf_file, mask_size, batch * i, batch * (i + 1)))
        for f in futures:
            c, s = f.result()
            conf += c
            sec += s
    print(cnf_file, ' ', end='')
    print_stats(conf)
    print_stats(sec)
    print('')


if __name__ == '__main__':
    solvers = ['mgh', 'cdl', 'rc2']
    tests = []
    tests.append('Data/Multipliers/lec_CvK_12.cnf')
    tests.append('Data/Multipliers/lec_CvW_12.cnf')
    tests.append('Data/Multipliers/lec_DvC_12.cnf')
    tests.append('Data/Multipliers/lec_DvK_12.cnf')

    for s in solvers:
        print('Solver:', s)
        for t in tests:
            main(s, t, 12)

    tests = []
    tests.append('Data/Sorters/lec_BvP_7_4.cnf')
    tests.append('Data/Sorters/lec_BvS_7_4.cnf')
    tests.append('Data/Sorters/lec_PvS_7_4.cnf')

    for s in solvers:
        print('Solver:', s)
        for t in tests:
            main(s, t, 14)
