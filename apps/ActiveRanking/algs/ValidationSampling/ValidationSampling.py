import numpy as np
import next.utils as utils
from datetime import datetime
import dateutil.parser
import time
import random


class ValidationSampling:
    """
    The keys in waitingforresponse are 'id,first_item,second_item'. The id is 1, 2, or 3. The values are (id, first_item, second_item, time_sent). time_sent is set to 0 if it has been more than 20 seconds since the query was sent.
    """
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        """
        This function is meant to set keys used later by the algorith implemented
        in this file.
        """
        queryqueue = []
        while len(queryqueue) < 1000:
            a1 = np.random.randint(n)
            b1 = np.random.randint(n)
            while b1==a1:
                b1 = np.random.randint(n)
            queryalreadyexists = False
            for query in queryqueue:
                if (((query[0],query[1])==(a1,b1)) or ((query[1],query[0])==(b1,a1))):
                    queryalreadyexists = True
                    break
            if queryalreadyexists:
                continue
            else:
                queryqueue.append([a1,b1,[1,'0']])

        queryqueue2 = []
        for query in queryqueue:
            queryqueue2.append([query[0], query[1], [2,'0']])
        queryqueue3 = []
        for query in queryqueue:
            queryqueue3.append([query[0], query[1], [3,'0']])

        butler.algorithms.set(key='n', value=n)
        butler.other.set(key='VSqueryqueue', value=queryqueue+queryqueue2+queryqueue3)
        butler.algorithms.set(key='VSwaitingforresponse', value={})
        return True

    def getQuery(self, butler, participant_uid):
        utils.debug_print('In Validation getQuery')

        n = butler.algorithms.get(key='n')
        queryqueue = butler.other.get(key='VSqueryqueue')
        waitingforresponse = butler.algorithms.get(key='VSwaitingforresponse')

        #for all queries in waitingforresponse, check if there are any queries that have been lying around in waitingforresponse for a long time
        cur_time = datetime.now()
        for key in waitingforresponse:
            senttimeiniso = waitingforresponse[key][2][1]
            if senttimeiniso=='0':
                continue #this query has been added to the queue already
            else:
                senttime = dateutil.parser.parse(senttimeiniso)
                timepassedsincesent = cur_time-senttime
                timepassedsincesentinsecs = timepassedsincesent.total_seconds()
                if timepassedsincesentinsecs > 50:
                    #setting time to '0' indicates that the query has been added to the queue, avoid repeat additions.
                    utils.debug_print('Validation: adding back to queue')
                    utils.debug_print('Current time: '+str(cur_time))
                    utils.debug_print('Sent time: '+str(senttime))
                    query = waitingforresponse[key]
                    query[2][1] = '0'
                    waitingforresponse[key] = query
                    queryqueue.append(query) 

        #pop the query
        query = queryqueue.pop(0)

        #flip with 50% chance
        if random.choice([True,False]):
            query[0],query[1] = query[1],query[0]

        #add timestamp to query
        query[2][1] = datetime.now().isoformat()
        smallerindexitem = min(query[0], query[1])
        largerindexitem = max(query[0], query[1])
        waitingforresponse[str(smallerindexitem)+','+str(largerindexitem)+','+str(query[2][0])] = query

        butler.log('VSampling', {'exp_uid': butler.exp_uid,
                                 'calledfrom':'VSgetQuery', 
                                 'waitingforresponse': waitingforresponse, 
                                 'timestamp':utils.datetimeNow()})

        butler.other.set(key='VSqueryqueue', value=queryqueue)
        butler.algorithms.set(key='VSwaitingforresponse', value=waitingforresponse)

        utils.debug_print('Current Query ' + str(query))
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        utils.debug_print('In Validation processAnswer '+str([left_id, right_id, winner_id, quicksort_data]))

        waitingforresponse = butler.algorithms.get(key='VSwaitingforresponse')
        queryqueue = butler.other.get(key='VSqueryqueue')

        butler.log('VSampling', {'exp_uid': butler.exp_uid,
                                 'calledfrom':'VSprocessAnswer', 
                                 'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'validationid':quicksort_data[0], 
                                 'timestamp':utils.datetimeNow()}) 

        smallerindexitem = min(left_id, right_id)
        largerindexitem = max(left_id, right_id)
        try:
            query = waitingforresponse[str(smallerindexitem)+','+str(largerindexitem)+','+str(quicksort_data[0])]
        except KeyError:
            #this means that the query response has been received from a different user maybe, and this response should be ignored. This shouldn't happen too often.
            butler.log('Bugs', {'exp_uid': butler.exp_uid,
                                'calledfrom':'VSprocessAnswer', 
                                'msg':'Did not find in waitingforresponse',
                                'left_id':left_id, 'right_id':right_id, 'validationid':quicksort_data[0],
                                'timestamp':utils.datetimeNow()})

            utils.debug_print('End of Validation processAnswer: KeyError')
            return True

        del waitingforresponse[str(smallerindexitem)+','+str(largerindexitem)+','+str(quicksort_data[0])]
        
        #if this query was added to the queue again to be resent because the first response wasn't received soon, delete it from the queue - the response has been received.
        for q in queryqueue:
            if ((q[0]==left_id and q[1]==right_id and q[2][0]==quicksort_data[0]) or (q[0]==right_id and q[1]==left_id and q[2][0]==quicksort_data[0])):
                queryqueue.remove(q)
                break

        butler.log('Queries', {'exp_uid': butler.exp_uid,
                               'alg':'VS', 
                               'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'validationid':quicksort_data[0], 
                               'timestamp':utils.datetimeNow()})

        butler.log('VSAnalysis', {'exp_uid': butler.exp_uid,
                                  'calledfrom':'VSprocessAnswer',
                                  'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'validationid':quicksort_data[0], 
                                  'timestamp':utils.datetimeNow()})

        #write everything back
        butler.algorithms.set(key='VSwaitingforresponse', value=waitingforresponse)
        butler.other.set(key='VSqueryqueue', value=queryqueue)

        utils.debug_print('End of Validation processAnswer')
        return True

    def getModel(self,butler):
        n = butler.algorithms.get(key='n')
        return range(n)

