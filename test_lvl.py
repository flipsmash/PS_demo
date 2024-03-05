# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 11:34:56 2024

@author: brian_local
"""

import pandas as pd
import numpy as np

df = pd.read_csv('clean_data.csv')

# Adjust for test-level rows
# 
#cols = [i for r in (range(1,16), range(40,80), range(117-145)) for i in r]
#df = df.iloc[:, cols]