"""
Quicksort app implements Quicksort Active Sampling Algorithm
author: Sumeet Katariya, sumeetsk@gmail.com
last updated: 09/20/2016
"""

import numpy as np
from datetime import datetime
import dateutil.parser
import next.utils as utils
import random
import time

class Quicksort:
    app_id = 'ActiveRanking'
    def initExp(self, butler, n=None, params=None):
        nquicksorts = 8
        arrlist = []
        for _ in range(nquicksorts):
            arrlist.append(list(np.random.permutation(range(n))))

        queryqueuesallqs = [] #list of queryqueues for all the quicksorts
        for _ in range(nquicksorts):
            queryqueuesallqs.append([])

        stackparametersallqs = []
        for _ in range(nquicksorts):
            stackparametersallqs.append({})

        for c1 in range(nquicksorts):
            arr = arrlist[c1]
            stackvalue = {'l':0, 'h':n, 'pivot':arr[n-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
            stackkey = utils.getNewUID()
            stacks = {stackkey: stackvalue}
            stackparametersallqs[c1] = stacks
            queryqueue = []
            for c2 in range(len(arr)-1):
                queryqueue.append([arr[c2], arr[n-1], [c1,stackkey,'0']])
                #each query maintains a quicksort_id, a stack index (which is stackkey in the beginning), and a time when it was sent out, which is added when it is sent. That is why the sent time is '0' for now. It is also set to '0' if the query was removed from waitingforresponse because the response did not arrive within the prescribed limit.
            queryqueuesallqs[c1] = queryqueue

        waitingforresponse = []
        for _ in range(nquicksorts):
            waitingforresponse.append({})

        ranking = np.zeros(n)

        butler.algorithms.set(key='nquicksorts', value=nquicksorts)
        butler.algorithms.set(key='n', value=n)
        butler.algorithms.set(key='arrlist', value=arrlist)
        butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        butler.algorithms.set(key='ranking', value=ranking)

        return True

    def getQuery(self, butler, participant_uid):
        lock = butler.memory.lock('QSlock')
        lock.acquire()
        utils.debug_print('In Quicksort getQuery')

        nquicksorts = butler.algorithms.get(key='nquicksorts')
        n = butler.algorithms.get(key='n')
        arrlist = butler.algorithms.get(key='arrlist')
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        waitingforresponse = butler.algorithms.get(key='waitingforresponse')
        stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')

        #for all quicksort_ids, check if there are any queries that have been lying around in waitingforresponse for a long time
        cur_time = datetime.now()
        for qsid in range(nquicksorts): 
            for key in waitingforresponse[qsid]:
                senttimeiniso = waitingforresponse[qsid][key][2][2]
                if senttimeiniso == '0':
                    continue #this query has been added to the queue already
                else:
                    senttime = dateutil.parser.parse(senttimeiniso)

                    timepassedsincesent = cur_time - senttime
                    timepassedsincesentinsecs = timepassedsincesent.total_seconds()
                    if timepassedsincesentinsecs > 50:
                        query = waitingforresponse[qsid][key]
                        query[2][2] = '0'
                        queryqueuesallqs[qsid].append(query)
                        waitingforresponse[qsid][key] = query
                        #setting time to '0' indicates that the query has been added to the queue, avoid repeat additions.

        if queryqueuesallqs == [[]]*nquicksorts:
            #all quicksort queues empty: fork a new quicksort
            nquicksorts = nquicksorts + 1
            arr = np.random.permutation(range(n))
            arrlist.append(list(arr))
            stackvalue = {'l':0, 'h':n, 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
            stackkey = utils.getNewUID()
            stackparametersallqs.append({stackkey: stackvalue})
            quicksort_id = nquicksorts-1
            queryqueue = []
            for c1 in range(len(arr)-1):
                queryqueue.append([arr[c1], arr[-1], [quicksort_id, stackkey, '0']])
            queryqueuesallqs.append(queryqueue)
            waitingforresponse.append({})
            butler.algorithms.set(key='nquicksorts', value=nquicksorts)
            butler.algorithms.set(key='stackparametersallqs', value= stackparametersallqs)
            butler.algorithms.set(key='arrlist', value=arrlist)

        #pop the query
        quicksort_id = np.random.randint(nquicksorts)

        while queryqueuesallqs[quicksort_id] == []:
            #current queue empty, switch to a different one
            quicksort_id = np.random.randint(nquicksorts)
        query_index = np.random.randint(len(queryqueuesallqs[quicksort_id])) #removed last_query business
        query = queryqueuesallqs[quicksort_id].pop(query_index)

        #flip with 50% chance
        if random.choice([True,False]):
            query[0],query[1] = query[1],query[0]

        #add timestamp to query
        query[2][2] = datetime.now().isoformat()
        smallerindexitem = min(query[0], query[1])
        largerindexitem = max(query[0], query[1])
        waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)] = query

        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)

        utils.debug_print('Current Query ' + str(query))

        utils.debug_print('End of Quicksort getQuery')
        butler.log('Events', {'exp_uid':butler.exp_uid,
                              'alg':'QS', 'function':'getQuery',
                              'left_id':query[0], 'right_id':query[1], 'winner_id':'None', 'id':query[2][0],
                              'timestamp':utils.datetimeNow(),
                              'waitingforresponse':waitingforresponse,
                              'queryqueuesallqs':queryqueuesallqs,
                              'stackparametersallqs':stackparametersallqs,
                              'arrlist':arrlist,
                              'participant':participant_uid,
                              'msg':'Success'})
        lock.release()
        return query

    def processAnswer(self, butler, left_id=0, right_id=0, winner_id=0, quicksort_data=0):
        lock = butler.memory.lock('QSlock')
        lock.acquire()
        utils.debug_print('In Quicksort processAnswer ' + str([left_id, right_id, winner_id, quicksort_data[0]]))

        nquicksorts = butler.algorithms.get(key='nquicksorts')
        n = butler.algorithms.get(key='n')
        arrlist = butler.algorithms.get(key='arrlist')
        queryqueuesallqs = butler.algorithms.get(key='queryqueuesallqs')
        stackparametersallqs = butler.algorithms.get(key='stackparametersallqs')
        waitingforresponse = butler.algorithms.get(key='waitingforresponse')
        quicksort_id = quicksort_data[0]
        arr = np.array(arrlist[quicksort_id])
        stackkey = quicksort_data[1]
        stacks = stackparametersallqs[quicksort_id] #dictionary of stacks for current quicksort_id
        smallerindexitem = min(left_id, right_id)
        largerindexitem = max(left_id, right_id)
        try:
            query = waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)]
        except KeyError:
            #this means that the query response has been received from a different user maybe, and this response should be ignored. This shouldn't happen too often.

            butler.log('Repeats', {'exp_uid': butler.exp_uid,
                                'calledfrom':'QSprocessAnswer',
                                'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'quicksort_id':quicksort_id, 
                                'msg':'Query not found',
                                'timestamp': utils.datetimeNow()})
            utils.debug_print('End of Quicksort processAnswer: Query not found')
            butler.log('Events', {'exp_uid':butler.exp_uid,
                                  'alg':'QS', 'function':'processAnswer',
                                  'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'id':quicksort_id,
                                  'timestamp':utils.datetimeNow(),
                                  'waitingforresponse':waitingforresponse,
                                  'queryqueuesallqs':queryqueuesallqs,
                                  'stackparametersallqs':stackparametersallqs,
                                  'arrlist':arrlist,
                                  'participant':None,
                                  'msg':'Error: Query not found'})
            lock.release()
            return True
        
        del waitingforresponse[quicksort_id][str(smallerindexitem)+','+str(largerindexitem)]
        #if waitingforresponse is empty, it means there might be queries that have not been sent out to users so far.

        #if this query was added to the queue again to be resent because the first response wasn't received soon, delete it from the queue - the response has been received.
        for q in queryqueuesallqs[quicksort_id]:
            if ((q[0]==left_id and q[1]==right_id) or (q[0]==right_id and q[1]==left_id)):
                queryqueuesallqs[quicksort_id].remove(q)
                break

        curquerystackvalue = stacks[stackkey]
        if winner_id==left_id:
            loser = right_id
        else:
            loser = left_id

        #second check to make sure this response hasn't been recorded already. Check that the non-pivot id is not in the smallerthanpivot or largerthanpivot list
        nonpivot_id = (left_id==curquerystackvalue['pivot'])*right_id + (right_id==curquerystackvalue['pivot'])*left_id
        if nonpivot_id in curquerystackvalue['smallerthanpivot'] or nonpivot_id in curquerystackvalue['largerthanpivot']:
            butler.log('Repeats', {'exp_uid': butler.exp_uid,
                                'calledfrom':'QSprocessAnswer', 
                                'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'quicksort_id':quicksort_id, 
                                'msg':'Response for this query has already been recorded', 
                                'curquerystackvalue':curquerystackvalue,
                                'timestamp': utils.datetimeNow()})

            utils.debug_print('End of Quicksort processAnswer: Response for this query recorded already')
            butler.log('Events', {'exp_uid':butler.exp_uid,
                                  'alg':'QS', 'function':'processAnswer',
                                  'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'id':quicksort_id,
                                  'timestmp':utils.datetimeNow(),
                                  'waitingforresponse':waitingforresponse,
                                  'queryqueuesallqs':queryqueuesallqs,
                                  'stackparametersallqs':stackparametersallqs,
                                  'arrlist':arrlist,
                                  'participant':None,
                                  'msg':'Error: Response recorded earlier'})
            lock.release()
            return True


        if winner_id==curquerystackvalue['pivot']:
            curquerystackvalue['smallerthanpivot'].append(loser)
        else:
            curquerystackvalue['largerthanpivot'].append(winner_id)

        curquerystackvalue['count'] = curquerystackvalue['count']+1
        if curquerystackvalue['count'] == curquerystackvalue['h']-curquerystackvalue['l']-1:
            del stackparametersallqs[quicksort_id][stackkey]
            l = curquerystackvalue['l']
            h = curquerystackvalue['h']
            smallerthanpivot = curquerystackvalue['smallerthanpivot']
            largerthanpivot = curquerystackvalue['largerthanpivot']
            pivot = curquerystackvalue['pivot']

            #update array
            arr[l:h] = smallerthanpivot + [pivot] + largerthanpivot
            arrlist[quicksort_id] = list(arr)
            butler.algorithms.set(key='arrlist', value=arrlist)

            #create two new stacks
            if len(smallerthanpivot) > 1:
                newstackvalue = {'l':l, 'h':l+len(smallerthanpivot), 'pivot':smallerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                newstackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(smallerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([smallerthanpivot[c3], smallerthanpivot[-1], [quicksort_id, newstackkey, '0']])
            if len(largerthanpivot) > 1:
                newstackvalue = {'l': l+len(smallerthanpivot)+1, 'h':h, 'pivot':largerthanpivot[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                newstackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id][newstackkey] = newstackvalue
                for c3 in range(len(largerthanpivot)-1):
                    queryqueuesallqs[quicksort_id].append([largerthanpivot[c3], largerthanpivot[-1], [quicksort_id, newstackkey, '0']])

            if stackparametersallqs[quicksort_id] == {}:
                #if stack is empty

                #1) update ranking
                ranking = np.array(butler.algorithms.get(key='ranking'))
                ranking = ranking + arr
                #g = open('QSranking.log','a')
                #g.write(str(arr)+'\n')
                #g.close()
                butler.algorithms.set(key='ranking', value=ranking)
                #f.write('ranking = '+str(ranking)+'\n')
                    
                #2) create a new permutation
                arr = np.random.permutation(range(n))
                arrlist[quicksort_id] = arr
                butler.algorithms.set(key='arrlist', value=arrlist)
        
                #3) add queries to queue, and stack parameters to stack
                stackvalue = {'l':0, 'h':len(arr), 'pivot':arr[-1], 'smallerthanpivot':[], 'largerthanpivot':[], 'count':0}
                stackkey = utils.getNewUID()
                stackparametersallqs[quicksort_id] = {stackkey: stackvalue}
                for c4 in range(len(arr)-1):
                    queryqueuesallqs[quicksort_id].append([arr[c4], arr[-1], [quicksort_id, stackkey, '0']])

        butler.log('Queries', {'exp_uid': butler.exp_uid,
                               'alg':'QS', 
                               'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'data':quicksort_id, 
                               'timestamp': utils.datetimeNow()})
        butler.log('QuicksortArrays', {'exp_uid': butler.exp_uid,
                                       'calledfrom':'QSprocessAnswer',
                                       'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'quicksort_id':quicksort_id, 
                                       'arrlist': arrlist,
                                       'timestamp': utils.datetimeNow()})

        butler.algorithms.set(key='stackparametersallqs', value=stackparametersallqs)
        butler.algorithms.set(key='queryqueuesallqs', value=queryqueuesallqs)
        butler.algorithms.set(key='waitingforresponse', value=waitingforresponse)

        utils.debug_print('End of Quicksort processAnswer')
        butler.log('Events', {'exp_uid':butler.exp_uid,
                              'alg':'QS', 'function':'processAnswer',
                              'left_id':left_id, 'right_id':right_id, 'winner_id':winner_id, 'id':quicksort_id,
                              'timestamp':utils.datetimeNow(),
                              'waitingforresponse':waitingforresponse,
                              'queryqueuesallqs':queryqueuesallqs,
                              'stackparametersallqs':stackparametersallqs,
                              'arrlist':arrlist,
                              'participant':None,
                              'msg':'Success'})
        lock.release()
        return True

    def getModel(self,butler):
        arrlist = butler.algorithms.get(key='arrlist')
        arrlist = np.array(arrlist)
        positionlist = np.zeros(np.shape(arrlist))
        for j in range(np.shape(arrlist)[0]):
            positionlist[j,:] = np.argsort(arrlist[j,:])
        meanposition = np.mean(positionlist, 0)
        ranklist = np.argsort(meanposition)
        return np.argsort(ranklist).tolist()
