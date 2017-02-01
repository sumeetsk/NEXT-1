'''
Questions:
1. What is butler.dashboard used for?
2. Why an _ after exp_uid in other? 
'''

import numpy as np
from datetime import datetime
import dateutil.parser
import next.utils as utils
import random
import time

class QuicksortTree:
    app_id = 'ActiveRanking'

    def initExp(self, butler, n=None, params=None):
        perm = list(np.random.permutation(range(n)))
        pivot = np.random.choice(n)
        queries = [[pivot, i] for i in perm if i != pivot]
        tree = [[-1, -1] for i in range(n)]
        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='pivot', value=pivot)
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='without_response_answered', value=[])
        butler.algorithms.set(key='without_response', value=[])
        butler.algorithms.set(key='tree', value=tree)
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        return True

    def getQuery(self, butler, participant_uid):
        lock = butler.memory.lock('QSTreelock_{}'.format(butler.alg_label), timeout=1)
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        without_response = butler.algorithms.get(key='without_response')
        curr_time = time.time()
        for q in without_response:
            if (curr_time - q[1] > 5000 and q[1] != 0) or not queries:
                q[1] = 0
                queries.append(q[0])
        if not queries:
            if not without_response:
                butler.other.set(key='{}_available'.format(butler.alg_label), value=0)
            n = butler.algorithms.get(key='n')
            query = [np.random.randint(n), np.random.randint(n), 0]

        else:
            query = queries.pop(np.random.choice(len(queries)))
            query.append(1)
            x = filter(lambda x: x[0] == [query[0], query[1]], without_response)
            if x:
                x[0][1] = curr_time
            else:
                without_response.append([query, time.time()])
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='without_response', value=without_response)
        lock.release()
        # Ideally find a clean way to move this to processAnswer and remove overhead here
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid,
                                      'timestamp': utils.datetimeNow(),
                                      'queries': len(queries),
                                      'alg_label': butler.alg_label,
                                      'without_response': len(without_response),
                                      'available': available})
        return query

    def processAnswer(self, butler, left_id, right_id, winner_id,
                      quicksort_data=0):
        curr_pivot, b, ans = left_id, right_id, winner_id
        lock = butler.memory.lock('QSTreelock_{}'.format(butler.alg_label), timeout=1)
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))
        without_response = butler.algorithms.get(key='without_response')
        # If the alg is not available, or the query was random
        if not available or quicksort_data == 0:
            lock.release()
            return True
        for i, x in enumerate(without_response):
            if x[0] == [curr_pivot, b]:
                del without_response[i]
                break
            # If the query is not found, its already been answered
            if i == len(without_response)-1:
                lock.release()
                return True

        tree = butler.algorithms.get(key='tree')
        if ans == curr_pivot:
            # curr_pivot > b
            if tree[curr_pivot][0] is -1:
                tree[curr_pivot][0] = b
            else:
                queries.append([tree[curr_pivot][0], b])
        elif ans == b:
            # curr_pivot < b
            if tree[curr_pivot][1] is -1:
                tree[curr_pivot][1] = b
            else:
                queries.append([tree[curr_pivot][1], b])
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='tree', value=tree)
        butler.algorithms.set(key='without_response', value=without_response)
        lock.release()
        return True

    def getModel(self, butler):
        pivot = butler.algorithms.get(key='pivot')
        tree = butler.algorithms.get(key='tree')
        a = []
        self.treetolist(tree, pivot, a)
        return a

    def treetolist(self, tree, pivot, a):
        if pivot == -1:
            return
        self.treetolist(tree, tree[pivot][0], a)
        a.append(pivot)
        self.treetolist(tree, tree[pivot][1], a)
        return
