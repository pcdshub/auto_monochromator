import logging 
import pandas as pd
import numpy as np
from auto_monochromator.rapid_stats import RapidHist
from collections import deque
logger = logging.getLogger(__name__)

def test_RapidHist_push():
    rh = RapidHist(
        maxlen = 5,
        minlen = 3,
        bins = list(range(5))
    )
    data = list(range(3))*10
    rh.push(data)
    assert np.all(rh.data == np.array([1,2,0,1,2]))


def test_RapidHist_hist():
    rh = RapidHist(
        maxlen = 5,
        minlen = 3,
        bins = list(range(5))
    )
    data = list(range(3))*10
    rh.push(data)
    hits, bins = rh.hist()
    print(hits,bins)
    assert np.all(hits == np.array([1,2,2,0]))
    assert np.all(bins == np.array(list(range(5))))
    

def test_RapidTransmissionHist_push():
    raise NotImplementedError

def test_RapidTransmissionHist_hist():
    raise NotImplementedError
