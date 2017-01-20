import numpy as np
from collections import defaultdict
import pdb
def trial():
    n = 100
    queryqueue = []
    while len(queryqueue) < 1000:
        a1 = np.random.randint(n)
        b1 = np.random.randint(n)
        while b1==a1:
            b1 = np.random.randint(n)
        queryalreadyexists = False
        for query in queryqueue:
            if (((query[0],query[1])==(a1,b1)) or ((query[1],query[0])==(b1,a1))):
                queryalreadyexists = True
                break
        if queryalreadyexists:
            continue
        else:
            queryqueue.append((1,a1,b1))

    queryqueue2 = []
    for query in queryqueue:
        queryqueue2.append((2, query[1], query[2]))
    queryqueue3 = []
    for query in queryqueue:
        queryqueue3.append((3, query[1], query[2]))

    return queryqueue+queryqueue2+queryqueue3

if __name__ == "__main__":
    queryqueue = trial()

