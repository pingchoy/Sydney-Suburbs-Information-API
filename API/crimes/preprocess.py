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
    BOCSAR - Recorded Crime by Offense (Suburb)
        datasets/suburb-data-2018.csv
        https://www.bocsar.nsw.gov.au/Pages/bocsar_datasets/Datasets-.aspx
"""
import pandas as pd
import re


def summarise_original():
    """
    Reduce the size of the original dataset by grouping by year and category
    """
    # Load original crimes dataset
    crimes_df = pd.read_csv('datasets/suburb-data-2018.csv')

    # Remove month from column names
    crimes_df.columns = [re.sub(r'[A-Za-z]{3} ([0-9]{4})', '\g<1>', col) for col in crimes_df.columns]

    # Merge years and categories
    crimes_df = crimes_df.groupby(level=0, axis=1).sum()
    crimes_df = crimes_df.groupby(['Offence category', 'Suburb']).sum()
    crimes_df.reset_index(inplace=True)
    crimes_df.to_csv('datasets/crimes-summary.csv', index=False)


def main():
    # Load suburbs and crimes
    suburbs_df = pd.read_csv('../suburbs/suburbs.csv', index_col=None)
    crimes_df = pd.read_csv('datasets/crimes-summary.csv', index_col=None)

    # Clean column names
    crimes_df.columns = [col.lower().replace(' ', '_') for col in crimes_df.columns]

    # Join suburb ids, remove duplicate suburb name
    crimes_df = crimes_df.merge(suburbs_df[['id', 'name']], how="left", left_on="suburb", right_on="name")
    crimes_df = crimes_df.rename(columns={'id': 'suburb_id'})
    crimes_df.drop(columns=['name'], inplace=True)
    crimes_df.dropna(inplace=True)
    crimes_df['suburb_id'] = crimes_df['suburb_id'].astype(int)

    # Rename and reset index
    crimes_df.index.rename('id', inplace=True)
    crimes_df.index += 10000

    # Save to new file
    crimes_df.to_csv('crimes.csv')


if __name__ == '__main__':
    main()
