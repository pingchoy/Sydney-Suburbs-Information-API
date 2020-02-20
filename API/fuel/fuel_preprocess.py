"""
fuel_preprocess.py
University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates
Further preprocessing given individual csv files containing fuel data
"""
import re
import os
import glob
import pandas as pd
import numpy as np
from math import log, ceil

def second_element(list_obj):
    return list_obj[1]

def main():
    # Initialize dictionary containing dataframes for each fuel type from the cleaned database directory
    fuel_dfs = {}
    # Searches the database directory for the monthly fuel CSV files sorted by fuel type
    filepath = str(os.getcwd())
    fuel_relations = glob.glob(filepath + "/database/*.csv")
    # Fills a dictionary with dataframes pertaining to each fuel type's dataset
    nonzero_list = []
    for fuel_relation in fuel_relations:
        # Search for the fuel code from within the file path name    
        fuel_code = re.search("(?<=[/database/])([A-Z0-9]{1,4})(?=[_])", fuel_relation)
        if fuel_code:
            fuel_dfs[fuel_code[0]] = pd.read_csv(fuel_relation, index_col='id')
            # Counts the number of items which are nonzero in each row and sums it up
            nonzero_list.append([ fuel_code[0], np.count_nonzero(fuel_dfs[fuel_code[0]].iloc[:,2:]) ])
        else:
            continue
    
    # Filters each dataframe for the top 4 containing nonzero values
    fuel_culling = sorted(nonzero_list, key=second_element, reverse=True)
    culled_df = fuel_dfs[fuel_culling[0][0]]#.reset_index()
    for idx in range(1,4):
        culled_df = pd.concat([culled_df, fuel_dfs[fuel_culling[idx][0]]])#, ignore_index=True)
    
    # Compiles all four datasets into one, culling the rest in the process (just like Stratholme...)
    culled_df.reset_index(inplace=True)
    culled_df.rename(columns = {'id' : 'suburb_id'}, inplace=True)
    culled_df.index.rename('id', inplace=True)
    # the base-10 logarithm of a positive integer x returns a float between:
    # the num digits in x minus 1 and the num of digits in x; taking the ceiling returns num digits 
    culled_df.index += 1*(10 ** (ceil(log(culled_df.shape[0], 10))))
    culled_df.to_csv('fuel.csv')

if __name__ == "__main__":
    main()

