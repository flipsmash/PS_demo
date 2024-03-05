# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 09:43:55 2024

@author: brian_local
"""
import pandas as pd
import numpy as np

df_tags = pd.read_excel('data.xlsx', sheet_name = 1)
df = pd.read_csv('clean_data.csv')

cols = [i for r in (range(1,16), range(40,80), range(117-145)) for i in r]
df = df.iloc[:, cols]
