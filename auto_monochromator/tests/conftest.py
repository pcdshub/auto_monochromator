import logging 
import pandas as pd
import numpy as np
import pytest
import h5py
import os
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def sxrR6_dataFrame():
    directory = os.path.dirname(os.path.realpath(__file__))
    test_file_path = os.path.join(directory, "sxrx30116run6_slim.h5") 
    file = h5py.File(test_file_path)
    return file



