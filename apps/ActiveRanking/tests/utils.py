import json
import unittest
import urllib2
import pdb


experiment_url = 'http://ec2-52-32-217-76.us-west-2.compute.amazonaws.com:8000/api/experiment/0ba5350ab538e55d967b8ee126726b/logs'

#with open('../Drops.log','r') as f:
#    for line in f:
#        a = eval(line)
#        #pdb.set_trace()
#        print a['alg_id'],a['target_indices'][0]['target']['target_id'],a['target_indices'][1]['target']['target_id']
#
logs = json.loads(urllib2.urlopen(experiment_url+'/Repeats').read())['log_data']
for l in logs:
    print l['calledfrom'][:2],l['left_id'], l['right_id'],l['msg'],l['timestamp']

events = json.loads(urllib2.urlopen(experiment_url+'/Events').read())['log_data']
f = open('Events.log','w')
for l in events:
    #pdb.set_trace()
    if l['alg']=='VS':
        f.write(str([l['alg'], l['function'],l['left_id'],l['right_id'],l['winner_id'],l['id'],l['timestamp'],l['participant'],l['msg'],l['waitingforresponse']])+'\n')
    #print l['calledfrom'][:2],l['left_id'], l['right_id'],l['msg'],l['timestamp']
f.close()
