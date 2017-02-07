import json
import numpy

import next.apps.SimpleTargetManager
import next.utils as utils


class MyApp:

    def __init__(self, db):
        self.app_id = 'ActiveRanking'
        self.TargetManager = next.apps.SimpleTargetManager.SimpleTargetManager(
            db)

    def initExp(self, butler, init_algs, args):
        utils.debug_print('initExp num_active:{},  alg_list:{}'.format(args['num_active'], len(args['alg_list'])))
        utils.debug_print('initExp args:{}'.format(args)) 
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
        utils.debug_print('exiting')
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
        butler.experiment.increment(key='num_reported_answers_for_' + query['alg_label'])
        alg({'left_id': left_id, 'right_id': right_id, 'winner_id': winner_id,
             'quicksort_data': quicksort_data})
        return {'winner_id': winner_id, 'quicksort_data': quicksort_data}

    def getModel(self, butler, alg, args):
        ranks = alg()
        targets = []
        for index in range(len(ranks)):
            targets.append({'index': ranks[index],
                            'target': self.TargetManager.get_target_item(butler.exp_uid, ranks[index]),
                            'rank': index})
        num_reported_answers = butler.experiment.get('num_reported_answers')
        return {'targets': targets, 'num_reported_answers': num_reported_answers}
    
    def chooseAlg(self, butler, alg_list, args, prop):
        random_alg = filter(lambda x: x['alg_label'] == 'Random', alg_list)[0]
        test_alg = filter(lambda x: x['alg_label'] == 'TEST', alg_list)[0]

        if numpy.random.rand() < 9/28.:
            return random_alg

        args = butler.experiment.get()['args']
        active_set = args['active_set']
        num_active = args['num_active']

        utils.debug_print('num_active {}'.format(num_active))
        utils.debug_print('active_set {}'.format(active_set))
        utils.debug_print('TEST status {}'.format(butler.other.get(key='TEST_available')))
        if butler.other.get(key='TEST_available') and numpy.random.rand() < 5./19:
            return test_alg

        for i, qs in enumerate(active_set):
            utils.debug_print('qs {} {}'.format(qs, butler.other.get(key=qs+'_available')))
            if not butler.other.get(key=qs+'_available'):
                del active_set[i]
        utils.debug_print('active_set trimmed {}'.format(active_set))        

        if not active_set:
            for a in alg_list:
                if (a['alg_label'].startswith('Quicksort') and
                    butler.other.get(key=a['alg_label']+'_available')):
                    active_set.append(a['alg_label'])
            active_set = sorted(active_set)
            if len(active_set) > num_active:
                active_set = active_set[:num_active]
        utils.debug_print('active_set updated {}'.format(active_set))
        args['active_set'] = active_set
        butler.experiment.set(key='args', value=args)
        return {'alg_label':numpy.random.choice(active_set), 'alg_id':'QuicksortTree'}
        
        # if chosen_alg['alg_id'] == 'ValidationSampling':
        #     l = butler.memory.lock('validation')
        #     l.acquire()
        #     if butler.other.get(key='VSqueryqueue') == []:
        #         prop = [p for p, a in zip(prop, alg_list) if a['alg_id'] != 'ValidationSampling']
        #         prop = [p / sum(prop) for p in prop]
        #         alg_list = [ai for ai in alg_list if ai['alg_id'] != 'ValidationSampling']
        #         chosen_alg = numpy.random.choice(alg_list, p=prop)
        #     l.release()
