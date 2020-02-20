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
    Domain Property API
        datasets/property-prices-2019-09.csv
"""
import pandas as pd

def main():
    # Load property dataset
    property_df = pd.read_csv('datasets/property-prices-2019-09.csv')

    # Load suburb dataset
    suburbs_df = pd.read_csv('../suburbs/suburbs.csv')

    property_df = property_df.merge(suburbs_df[['id', 'name']], how='left', left_on='suburb', right_on='name')
    property_df.drop(columns=['name'], inplace=True)
    property_df.rename(columns={'medianSoldPrice': 'median_sold_price', 'lowestSoldPrice': 'lowest_sold_price',
                                'highestSoldPrice': 'highest_sold_price', 'medianRentListingPrice': 'median_rent_price',
                                'id': 'suburb_id'}, inplace=True)

    # Remove any suburbs that aren't found in suburbs
    property_df.drop(property_df[property_df['suburb_id'].isna()].index, inplace=True)
    property_df['suburb_id'] = property_df['suburb_id'].astype(int)

    # Remove suburbs with no data
    property_df.drop(property_df[property_df[['median_sold_price', 'lowest_sold_price', 'highest_sold_price', 'median_rent_price']].isna().all(axis=1)].index, inplace=True)

    # Save to new file
    property_df.to_csv('property.csv', index=False)


if __name__ == '__main__':
    main()
