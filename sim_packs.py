# %% libraries
import pandas as pd
import json
import datetime
import sys
import fun
from statistics import mean
import tqdm

back_url = 'https://customcards.s3.us-east-2.amazonaws.com/card_back.jpg'

#%% setup
type = 'packs'
df = fun.parse_sheet(type)
pack_size = 12
num_packs=16
threshold=1.1

sim_count = 50 # number of times to run simulation
pack_stddevs = []
no_algo_stddevs = []

# %% run simulation for pack algorithm
for c in tqdm.tqdm(range(sim_count)):
    # Make packs
    pack_df = fun.make_packs(pack_size = pack_size, num_packs=num_packs, threshold=threshold, df=df)

    # test the packs
    list_of_packs = fun.split_deck(pack_df, pack_size)

    # stddev calc
    stddevs = [fun.calculate_std_of_counts(p, 'pack_category', df) for p in list_of_packs]
    avg_stddev = mean(stddevs)
    pack_stddevs.append(avg_stddev)

# %%
for c in tqdm.tqdm(range(sim_count)):
    tot_card_count = pack_size*num_packs
    no_algo_df = df.sample(frac=1).reset_index(drop=True)[0:tot_card_count]

    list_of_packs = fun.split_deck(no_algo_df, pack_size)

    # stddev calc
    stddevs = [fun.calculate_std_of_counts(p, 'pack_category', df) for p in list_of_packs]
    avg_stddev = mean(stddevs)
    no_algo_stddevs.append(avg_stddev)

#%%
pack_avg_stddev = mean(pack_stddevs)
no_algo_avg_stddev = mean(no_algo_stddevs)
print('The mean std dev for the pack algorithm is {}'.format(pack_avg_stddev))
print('The mean std dev for pure shuffling is {}'.format(no_algo_avg_stddev))

