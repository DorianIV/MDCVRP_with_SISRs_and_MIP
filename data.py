from collections import namedtuple


import numpy as np

def read_instance(instance):

    Vertex = namedtuple("Vertex", ['kind', 'start', 'end', 'xcoord', 'ycoord'])
    VERTICES = []
    dMatrix = np.zeros((220, 220))
    Solutions = []
    total_dist = 0

    with open(instance) as f:
        lines = f.readlines()

    count = 1
    for line in lines:
        if count < 5:
            pass
        elif count < 225:
            kind = 'customer'
            if 'TECH HOME' in line:
                kind = 'tech'
            parsed = line.split("\t")
            VERTICES.append(Vertex(kind, int(parsed[3]), int(parsed[4]), int(parsed[1]), int(parsed[2])))
        elif count > 227 and count < 448:
            parsed = line.split(' ')
            s = count - 228
            for r in range(220):
                dMatrix[s][r] = int(parsed[r])
        elif count > 450 and count < 471:
            parsed1 = line.split('  // ')
            parsed2 = parsed1[0].split(' ')
            parsed3 = parsed1[1].split(' ')
            Solutions.append(([int(i) for i in parsed2], int(parsed3[1])))
            total_dist += int(parsed3[1])

        count += 1
    #print(total_dist)
    return(VERTICES, dMatrix, Solutions, total_dist)

#print(read_instance('Instances/C1_2_1.txt')[1])


