from pysat.formula import CNF
from pysat.solvers import Solver
import matplotlib.pyplot as plt

implications = CNF(from_file='Backdoors/implications_cnf.txt')
units = set()
pairs = set()
vars = set()

for cl in implications.clauses:
    if len(cl) == 1:
        units.add(cl[0])
    else:
        x1, x2 = cl
        if abs(x1) > abs(x2):
            x2, x1 = x1, x2
        if x1 not in units and x2 not in units:
            pairs.add((x1, x2))
            vars.add(abs(x1))
            vars.add(abs(x2))

# for cl in pairs:
#     x1, x2 = cl
#     if (-x1, x2) in pairs:
#         print('!', x2)
#     if (x1, -x2) in pairs:
#         print('!', x1)
# -- Gave no result

in_file = 'Backdoors/CvK12_horn.cnf'
cnf = CNF(from_file=in_file)
with open(in_file, 'r') as fin:
    line = fin.readline().split()
    VARS = int(line[2])
    CLAUSES = int(line[3])
solver = Solver(name='cd15', bootstrap_with=cnf.clauses)

cnf_pairs = set()
cnf_long = set()
for cl in cnf.clauses:
    if len(cl) == 2:
        x1, x2 = cl
        if abs(x1) > abs(x2):
            x2, x1 = x1, x2
        cnf_pairs.add((x1, x2))
    else:
        cnf_long.add(tuple(cl))

hist = [[0, i] for i in range(1, VARS + 1)]
for cl in pairs:
    x, y = cl
    hist[x][0] += 1
    hist[y][0] += 1
plt.hist([x[0] for x in hist if x[0] > 2], bins=500)
plt.show()
hist.sort(reverse=True)
print(hist)

intersection = cnf_pairs.intersection(pairs)
print(len(intersection))


solver = Solver(name='cd15')
for cl in pairs.union(cnf_pairs):
    solver.add_clause(cl)
cnt = 0
for lit in range(1, VARS + 1):
    if lit in units or -lit in units:
        continue
    if not solver.solve(assumptions=[lit]):
        print(lit, 'is False')
        units.add(-lit)
    elif not solver.solve(assumptions=[-lit]):
        print(lit, 'is True')
        units.add(lit)
    cnt += 1
    if cnt % 100 == 0:
        print('Progress - ', cnt)
print(len(units))
with open('out.txt', 'w') as fout:
    print(*list(units), file=fout)


# print(len(cnf_long))
# cnt = 0
# for cl in pairs:
#     to_delete = []
#     for big_cl in cnf_long:
#         if cl[0] in big_cl and cl[1] in big_cl:
#             to_delete.append(big_cl)
#             cnt += 1
#     for big_cl in to_delete:
#         cnf_long.remove(big_cl)
#     if to_delete:
#         cnf_pairs.add(cl)
# -- Removed 111 clauses

# final_cnf = CNF()
# for lit in units:
#     final_cnf.append([lit])
# for cl in cnf_pairs:
#     final_cnf.append(cl)
# for cl in cnf_long:
#     final_cnf.append(cl)
# with open('tests/cnf.txt', 'w') as fout:
#     print(final_cnf.to_dimacs(), file=fout)
