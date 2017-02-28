"""
author: Lalit Jain, lalitkumarjj@gmail.com
modified: Chris Fernandez, chris2fernandez@gmail.com
modified 2015-11-24: Scott Sievert, stsievert@wisc.edu (added docs)
modified 2016-10-01: Sumeet Katariya, sumeetsk@gmail.com
last updated: 2016-10-01

A module for replicating the Quicksort active ranking experiments. 

Usage:
python chicago_images.py
"""

import os, sys
import zipfile
import numpy as np

# The line below imports launch_experiment.py.
# We assume that it is located in next/examples
# This function is used at the very bottom of this file
sys.path.append("../")
from launch_experiment import *

experiment_list = []

# A list of the currently available StochasticDuelingBanditPureExploration
# algorithms

alg_list = [{'alg_id': 'AR_Random', 'alg_label': 'Random'}]
            #{'alg_id': 'ValidationSampling', 'alg_label': 'TEST'}]

num_quicksorts = 8 
for i in range(num_quicksorts):
  alg_list.append({'alg_id': 'QuicksortTree',
                   'alg_label': 'QuicksortTree_{}'.format(i)})


params = [{'alg_label': 'QuicksortTree_{}'.format(i), 'proportion': 1.}
          for i in range(num_quicksorts)]
algorithm_management_settings = {'mode': 'custom', 'params': params}
print "alg_list = ", alg_list

# Create experiment dictionary
initExp = {}
initExp['args'] = {}

# probability of error. similar to "significant because p < 0.05"
#initExp['args']['failure_probability'] = .01
# one parcipant sees many algorithms? 'one_to_many' means one participant will
# see many algorithms
initExp['args']['participant_to_algorithm_management'] = 'one_to_many'
initExp['args']['algorithm_management_settings'] = algorithm_management_settings
initExp['args']['num_active'] = 2
initExp['args']['alg_list'] = alg_list
initExp['args']['num_tries'] = 50 #How many tries does each user see?

# Which app are we running? (examples of other algorithms are in examples/
initExp['app_id'] = 'ActiveRanking'

curr_dir = os.path.dirname(os.path.abspath(__file__))
experiment = {}
experiment['initExp'] = initExp

# The user chooses between two images. This could be text or video as well.
experiment['primary_type'] = 'image'
target_zip = '{}/chicagoimages.zip'.format(curr_dir)
experiment['primary_target_file'] = target_zip
experiment['context'] = "Which place looks safer?"
experiment['context_type'] = 'text'
experiment_list.append(experiment)

# Launch the experiment.
try:
  AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
  AWS_ACCESS_ID = os.environ['AWS_ACCESS_KEY_ID']
  AWS_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']
  host = os.environ['NEXT_BACKEND_GLOBAL_HOST']+ ":" \
          + os.environ.get('NEXT_BACKEND_GLOBAL_PORT', '8000')

except:
    print 'The following environment variables must be defined:'

    for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
                'AWS_BUCKET_NAME', 'NEXT_BACKEND_GLOBAL_HOST']:
        if key not in os.environ:
            print '    ' + key

    sys.exit()


# Call launch_experiment module found in NEXT/lauch_experiment.py
exp_uid_list = launch_experiment(host, experiment_list, AWS_ACCESS_ID,
                                 AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME,
                                 parallel_upload=True)
