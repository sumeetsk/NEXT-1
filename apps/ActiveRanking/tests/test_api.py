import numpy
import numpy as np
import numpy.random
import random
import json
import time
from datetime import datetime
import requests
from scipy.linalg import norm
import time
from multiprocessing import Pool
import os
import sys
from joblib import Parallel, delayed
try:
    import next.apps.test_utils as test_utils
except:
    sys.path.append('../../next/apps/')
    import test_utils


def test_api(assert_200=True, num_arms=100, num_clients=20, delta=0.05,
             total_pulls_per_client=500, num_experiments=1):

    true_means = numpy.array(range(num_arms)[::-1])/float(num_arms)
    true_means = np.arange(num_arms)
    pool = Pool(processes=num_clients)
    num_quicksorts = 16

    alg_list = [{'alg_id': 'AR_Random', 'alg_label': 'Random'},
                {'alg_id': 'ValidationSampling', 'alg_label': 'TEST'}]
    for i in range(num_quicksorts):
        alg_list.append({'alg_id': 'QuicksortTree',
                         'alg_label': 'QuicksortTree_{}'.format(i)})

    params = [{'alg_label': 'QuicksortTree_{}'.format(i), 'proportion': 1.}
              for i in range(num_quicksorts)]
    params.extend([{'alg_label': 'Random', 'proportion': 1},
                   {'alg_label': 'TEST', 'proportion': 1}])
    algorithm_management_settings = {'mode': 'custom', 'params': params}
    #################################################
    # Test POST Experiment
    #################################################
    initExp_args_dict = {'app_id' : 'ActiveRanking'}
    initExp_args_dict['args'] = {'alg_list': alg_list,
                                 'algorithm_management_settings': algorithm_management_settings,
                                 'num_active': 8,
                                 'context': 'Which place looks safer?',
                                 'context_type': 'text',
                                 'debrief': 'Test debrief.',
                                 'instructions': 'Test instructions.',
                                 'participant_to_algorithm_management': 'one_to_many',
                                 'targets': {'n': num_arms}}
    exp_info = []
    for ell in range(num_experiments):
        print 'launching experiment'
        exp_info += [test_utils.initExp(initExp_args_dict)[1]]
        print 'done launching'

    # Generate participants
    participants = ['%030x' % random.randrange(16**30) for i in range(num_clients)]
    pool_args = [(numpy.random.choice(exp_info)['exp_uid'],
                  participant_uid,
                  total_pulls_per_client,
                  true_means,assert_200) for participant_uid in participants]

    print 'starting to simulate all the clients...'
    results = pool.map(simulate_one_client, pool_args)
    print 'done simulating clients'

    for result in results:
        result


def simulate_one_client(input_args):
    exp_uid,participant_uid,total_pulls,true_means,assert_200 = input_args

    getQuery_times = []
    processAnswer_times = []
    for t in range(total_pulls):
        print "        Participant {} is pulling {}/{} arms: ".format(participant_uid, t, total_pulls)

        # test POST getQuery #
        getQuery_args_dict = {'args': {'participant_uid': participant_uid, 'widget': False},
                              'exp_uid': exp_uid}
        query_dict, dt = test_utils.getQuery(getQuery_args_dict, verbose=True)
        getQuery_times.append(dt)
        query_uid = query_dict['query_uid']
        targets = query_dict['target_indices']
        left = targets[0]['target']
        right = targets[1]['target']
        # sleep for a bit to simulate response time
        ts = test_utils.response_delay(mean=1, std=.1)
        target_winner = max(left['target_id'], right['target_id'])
        print 'query:',left['target_id'], right['target_id'], target_winner
        response_time = time.time() - ts
        # test POST processAnswer 
        processAnswer_args_dict = {'args': {'query_uid': query_uid,
                                            'response_time': response_time,
                                            'target_winner': target_winner},
                                   'exp_uid': exp_uid}
        processAnswer_json_response, dt = test_utils.processAnswer(processAnswer_args_dict,
                                                                   verbose=True)
        processAnswer_times += [dt]



if __name__ == '__main__':
    test_api()
