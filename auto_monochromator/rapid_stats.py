import numpy as np
from collections import deque

class RapidHist:
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
        self.bins = bins
        self.minlen = minlen

    def push(self, data):
        """
        Parameters
        ----------
        data : float, int or iterable
            Append these elements to the data for this hist.
        """
        if type(data) is list:
            self._data.extend(data)
        else:
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
        if bins == None:
            bins = self.bins
        if self.minlen is not None:
            if len(self._data) < self.minlen:
                raise Exception("Insufficient data")
        return np.histogram(self._data, bins=bins, density=density)

    @property
    def data(self):
        return np.array(self._data)
