"""
Quicksort app implements Quicksort Active Sampling Algorithm
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/20/2016
"""

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
        queries = [(pivot, i) for i in perm if i != pivot]
        tree = [[-1, -1] for i in range(n)]
        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='pivot', value=pivot)
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='answered', value=[])
        butler.algorithms.set(key='without_response', value=[])
        butler.algorithms.set(key='tree', value=tree)
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        return True

    def getQuery(self, butler, participant_uid):
        lock = butler.memory.lock('QSTreelock', timeout=1)
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        without_response = butler.algorithms.get(key='without_response')
        curr_time = time.time()
        for q in without_response:
            if q[1] - curr_time > 5000 or not queries:
                q[1] = curr_time
                queries.append(q[0])

        if not queries and not without_response:
            butler.other.set(key='{}_available'.format(butler.alg_label), value=0)
            n = butler.algorithms.get(key='n')
            lock.release()
            return [np.random.randint(n),
                    np.random.randint(n), np.random.randint(n)]

        query = queries.pop(0)
        # make this prettier
        for x in without_response:
            if x[0] == [query[0], query[1]]:
                x[1] = curr_time
                lock.release()
                return [query[0], query[1], query[0]]

        without_response.append([[query[0], query[1]], time.time()])
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='without_response', value=without_response)
        lock.release()
        return [query[0], query[1], query[0]]

    def processAnswer(self, butler, left_id, right_id, winner_id,
                      quicksort_data=0):
        curr_pivot = left_id
        b = right_id
        ans = winner_id

        lock = butler.memory.lock('QSTreelock', timeout=1)
        lock.acquire()
        queries = butler.algorithms.get(key='queries')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))
        without_response = butler.algorithms.get(key='without_response')
        answered = butler.algorithms.get(key='answered')
        utils.debug_print('available', available)
        utils.debug_print('without_response', without_response)
        # is this the fastest way to check this?
        # actually, this check is pretty slow, I should maintain
        # a sorted list or something
        # let's think a bit about this data structure, might want to
        # maintain a mongo dictionary for this, or put it in butler memory
        # in general let's rethink all these data structures
        if not available or '{}_{}'.format(curr_pivot, b) in answered:
            lock.release()
            return True

        answered.append('{}_{}'.format(curr_pivot, b))
        # make this prettier - one line
        for i, x in enumerate(without_response):
            if x[0] == [curr_pivot, b]:
                utils.debug_print('removed from without_response')
                del without_response[i]

        tree = butler.algorithms.get(key='tree')
        if ans == curr_pivot:
            # curr_pivot > b
            if tree[curr_pivot][0] is -1:
                tree[curr_pivot][0] = b
            else:
                queries.append((tree[curr_pivot][0], b))
        elif ans == b:
            # curr_pivot < b
            if tree[curr_pivot][1] is -1:
                tree[curr_pivot][1] = b
            else:
                queries.append((tree[curr_pivot][1], b))
        butler.algorithms.set(key='queries', value=queries)
        butler.algorithms.set(key='tree', value=tree)
        butler.algorithms.set(key='answered', value=answered)
        butler.algorithms.set(key='without_response', value=without_response)
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid,
                                      'timestamp': utils.datetimeNow(),
                                      'queries': len(queries),
                                      'alg_label': butler.alg_label,
                                      'without_response': len(without_response),
                                      'available': available,
                                      'answered': len(answered)})
        lock.release()

        utils.debug_print('tree:{}'.format(tree))
        utils.debug_print('without_response:{}'.format(without_response))
        utils.debug_print('answered:{}'.format(answered))
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
