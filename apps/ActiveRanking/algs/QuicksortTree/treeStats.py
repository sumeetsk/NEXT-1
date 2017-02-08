import numpy as np

def partialRankingFromTree(tree, pivot, queryqueue, without_response):
    """
    tree: tree maintained by QuicksortTree 
    pivot: first pivot chosen
    queryqueue: list of queries ready to be sent
    without_response: queries sent out, but response not received
    """
    queryqueue = set([(x[0], x[1]) for x in l['queries']])
    without_response = set([tuple(x[0]) for x in l['without_response']])
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

def aggregateRanking(ranks):
    """
    ranks: list of lists. Each element of ranks is a (partial) ranking from QuicksortTree
    """
    n = len(ranks[0])
    nQS = len(ranks)
    positionlist = np.zeros(np.shape(ranks))
    for (j,rank) in enumerate(ranks):
        positionlist[j,:] = np.argsort(rank)
    meanposition = np.mean(positionlist, 0)
    #stdposition = np.std(positionlist, axis=0)
    return np.argsort(meanposition).tolist()
