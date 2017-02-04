import numpy as np
from datetime import datetime
import dateutil.parser
import next.utils as utils
import random
import time

class QuicksortMongoTest:
    app_id = 'ActiveRanking'

    def initExp(self, butler, n=None, params=None):
        perm = list(np.random.permutation(range(n)))
        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='asked', value=[])
        butler.algorithms.set(key='answered', value=[])
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        return True

    def getQuery(self, butler, participant_uid):
        lock = butler.memory.lock('MongoTest_{}'.format(butler.alg_label), timeout=5)
        lock.acquire()
        n = butler.algorithms.get(key='n')
        asked = butler.algorithms.get(key='asked')
        answered = butler.algorithms.get(key='answered')
        query = [np.random.randint(n), np.random.randint(n), np.random.randint(1e10)]
        if len(asked) >= 100:
            asked = []
        asked.append(query)
        utils.debug_print('asked ', asked)
        butler.algorithms.set(key='asked', value=asked)
        self.log(butler, 'getQuery', query, asked, answered)
        lock.release()
        return query

    def processAnswer(self, butler, left_id, right_id, winner_id, quicksort_data=0):
        lock = butler.memory.lock('MongoTest_{}'.format(butler.alg_label), timeout=5)
        lock.acquire()
        asked  = butler.algorithms.get(key='asked')
        answered  = butler.algorithms.get(key='answered')
        query = [left_id, right_id, quicksort_data, winner_id]
        if len(answered) >= 100:
            answered = []
        answered.append(query)
        butler.algorithms.set(key='answered', value=answered)
        self.log(butler, 'processAnswer', query, asked, answered)
        lock.release()
        return True

    def log(self, butler, api_call, query, asked, answered):
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid,
                                      'timestamp': utils.datetimeNow(),
                                      'alg_label': butler.alg_label,
                                      'api_call':api_call,
                                      'query': query,
                                      'asked':asked, 
                                      'answered':answered})
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
