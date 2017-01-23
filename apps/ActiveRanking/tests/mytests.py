import json
import unittest
import urllib2
experiment_url = 'http://ec2-52-32-217-76.us-west-2.compute.amazonaws.com:8000/api/experiment/0ba5350ab538e55d967b8ee126726b/logs'

class ActiveRankingTest(unittest.TestCase):
    def test_quicksort_arrays_distinct(self):
        logs = json.loads(urllib2.urlopen(experiment_url+'/QuicksortArrays').read())['log_data']
        for item in logs:
            arrlist = item['arrlist']
            for l in arrlist:
                assert sorted(l) == range(100)
