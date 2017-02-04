import json
import unittest
import urllib2
import pdb


experiment_url = 'http://ec2-52-32-217-76.us-west-2.compute.amazonaws.com:8000/api/experiment/0ba5350ab538e55d967b8ee126726b/logs'

events = json.loads(urllib2.urlopen(experiment_url+'/Events').read())['log_data']
f = open('Events.log','w')
for l in events:
    if l['calledfrom']=='QSinitExp':
        queryqueue = l['queries']
        tree = l['tree']
        without_response = l['without_response']
        answered = l['answered']


    if l['calledfrom'] == 'QSgetQuery':
        new_queryqueue = l['queries']
        new_without_response = l['without_response']
        left_id = l['left_id']
        right_id = l['right_id']

        # check if new query has been removed from queryqueue. Here I'm not checking if queries sitting in without_response for too long have been added or not. 
        if ([left_id, right_id] not in queryqueue ):
            print "This query is not in old queryqueue"
            break
        if ([left_id, right_id] in new_queryqueue):
            print "This query should have been removed from queryqueue"
            break
        x = filter(lambda x: x==[left_id,right_id], new_without_response)
        if len(x)==0:
            print "This query should have been in without_response"
            break

        queryqueue = new_queryqueue
        without_response = new_without_response




    if l['calledfrom'] == 'QSprocessAnswer':
        new_queryqueue = l['queries']
        new_without_response = l['without_response']
        new_tree = l['tree']
        left_id = l['left_id']
        right_id = l['right_id']
        winner_id = l['winner_id']

        x = filter(lambda x: x==[left_id, right_id], new_without_response)
        if len(x) != 0:
            print "This should have been removed from without_response"
            break
        if winner_id == left_id:
            if tree[left_id][0]==-1:
                if new_tree[left_id][0]!=right_id:
                    print "Left node should be right_id"
                    break
            else:
                if [tree[left_id][0], right_id] not in new_queryqueue:
                    print "New query should have been appended"
                    break
        else: #winner = right_id
            if tree[left_id][1]==-1:
                if new_tree[left_id][1]!=right_id:
                    print "Right node should be right_id"
                    break
                else:
                    if [tree[left_id][1], right_id] not in new_queryqueue:
                        print "New query should have been appended"
                        break
                    
        queryqueue = new_queryqueue
        without_response = new_without_response
        tree = new_tree
