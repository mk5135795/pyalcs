import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.colors as mcl
import matplotlib.lines as lines
import matplotlib.text as text

class GraphData():
    '''
    Attributes
    ----------
    min: int
        lowest value across whole dataset
    max: int
        highest value across whole dataset
    freq: int
        frequency of collected data
        if freq = None hide x axis
    intrv_num: int
        number of intervals
    style: str
        cmap - matplotlib colorset
    '''
    def __init__(self, freq, intrv_func, intrv_num, style):
        '''
        Parameters
        ----------
        intrv_func: Callable
            function generating intervals
        '''
        self.dataset = None
        self.intrv_func = intrv_func
        self.intrv_num = intrv_num
        self.freq = freq
        self.style = style

    def set_data(self, data, con, text):
        '''
        Process and sets data

        Parameters
        ----------
        data: list
            unprocessed dataset
        con:
            list describing dataset merge points
        text:
            list of str describing merged areas
        '''
        raise NotImplementedError()

    def plot(self, ax, title):
        '''
        Plot data on given axis

        Parameters
        ----------
        ax: matplotlib.axes.Axes
            axis on which data will be drawn
        title:
            title of graph
        '''
        if self.freq is None:
            scale = 1
            ax.get_xaxis().set_visible(False)
        else:
            scale = self.freq
        
        self._plot(ax, scale)
        
        height = ax.get_ylim()
        if len(self.con) > 1:
            for txt, cn in zip(self.text, self.con):
                l = lines.Line2D([cn*scale]*2, height, lw=1, color='black', axes=ax)
                t = text.Text(cn*scale+2, height[1], txt, axes=ax,
                        horizontalalignment='left', verticalalignment='top')
                ax.add_line(l)
                ax.add_artist(t)

        ax.set_title(title)

    def _plot(self, ax, scale):
        raise NotImplementedError()

    def _min_max(self, data):
        '''
        Find min and max values of given dataset

        Parameters
        ----------
        data:
            data set for analyze
        '''
        self.min = data[0][0]
        self.max = data[0][-1]
        for d in data:
            if d[0] < self.min:
                self.min = d[0]
            if d[-1] > self.max:
                self.max = d[-1]


class StackedGraph(GraphData):
    def set_data(self, data, con, text):
        '''
        counts how many classifiers have (choosen value)
        in range of each of interval
        '''
        self.con = con
        self.text = text
        self._min_max(data)
        self.intervals = self.intrv_func(self.min, self.max, self.intrv_num)

        self.intervals[-1] += 1
        self.dataset = []
        for j in range(self.intrv_num):
            self.dataset.append([])
        for i, step in enumerate(data):
            intrv_i = 0
            for j in range(self.intrv_num):
                self.dataset[j].append(0)
            for cl in step:
                while True:
                    if cl <= self.intervals[intrv_i]:
                        break
                    else:
                        intrv_i += 1
                self.dataset[intrv_i][i] += 1
        self.intervals[-1] -= 1

    def _plot(self, ax, scale):

        class Normalize(mcl.Normalize):
            def __init__(self, data):
                super(Normalize, self).__init__(data[0], data[-1])
                self.f = interp1d(data, np.linspace(0, 1, len(data)))

            def __call__(self, value, clip=None):
                return np.ma.masked_array(self.f(np.array(value)))

        class Colmap(mcl.LinearSegmentedColormap):
            def __init__(self, cmap, data):
                self.cmap = cmap
                self.N = cmap.N
                self.monochrome = cmap.monochrome
                self.f = interp1d(data/data[-1], np.linspace(0, 1, len(data)))

            def __call__(self, val, alpha=1, **kw):
                return self.cmap(np.ma.masked_array(self.f(np.array(val))), alpha)

        if self.style is None:
            self.style = 'rainbow'
        
        interp = Normalize(self.intervals)
        colors = plt.get_cmap(self.style, len(self.intervals))
        col_map = Colmap(colors, self.intervals)
        
        ax.stackplot(np.arange(0, len(self.dataset[0])*scale, scale), self.dataset, 
                colors=colors(np.linspace(0, 1, self.intrv_num)))

        cbar = plt.cm.ScalarMappable(cmap=col_map, norm=interp)
        if len(self.intervals) <= 10:
            pcbar = plt.colorbar(cbar, ax=ax, ticks=np.linspace(self.intervals[-1], self.intervals[0], len(self.intervals)) )
            pcbar.ax.set_yticklabels(np.around(np.flipud(self.intervals), 2))
        else:
            pcbar = plt.colorbar(cbar, ax=ax, ticks=[self.intervals[-1], self.intervals[0]])
            norm = self.intervals/self.intervals[-1]
            pcbar.ax.yaxis.set_ticks(np.linspace(norm[-1], norm[0], len(norm)), minor=True)


class LineRangeGraph(GraphData):
    def set_data(self, data, con, text):
        self.con = con
        self.text = text
       
        self._min_max(data)
       
        self.intervals = self.intrv_func(self.min, self.max, self.intrv_num)
        self.intervals[-1] += 1

        self.dataset = [[], [], [], []]
        for step in data:
            self.dataset[0].append(step[0])
            self.dataset[1].append(step[-1])
            self.dataset[2].append(np.mean(step))
#           self.dataset[3].append(np.median(step))

    def _plot(self, ax, scale):
        x = np.arange(0, len(self.dataset[0])*scale, scale)
        if self.style is None:
            self.style = [(0, ()), (0, (1, 1)), (0, (5, 1))]#, (0, (5, 1, 1, 1))]
        
        ax.plot(x, self.dataset[0], linestyle=self.style[0], label='min')
        ax.plot(x, self.dataset[1], linestyle=self.style[1], label='max')
        ax.plot(x, self.dataset[2], linestyle=self.style[2], label='avg')
#       ax.plot(x, self.dataset[3], linestyle=self.style[3], label='med')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper right', borderaxespad=0.)
        ax.legend()


