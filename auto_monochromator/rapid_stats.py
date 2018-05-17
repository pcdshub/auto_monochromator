import numpy as np
from collections import deque


class BaseHist:
    def push(self):
        raise NotImplementedError

    def hist(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @data.setter
    def data(self):
        raise NotImplementedError


class RapidHist(BaseHist):
    """
    Wrapper on np.histogram for rapidly regenerating histograms of dynamic data
    """
    def __init__(self, maxlen, minlen=None, bins=None):
        """
        Parameters
        ----------
        maxlen : int
            Maximum number of data points for hist.

        minlen : int or None
            Minimum number of data points for hist. Causes error to be thrown.

        bins : int, iterable or None
            Set up default bins for the hist following np.histogram rules for
            'bins' argument.
        """
        self._data = deque(maxlen=maxlen)
        if bins == None:
            self.bins = 10
        else:
            self.bins = bins
        self.minlen = minlen

    def push(self, data):
        """
        Parameters
        ----------
        data : float, int or iterable
            Append these elements to the data for this hist.
        """
        try:
            self._data.extend(data)
        except TypeError:
            self._data.append(data)

    def hist(self, bins=None, density=False):
        """
        Parameters
        ---------
        bins : int, iterable or None
            Force binning on this hist. Defaults to binning set at class
            instantiation if this is left as None. Argument follows
            np.histogram's rules for 'bins' argument.

        density : bool
            Follows np.histogram's rules for 'density' argument.
        """
        if bins is None:
            bins = self.bins
        if self.minlen is not None:
            if len(self._data) < self.minlen:
                raise Exception("Insufficient data")
        return np.histogram(self._data, bins=bins, density=density)

    @property
    def data(self):
        return np.array(self._data)


class RapidWeightHist(RapidHist):
    def __init__(self, maxlen, minlen=None, bins=None):
        super().__init__(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins,
        )
        self._weights = deque(maxlen=maxlen)

    def push(self, data, weights):
        try:
            if len(data) is not len(weights):
                raise Exception("Data, weights lengths differ")
        except TypeError:
            pass
        super().push(data)
        try:
            self._weights.extend(weights)
        except TypeError:
            self._weights.append(weights)

    @property
    def weights(self):
        return np.array(self._weights)

    def hist(self, bins=None, density=False):
        if bins is None:
            bins = self.bins
        if self.minlen is not None:
            if len(self._data) < self.minlen:
                raise Exception("Insufficient data")
        return np.histogram(
            self._data, 
            weights=self._weights,
            bins=bins, 
            density=density
        )


class RapidTransmissionHist(BaseHist):
    def __init__(self, maxlen, minlen=None, bins=None):
        """
        Parameters
        ----------
        maxlen : int
            Maximum number of data points for hist.

        minlen : int or None
            Minimum number of data points for hist. Causes error to be thrown.

        bins : int, iterable or None
            Set up default bins for the hist following np.histogram rules for
            'bins' argument.
        """
        self._data = deque(maxlen=maxlen)
        if bins is None:
            self.bins = 10
        else:
            self.bins = bins
        self.minlen = minlen

        # Abbreviation for incedent energy
        self.inc_hist = RapidHist(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins
        )

        self.outgoing_hist = RapidWeightHist(
            maxlen=maxlen,
            minlen=minlen,
            bins=bins
        )
    
    def push(self, data, weights):
        """
        Parameters
        ----------
        data : float, int or iterable
            Append these elements to the data for this hist. Must have the same
            length as weights.
        
        weights : float, int or iterable
            Append these elements to the weights for this hist. Must have the
            same length as data.
        """
        self.inc_hist.push(data)
        self.outgoing_hist.push(data,weights)

    @property
    def data(self):
        return self.inc_hist.data

    @property
    def weights(self):
        return self.outgoing_hist.weights

    def hist(self, bins=None, density=False):
        if bins == None:
            bins = self.bins
        if self.minlen is not None:
            if len(self.inc_hist._data) < self.minlen:
                raise Exception("Insufficient data")

        inc, bins = self.inc_hist.hist(bins=bins, density=density)
        outgoing, _ = self.outgoing_hist.hist(bins=bins, density=density)
        with np.errstate(divide='ignore',invalid='ignore'):
            fractional_yield = np.nan_to_num(outgoing / inc)
            #fractional_yield = outgoing / inc
    
        return inc, outgoing, fractional_yield, bins
        

        


