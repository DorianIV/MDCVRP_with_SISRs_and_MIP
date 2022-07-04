from docplex.mp.model import Model
from copy import deepcopy
import data
r = 200
v = 20

alpha = 10000

# capacity techs
Q = 86400
# duration at customer
q = [0 for i in range(v)] + [5400 for i in range(v, v+r)]
print(q)


def create_model(instance):
    A = [(i,j) for i in range(v + r) for j in range(v + r)] 
    Aplus = [(a[0], a[1], k) for a in A for k in range(v)]
    N = [(i,j) for i in range(v, v + r) for j in range(v, v + r) if i != j] 

    mdl = Model('VRP')

    x = mdl.binary_var_cube((i for i in range(v+r)), (j for j in range(v+r)), (k for k in range(v)), name='x')
    s = mdl.continuous_var_dict((i for i in range(v+r)), name='s')

    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)

    print('started')

    #u = mdl.continuous_var_dict(Vertices[20:])

    # minimization goal
    mdl.minimize(-alpha * mdl.sum(x[i,j,k] for i in range(v+r) for j in range(v, v+r) for k in range(v)) 
    + mdl.sum(dmatrix[i,j]*x[i,j,k] for k in range(v) for i in range(v+r) for j in range(v+r)))

    print('minimization done')

    # one vehicle in
    in_cts = []
    for j in range(v + r):
        ct = mdl.sum(x[i,j,k] for k in range(v) for i in range(v + r)) <= 1
        in_cts.append(ct)
    mdl.add_constraints(in_cts)

    print('vehicle in done')

    # one vehicle out
    out_cts = []
    for i in range(v + r):
        ct = mdl.sum(x[i,j,k] for k in range(v) for j in range(v + r)) <= 1
        out_cts.append(ct)
    mdl.add_constraints(out_cts)

    print('vehicle out done')

    # same vehicle in and out
    mdl.add_constraints(mdl.sum(x[i,j,k] for i in range (v + r)) - mdl.sum(x[j,l,k] for l in range(v + r)) == 0
    for j in range (v + r) for k in range(v))
    
    print('same vehicle done')

    # start and end at depot TODO
    mdl.add_constraints(mdl.sum(x[k,j,k] for j in [j1 for j1 in range(v, v + r)] + [k]) == 1 for k in range(v))

    print('start done')

    mdl.add_constraints(mdl.sum(x[j,k,k] for j in [j1 for j1 in range(v, v + r)] + [k]) == 1 for k in range(v))

    print('end done')

    # not same start and end

    '''
    for k in range(v):
        for i in range(v+r):
            if k != i:
                mdl.add_constraint(x[i,i,k] == 0)
                

    print('prevent loops done')
    '''
    #mdl.add_constraints(x[i,i,k] == 0 for i in range(v+r) for k in range(v) if i != k)

    # capacity
    mdl.add_constraints(Q >= s[i] + (x[i,k,k] * dmatrix[i,k]) + q[i]
    for i in range(v+r) for k in range(v))

    print('capacity done')

    # Start service at 0
    mdl.add_constraints(s[k] == 0 for k in range(v))

    print('start service done')

    # time windows
    for j in range(v, v+r):
        for i in range(v+r):
            for k in range(v):
                mdl.add_constraint(s[j] + Q * (1 - x[i,j,k]) >= s[i] + (x[i,j,k] * dmatrix[i,j]) + q[i])
                

    print('first done')

    mdl.add_constraints(Vertices[i][1] <= s[i] for i in range(v, v+r))

    print('second done')

    mdl.add_constraints(s[i] <= Vertices[i][2] for i in range(v, v+r))

    print('time windows done')

    return mdl
    

def solve_model(modl, out=True, limit=2000):
    modl.parameters.timelimit=limit
    modl.set_time_limit(limit) #The same

    solution = modl.solve(log_output=out)

    f = open("solution.txt", "w")
    f.write(solution.__str__())
    f.close()


'''print(max(0,1), sum(sum(x[i,j,k] for j in range(v, v+r)) for i in range(v, v+r)))
    m = max(1, sum(sum(x[i,j,k] for j in range(v, v+r)) for i in range(v, v+r)))
    ct = sum(x[k,j,k] for j in range(v, v + r)) == ((sum(sum(x[i,j,k] for j in range(v, v+r)) for i in range(v, v+r)))/m)
    se_cts.append(ct)'''
    

def get_routes(instance):
    
    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)

    routes = [[] for k in range(v)]

    with open('solution.txt') as f:
        lines = f.readlines()

    result = float(lines[1].split(' ')[1])
    served = 0

    for line in lines[2:]:
        if 's' in line:
            break
        parsed = line.split('_')
        parsed2 = parsed[3].split('=')
        routes[int(parsed2[0])].append((int(parsed[1]), int(parsed[2])))
        if int(parsed[2]) >= v:
            served += 1

    dict = {}
    for r in  routes:
        for e in r:
            dict[e[0]]= e[1]

    new_routes = []
    for r in range(len(routes)):
        new_routes.append([])
        i = 0
        node = routes[r][0][0]
        while node not in new_routes[r]:
            old_node = node
            new_routes[r].append(node)
            node = dict[old_node]

    distances = []
    for r in new_routes:
        total = sum(dmatrix[r[i],r[i+1]] for i in range(len(r) - 1)) + dmatrix[r[len(r) - 1],r[0]]
        distances.append(total)
    return new_routes, distances, sum(distances)

'''
def subtour_elimination(mdl, sol):
    cts = []

    for r in sol:


        to_remove = []
        for e in r:
            if e[0] < v or e[1] < v:
                to_remove.append(e)
        for e in to_remove:
            r.remove(e)

        nodes = set()
        for e in r:
            if e[0] > v - 1:
                nodes.add(e[0])
            if e[1] > v - 1:
                nodes.add(e[1])
            
        length = len(r)

        if length != len(nodes) - 1 and length != 0:
            cts.append(mdl.sum(mdl.x[i,j,k] for i in nodes for j in nodes for k in range(v)) <= length - 1)

    return cts
'''

'''
def get_solutions(mdl, instance, read=False, to_remove=[]):
    if read:
        read_sol(mdl, instance)
        for route in to_remove:
            remove_route(mdl, route, instance)
    found = True
    solve_model(mdl)
    sol = get_routes(instance)
    # cts = subtour_elimination(deepcopy(sol[0]))
    cts = False
    if cts:
        print('---------------------')
        mdl.add_constraints(cts)
        found = False
    while found == False:
        solve_model(mdl)
        sol = get_routes(instance)
        cts = subtour_elimination(sol[0])
        if cts:
            mdl.add_constraints(cts)
            found = False
    return sol
'''


def read_sol(mdl, instance):
    
    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)
    for x1 in solutions:
        r = x1[0]
        k = r[0]
        for i in range(len(r) - 1):
            x = mdl.get_var_by_name('x_' + str(r[i]) + '_' + str(r[i+1]) + '_' + str(k))
            mdl.add_constraint(x == 1, str(r[i]) + '-' + str(r[i+1]) + '-' + str(k))
        x = mdl.get_var_by_name('x_' + str(r[len(r)-1]) + '_' + str(k) + '_' + str(k))
        mdl.add_constraint(x == 1, str(r[len(r)-1]) + '-' + str(k) + '-' + str(k))

    print('reading done')

def remove_route(modl, v_number, instance):

    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)
    
    x1 = solutions[v_number]
    r = x1[0]
    k = r[0]
    for i in range(len(r) - 1):
        modl.remove_constraint(str(r[i]) + '-' + str(r[i+1]) + '-' + str(k))
    modl.remove_constraint(str(r[len(r)-1]) + '-' + str(k) + '-' + str(k))


def add_customer(ins, mdl, cust):
    Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
    for r in range(20):
        x1 = solutions[r][0]
        if cust in x1:
            mdl.add_constraint(str(x1[x1.index(cust)-1]) + '-' + str(cust) + '-' + str(r))
        if x1.index(cust) != len(x1-1):
            mdl.add_constraint(str(cust) + '-' +  str(x1[x1.index(cust)+1])+ '-' + str(r))
            return
        else:
            mdl.add_constraint(str(cust) + '-' +  str(x1[0])+ '-' + str(r))
            return

def remove_customer(ins, mdl, cust):
    Vertices, dmatrix, solutions, total_dist = data.read_instance(ins)
    
    for r in range(20):
        x1 = solutions[r][0]
        if cust in x1:
            mdl.remove_constraint(str(x1[x1.index(cust)-1]) + '-' + str(cust) + '-' + str(r))
            if x1.index(cust) != len(x1)-1:
                mdl.remove_constraint(str(cust) + '-' +  str(x1[x1.index(cust)+1])+ '-' + str(r))
                return
            else:
                mdl.remove_constraint(str(cust) + '-' +  str(x1[0])+ '-' + str(r))
                return


def add_route(modl, v_number, instance):

    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)

    x1 = solutions[v_number]
    r = x1[0]
    k = r[0]
    for i in range(len(r) - 1):
        x = modl.get_var_by_name('x_' + str(r[i]) + '_' + str(r[i+1]) + '_' + str(k))
        modl.add_constraint(x == 1, str(r[i]) + '-' + str(r[i+1]) + '-' + str(k))
    x = modl.get_var_by_name('x_' + str(r[len(r)-1]) + '_' + str(k) + '_' + str(k))
    modl.add_constraint(x == 1, str(r[len(r)-1]) + '-' + str(k) + '-' + str(k))


def remove_customer_route(mdl, cust, route):

    mdl.remove_constraint(str(route[route.index(cust)-1]) + '-' + str(cust) + '-' + str(r))
    if route.index(cust) != len(route)-1:
        mdl.remove_constraint(str(cust) + '-' +  str(route[route.index(cust)+1])+ '-' + str(r))
        return
    else:
        mdl.remove_constraint(str(cust) + '-' +  str(route[0])+ '-' + str(r))
        return


def add_customer_route(mdl, cust, route):

    mdl.add_constraint(str(route[route.index(cust)-1]) + '-' + str(cust) + '-' + str(r))
    if route.index(cust) != len(route)-1:
        mdl.add_constraint(str(cust) + '-' +  str(route[route.index(cust)+1])+ '-' + str(r))
        return
    else:
        mdl.add_constraint(str(cust) + '-' +  str(route[0])+ '-' + str(r))
        return


def old_to_new(mdl, s_old, s_new):
    for i in range(20):
        r_old = s_old[i]
        r_new = s_new[i]
        k = r_new[0]
        if r_old != r_new:
            for i in range(len(r_old) - 1):
                x = mdl.get_var_by_name('x_' + str(r_old[i]) + '_' + str(r_old[i+1]) + '_' + str(k))
                mdl.remove_constraint(str(r_old[i]) + '-' + str(r_old[i+1]) + '-' + str(k))
            x = mdl.get_var_by_name('x_' + str(r_old[len(r_old)-1]) + '_' + str(k) + '_' + str(k))
            mdl.remove_constraint(str(r_old[len(r_old)-1]) + '-' + str(k) + '-' + str(k))
            for i in range(len(r_new) - 1):
                x = mdl.get_var_by_name('x_' + str(r_new[i]) + '_' + str(r_new[i+1]) + '_' + str(k))
                mdl.add_constraint(x == 1, str(r_new[i]) + '-' + str(r_new[i+1]) + '-' + str(k))
            x = mdl.get_var_by_name('x_' + str(r_new[len(r_new)-1]) + '_' + str(k) + '_' + str(k))
            mdl.add_constraint(x == 1, str(r_new[len(r_new)-1]) + '-' + str(k) + '-' + str(k))


def two_routes(instance):

    Vertices, dmatrix, solutions, total_dist = data.read_instance(instance)

    mdl = create_model(instance)
    read_sol(mdl, instance)
    for r1 in range(v):
        print(r1)
        for r2 in range(v):
            r1 = 11
            r2 = 16
            if r1 < r2:
                remove_route(mdl, r1, instance)
                remove_route(mdl, r2, instance)
                solve_model(mdl, limit=200, out=True)
                sol = get_routes(instance)
                print(sol, r1, r2, total_dist)
                if sol[2] < total_dist:
                    print('Improvement found!')
                    print(r1, r2, sol)

                add_route(mdl, r1, instance)
                add_route(mdl, r2, instance)
                break

