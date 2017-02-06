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
        queryset = set()
        querylist = []
        np.random.seed()
        while len(querylist) < 1000:
            a = np.random.randint(n)
            b = np.random.randint(n)
            while b==a:
                b = np.random.randint(n)
            if (a,b) not in queryset and (b,a) not in queryset:
                queryset.append((a,b))
                querylist.append([a, b, 0])

        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='querylist', value=querylist)
        butler.algorithms.set(key='list_iterator', value=0)
        butler.other.set(key='{}_available'.format(butler.alg_label), value=1)
        self.log(butler, 'initExp', [], querylist, 1)
        return True

    def getQuery(self, butler, participant_uid):
        querylist = butler.algorithms.get(key='querylist')
        it = butler.algorithms.get(key='list_iterator')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))

        nothing_to_send = True
        for count in range(1000):
            if querylist[it][2] < 3:
                q = querylist[it]
                query = [q[0], q[1], 1]
                it = it + 1
                nothing_to_send = False
                break
            else:
                it = it + 1

        if nothing_to_send:
            n = butler.algorithms.get(key='n')
            query = [np.random.randint(n), np.random.randint(n), 0]
            butler.other.set(key='{}_available'.format(butler.alg_label), value=0)
            self.log(butler, 'getQuery', query, [], 0)
            return query

        butler.algorithms.set(key='list_iterator', value=it)
        self.log(butler, 'getQuery', query, [], 1)
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        query = [left_id, right_id, winner_id]
        querylist = butler.algorithms.get(key='querylist')
        it = butler.algorithms.get(key='list_iterator')
        available = butler.other.get(key='{}_available'.format(butler.alg_label))

        if not available or quicksort_data == 0:
            self.log(butler, 'processAnswer', query, querylist, available)
            return True

        found = False
        x = (it-30)%1000 #iterator over the list, start close to current iterator
        for count in range(1000):
            q = [querylist[x][0], querylist[x][1]]
            if q == [left_id, right_id]:
                querylist[x][2] += 1
                found = True
                break
            else:
                x = (x+1)%1000

        if not found:
            self.log(butler, 'processAnswer', query, querylist, available)
            return True

        butler.algorithms.set(key='querylist', value='querylist')
        self.log(butler, 'getQuery', query, [], 1)
        return True

    def getModel(self,butler):
        n = butler.algorithms.get(key='n')
        return range(n)

    def log(self, butler, api_call, query, querylist, available):
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid, 'timestamp': utils.datetimeNow(),
                                      'alg_label': butler.alg_label, 'api_call': api_call,
                                      'query': query, 'queryqueue': querylist,
                                      'available': available})
