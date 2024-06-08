import sys
from pysat.formula import CNF
import ast

def readCNF(in_file):
    in_file = sys.argv[1]
    with open(in_file, 'r') as fin:
        line = fin.readline().split()
        VARS = int(line[2])
        CLAUSES = int(line[3])
    cnf = CNF(from_file=in_file)
    return cnf


def readWcnfLayers(in_file, n_soft):
    cnf = readCNF(in_file)
    with open(in_file, 'r') as fin:
        _ = fin.readline()
        line = fin.readline()
        layers = ast.literal_eval(line)

    var_layers = [0] * cnf.nv
    for i in range(len(layers)):
        for v in layers[i]:
            var_layers[v] = i + 1

    bitmask = []
    for cl in cnf.clauses:
        max_l = 0
        for lit in cl:
            max_l = max(max_l, var_layers[abs(lit)])
        if max_l <= n_soft:
            bitmask.append(1)
        else:
            bitmask.append(0)

    # with open('bitmask.txt', 'w') as fout:
    #     print(*bitmask, file=fout)
    return bitmask


def readWcnfHorn(in_file):
    cnf = readCNF(in_file)

    bitmask = []
    for cl in cnf.clauses:
        l = 0
        for lit in cl:
            if lit < 0:
                l += 1
        if l <= 1:
            bitmask.append(0)
        else:
            bitmask.append(1)

    return bitmask
