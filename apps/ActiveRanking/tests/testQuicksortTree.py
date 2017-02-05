import json



with open('ALG-EVALUATION','r') as f:
    events = json.loads(f.read())

events = sorted(events['log_data'], key=lambda x: x['timestamp'])
alg_label = 'QuicksortTree_0'
for l in events:
    if l['alg_label'] != alg_label:
        continue
    
    new_queryqueue = l['queries']
    new_without_response = l['without_response']
    new_tree = l['tree']
    query = l['query']

    if l['api_call'] == 'initExp':
        queryqueue = new_queryqueue
        tree = new_tree
        without_response = new_without_response

    elif l['api_call'] == 'getQuery':
        # check if new query has been removed from queryqueue.
        # I'm not checking if queries sitting in without_response for too long
        # have been added or not.
        if query not in queryqueue:
            print "This query is not in old queryqueue"
            break
        elif query in new_queryqueue:
            print "This query should have been removed from queryqueue"
            break
        x = filter(lambda x: x[0] == [left_id, right_id], new_without_response)
        if len(x) == 0:
            print "This query should have been in without_response"
            break

    elif l['api_call'] == 'processAnswer':
        left_id = query[0]
        right_id = query[1]
        winner_id = query[2]
        x = filter(lambda x: x[0] == [left_id, right_id], new_without_response)
        if len(x) != 0:
            print "This should have been removed from without_response"
            break
        if winner_id == left_id:
            if tree[left_id][0] == -1:
                if new_tree[left_id][0] != right_id:
                    print "Left node should be right_id"
                    break
            else:
                if [tree[left_id][0], right_id] not in new_queryqueue:
                    print "New query should have been appended"
                    break
        else:
            if tree[left_id][1] == -1:
                if new_tree[left_id][1] != right_id:
                    print "Right node should be right_id"
                    break
                else:
                    if [tree[left_id][1], right_id] not in new_queryqueue:
                        print "New query should have been appended"
                        break

    queryqueue = new_queryqueue
    without_response = new_without_response
    tree = new_tree
