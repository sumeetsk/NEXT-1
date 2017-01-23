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


def test_validation_params():
    params = [{'num_tries': 5},
              {'query_list': [[0, 1], [1, 2], [3, 4]]}]
    for param in params:
        print(param)
        test_api(params=param)


def test_api(assert_200=True, num_arms=100, num_clients=30, delta=0.05,
             total_pulls_per_client=20, num_experiments=1,
             params={'num_tries': 5}):


    true_means = numpy.array(range(num_arms)[::-1])/float(num_arms)
    true_means = np.arange(num_arms)
    pool = Pool(processes=num_clients)
    supported_alg_ids = ['AR_Random', 'Quicksort', 'ValidationSampling']

    alg_list = []
    for i, alg_id in enumerate(supported_alg_ids):
        alg_item = {}
        if alg_id == 'ValidationSampling':
            alg_item['params'] = params
        alg_item['alg_id'] = alg_id
        alg_item['alg_label'] = alg_id+'_'+str(i)
        alg_list.append(alg_item)

    params = [{'alg_label': 'AR_Random', 'proportion': 9./28},
              {'alg_label': 'Quicksort', 'proportion': 14./28},
              {'alg_label': 'ValidationSampling', 'proportion': 5./28}]
    algorithm_management_settings = {'mode':'custom', 'params':params}
    #################################################
    # Test POST Experiment
    #################################################
    initExp_args_dict = {'app_id' : 'ActiveRanking'}
    initExp_args_dict['args'] = {'alg_list': alg_list,
                                 'algorithm_management_settings': algorithm_management_settings,
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
        query_dict, dt = test_utils.getQuery(getQuery_args_dict)
        getQuery_times.append(dt)

        query_uid = query_dict['query_uid']
        targets = query_dict['target_indices']

        left = targets[0]['target']
        right = targets[1]['target']

        np.random.seed()
        if np.random.random()<1./10:
            f = open('Drops.log', 'a')
            f.write(str(query_dict)+'\n')
            f.close()
            break

        # sleep for a bit to simulate response time
        ts = test_utils.response_delay(mean=0, std=0)

        #  print left
        reward_left = true_means[left['target_id']]# + numpy.random.randn()*0.5
        reward_right = true_means[right['target_id']]# + numpy.random.randn()*0.5
        if reward_left > reward_right:
            target_winner = left
        else:
            target_winner = right

        response_time = time.time() - ts

        # test POST processAnswer 
        processAnswer_args_dict = {'args': {'query_uid': query_uid,
                                            'response_time': response_time,
                                            'target_winner': target_winner["target_id"]},
                                   'exp_uid': exp_uid}
        processAnswer_json_response, dt = test_utils.processAnswer(processAnswer_args_dict)
        processAnswer_times += [dt]



if __name__ == '__main__':
    test_api()
