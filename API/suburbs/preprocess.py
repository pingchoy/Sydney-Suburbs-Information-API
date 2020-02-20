"""
preprocess.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Import and clean data to be used by our API.
- Load any datasets from the .datasets/ directory
- Clean/prepare the data
- Merge multiple datasets
- Save compiled dataset in local directory

Datasets used:
    Google Maps API
        datasets/sydney-suburbs.json
        https://developers.google.com/maps/documentation/geocoding

    ABS SSC suburbs index
        datasets/2016-ssc-aust.csv
        https://www.abs.gov.au/ausstats/subscriber.nsf/log?openagent&1270055003_ssc_2016_aust_csv.zip

    ABS Population data by suburb
        datasets/2016-census-G01-nsw_ssc.csv
        https://datapacks.censusdata.abs.gov.au/datapacks/

    ATO Taxation Statistics 2016-17 (by postcode)
        datasets/taxable-income-16-17.csv
        https://www.ato.gov.au/About-ATO/Research-and-statistics/In-detail/Taxation-statistics/Taxation-statistics-2016-17/
"""
import pandas as pd
import re

def main():
    # Load suburbs list (scraped from Google Maps)
    suburbs_df = pd.read_json('datasets/sydney-suburbs.json', orient='records')
    # Set post code to float (Flask support)
    suburbs_df['post_code'] = suburbs_df['post_code'].astype('float')
    # Rename suburb columns
    suburbs_df.rename(columns={'suburb': 'name'}, inplace=True)
    suburbs_df.sort_values(by='name', inplace=True)

    # Load the ABS suburb identifier dataset
    abs_id_df = pd.read_csv('datasets/2016-ssc-aust.csv')
    # Remove non-NSW data
    abs_id_df = abs_id_df.drop(abs_id_df[abs_id_df['STATE_NAME_2016'] != 'New South Wales'].index)
    # Remove un-needed fields
    abs_id_df.drop(columns=['MB_CODE_2016', 'STATE_CODE_2016', 'STATE_NAME_2016'], inplace=True)
    # Rename columns
    abs_id_df.columns = ['ssc_id', 'name', 'sqkm']
    # Clean suburb (remove brackets and leading/trailing spaces)
    abs_id_df['name'] = abs_id_df['name'].str.replace(r'\(.*\)|\[.*\]', '')
    abs_id_df['name'] = abs_id_df['name'].str.strip()
    # Group by ID + Suburb name and sum square kilometers
    abs_id_df = abs_id_df.groupby(['ssc_id', 'name'], as_index=False)['sqkm'].sum()
    # Remove duplicates
    abs_id_df.drop_duplicates('name', keep='last', inplace=True)
    # Check that no rows contain NaN
    assert len(abs_id_df[abs_id_df.isna().any(axis=1)]) == 0
    # Merge with suburb data frame
    suburbs_df = suburbs_df.merge(abs_id_df, how='left', validate='one_to_one')

    # Join the ABS population data
    abs_people_df = pd.read_csv('datasets/2016-census-G01-nsw-ssc.csv', usecols=['SSC_CODE_2016', 'Tot_P_M', 'Tot_P_F'])
    # Rename the columns
    abs_people_df.columns = ['ssc_id', 'population_male', 'population_female']
    # Clean ssc id
    abs_people_df['ssc_id'] = abs_people_df['ssc_id'].str.replace(r'^SSC', '')
    abs_people_df['ssc_id'] = pd.to_numeric(abs_people_df['ssc_id'])
    # Merge with suburbs
    suburbs_df = suburbs_df.merge(abs_people_df, how='left')
    # Remove ssc_id
    suburbs_df.drop(columns=['ssc_id'], inplace=True)
    suburbs_df['population_total'] = suburbs_df['population_male'] + suburbs_df['population_female']

    # Load taxable income data frame
    income_df = pd.read_csv('datasets/taxable-income-16-17.csv', index_col=False, thousands=',')
    income_df.columns = [re.sub('[^0-9A-Za-z]', '', col.lower()) for col in income_df.columns]
    # Remove na on income
    income_df.drop(income_df[income_df['average3taxableincome201617'] == 'na'].index, inplace=True)
    # Convert to float
    income_df['average3taxableincome201617'] = income_df['average3taxableincome201617'].str.replace(',', '').astype(float)


    suburbs_df = suburbs_df.merge(income_df[['postcode2', 'average3taxableincome201617']], how='left', left_on='post_code', right_on='postcode2')
    suburbs_df.drop(columns=['postcode2'], inplace=True)
    suburbs_df.rename(columns={'average3taxableincome201617': 'avg_income'}, inplace=True)

    # Rename and reset index
    suburbs_df.index.rename('id', inplace=True)
    suburbs_df.index += 10000

    # Save to new file
    suburbs_df.to_csv('suburbs.csv')


if __name__ == '__main__':
    main()
