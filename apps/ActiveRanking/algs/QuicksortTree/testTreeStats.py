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
    with open('ALG-EVALUATION','r') as f:
        events = json.loads(f.read())

    events = sorted(events['log_data'], key=lambda x: x['timestamp'])
    for (count, l) in enumerate(events):
        alg_label = 'QuicksortTree_5'
        #pivot = 24
        #pivot = 1
        #pivot = 62
        #pivot = 5
        #pivot = 5
        pivot = 82
        try:
            if l['alg_label'] == alg_label:
                pdb.set_trace()
        except KeyError:
            continue
        try:
            if l['alg_label'] != alg_label:
                continue
        except KeyError:
            continue
        if l['api_call'] != 'initExp':
            continue
        tree = l['tree']
        queryqueue = l['queries']
        without_response = l['without_response']
        ranking = partialRankingFromTree(tree, pivot, queryqueue, without_response)
        print ranking
        if len(ranking) != 100:
            pdb.set_trace()
