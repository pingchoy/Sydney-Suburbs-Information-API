"""
preprocess_dbfuel_.py
University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

***** DEPENDENCIES: xlrd
        pip3 install xlrd

Import and clean data to be used by the fuel check API endpoint.
- Clean/prepare fuel price data for regressions
- Save cleaned datasets in local directory

Datasets used:
    Fuel Check - monthly fuel price checks in NSW
        multiple xlsx files
        https://data.nsw.gov.au/data/dataset/fuel-check
        
Datasets cleaned, baked & prepared:
    Monthly fuel price data per fuel type
        /database/<fuel_code>_monthly_fuel_price.csv
"""
import pandas as pd
import os
import sys
import glob
import re
import numpy as np
#from math import log, ceil  # optional -- see note below

def progress_bar(progress, total):
    """
    inspired from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    Called within a loop to print a progress bar to stdout
    """
    bar_length = 50
    current_fill = int(bar_length * progress // total)
    percentage = round(100.0 * progress / float(total), 1)
    bar = chr(9608) * current_fill + '-' * (bar_length - current_fill)
    sys.stdout.write('\r>Progress |%s| %s%% Complete\r' % (bar, percentage))
    sys.stdout.flush()
    if progress == total: 
        sys.stdout.write('\r\n')

def main():
    # Load the suburbs csv to build the base from
    suburbs_df = pd.read_csv('API/suburbs/suburbs.csv', usecols=['id', 'name'])
    suburbs_df.set_index('id', drop=True, inplace=True)
    # Swap the id index with suburb names
    suburbs_df.reset_index(inplace=True)
    suburbs_df.set_index('name',inplace=True, drop=True)
    # fuel codes were researched and pre-determined to avoid calling df.fuel_codes.unique() every iteration
    fuel_codes = ['U91', 'E10', 'P98', 'P95', 'PDL', 'DL', 'E85', 'LPG', 'CNG', 'B20', 'EV']
    # Set up a fuel dataframes dictionary
    fuel_dfs = {}
    for idx in range(0,len(fuel_codes)):
        fuel_dfs[fuel_codes[idx]] = suburbs_df
    filepath = str(os.getcwd())
    xlsx_files = glob.glob(filepath + "/datasets/*.xlsx")
    
    # Initialize the progress bar
    progress_total = len(xlsx_files) + 1; progress = 0
    progress_bar(progress, progress_total)
    for xlsx_file in xlsx_files:
        # Load a test xlsx
        test_df = pd.read_excel(xlsx_file, header=None)
        # Determine whether first row contains the appropriate headers starting with "ServiceStationName"
        headers_search = re.search("[Ss]ervice", str(test_df.iloc[0,0]))
        headers = 1 if headers_search else 0
        while not headers:
            test_df.drop(test_df.index[0], inplace=True)
            test_df.reset_index(inplace=True, drop=True)
            headers = 1 if re.search("[Ss]ervice", str(test_df.iloc[0,0])) else 0
        if headers:
            # Found the row containing desired column names
            column_names = test_df.iloc[0,:].values.tolist()
            for idx in range(0,len(column_names)):
                column_names[idx] = re.sub('(?!^)([A-Z]+)', r'_\1', column_names[idx]).lower()
            test_df.columns = column_names
            # Drop the first row as it is the same as the column headers
            test_df.drop(test_df.index[0], inplace=True)
            test_df.price = pd.to_numeric(test_df.price,errors='coerce')
            test_df.dropna(subset=['suburb'],inplace=True)
            '''
            # Note: only use below to convert individual monthly files containing raw DAILY prices to .csv
            # uncomment: from math import log, ceil
            test_df.reset_index(inplace=True, drop=True)
            test_df.index.rename('id', inplace=True)
            # the base-10 logarithm of a positive integer x returns a float between:
            # the num digits in x minus 1 and the num of digits in x; taking the ceiling returns num digits 
            test_df.index += 1*(10 ** (ceil(log(test_df.shape[0], 10))))
            csv_filename = re.sub(".xlsx", ".csv", xlsx_file)
            test_df.to_csv('datasets/' + csv_filename)
            '''
        else:
            sys.stdout.write("Could not clean %s\r\n" %(xlsx_file))
            test_df = None
            continue
           
        # Drop unneccessary columns since we are just after monthly averages per suburb
        columns_to_drop = ['service_station_name', 'address', 'postcode', 'brand', 'price_updated_date']
        test_df.drop(columns=columns_to_drop, inplace=True)
        # Ensure all column names adhere to the same naming policy
        naming = ['suburb', 'fuel_code', 'price']
        test_df.columns = naming
        # Ensure all suburb names are the same
        test_df['suburb'] =  test_df.apply(lambda row: row['suburb'].title(), axis=1)
        # The aggregation must be done individually per fuel code, copied to an aggregated dataframe avg_df
        grouped = test_df.groupby(['fuel_code','suburb'])
        avg_df = grouped['price'].agg(np.mean).reset_index()
        
        file_year = ""
        '''
        ?<= is look behind to ensure no other potential number is detected in file path (hence \D)
        ?= looks ahead to ensure no digits either
        '''
        year_search = re.search("(?<=[A-Za-z-_ \D])([1-3][0-9]{3})(?=[A-Za-z-_ .,'/\D'\'])", xlsx_file)
        if year_search:
            file_year = year_search[0]
        else:
            file_year = ""
        months_regex = "[Jj]an|[Ff]eb|[Mm]ar|[Aa]pr|[Mm]ay|[Jj]un|[Jj]ul|[Aa]ug|[Ss]ep|[Oo]ct|[Nn]ov|[Dd]ec"
        file_month = None
        if re.search(months_regex, xlsx_file):
            file_month = re.search(months_regex, xlsx_file)[0].title()
        else:
            file_month = ""
        avg_df.rename(columns={'price': pd.to_datetime(file_month + ' ' + file_year, format='%b %Y')},\
                            inplace=True)
        
        # fuel_list ensures only the codes contained in the current month file are merged
        fuel_list = avg_df.fuel_code.unique().tolist()
        for code in fuel_list:
            '''
            Merge each aggregated group by fuel code with a placeholder dataframe
            '''
            if code not in fuel_codes:
                continue
            temp_df = pd.DataFrame({"fuel_code":[code]})
            temp_df = pd.merge(temp_df, avg_df, on='fuel_code', how='left')
            temp_df.set_index('suburb',drop=True,inplace=True)
            fuel_dfs[code] = pd.merge(fuel_dfs[code],temp_df, left_index=True,\
                                right_index=True, how='outer', suffixes=('', '_drop'))
            if 'fuel_code_drop' in fuel_dfs[code].columns:
                fuel_dfs[code].drop('fuel_code_drop',axis=1,inplace=True)
            fuel_dfs[code].dropna(subset=['id'],inplace=True)
            fuel_dfs[code].id = fuel_dfs[code].id.astype(int)
            fuel_dfs[code].fuel_code.fillna(value=code, inplace=True)
            fuel_dfs[code][pd.to_datetime(file_month + ' ' + file_year, format='%b %Y')].fillna(value=0.0, inplace=True)
        progress += 1
        progress_bar(progress, progress_total)
    
    '''
    Main iteration done - sort each fuel dataframe into appropriate month/year order
    '''
    for code in fuel_dfs.keys():
        # Swap the indices back to the identifier being the index as merging by suburb is no longer an issue
        try:
            fuel_dfs[code].index.rename('suburb', inplace=True)
            fuel_dfs[code].reset_index(inplace=True)
            fuel_dfs[code].set_index('id',drop=True,inplace=True) 
            columns_to_save = ['suburb', 'fuel_code']
            temp_frame = fuel_dfs[code][columns_to_save]
            fuel_dfs[code].drop(columns_to_save, axis=1, inplace=True)
            fuel_dfs[code] = fuel_dfs[code][sorted(fuel_dfs[code].columns)]
            for datetime in fuel_dfs[code].columns:
                fuel_dfs[code].rename(columns={datetime: datetime.strftime('%b_%Y')}, inplace=True)
            fuel_dfs[code] = pd.merge(temp_frame, fuel_dfs[code], left_index=True, right_index=True,\
                                how='left')
        except (KeyError, ValueError):
            continue
        '''
        Save individual fuel dataframes to CSV files
        '''
        fuel_dfs[code].to_csv('database/'+ code + '_monthly_fuel_price.csv', index_label='id')
    
    progress += 1    
    progress_bar(progress, progress_total)
    sys.stdout.write("All done!\r\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write("\nData cleansing stopped - shutting down\r\n")
        sys.exit(0)

