"""
AR_Random app implements Active ranking Random
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/24/2016

AR_Random implements random sampling 
"""

import numpy as np
import numpy.random
import next.utils as utils

class AR_Random:
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        W = numpy.zeros((n,n))

        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='W', value=W)
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

        f = open('AR_Random.log','a')
        f.write(str([left_id,right_id,winner_id])+'\n')
        f.close()
        f = open('Queries.log','a')
        f.write('AR '+str([left_id,right_id,winner_id])+'\n')
        f.close()

        if left_id == winner_id:
            W[left_id, right_id] = W[left_id, right_id] + 1
        else:
            W[right_id, left_id] = W[right_id, left_id] + 1

        butler.algorithms.set(key='W', value=W)

        utils.debug_print('End of AR_Random processAnswer')
        return True

    def getModel(self,butler):
        W = butler.algorithms.get(key='W')
        return W, range(5)
