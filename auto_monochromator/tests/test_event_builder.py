import logging 
import pandas as pd
import numpy as np
from auto_monochromator.rapid_stats import (RapidHist, RapidWeightHist,
    RapidTransmissionHist)
from auto_monochromator.event_builder import basic_event_builder
from collections import deque
logger = logging.getLogger(__name__)



def test_simple_event_builder():
    # missing 1,8
    at = [1,2,3]
    ad = [1,2,3]
    # missing 1,3,7,9
    bt = [1,2,4]
    bd = [1,2,4]
    series_a = pd.Series(ad,index=at)
    series_b = pd.Series(bd,index=bt)
    result = basic_event_builder(series_a, second=series_b)
    target = pd.DataFrame(
        {
            0: [1,2],
            'second': [1,2]
        },
        index = [1,2]
    )
    print(target)
    a_result = result[0] == target[0]
    b_result = result['second'] == target['second']
    index_result = result.index == target.index
    col_result = result.columns == target.columns
    assert a_result.all()
    assert b_result.all()
    assert index_result.all()
    assert col_result.all()

