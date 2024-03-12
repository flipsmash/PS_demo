# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 19:09:06 2024
@author: brian_local
"""
import pandas as pd
import numpy as np
import re
from scipy.stats import mannwhitneyu
import statsmodels.api as sm

# Import original Excel-cleaned data
df_main = pd.read_excel('original_data/data.xlsx', sheet_name = 0)
df_tags = pd.read_excel('original_data/data.xlsx', sheet_name = 1)

# Add calculated cols incl Pass/Fail -  assume round to highest int pct, 92% passes
df_main['score'] = df_main.loc[:,'q01-score':'q14-score'].sum(axis=1)
df_main['score_pct'] = (df_main['score']/df_main['max_score']).round(2)
df_main['total_q_time'] = df_main.loc[:,'q01-time':'q14-time'].sum(axis=1)
df_main['score_pass_bool'] = np.where(df_main['score_pct']>=.92, 1, 0)
df_main['copy_paste_bool'] = np.where(df_main['copy_paste_ct']>0, 1, 0)

# Identify columns that include string 'time' and convert to hours for easier reading, analysis
time_columns = df_main.filter(like='time').columns
df_main[time_columns] = df_main[time_columns] / 3600  # duration easier in hours

# Maybe time of data is credible even if date isn't?
df_main['attempt_time_of_day'] = df_main['attempt_start_dt'].dt.time

# Divide data into 3 frames: all data, one for test-level, one for quest-level
pattern = re.compile(r'^q\d+')
test_columns = [col for col in df_main.columns if not pattern.match(col)]
quest_columns  = [col for col in df_main.columns if pattern.match(col)]

df_main.to_csv('clean_main_data.csv')
df_test = df_main[test_columns]
df_test.to_csv('clean_test_only_data.csv')

# Removing Q1 from further analysis
df_quest = df_main[quest_columns].iloc[:,1:].copy()
df_quest['id'] = df_main['cand_id']
df_quest.to_csv('clean_quest_only_data.csv')


## Making long forms of all q data and then assembling for a transposed 
## id, question per row with question vars in columns
## To Do: Does this actually accomplish anything?

score_columns = [col for col in df_quest.columns if 'score' in col]
time_columns = [col for col in df_quest.columns if 'time' in col]
loc_columns = [col for col in df_quest.columns if 'loc' in col]
compile_columns = [col for col in df_quest.columns if 'compile' in col]

df_scores = df_quest[score_columns].copy()
df_times = df_quest[time_columns].copy()
df_locs = df_quest[loc_columns].copy()
df_compiles = df_quest[compile_columns].copy()

df_scores['id'] = df_quest['id']
df_times['id'] = df_quest['id']
df_locs['id'] = df_quest['id']
df_compiles['id'] = df_quest['id']

df_scores_melted = pd.melt(df_scores, id_vars=['id'], var_name='question', value_name='score')
df_times_melted = pd.melt(df_times, id_vars=['id'], var_name='question', value_name='time')
df_locs_melted = pd.melt(df_locs, id_vars=['id'], var_name='question', value_name='loc')
df_compiles_melted = pd.melt(df_compiles, id_vars=['id'], var_name='question', value_name='compile&test_ct')

df_scores_melted['question'] = df_scores_melted['question'].str.replace('-score', '')
df_times_melted['question'] = df_times_melted['question'].str.replace('-time', '')
df_locs_melted['question'] = df_locs_melted['question'].str.replace('-loc', '')
df_compiles_melted['question'] = df_compiles_melted['question'].str.replace('-compile&test_ct', '')


df_long1 = pd.merge(df_scores_melted, df_times_melted, on=['id', 'question'])
df_long2 = pd.merge(df_locs_melted, df_compiles_melted, on=['id', 'question'])
df_long = pd.merge(df_long1, df_long2, on=['id', 'question'])
df_long_w_tags = pd.merge(df_long, df_tags, left_on = "question", right_on = "Qnum", how = "inner")
df_long.to_csv('clean_quest_long_data.csv')
df_long_w_tags.to_csv('clean_quest_w_tags_long_data.csv')




#########################
## Copy Paste Analysis ##
#########################

## Copying as a category - t-test
group1 = df_main[df_main['copy_paste_bool'] == 1]['score']
group2 = df_main[df_main['copy_paste_bool'] == 0]['score']

mean_group1 = group1.mean()
mean_group2 = group2.mean()

# Conducting the Mann-Whitney U test
# Set alpha = 0.05 - typical alpha value for statistical significance
stat, p_value = mannwhitneyu(group1, group2, alternative='greater')
print(f'Mann-Whitney U Test Statistic: {stat}, P-value: {p_value}')

## Copy as a count - simple linear regression
x = sm.add_constant(df_main['copy_paste_ct'])
y = df_main['score']

model = sm.OLS(y, x).fit()

# Print the summary of the regression
print(model.summary())


# Add 2nd indep. var, time out of window
x2 = df_main[['copy_paste_ct', 'window_exit_ct']]

# It's important to add a constant term for the intercept
x2 = sm.add_constant(x2)

# Fit the model
model = sm.OLS(y, x2).fit()

# #####################
# ## Item Analysis - See R beyond basics   ##
# #####################

# ## Difficulty ##
# df_scores.drop('id', axis=1, inplace=True)
# agg = df_scores.agg('sum')/df_scores.agg('count')
# agg[1:14] = agg[1:14]/10

# ## Add Overall Mean
# #agg.drop('id', inplace=True)
# agg['total-score'] = agg.values.mean()
# df_agg = agg.round(4).to_frame(name="Mean")
# df_agg['rank'] = agg.rank()

# ## Discrimination ##
# ## subtracting the item under investigation from the total score for each item:
# df_totals = df_main.loc[:, 'score'].to_frame()
# df_adj_correl_tota1s = abs(df_scores.sub(df_totals['score'], axis=0))

# corrected_item_total_correlations = df_scores.corrwith(df_adj_correl_tota1s, method = 'kendall')

# ## To Do - Deal with NaNs in Q1, which may be lowering results



# # ## Tags ##
# # df_tags = pd.read_excel('original_data/data.xlsx', sheet_name = 1)
# # df_agg.index = df_agg.index.str.split('-').str[0]
# # df_agg = df_agg["Mean"]
# # df_agg.drop('total', inplace=True)

# # ## Join questions to tags ##
# # df_tags.set_index('Qnum', inplace = True)
# # df_tags.index.equals(agg.index)
# # df_tags["question"] = df_agg
# # grouped_data = df_tags.groupby(['Tag'])

# # ## Create score data aggregated by tag
# # ## To Do:  Add correl to this aggregation
# # agg_data = grouped_data['question'].agg(['mean', 'count'])






