import csv
import json
import numpy as np
import matplotlib.pyplot as plt

from .CollectData import *
from .GraphData import *
from .PlotDict import *

class Plots():
    '''
    Attributes
    ----------
    datasets: 
        Dictionary associating id with raw data and conversion function
    graphs: Dict['data_id': str, 'data_key': str, 'obj': GraphData]
    '''
    def __init__(self, conf_file=None, freq=None):
        '''
        Parameters
        ----------
        conf_file: str
            name of json file with configuration 
            as list of dicts holding self.add_graph() arguments
        freq: int
            frequency of data collecting
            that will be passed to GraphData objects
        '''
        self.coll_func = {}
        self.logger = None
        self.req_fields = None

        self.graphs = []
        self.datasets = {}

        if conf_file is not None:
            with open(conf_file, 'r') as conf:
                settings = json.load(conf)
                for sett in settings:
                    sett['graph'] = PlotDict().graph[sett['graph']]
                    self.add_graph(**sett, freq=freq)

    def get_logger(self):
        '''
        Returns default logger collect function
        '''
        if self.logger is None:
            if self.req_fields is None and not self.coll_func:
                return None
            self.logger = CollectData(self.req_fields, self.coll_func)
        return self.logger.collect

    def add_graph(self, graph, data_id, data_key, window=0, freq=None, save=False,
            intrv_func='lin', intrv_num=10, color=None, title=None):
        '''
        Creates and initializes new GraphData obj

        Parameters
        ----------
        graph: GraphData
            graph type
        data_id:
            id of required dataset
        data_key:
            dict key of needed data from dataset
        window:
            window on which plot shoud be shown
        args for GraphData
        title:
            title of graph
        '''
        if PlotDict().coll.get(data_key, None) is not None:
            if self.coll_func.get(data_key, None) is None:
                self.coll_func[data_key] = PlotDict().coll[data_key]
        if title is None:
            title = f'{data_id} {data_key} 1/{freq} {intrv_func}{intrv_num}'
        if self.req_fields is None:
            self.req_fields = {data_key}
        else:
            self.req_fields.add(data_key)
        while len(self.graphs) <= window:
            self.graphs.append([])

        self.graphs[window].append({'id': data_id, 'key': data_key, 'csv': save,
            'obj': graph(freq, PlotDict().intrv[intrv_func], intrv_num, color), 'title': title})

    def add_data(self, data_id, text, new_data=None):
        '''
        Stores dataset or concatenate if already exist
        if 'new_data' is None get data from default logger

        Parameters
        ----------
        data_id:
            id that identifies dataset to which new_data will be added
        text: 
            text describing area in case of data merge
        new_data:
            new dataset to store
        '''
        if new_data is None:
            if self.logger is not None:
                data = self.logger.get_data()
                if len(data) > 0:
                    self.add_data(data_id, data, text)
        else:
            if self.datasets.get(data_id, None) is None:
                self.datasets[data_id] = {'data': new_data, 'con': [0], 'text': [text]}
            else:
                self.datasets[data_id]['con'].append(
                        len(self.datasets[data_id]['data']) )
                self.datasets[data_id]['text'].append(text)
                self.datasets[data_id]['data'].extend(new_data)

    def _save_plot_data(self, name, data):
        name += '.csv'
        with open(name, mode='w') as f:
            writer = csv.writer(f)
            for row in data:
                writer.writerow(row)

    def save_datasets(self, filename):
#       print(self.datasets)
        return

    def draw(self):
        '''
        Plots graphs
        '''
        for graphs in self.graphs:
            fig, axs = plt.subplots(len(graphs),1)
            if len(graphs) < 2:
                axs = [axs]
            for ax, graph in zip(axs, graphs):
                graph['obj'].set_data(
                        self._extract(self.datasets[graph['id']]['data'], graph['key']),
                        self.datasets[graph['id']]['con'],
                        self.datasets[graph['id']]['text'])
                graph['obj'].plot(ax, graph['title'])
                if graph['csv']:
                    self._save_plot_data(graph['title'], graph['obj'].dataset)
            plt.tight_layout()

        plt.show()

    def _extract(self, data, key):
        '''
        Extracts choosen field from given dataset

        Parameters
        ----------
        data:
            dataset
        key:
            key of needed field

        Returns
        ----------
        new_data:
            dataset containing onlu choosen data from original dataset
        '''
        new_data = []
        for step in data:
            new_data.append(step[key])
        return new_data
        
