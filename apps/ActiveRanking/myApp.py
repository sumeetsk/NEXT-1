# TODO:
# x change the algorithm definitions. Done for LilUCB only
# o explore the dashboard, see what you need to change
# ? modify the widgets?
import json
import numpy

import next.apps.SimpleTargetManager
import next.utils as utils
class myApp:
    def __init__(self,db):
        self.app_id = 'ActiveRanking'
        self.TargetManager = next.apps.SimpleTargetManager.SimpleTargetManager(db)

    def initExp(self, butler, init_algs, args):
        """
        This function is meant to store an additional components in the
        databse.

        In the implementation of two apps, DuelingBanditsPureExploration and
        PoolBasedTripletMDS, we only managed targets in this function. We
        stored the targets to the database than deleted the 'targets' key
        from args, replacing it with ``args['n']`` to
        represent a list of n targets. This is easier when doing numerical
        computation.

        Inputs
        ------
        exp_uid : The unique identifier to represent an experiment.
        args : The keys specified in the app specific YAML file in the
                   initExp section.
        butler : The wrapper for database writes. See next/apps/Butler.py for
                 more documentation.

        Returns
        -------
        args: The experiment data, potentially modified.
        """
        # TODO: change this in every app type coded thus far!
        if 'targetset' in args['targets'].keys():
            n = len(args['targets']['targetset'])
            self.TargetManager.set_targetset(butler.exp_uid, args['targets']['targetset'])
        else:
            n = args['targets']['n']
        args['n'] = n
        del args['targets']

        alg_data = {}
        algorithm_keys = ['n']
        for key in algorithm_keys:
            alg_data[key] = args[key]

        init_algs(alg_data)
        return args

    def getQuery(self, butler, alg, args):
        alg_response = alg({'participant_uid':args['participant_uid']})
        targets = [self.TargetManager.get_target_item(butler.exp_uid, alg_response[i])
                   for i in [0, 1]]

        targets_list = [{'target':targets[0],'label':'left'}, 
                        {'target':targets[1],'label':'right'}]


        #if targets[0]['target_id'] == targets[-1]['target_id']:
        #    targets_list[0]['flag'] = 1
        #    targets_list[1]['flag'] = 0
        #else:
        #    targets_list[0]['flag'] = 0
        #    targets_list[1]['flag'] = 1

        return_dict = {'target_indices':targets_list, 'quicksort_data': alg_response[2]}

        experiment_dict = butler.experiment.get()

        #if 'labels' in experiment_dict['args']['rating_scale']:
            #labels = experiment_dict['args']['rating_scale']['labels']
            #return_dict.update({'labels':labels})

        if 'context' in experiment_dict['args'] and 'context_type' in experiment_dict['args']:
            return_dict.update({'context':experiment_dict['args']['context'],'context_type':experiment_dict['args']['context_type']})

        return return_dict

    def processAnswer(self, butler, alg, args):
        query = butler.queries.get(uid=args['query_uid'])
        targets = query['target_indices']
        left_id = targets[0]['target']['target_id']
        right_id = targets[1]['target']['target_id']
        quicksort_data = query['quicksort_data']
        winner_id = args['target_winner']
        butler.experiment.increment(key='num_reported_answers_for_' + query['alg_label'])

        alg({'left_id':left_id, 
             'right_id':right_id, 
             'winner_id':winner_id,
             'quicksort_data':quicksort_data})
        return {'winner_id':winner_id, 'quicksort_data':quicksort_data}
                

    def getModel(self, butler, alg, args):
        scores, precisions = alg()
        ranks = (-numpy.array(scores)).argsort().tolist()
        n = len(scores)
        indexes = numpy.array(range(n))[ranks]
        scores = numpy.array(scores)[ranks]
        precisions = numpy.array(precisions)[ranks]
        ranks = range(n)

        targets = []
        for index in range(n):
          targets.append( {'index':indexes[index],
                           'target':self.TargetManager.get_target_item(butler.exp_uid, indexes[index]),
                           'rank':ranks[index],
                           'score':scores[index],
                           'precision':precisions[index]} )
        num_reported_answers = butler.experiment.get('num_reported_answers')
        return {'targets': targets, 'num_reported_answers':num_reported_answers} 

    def chooseAlg(self, butler, args, alg_list, prop):
        chosen_alg = numpy.random.choice(alg_list, p=prop)
        #utils.debug_print(chosen_alg)
        if chosen_alg['alg_id'] == 'ValidationSampling':
            l = butler.memory.lock('validation')
            l.acquire()
            if butler.other.get(key='VSqueryqueue') == []:
                prop = [p for p, a in zip(prop, alg_list) if a['alg_id'] != 'ValidationSampling']
                prop = [p/sum(prop) for p in prop]
                alg_list = [ai for ai in alg_list if ai['alg_id'] != 'ValidationSampling']
                chosen_alg = numpy.random.choice(alg_list, p=prop)
                #utils.debug_print('sumeet')
                #utils.debug_print([a['alg_id'] for a in alg_list])
                #utils.debug_print(prop)
                #utils.debug_print(chosen_alg)
            l.release()
        return chosen_alg


