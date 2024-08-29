"""
INCOMPLETE
This script is the main pipeline for the target finding program. 
It allows the user to input dates manually or use a preset file to query the database for targets.
The results are written to a file for further analysis.
"""
from inputs import Input
from query import Query
import os
import numpy as np
import time
import datetime
import json
import sys
from tqdm import tqdm

class Pipeline:
    mag_lim = None
    dec_min = None
    dec_max = None
    limit = None
    input_mode = None

    def __init__(self, mag_lim=None, dec_min=None, dec_max=None, limit=None, input_mode=None):
        if mag_lim is None:
            self.mag_lim = 16
        if dec_min is None:
            self.dec_min = -20
        if dec_max is None:
            self.dec_max = 72
        if limit is None:
            self.limit = 1000
        if input_mode is None:
            self.input_mode = 0