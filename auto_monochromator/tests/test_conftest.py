import logging 
import pandas as pd
import numpy as np
import auto_monochromator
logger = logging.getLogger(__name__)


def test_sxrR6_dataFrame(sxrR6_dataFrame):
    assert 3.9178448795299 == sxrR6_dataFrame['weightings_group']['weightings'][0,0]
    assert 660.8423229505113 == sxrR6_dataFrame['photon_energy_group']['photon_energy'][0]
