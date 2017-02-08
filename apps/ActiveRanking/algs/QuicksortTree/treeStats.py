import numpy as np

def getErrorsQS(trees, pivots, queryqueues, without_responses, vsW):
    """
    trees: tree maintained by QuicksortTree 
    pivots: first pivot chosen
    queryqueues: list of queries ready to be sent
    without_responses: queries sent out, but response not received
    """
    nQS = len(pivots)
    n = len(trees[0])
    rankings = np.zeros((nQS, n))
    positions = np.zeros((nQS, n))
    for i in range(nQS):
        rankings[i,:] = partialRankingFromTree(trees[i], pivots[i], queryqueues[i], without_responses[i])
        positions[i,:] = np.argsort(rankings[i,:])

    meanposition = np.mean(positions, 0)
    score = -meanposition #lists from quicksort are ascending
    return predictionAccuracy(score, vsW)

def getErrorsRandom(W, vsW):
    n = np.shape(W)[0]
    P = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if (W[i][j] + W[j][i] == 0):
                P[i][j] = 0.5
            else:
                P[i][j] = float(W[i][j])/(W[i][j]+W[j][i])

    bordascores = np.sum(P, 1)/(n-1)  # +np.random.random(n)*1.e-7
    return predictionAccuracy(bordascores, vsW)

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
                elif score[i] == score[j]:
                    correct += 0.5 * W[i][j]
    return float(correct)/total

def partialRankingFromTree(tree, pivot, queryqueue, without_response):
    """
    tree: tree maintained by QuicksortTree 
    pivot: first pivot chosen
    queryqueue: list of queries ready to be sent
    without_response: queries sent out, but response not received
    """
    queryqueue = set([(x[0], x[1]) for x in queryqueue])
    without_response = set([tuple(x[0]) for x in without_response])
    remainingqueries = queryqueue.union(without_response)

    tree1 = [[-1,-1,[i]] for i in range(len(tree))]

    for node in range(len(tree)):
        left_child = tree[node][0]
        right_child = tree[node][1]
        if left_child != -1:
            tree1[node][0] = left_child
        if right_child != -1:
            tree1[node][1] = right_child

    unranked = []
    for q in remainingqueries:
        p = q[0]
        tree1[p][2].append(q[1])

    ranked = getrankedlist(tree1, pivot)
    return ranked

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
