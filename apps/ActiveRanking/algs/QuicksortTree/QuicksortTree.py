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
        butler.algorithms.set(key='without_response', value=[])
        butler.algorithms.set(key='tree', value=tree)
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        self.log(butler, 'initExp', [], queries, [], tree, 1)
        return True

    def getQuery(self, butler, participant_uid):
        lock = butler.memory.lock('QSTreelock_{}'.format(butler.alg_label))
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        without_response = butler.algorithms.get(key='without_response')
        tree = butler.algorithms.get(key='tree')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))
        curr_time = time.time()
        queries_empty = not len(queries) > 0
        for q in without_response:
            if (curr_time - q[1] > 5000 and q[1] != 0) or queries_empty:
                # flag of 0 to ensure its not added to the query queue again before it is asked
                q[1] = 0
                queries.append([q[0][0], q[0][1]])
        if not queries:
            if not without_response:
                # the algorithm is done
                butler.other.set(key='{}_available'.format(butler.alg_label), value=0)
            n = butler.algorithms.get(key='n')
            query = [np.random.randint(n), np.random.randint(n), 0]
        else:
            query = queries.pop(np.random.choice(len(queries)))
            query.append(1)
            x = filter(lambda x: x[0] == [query[0], query[1]], without_response)
            # if in without_response
            if x:
                x[0][1] = curr_time
            else:
                without_response.append([[query[0], query[1]], time.time()])
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='without_response', value=without_response)
        self.log(butler, 'getQuery', query, queries, without_response, tree, available)
        lock.release()
        return query

    def processAnswer(self, butler, left_id, right_id, winner_id, quicksort_data=0):
        curr_pivot, b, ans = left_id, right_id, winner_id
        query = [curr_pivot, b, ans, quicksort_data]
        lock = butler.memory.lock('QSTreelock_{}'.format(butler.alg_label))
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))
        without_response = butler.algorithms.get(key='without_response')
        tree = butler.algorithms.get(key='tree')
        # If the alg is not available, or the query was random
        if not available or quicksort_data == 0:
            self.log(butler, 'processAnswer', query, queries, without_response, tree, available, msg='discard')
            lock.release()
            return True

        # We need to remove it from queries to make sure we don't ask it again.
        # This also fixes a bug where a query gets added to the tree twice.
        for i, x in enumerate(queries):
            if x == [curr_pivot, b]:
                del queries[i]

        # Remove query from without_response if it is there, if not, move on
        # have to do a special case if without_response is empty - not caught in the loop
        if not without_response:
            self.log(butler, 'processAnswer', query, queries, without_response, tree, available, msg='discard')
            lock.release()
            return True
        else:
            for i, x in enumerate(without_response):
                if x[0] == [curr_pivot, b]:
                    del without_response[i]
                    break
                # If the query is not found, its already been answered
                if i == len(without_response)-1:
                    self.log(butler, 'processAnswer', query, queries, without_response, tree, available, msg='discard')
                    lock.release()
                    return True

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
        self.log(butler, 'processAnswer', query, queries, without_response, tree, available)
        lock.release()
        return True

    def log(self, butler, api_call, query, queries, without_response, tree, available, msg=''):
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid, 'timestamp': utils.datetimeNow(),
                                      'alg_label': butler.alg_label, 'api_call': api_call,
                                      'query': query, 'queries': queries,
                                      'without_response': without_response, 'tree': tree,
                                      'available': available, 'msg': msg})
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
