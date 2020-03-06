import numpy as np
from .GraphData import *

def intrv_log(min_val, max_val, num):
    if min_val <= 0:
        min_val = 0.1
    return np.geomspace(min_val, max_val, num)


class PlotDict():
    __instance = None
    __slots__ = ['intrv', 'coll', 'graph']

    def __new__(cls):
        if PlotDict.__instance is None:
            PlotDict.__instance = object.__new__(cls)
            PlotDict.__instance.intrv = {
                    'lin': np.linspace,
                    'log': intrv_log}
            PlotDict.__instance.coll = {
                    'rel': lambda cl: cl.is_reliable(),
                    'mark': lambda cl: cl.is_marked()}
            PlotDict.__instance.graph = {
                    'stacked': StackedGraph,
                    'linerange': LineRangeGraph}
        return PlotDict.__instance
