import json
import numpy

import next.apps.SimpleTargetManager
import next.utils as utils
import algs.QuicksortTree.treeStats as treeStats

class MyApp:

    def __init__(self, db):
        self.app_id = 'ActiveRanking'
        self.TargetManager = next.apps.SimpleTargetManager.SimpleTargetManager(
            db)

    def initExp(self, butler, init_algs, args):
        if not args['num_active'] < len(args['alg_list']):
            raise Exception('alg count does not agree with num_active')
        args['active_set'] = ['QuicksortTree_{}'.format(i) for i in range(args['num_active'])]
        if 'targetset' in args['targets'].keys():
            n = len(args['targets']['targetset'])
            self.TargetManager.set_targetset(
                butler.exp_uid, args['targets']['targetset'])
        else:
            n = args['targets']['n']
        args['n'] = n
        del args['targets']
        init_algs({'n': args['n']})

        ########################################################
        # Generate some rubbish queries to test dasboard againgst
        # Remove this from production code.
        lamb = 1. #higher lambda = higher noise
        scale = 1.0/lamb
        nqueries = 500000

        W = numpy.zeros((n,n))
        for _ in range(nqueries):
            i1 = numpy.random.randint(n)
            i2 = numpy.random.randint(n)
            while i2==i1:
                i2 = numpy.random.randint(n)
            if numpy.random.rand() < 1./(1+numpy.exp(-scale*(i1-i2))):
                W[i1,i2] += 1.
            else:
                W[i2,i1] += 1.

        numpy.save('holdout_queries', W)
        ########################################################
        return args

    def getQuery(self, butler, alg, args):
        alg_response = alg({'participant_uid': args['participant_uid']})
        targets = [self.TargetManager.get_target_item(butler.exp_uid,
                                                      alg_response[i])
                   for i in [0, 1]]
        targets_list = [{'target': targets[0], 'label':'left'},
                        {'target': targets[1], 'label':'right'}]
        return_dict = {'target_indices': targets_list,
                       'quicksort_data': alg_response[2]}
        experiment_dict = butler.experiment.get()
        #
        if 'context' in experiment_dict['args'] and 'context_type' in experiment_dict['args']:
            return_dict.update({'context': experiment_dict['args']['context'],
                                'context_type': experiment_dict['args']['context_type']})

        return return_dict

    def processAnswer(self, butler, alg, args):
        query = butler.queries.get(uid=args['query_uid'])
        targets = query['target_indices']
        left_id = targets[0]['target']['target_id']
        right_id = targets[1]['target']['target_id']
        quicksort_data = query['quicksort_data']
        winner_id = args['target_winner']
        if query['alg_label'].startswith('Quicksort'):
            butler.other.increment(key='num_qs_reported_answers')
            num_reported_answers = butler.other.get(key='num_qs_reported_answers')
        elif query['alg_label'].startswith('Random'):
            butler.other.increment(key='num_random_reported_answers')
            num_reported_answers = butler.other.get(key='num_random_reported_answers')
        alg({'left_id': left_id, 'right_id': right_id, 'winner_id': winner_id,
             'quicksort_data': quicksort_data})

        if not query['alg_label'].startswith('TEST') and num_reported_answers % 5 == 0:
            # Note the alg_label here does nothing!
            butler.job('getModel', json.dumps({'exp_uid':butler.exp_uid,
                                               'args':{'error_plot':1, 'alg_label':'Random', 'logging':False}}))
        return {'winner_id': winner_id, 'quicksort_data': quicksort_data}

    def getModel(self, butler, alg, args):
        if args['error_plot']:
            # Mostly done just to make sure I have log_entry_durations....not necessary
            alg()
            return self.rankErrors(butler)
        else:
            ranks = alg()
            targets = []
            for index in range(len(ranks)):
                targets.append({'index': ranks[index],
                                'target': self.TargetManager.get_target_item(butler.exp_uid, ranks[index]),
                                'rank': index})
            return {'targets': targets}

    def rankErrors(self, butler):
        alg_list = butler.experiment.get()['args']['alg_list']
        active_set = butler.experiment.get()['args']['active_set']
        top_qs = max([int(x.split('_')[1]) for x in active_set])
        utils.debug_print('RANK ERRORS top_qs {}'.format(top_qs))
        qs_algs = filter(lambda x: x['alg_label'].startswith('QuicksortTree') and int(x['alg_label'].split('_')[1]) <= top_qs, alg_list)                
        random_alg = filter(lambda x: x['alg_label'].startswith('Random'), alg_list)[0]
        trees, pivots, queryqueues, wrs = [], [], [], []
        utils.debug_print('RANK ERRORS qs algs {}'.format(qs_algs))
        for qs in qs_algs:
            lock = butler.memory.lock('QSTreelock_{}'.format(qs['alg_label']))
            lock.acquire()
            alg_data = butler.algorithms.get(uid=qs['alg_label'])
            trees.append(alg_data['tree'])
            pivots.append(alg_data['pivot'])
            queryqueues.append(alg_data['queries'])
            wrs.append(alg_data['without_response'])
            lock.release()
        W_random = butler.algorithms.get(uid=random_alg['alg_label'])['W']
        W_holdout = numpy.load('holdout_queries.npy')
        qs_error = treeStats.getErrorsQS(trees, pivots, queryqueues, wrs, W_holdout)
        random_error = treeStats.getErrorsRandom(W_random, W_holdout)
        butler.log('ALG-EVALUATION', {'exp_uid': butler.exp_uid, 'task': 'rankErrors',
                                      'num_reported_answers': [butler.other.get(key='num_random_reported_answers'),
                                                               butler.other.get(key='num_qs_reported_answers')],
                                      'timestamp': str(utils.datetimeNow()),
                                      'errors': [random_error, qs_error]})
        return {'errors': [random_error, qs_error]}

    def chooseAlg(self, butler, alg_list, args, prop):
        random_alg = filter(lambda x: x['alg_label'] == 'Random', alg_list)[0]
        test_alg = filter(lambda x: x['alg_label'] == 'TEST', alg_list)[0]

        if numpy.random.rand() < 9/28.:
            return random_alg

        args = butler.experiment.get()['args']
        active_set = args['active_set']
        num_active = args['num_active']

        if butler.other.get(key='TEST_available') and numpy.random.rand() < 5./19:
            return test_alg

        for i, qs in enumerate(active_set):
            if not butler.other.get(key=qs+'_available'):
                del active_set[i]

        if not active_set:
            for a in alg_list:
                if (a['alg_label'].startswith('Quicksort') and
                    butler.other.get(key=a['alg_label']+'_available')):
                    active_set.append(a['alg_label'])
            active_set = sorted(active_set)
            if len(active_set) > num_active:
                active_set = active_set[:num_active]

        args['active_set'] = active_set
        butler.experiment.set(key='args', value=args)
        return {'alg_label':numpy.random.choice(active_set), 'alg_id':'QuicksortTree'}
