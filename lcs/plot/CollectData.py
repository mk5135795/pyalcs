class CollectData():
    def __init__(self, attrs, dfunc):
        '''
        Parameters
        ----------
        data_id:
            id of dataset
        attrs: List
            list of population attributes to record
        dfunc:
            dictionary containing additional functions analyzing clasifiers
            and putting them under theirs key
        '''
        if dfunc is not None:
            for key in dfunc.keys():
                attrs.discard(key)
        self.attrs = set(attrs)
        self.dataset = []
        self.dfunc = dfunc

    def get_data(self):
        tmp = self.dataset
        self.dataset = []
        return tmp

    def clear(self):
        self.dataset = []

    def collect(self, population, enviroment):
        '''
        Collects values of selected fields
        from population for later processing

        Parameters
        ----------
        population
        enviroment

        Returns
        ----------
        pop_data: dict
            data collected from current population
        '''
        val = {}
        if self.dfunc is not None:
            for fkey, func in zip(self.dfunc.keys(), self.dfunc.values()):
                val[fkey] = []
                for cl in population:
                    val[fkey].append(func(cl))
                val[fkey].sort()

        for attr in self.attrs:
            val[attr] = []
            for cl in population:
                val[attr].append(getattr(cl, attr))
            val[attr].sort()
        self.dataset.append(val)

        return val

        
