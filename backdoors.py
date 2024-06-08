import re
import sys
from pathlib import Path
from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
from concurrent.futures import ProcessPoolExecutor


def find_hards(backdoor, solver):
    hards = []
    for bitmask in range(2**len(backdoor)):
        assump = []
        for bit in range(len(backdoor)):
            assump.append(backdoor[bit] if ((bitmask >> bit) & 1) == 0 else -backdoor[bit])
        solver.conf_budget(CONF_BUDGET)
        res = solver.solve_limited(assumptions=assump)
        if res is None:
            hards.append(assump)
    return hards


def merge_assump(a1, a2, units):
    res = a1.copy()
    for lit in a2:
        if -lit in units:
            return None
        elif lit in units:
            continue
        if -lit in a1:
            return None
        elif lit not in a1:
            res.append(lit)
    return res


def check_hard(hard, clauses, unit_list):
    solver = Solver(name='cd15', bootstrap_with=clauses)
    assump = hard + unit_list
    solver.conf_budget(1000)
    res = solver.solve_limited(assumptions=assump)
    solver.delete()
    return res is None


def print_stats(units, cur_hards):
    global bd_id
    bd_id += 1
    print('Backdoors:', bd_id, 'Literals now:', len(cur_hards[0]), 'Units found:', len(units), 'Hards now:', len(cur_hards), flush=True)


def task(h1, h2, clauses, units, cur_hards):
    tmp = merge_assump(h1, h2, units)
    if tmp is None:
        return None
    if check_hard(tmp, clauses, list(units)):
        return tmp
    return None

def process_backdoor(backdoor, solver, units, cur_hards, cnf):
    bd_hards = find_hards(backdoor, solver)
    new_hards = []

    with ProcessPoolExecutor() as pool:
        futures = []
        for h1 in cur_hards:
            for h2 in bd_hards:
                futures.append(pool.submit(task, h1, h2, cnf.clauses, units, cur_hards))
        for f in futures:
            res = f.result()
            if res is not None:
                new_hards.append(res)

    if not new_hards:
        print('HOLY SHIT WE SOLVED IT!!!')

    fl = [True] * len(new_hards[0])
    for i in range(1, len(new_hards)):
        for j in range(len(new_hards[0])):
            if new_hards[i][j] != new_hards[0][j]:
                fl[j] = False
    for i in range(len(new_hards[0])):
        if fl[i]:
            units.add(new_hards[0][i])

    cur_hards.clear()
    for h in new_hards:
        new_h = []
        for i in range(len(h)):
            if not fl[i]:
                new_h.append(h[i])
        cur_hards.append(new_h)

    print_stats(units, cur_hards)


def dump(units, cur_hards):
    global dump_id
    dump_id += 1
    with open("Backdoors/implications.txt", 'w') as fout:
        print(*list(units), file=fout)
    with open("Backdoors/hards_dump" + str(dump_id), 'w') as fout:
        print(*cur_hards, sep='/n', file=fout)


def process_file(backdoor_file, solver, units, cur_hards, cnf):
    with open(backdoor_file, 'r') as fin:
        for line in fin:
            global bd_id
            if bd_id < SKIP_BD_ID:
                bd_id += 1
                continue
            tmp = [s for s in re.split('[ [\],]', line) if s]
            backdoor = [int(x) for x in tmp[1:11]]
            process_backdoor(backdoor, solver, units, cur_hards, cnf)
            if len(cur_hards) * len(cur_hards[0]) > 50000:
                dump(units, cur_hards)
                cur_hards.clear()
                cur_hards.append([])


if __name__ == '__main__':
    in_file = sys.argv[1]
    INPUT_VARS = 24
    SKIP_BD_ID = 81
    bd_id = 0
    dump_id = 0
    CONF_BUDGET = 1000

    with open(in_file, 'r') as fin:
        line = fin.readline().split()
        VARS = int(line[2])
        CLAUSES = int(line[3])
    cnf = CNF(from_file=in_file)
    solver = Solver(name='cd15', bootstrap_with=cnf.clauses)
    units = set()
    cur_hards = [[]]

    with open('Backdoors/implications.txt', 'r') as fin:
        for lit in [int(x) for x in fin.readline().split()]:
            units.add(lit)
    
    files = Path("Backdoors").glob("*10*")
    for path in files:
        process_file(str(path), solver, units, cur_hards, cnf)
        print('Processed another file!')
