"""
AR_Random app implements Active ranking Random
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/24/2016

AR_Random implements random sampling 
"""

import numpy as np
import numpy.random
import next.utils as utils
from datetime import datetime

class AR_Random:
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        W = numpy.zeros((n,n))

        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='W', value=W.tolist())
        return True

    def getQuery(self, butler, participant_uid):
        utils.debug_print('In AR_Random: getQuery')
        n = butler.algorithms.get(key='n')

        index = np.random.randint(n)
        alt_index = np.random.randint(n)
        while alt_index == index:
            alt_index = np.random.randint(n)

        utils.debug_print('Current Query ' + str([index, alt_index]))
        return [index, alt_index, 0]

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        utils.debug_print('In AR_Random processAnswer '+str([left_id, right_id, winner_id, quicksort_data]))

        W = np.array(butler.algorithms.get(key='W'))
        utils.debug_print('processAnswer exp_uid', butler.exp_uid)
        butler.log('AR_Random', {'exp_uid': butler.exp_uid,
                                 'calledfrom':'ARprocessAnswer',
                                 'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id,
                                 'timestamp':utils.datetimeNow()})
        butler.log('Queries', {'exp_uid': butler.exp_uid,
                               'alg':'AR',
                               'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id,
                               'timestamp':utils.datetimeNow()})
        #f = open('AR_Random.log','a')
        #f.write(str([left_id,right_id,winner_id])+'\n')
        #f.close()
        #f = open('Queries.log','a')
        #f.write('AR '+str([left_id,right_id,winner_id])+'\n')
        #f.close()

        if left_id == winner_id:
            W[left_id, right_id] = W[left_id, right_id] + 1
        else:
            W[right_id, left_id] = W[right_id, left_id] + 1

        butler.algorithms.set(key='W', value=W.tolist())

        utils.debug_print('End of AR_Random processAnswer')
        return True

    def getModel(self,butler):
        W = np.array(butler.algorithms.get(key='W'))
        n = W.shape[0]
        P = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i==j:
                    continue
                if (W[i][j]+W[j][i]==0):
                    P[i][j] = 0.5
                else:
                    P[i][j] = float(W[i][j])/(W[i][j]+W[j][i])
        scores = np.sum(P, axis=1)/(n-1)
        sortedimages = np.argsort(scores)
        positions = np.argsort(sortedimages)
        return positions.tolist()
