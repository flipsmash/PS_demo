# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 19:09:06 2024
@author: brian_local
"""

import pandas as pd
import numpy as np


# Import original data
df = pd.read_excel('original_data/data.xlsx', sheet_name = 0)

# Diagnose issues with original question scores
scores_desc_before = df.iloc[:, 1:15].describe().round(2)
df['score-calc']= df.iloc[:, 1:15].sum(axis=1)
df['diff(calc-static)'] = df['score-calc'] - df['score']
df['cand_id'] = df['cand_id'].astype('category')

#Fix issues with Q1 & Q14
# scores are off by 120 in 50 cases due to q1 = 10, should be 0 and q14=120, should be 10
df['q1-score'] = np.where(df['q1-score']==10, 0, df['q1-score'])
df['q14-score'] = np.where(df['q14-score']==120, 10, df['q14-score'])

# Verify apparent fix
df['total-calc-after']= df.iloc[:, 1:15].sum(axis=1)
df['diff(calc-static after)'] = df['total-calc-after'] - df['score']
scores_desc_after = df.iloc[:, 1:15].describe().round(2)

# Remove test_fields from above
df = df.iloc[:,0:-4]

# Add Score Pct & Pass/Fail -  assume round to highest int pct, 92% passes
df['score_pct'] = (df['score']/df['max_score']).round(2)
df['pass'] = np.where(df['score_pct']>=.92, 1, 0)

# Save corrected data to file
df.to_csv('clean_master_data.csv')

# create question-level data csv file
# To Do: add ply for quest - tag mapping
cols = [i for r in (range(0, 15), range(39, 144)) for i in r] + [16]
df_quest = df.iloc[:, cols]
df_quest.to_csv('clean_question_data.csv')


# create test-level data csv file
cols = [i for s in (range(15,31), range(144, 155)) for i in s]
df_test = df.iloc[:, cols]
df_test.to_csv('clean_test_data.csv')



#####################
## Item Analysis   ##
#####################

## Difficulty ##
df_scores = df.iloc[:, 1:15]
agg = df_scores.agg('sum')/df_scores.agg('count')
agg[1:14] = agg[1:14]/10

## Add Overall Mean
agg['total-score'] = agg.values.mean()
df_agg = agg.round(4).to_frame(name="Mean")
df_agg['rank'] = agg.rank()

## Discrimination ##
## subtracting the item under investigation from the total score for each item:
df_totals = df.iloc[:, 15].to_frame()
df_adj_correl_tota1s = abs(df_scores.sub(df_totals['score'], axis=0))

corrected_item_total_correlations = df_scores.corrwith(df_adj_correl_tota1s)

## To Do - Deal with NaNs in Q1, which may be lowering results



## Tags ##
df_tags = pd.read_excel('original_data/data.xlsx', sheet_name = 1)
df_agg.index = df_agg.index.str.split('-').str[0]
df_agg = df_agg["Mean"]
df_agg.drop('total', inplace=True)

## Join questions to tags ##
df_tags.set_index('Qnum', inplace = True)
df_tags.index.equals(agg.index)
df_tags["question"] = df_agg
grouped_data = df_tags.groupby(['Tag'])

## Create score data aggregated by tag
## To Do:  Add correl to this aggregation
agg_data = grouped_data['question'].agg(['mean', 'count'])



