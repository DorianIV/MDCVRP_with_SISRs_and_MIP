import model
import SISRS
import data
import copy
import math
import random
import time

instances = ['Instances/C1_2_' + str(i) + '.txt' for i in range(1, 11)]
After_Construction = ['After_Construction/C1_2_' + str(i) + '.txt' for i in range(1, 11)]
After_Local_Search = ['After_Local_Search/C1_2_' + str(i) + '.txt' for i in range(1, 11)]
costs = {}

def init(first_time=False):
    for ins in instances:
        SISRS.initialize(ins, 1000)
        Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
        routes = [r[0] for r in solutions]
        costs[ins] = SISRS.costTotal(routes)
        if first_time:
            f = open("Improvements/" + ins, "w")
            f.write(str(costs[ins]) + '\n')
            f.write(str([SISRS.costRoute(r) for r in routes]) + '\n')
            f.close()

def init_worse_sol(first_time=False):
    for ins in After_Construction:
        SISRS.initialize(ins, 1000)
        Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
        routes = [r[0] for r in solutions]
        costs[ins] = SISRS.costTotal(routes)
        if first_time:
            f = open("Improvements/" + ins, "w")
            f.write(str(costs[ins]) + '\n')
            f.write(str([SISRS.costRoute(r) for r in routes]) + '\n')
            f.close()
    for ins in After_Local_Search:
        SISRS.initialize(ins, 1000)
        Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
        routes = [r[0] for r in solutions]
        costs[ins] = SISRS.costTotal(routes)
        if first_time:
            f = open("Improvements/" + ins, "w")
            f.write(str(costs[ins]) + '\n')
            f.write(str([SISRS.costRoute(r) for r in routes]) + '\n')
            f.close()


def optimal_routes():
    for ins in instances:
        SISRS.initialize(ins, 1000)
        mdl = model.create_model(ins)
        model.read_sol(mdl, ins)
        for r in range(20):
            model.remove_route(mdl, r, ins)
            model.solve_model(mdl)
            result = model.get_routes(ins)
            print(result[2])
            if result[2] < costs[ins]:
                f = open("Improvements/" + ins, "a")
                f.write('Improvement by exact: \n')
                f.write(str(result[0]) + '\n')
                f.write(str(result[1]) + '\n')
                f.write(str(result[2]) + '\n')
                f.close()
            model.add_route(mdl, r, ins)

def one_route(ins, r):
    SISRS.initialize(ins, 1000)
    mdl = model.create_model(ins)
    model.read_sol(mdl, ins)

    model.remove_route(mdl, r, ins)
    model.solve_model(mdl)
    result = model.get_routes(ins)
    print(result[2])
    if result[2] < costs[ins]:
        f = open("Improvements/" + ins, "a")
        f.write('Improvement by exact: \n')
        f.write(str(result[0]) + '\n')
        f.write(str(result[1]) + '\n')
        f.write(str(result[2]) + '\n')
        f.close()
    model.add_route(mdl, r, ins)

def SISRS_1000(iterations):
    for ins in instances:
        start = time.time()
        SISRS.initialize(ins, iterations)
        result = SISRS.local_search(SISRS.s_0)
        end = time.time()
        print(ins, result[2], costs[ins], 'time: ', end-start, 'percentage: ', (costs[ins] - result[2])/costs[ins] * 100)
        if result[2] < costs[ins]:
            print('??????????????')
            f = open("Improvements/" + ins, "a")
            f.write('Improvement by SISRS, iterations: ' + str(iterations) + ', T_0 = ' + str(SISRS.T_0) + ' : \n')
            f.write(str(result[0]) + '\n')
            f.write(str(result[1]) + '\n')
            f.write(str(result[2]) + '\n')
            f.close()

def SISRS_1000_worse(iterations):
    for ins in After_Construction:
        start = time.time()
        SISRS.initialize(ins, iterations)
        result = SISRS.local_search(SISRS.s_0)
        end = time.time()
        print(ins, result[2], costs[ins], 'time: ', end-start)
        if result[2] < costs[ins]:
            print('??????????????')
            f = open("Improvements/" + ins, "a")
            f.write('Improvement by SISRS ' + str(iterations) + ',  T_0 = ' + str(SISRS.T_0) + ': \n')
            f.write(str(result[0]) + '\n')
            f.write(str(result[1]) + '\n')
            f.write(str(result[2]) + '\n')
            f.close()
    for ins in After_Local_Search:
        start = time.time()
        SISRS.initialize(ins, iterations)
        result = SISRS.local_search(SISRS.s_0)
        end = time.time()
        print(ins, result[2], costs[ins], 'time: ', end-start)
        if result[2] < costs[ins]:
            print('??????????????')
            f = open("Improvements/" + ins, "a")
            f.write('Improvement by SISRS ' + str(iterations) + ', T_0 = ' + str(SISRS.T_0) + ' : \n')
            f.write(str(result[0]) + '\n')
            f.write(str(result[1]) + '\n')
            f.write(str(result[2]) + '\n')
            f.close()


def combi_10(iterations):
    for ins in instances:
        result = combination(ins, iterations)
        print(ins, result[2], costs[ins])
        if result[2] < costs[ins]:
            print('??????????????')
            f = open("Improvements/" + ins, "a")
            f.write('Improvement by combi: \n')
            f.write(str(result[0]) + '\n')
            f.write(str(result[1]) + '\n')
            f.write(str(result[2]) + '\n')
            f.close()


def find_removed(s, s_0):
    A = [i for i in range(220)]
    for r in s:
        for e in r:
            A.remove(e)

    B = [i for i in range(220)]
    for r in s_0:
        for e in r:
            B.remove(e)
    C = []
    for ab in A:
        if ab not in B:
            C.append(ab)
    return A, C


def combination(ins, iterations):
    print(time.time(), 'test')
    mdl = model.create_model(ins)
    model.read_sol(mdl, ins)
    SISRS.initialize(ins, iterations)
    Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
    s_0 = [r[0] for r in solutions]
    s_best = s_0
    T = SISRS.T_0
    s = copy.deepcopy(s_0)
    s_old = s
    for f in range(iterations):
        model.old_to_new(mdl, s_old, s)
        s = s_old
        s_ruin = SISRS.Ruin(copy.deepcopy(s))
        removed = find_removed(s_ruin, s_0)
        for custom in removed[1]:
            model.remove_customer(ins, mdl, custom)
        model.solve_model(mdl, limit=3000)
        s_new = model.get_routes(ins)[0]
        if s_new != -1:
            if SISRS.costTotal(s_new) < SISRS.costTotal(s) - T * math.log(random.uniform(0, 1)):
                s = s_new
            if SISRS.costTotal(s_new) < SISRS.costTotal(s_best):
                s_best = s_new
            T *= SISRS.c
    return s_best, [SISRS.costRoute(r) for r in s_best], SISRS.costTotal(s_best)


init(first_time=False)
# init_worse_sol(first_time=False)
# SISRS.initialize(instances[0], 1000)
# Vertices, dmatrix, solutions, total_dist = data.read_instance(instances[0])
# routes = [r[0] for r in solutions]
# print(SISRS.check_solution(routes))
# one_route(instances[6], 17)
# one_route(instances[0], 19)
# optimal_routes()
SISRS_1000(10000)
# SISRS_1000_worse(10000)
# combi_10(4)