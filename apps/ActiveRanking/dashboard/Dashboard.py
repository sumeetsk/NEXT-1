import json
import next.utils as utils
from next.apps.AppDashboard import AppDashboard


class MyAppDashboard(AppDashboard):

    def __init__(self, db, ell):
        AppDashboard.__init__(self, db, ell)

    def current_queues(self, app, butler):
        alg_list = butler.experiment.get(key='args')['alg_list']
        stats_data = {'headers': [{'label': 'Alg Label', 'field': 'alg_label'},
                                  {'label': 'Available', 'field': 'available'},
                                  {'label': 'Query Queue Length', 'field': 'queries'},
                                  {'label': 'Queries Outstanding', 'field': 'without_response'}],
                      'plot_type': 'columnar_table',
                      'data':[]}
        plot_data = []
        # build plot_data and stats_data each alg at a time
        for alg in alg_list:
            if alg['alg_id'].startswith('Quicksort'):
                logs, _, _ = butler.ell.get_logs_with_filter(butler.app_id+':ALG-EVALUATION',
                                                             {'exp_uid': butler.exp_uid,
                                                              'alg_label': alg['alg_label']})
                logs = sorted(logs, key=lambda item: utils.str2datetime(item['timestamp']) )
                if logs:
                    plot_data.append({'legend_label': alg['alg_label'],
                                      'x':range(len(logs)), 'y': [len(l['queries']) for l in logs]})
                last = logs[-1]
                stats_data['data'].append({'alg_label': alg['alg_label'],
                                           'available': last['available'],
                                           'queries': len(last['queries']),
                                           'without_response': len(last['without_response'])})
            elif alg['alg_label'] == 'TEST':
                logs, _, _ = butler.ell.get_logs_with_filter(butler.app_id+':ALG-EVALUATION',
                                                             {'exp_uid': butler.exp_uid,
                                                              'alg_label': alg['alg_label']})
                logs = sorted(logs, key=lambda item: utils.str2datetime(item['timestamp']) )
                last = logs[-1]
                answered = sum([i[2] for i in last['querylist']])
                stats_data['data'].append({'alg_label': alg['alg_label'],
                                           'available': last['available'],
                                           'queries': '{} answered'.format(answered),
                                           'without_response': '{} left'.format(3*len(last['querylist'])-answered)})
        plot = self.build_plot(plot_data, 'Number of asked queries', 'Size of query queue', 'Query Queue Sizes')
        # Get error plot data
        logs, _, _ = butler.ell.get_logs_with_filter(butler.app_id+':ALG-EVALUATION',
                                                     {'exp_uid': butler.exp_uid,
                                                      'task': 'rankErrors'})
        logs = sorted(logs, key=lambda item: utils.str2datetime(item['timestamp']))
        error_plot_data =[ {'legend_label': 'Random',
                       'x': [l['num_reported_answers'] for l in logs],
                       'y': [l['errors'][0] for l in logs]},
                      {'legend_label': 'Aggregated Quicksorts',
                       'x': [l['num_reported_answers'] for l in logs],
                       'y': [l['errors'][1] for l in logs]}]
        error_plot = self.build_plot(error_plot_data, 'Number of asked queries', 'Test Error', 'Test Error on Holdout')
        # info about validation_status and active_set
        active_set = butler.experiment.get()['args']['active_set']
        validation_status = butler.other.get(key='TEST_available')
        return {'stats_data': stats_data, 'plot': plot, 'active_set':active_set, 'error_plot':error_plot}


    def build_plot(self, plot_data, xlabel, ylabel, title):
        import matplotlib.pyplot as plt
        import mpld3
        fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
        for alg in plot_data:
            ax.plot(alg['x'], alg['y'], label=alg['legend_label'])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(color='white', linestyle='solid')
        ax.set_title(title, size=14)
        legend = ax.legend(loc=2, ncol=3, mode="expand")
        for label in legend.get_texts():
            label.set_fontsize('small')
        plot = mpld3.fig_to_dict(fig)
        plt.close()
        return plot

    def most_current_ranking(self, app, butler, alg_label):
        item = app.getModel(json.dumps({'exp_uid': app.exp_uid, 'args': {'error_plot':0,'alg_label': alg_label}}))

        targets = item['targets']
        #targets = sorted(targets, key=lambda x: x['rank'])
        return_dict = {}
        return_dict['headers'] = [{'label': 'Target', 'field': 'index'}, {
            'label': 'Rank', 'field': 'rank'}]
        return_dict['data'] = item['targets']
        return_dict['plot_type'] = 'columnar_table'
        return return_dict


    
