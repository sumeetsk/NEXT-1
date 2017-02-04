import json

filename = '/Users/jain/Desktop/ALG-EVALUATION.2'

with open(filename,'r') as f:
    next_logs = json.load(f)
next_logs = sorted(next_logs['log_data'], key=lambda x:x['timestamp'])

asked = []
answered = []


def check_lists(a, b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i]!= b[i]:
            return False
    return True


verbose = True
count = 0
for entry in next_logs:
    query = entry['query']

    if entry['alg_label']== u'QuicksortMongoTest_7':
        if entry['api_call'] == 'getQuery':
            if len(asked) >= 100:
                asked = []
            asked.append(query)
            if verbose:
                print 'getQuery', query
                print 'server_asked', entry['asked']
                print 'local_asked', asked
                print 'server_answered', entry['answered']
                print 'local_answered', answered
                print '\n\n'
                if (not check_lists(asked, entry['asked'])
                    or not check_lists(answered, entry['answered'])):
                    print "lists don't match!"
                    print query
        else:
            if len(answered) >= 100:
                answered = []
            answered.append(query)
            if verbose:
                print 'processAnswer', query
                print 'server_asked', entry['asked']
                print 'local_asked', asked
                print 'server_answered', entry['answered']
                print 'local_aanswered', answered
                print '\n\n'

            if (not check_lists(asked, entry['asked'])
                or not check_lists(answered, entry['answered'])):
                print "lists don't match!"
                print query
            
        count +=1
        print count

#print len(next_logs)
