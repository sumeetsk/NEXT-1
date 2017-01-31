import json
import unittest
import urllib2
import pdb


experiment_url = 'http://ec2-35-167-172-196.us-west-2.compute.amazonaws.com:8000/api/experiment/2d0b0b62e69e3d28a084972b3a4115/logs'

#with open('../Drops.log','r') as f:
#    for line in f:
#        a = eval(line)
#        #pdb.set_trace()
#        print a['alg_id'],a['target_indices'][0]['target']['target_id'],a['target_indices'][1]['target']['target_id']
#
#logs = json.loads(urllib2.urlopen(experiment_url+'/Repeats').read())['log_data']
#for l in logs:
#    print l['calledfrom'][:2],l['left_id'], l['right_id'],l['msg'],l['timestamp']
#
events = json.loads(urllib2.urlopen(experiment_url+'/Events').read())['log_data']
f = open('Events.log','w')
for l in events:
    if l['alg']=='QS':
            f.write('\n'.join(str(x) for x in [l['left_id'], l['right_id'], l['winner_id'], l['id'], l['function'], l['timestamp'], l['waitingforresponse'][3], l['queryqueuesallqs'][3], l['stackparametersallqs'][3], l['msg']]) + '\n\n')
f.close()

quicksortarrays = json.loads(urllib2.urlopen(experiment_url+'/QuicksortArrays').read())['log_data']
f = open('QuicksortArrays.log','w')
for l in quicksortarrays:
    #f.write(str(len(l['arrlist']))+',')
    f.write(','.join(str(x) for x in [l['left_id'], l['right_id'], l['quicksort_id'], l['arrlist']])+'\n')

f.close()
