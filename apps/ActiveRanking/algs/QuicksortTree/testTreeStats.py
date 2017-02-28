import numpy as np
import collections 
import pdb
import json

def partialRankingFromTree(tree, pivot, queryqueue, without_response):
    """
    tree: tree maintained by QuicksortTree 
    pivot: first pivot chosen
    queryqueue: list of queries ready to be sent
    without_response: queries sent out, but response not received
    """

    tree1 = [[-1,-1,[i],-1] for i in range(len(tree))]
    for node in range(len(tree)):
        left_child = tree[node][0]
        right_child = tree[node][1]
        if left_child != -1:
            tree1[node][0] = left_child
        if right_child != -1:
            tree1[node][1] = right_child

    tree1 = addHeight(tree1, pivot, 0)

    queryqueue = set([(x[0], x[1]) for x in queryqueue])
    without_response = set([tuple(x[0]) for x in without_response])
    remainingqueries = queryqueue.union(without_response)

    #key: second element
    #value: (height of first element, query)
    secondelements = {}
    for q in remainingqueries:
        if q[1] not in secondelements:
            secondelements[q[1]] = [tree1[q[0]][3], q]
        else:
            if tree1[q[0]][3] > secondelements[q[1]][0]:
                secondelements[q[1]] = [tree1[q[0]][3], q]

    impqueries = [secondelements[x][1] for x in secondelements]

    for q in impqueries:
        p = q[0]
        tree1[p][2].append(q[1])

    pdb.set_trace()
    ranked = getrankedlist(tree1, pivot)
    return ranked

def addHeight(tree, pivot, height):
    tree[pivot][3] = height
    if tree[pivot][0] != -1:
        tree = addHeight(tree, tree[pivot][0], height+1)
    if tree[pivot][1] != -1:
        tree = addHeight(tree, tree[pivot][1], height+1)
    return tree


def getrankedlist(tree, pivot):
    """
    This function is called by partialRankingFromTree. 
    tree: tree maintained by partialRankingFromTree, which contains at every node, the items unresolved with respect to that node.
    pivot: starting pivot
    """
    leftlist = []
    rightlist = []
    left_child = tree[pivot][0]
    right_child = tree[pivot][1]
    if (left_child, right_child) == (-1,-1):
        return tree[pivot][2]
    if left_child != -1:
        leftlist = getrankedlist(tree, left_child)
    if right_child != -1:
        rightlist = getrankedlist(tree, right_child)
    return leftlist + tree[pivot][2] + rightlist

def predictionAccuracy(score, W):
    n = np.shape(W)[0]
    correct = 0
    total = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            else:
                total += W[i][j]
                if score[i] > score[j]:
                    correct += W[i][j]
                    if W[i][j]>0:
                        pdb.set_trace()
                elif score[i] == score[j]:
                    correct += 0.5 * W[i][j]
    return float(correct)/total

if __name__ == "__main__":
    #with open('ALG-EVALUATION','r') as f:
    #    events = json.loads(f.read())

    #events = sorted(events['log_data'], key=lambda x: x['timestamp'])
    #for (count, l) in enumerate(events):
    #    alg_label = 'QuicksortTree_5'
    #    #pivot = 24
    #    #pivot = 1
    #    #pivot = 62
    #    #pivot = 5
    #    #pivot = 5
    #    pivot = 82
    #    try:
    #        if l['alg_label'] == alg_label:
    #            pdb.set_trace()
    #    except KeyError:
    #        continue
    #    try:
    #        if l['alg_label'] != alg_label:
    #            continue
    #    except KeyError:
    #        continue
    #    if l['api_call'] != 'initExp':
    #        continue
    #    tree = l['tree']
    #    queryqueue = l['queries']
    #    without_response = l['without_response']
    #    ranking = partialRankingFromTree(tree, pivot, queryqueue, without_response)
    #    print ranking
    #    if len(ranking) != 100:
    #        pdb.set_trace()



    tree = [[-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [0, 29], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [21, 53], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [49, 89], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1], [-1, -1]]
    pivot = 33
    queryqueue = [[33, 30], [33, 44], [33, 45], [33, 26], [33, 94], [33, 87], [33, 73], [33, 51], [33, 66], [33, 9], [33, 38], [33, 85], [33, 25], [33, 60], [33, 52], [33, 46], [33, 39], [33, 78], [33, 97], [33, 95], [33, 27], [33, 76], [33, 1], [33, 31], [33, 70], [33, 42], [33, 99], [33, 88], [33, 32], [33, 55], [33, 59], [33, 79], [33, 12], [33, 61], [33, 8], [33, 93], [33, 65], [33, 57], [33, 64], [33, 72], [33, 48], [33, 68], [33, 36], [33, 16], [33, 3], [33, 41], [33, 90], [33, 71], [33, 69], [33, 23], [33, 82], [33, 62], [33, 13], [53, 63], [53, 37], [53, 75], [21, 6], [21, 4], [21, 20], [53, 86], [21, 11], [53, 92], [53, 35], [21, 28], [0, 19], [21, 15], [53, 80], [29, 22], [53, 58], [53, 74], [53, 56], [89, 84], [53, 40], [89, 98], [0, 7], [21, 14], [89, 67], [21, 17], [21, 5], [29, 24], [53, 83], [0, 18], [21, 10], [53, 77], [53, 81]]
    without_response = [[[33, 2], 1486678700.290438], [[53, 34], 1486678700.671891], [[49, 43], 1486678700.685339], [[53, 47], 1486678700.734768], [[53, 54], 1486678700.801267], [[33, 50], 1486678701.031296], [[33, 91], 1486678701.284962]]
    ranking = partialRankingFromTree(tree, pivot, queryqueue, without_response)

