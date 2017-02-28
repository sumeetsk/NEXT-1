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
        butler.algorithms.set(key='n', value=n)
        self.log(butler, 'initExp', [])
        return True

    
    def getQuery(self, butler, participant_uid):
        utils.debug_print('In AR_Random: getQuery')
        n = butler.algorithms.get(key='n')

        index = np.random.randint(n)
        alt_index = np.random.randint(n)
        query = [index, alt_index]
        while alt_index == index:
            alt_index = np.random.randint(n)

        utils.debug_print('Current Query ' + str([index, alt_index]))
        utils.debug_print('End of AR_Random getQuery')
        self.log(butler, 'getQuery', query)
        return [index, alt_index, 0]

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        utils.debug_print('In AR_Random processAnswer '+str([left_id, right_id, winner_id, quicksort_data]))
        self.log(butler, 'processAnswer', [left_id, right_id, winner_id])
        return True

    def getModel(self,butler):
        n = butler.algorithms.get(key='n')
        return range(n)

    def log(self, butler, api_call, query, msg=''):
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid, 'timestamp': utils.datetimeNow(),
                                      'alg_label': butler.alg_label, 'api_call': api_call,
                                      'query': query, 'msg': msg})
