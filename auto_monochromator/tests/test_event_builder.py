import logging 
import pandas as pd
import numpy as np
from auto_monochromator.rapid_stats import (RapidHist, RapidWeightHist,
    RapidTransmissionHist)
from collections import deque
logger = logging.getLogger(__name__)

