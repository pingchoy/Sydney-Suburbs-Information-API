"""
preprocess.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Import and clean data to be used by the train stations API endpoint.
- Clean/prepare train station data for calculations
- Save cleaned dataset in local directory

Dataset used:
    Public Transport - Location Facilities and Operators
        LocationFacilityData.csv
        https://opendata.transport.nsw.gov.au/dataset/public-transport-location-facilities-and-operators
        
Dataset cleaned, baked & prepared:
    Train stations per location
        train_stations.csv
"""
import pandas as pd


def main():
    # Load the transport facilities CSV
    trains_df = pd.read_csv('datasets/LocationFacilityData.csv')
    # Drop all of the unnecessary columns
    columns_to_drop = ['TSN', 'EFA_ID', 'PHONE', 'ADDRESS', 'FACILITIES', 'ACCESSIBILITY']
    trains_df.drop(columns=columns_to_drop, inplace=True, axis=1)
    trains_df.columns = map(str.lower, trains_df.columns)
    # Remove any transport mode that does not contain "train"; the tilde '~' inverses the bool
    # since we do not want any string containing train to be removed
    indexNames = trains_df[~trains_df.transport_mode.str.contains('[Tt]rain')].index
    trains_df.drop(indexNames, inplace=True)
    # Rename location column and fill in blanks
    trains_df.rename(columns={'location_name': 'name'}, inplace=True)
    trains_df['morning_peak'].fillna('No peak', inplace=True)
    trains_df['afternoon_peak'].fillna('No peak', inplace=True)
    # Reset index to count from 0 & remove unnecessary column
    trains_df.reset_index(drop=True, inplace=True)
    trains_df.drop('transport_mode', inplace=True, axis=1)
    # Name and set index
    trains_df.index.rename('id', inplace=True)
    trains_df.index += 10000
    # Ensure that no rows contain NaN
    assert len(trains_df[trains_df.isna().any(axis=1)]) == 0
    # Save to CSV without index column as it is unnecessary
    trains_df.to_csv('stations.csv')


if __name__ == '__main__':
    main()

