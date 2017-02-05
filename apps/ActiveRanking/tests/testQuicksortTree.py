import json
import pdb

with open('ALG-EVALUATION','r') as f:
    events = json.loads(f.read())

events = sorted(events['log_data'], key=lambda x: x['timestamp'])

for algcount in range(2):
    alg_label = 'QuicksortTree_'+str(algcount)

    for (eventcount, l) in enumerate(events):

        if l['api_call']=='getQuery' and l['query'][2]==0:
            print "Quicksort %d ran flawless" %(algcount)
            break

        if l['api_call']=='processAnswer' and l['query'][3]==0:
            print "Quicksort %d ran flawless" %(algcount)
            break

        if l['alg_label'] != alg_label:
            continue
        
        new_queryqueue = l['queries']
        new_without_response = l['without_response']
        new_tree = l['tree']
        query = l['query']
        #print query

        if l['api_call'] == 'initExp':
            queryqueue = new_queryqueue
            tree = new_tree
            without_response = new_without_response

        elif l['api_call'] == 'getQuery':
            # check if new query has been removed from queryqueue.
            # I'm not checking if queries sitting in without_response for too long
            # have been added or not.
            left_id = query[0]
            right_id = query[1]

            if len(queryqueue)==0:
                # if old queryqueue is empty, make without_response the old queryqueue
                queryqueue = [w[0] for w in without_response]
            if [left_id, right_id] not in queryqueue:
                print "algcount %d eventcount %d getQuery: This query is not in old queryqueue" %(algcount, eventcount)
                pdb.set_trace()
                break
            elif [left_id, right_id] in new_queryqueue:
                print "algcount %d eventcount %d getQuery: This query should have been removed from queryqueue" %(algcount, eventcount)
                pdb.set_trace()
                break
            x = filter(lambda x: x[0] == [left_id, right_id], new_without_response)
            if len(x) == 0:
                print "algcount %d eventcount %d getQuery: This query should have been in without_response" %(algcount, eventcount)
                pdb.set_trace()
                break

        elif l['api_call'] == 'processAnswer':
            left_id = query[0]
            right_id = query[1]
            winner_id = query[2]
            x = filter(lambda x: x[0] == [left_id, right_id], new_without_response)
            # x represent's queries in without_response that are not equal to current query
            if len(x) != 0:
                print "algcount %d eventcount %d processAnswer: This should have been removed from without_response" %(algcount, eventcount)
                pdb.set_trace()
                break

            # check if this query is in old without_response. If it is not, ignore it.
            x = filter(lambda x: x[0] == [left_id, right_id], without_response)
            if len(x)==0:
                # this query should be ignored, it has been received already.
                continue

            if winner_id == left_id:
                if tree[left_id][0] == -1:
                    if new_tree[left_id][0] != right_id:
                        print "algcount %d eventcount %d processAnswer: Left node should be right_id" %(algcount, eventcount)
                        pdb.set_trace()
                        break
                else:
                    if [tree[left_id][0], right_id] not in new_queryqueue:
                        print "algcount %d eventcount %d processAnswer: New query should have been appended" %(algcount, eventcount)
                        pdb.set_trace()
                        break
            else:
                if tree[left_id][1] == -1:
                    if new_tree[left_id][1] != right_id:
                        print "algcount %d eventcount  %d processAnswer: Right node should be right_id" %(algcount, eventcount)
                        pdb.set_trace()
                        break
                else:
                    if [tree[left_id][1], right_id] not in new_queryqueue:
                        print "algcount %d eventcount %d: New query should have been appended" %(algcount, eventcount)
                        pdb.set_trace()
                        break

        queryqueue = new_queryqueue
        without_response = new_without_response
        tree = new_tree
