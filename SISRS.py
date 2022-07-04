from audioop import avg
import data
import math
import random
import numpy as np
import copy

q = 5400
Q = 86400

Vertices, dmatrix, solutions, total_dist = None, None, None, None
s_0 = None

T_0 = 100
T_f = 1
iterations = None
c = None
L_max = 10
c_avarage = 10
beta = 0.01
gamma = 0.01


def initialize(instance, iter):
    global Vertices, dmatrix, solutions, total_dist, s_0, iterations, c
    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)
    s_0 = [r[0] for r in solutions]
    iterations = iter
    c = (T_f/T_0)**(1/iterations)


def local_search(s):
    s_best = s_0
    T = T_0
    for f in range(iterations):
        s_ruin = Ruin(copy.deepcopy(s))
        s_new = Recreate(s_ruin)
        if s_new != -1:
            if costTotal(s_new) < costTotal(s) - T * math.log(random.uniform(0, 1)):
                s = s_new
            if costTotal(s_new) < costTotal(s_best):
                s_best = s_new
            T *= c
    return s_best, [costRoute(r) for r in s_best], costTotal(s_best)
    

def Ruin(s):
    A = [i for i in range(220)]
    route_dict = {}
    for r in s:
        for e in r:
            route_dict[e] = s.index(r)
            A.remove(e)
    l_max = min(L_max, sum(len(r) for r in s)/len(s) - sum([1 if len(r) == 0 else 0 for r in s]))
    k_max = (4*c_avarage)/(1 + l_max) - 1
    k_s = math.floor(random.uniform(1, k_max + 1))
    t = None
    c_seed = None
    while t == None:
        c_seed = random.randrange(20, 220)
        for r in s:
            if c_seed in r:
                t = r[0]
    c_adj = [(e, np.where(dmatrix[c_seed] == e)[0][0]) for e in dmatrix[c_seed]]
    c_adj.sort()
    c_adj_2 = [e[1] for e in c_adj]
    R = []

    for cust in c_adj_2: 
        if not len(R) < k_s:
            break
        if cust not in A and cust > 19:
            new_t = route_dict[cust]
            if new_t not in R:
                c_t = cust
                l_max_t = min(len(s[new_t]), l_max)
                l_t = math.floor(random.uniform(1, l_max_t + 1))
                A.extend(RemoveSelected(s, new_t, l_t, c_t))
                R.append(new_t)
    return s


def Recreate(s):
    A = [i for i in range(220)]
    for r in s:
        for e in r:
            A.remove(e)
    my_sort(A)
    to_remove = []
    to_route = None
    for cust in A:
        P = None
        for t in range(20):
            for P_t in range(1, len(s[t]) + 1):
                tw = checkTimeWindows(s[t], cust, P_t)
                if tw == 1:
                    break
                if tw == 0:
                    if random.uniform(0, 1) < 1 - gamma:
                        if P == None or costAt(s[t], cust, P_t) < costAt(s[to_route], cust, P):
                            P = P_t
                            to_route = t
        if P == None:
            return -1
        #print('another r', s[t])
        #print('P', P_t, cust, s[to_route])
        s[to_route].insert(P, cust)
        to_remove.append(cust)
    for cust in to_remove:
        A.remove(cust)
    return s

def RemoveSelected(s, t, l_t, c_t):
    removed = []
    up = s[t].index(c_t)
    low = s[t].index(c_t)
    removed.append(s[t].pop(up))
    for i in range(l_t - 1):
        rand = random.uniform(0, 1)
        if rand > 0.5 and up + 1 < len(s[t]):
            up += 1
            removed.append(s[t].pop(up))
        elif low - 1 > 0:
            low -= 1
            removed.append(s[t].pop(low))
    return removed


def my_sort(A):
    rand = random.uniform(0, 7)
    if rand <= 4:
        random.shuffle(A)
    elif rand <= 6:
        avg_distances = {}
        for cust in A:
            distances = []
            for x in range(20):
                distances.append(dmatrix[cust][x])
            avg_distances[cust] = min(distances)
        sorted_A = dict(sorted(avg_distances.items(), key=lambda item: item[1]))
        A = [cust for cust in sorted_A]
    elif rand <= 7:
        avg_distances = {}
        for cust in A:
            distances = []
            for x in range(20):
                distances.append(dmatrix[cust][x])
            avg_distances[cust] = min(distances)
        sorted_A = dict(sorted(avg_distances.items(), key=lambda item: item[1]))
        temp = [cust for cust in sorted_A]
        A = []
        j = len(sorted_A)
        for i in range(1, len(sorted_A)):
            A.append(temp[j-i])

def costAt(r, cust, P_t):
    route = copy.copy(r)
    old_cost = costRoute(route)
    route.insert(P_t, cust)
    new_cost = costRoute(route)
    return new_cost - old_cost

# 0 -> windows OK
# 1 -> timewindow of extra customer already over
# 2 -> customer after extra customer no longer have a working time window
def checkTimeWindows(r, cust, P_t):
    start_service = {}

    start_service[r[0]] = -5400

    for i in range(1, P_t):
        customer = r[i]
        start_service[customer] = max(Vertices[customer][1],
         start_service[r[i-1]] + q + dmatrix[r[i-1]][r[i]])

    start_service[cust] = max(Vertices[cust][1],
         start_service[r[P_t-1]] + q + dmatrix[r[P_t-1]][cust])

    if start_service[cust] > Vertices[cust][2]:
        return 1

    if P_t == len(r):
        if start_service[cust] + 5400 + dmatrix[cust][r[0]] > Q:
            return 1
        return 0

    start_service[r[P_t]] = max(Vertices[r[P_t]][1],
         start_service[cust] + q + dmatrix[cust][r[P_t]])

    if start_service[r[P_t]] > Vertices[r[P_t]][2]:
        return 2
    
    for i in range(P_t + 1, len(r)):
        customer = r[i]
        start_service[customer] = max(Vertices[customer][1],
         start_service[r[i-1]] + q + dmatrix[r[i-1]][r[i]])
        
        if start_service[customer] > Vertices[customer][2]:
            return 2

    if start_service[r[len(r) - 1]] + 5400 + dmatrix[r[len(r) - 1]][r[0]] > Q:
        return 2

    return 0


def costRoute(r):
    return  sum(dmatrix[r[i],r[i+1]] for i in range(max(len(r) - 1, 0))) + dmatrix[r[len(r) - 1],r[0]]


def costTotal(s):
    total = 0
    for r in s:
        total += costRoute(r)
    return total


def check_solution(s):

    start_service = {}
    total = 0
    for r in s:

        total += 1

        start_service[r[0]] = -5400

        for i in range(1, len(r)):
            total += 1
            start_service[r[i]] = max(Vertices[r[i]][1],
            start_service[r[i-1]] + q + dmatrix[r[i-1], r[i]])

        if start_service[r[len(r) - 1]] + 5400 + dmatrix[r[len(r) - 1], r[0]] > Q:
            print('faulty solution', 'end')
            #return False

    for cust in start_service:
        if cust > 19:
            if start_service[cust] > Vertices[cust][2] or start_service[cust] < Vertices[cust][1]:
                print('faulty solution', cust, start_service[cust], Vertices[cust][2], Vertices[cust][1])
                #return False

    for i in range(220):
        if i not in start_service:
            print('not everyone visited')

    if total != 220:
        print('weird total: ', total)
    
    print(costTotal(s))
    return True

'''
f = open("improvements.txt", "a")
to_write = ""
for r in s_0:
    to_write += str(r) + "\n"
f.write(to_write)
f.write(str(costTotal(s_0)))
f.close()


print('zerooooo', check_solution(s_0))

print('Total cost of old is: ', costTotal(s_0))

#print(solutions, sum(r[1] for r in solutions))
improved = local_search(s_0)

print(check_solution(improved))
if costTotal(improved) < costTotal(s_0):
    print('improvement found')
    f = open("improvements.txt", "a")
    to_write = ""
    for r in improved:
        to_write += str(r) + "\n"
    f.write(to_write)
    f.write(str( costTotal(improved)))
    f.close()

print('Total cost of improved is: ', costTotal(improved), improved, sum([sum(1 for e in r) for r in improved]))
'''