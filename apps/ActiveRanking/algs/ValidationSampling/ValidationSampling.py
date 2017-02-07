import numpy as np
import next.utils as utils
from datetime import datetime
import dateutil.parser
import time
import random


class ValidationSampling:
    """
    The format of a query is [item1, item2, #number of responses received for (item1, item2)
    """
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        """
        This function is meant to set keys used later by the algorith implemented
        in this file.
        """
        querylist = []
        np.random.seed()
        upper = np.floor(500*n*(n-1)/4950)
        while len(querylist) < upper:
            a = np.random.randint(n)
            b = np.random.randint(n)
            while b == a:
                b = np.random.randint(n)
            if [a, b, 0] not in querylist and [b, a, 0] not in querylist:
                querylist.append([a, b, 0])
        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='querylist', value=querylist)
        butler.algorithms.set(key='it', value=0)
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        self.log(butler, 'initExp', [], querylist, 1)
        return True

    def getQuery(self, butler, participant_uid):
        querylist = butler.algorithms.get(key='querylist')
        it = butler.algorithms.get(key='it')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))
        utils.debug_print('VALIDATION SAMPLING querylist {}'.format(querylist))
        nothing_to_send = True
        for count in range(1000):
            it = (it + 1) % len(querylist)
            q = querylist[it]
            if q[2] < 3:
                query = [q[0], q[1], it]
                nothing_to_send = False
                break

        if nothing_to_send:
            n = butler.algorithms.get(key='n')
            query = [np.random.randint(n), np.random.randint(n), -1]
            butler.other.set(key='{}_available'.format(butler.alg_label), value=0)

        utils.debug_print('VALIDATION SAMPLING iterator {}'.format(it))
        utils.debug_print('VALIDATION SAMPLING query {}'.format(query))
        butler.algorithms.set(key='it', value=it)
        self.log(butler, 'getQuery', query, querylist, available)
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        query = [left_id, right_id, winner_id]
        querylist = butler.algorithms.get(key='querylist')
        it = butler.algorithms.get(key='it')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))

        if not available or quicksort_data == -1:
            self.log(butler, 'processAnswer', query, querylist, available)
            return True

        querylist[quicksort_data][2] += 1
        butler.algorithms.set(key='querylist', value=querylist)
        self.log(butler, 'processAnswer', query, querylist, available)
        return True

    def getModel(self,butler):
        n = butler.algorithms.get(key='n')
        return range(n)

    def log(self, butler, api_call, query, querylist, available):
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid, 'timestamp': utils.datetimeNow(),
                                      'alg_label': butler.alg_label, 'api_call': api_call,
                                      'query': query, 'querylist': querylist,
                                      'available': available})
