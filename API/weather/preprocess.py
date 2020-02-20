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
    Open Weather API
"""
import pandas as pd

def main():
    # Load current weather dataset
    current_df = pd.read_csv('datasets/curr_weather_suburb.csv', index_col=False)
    current_df.rename(columns={'current_temp': 'temp'}, inplace=True)

    # Join forecast with current
    forecast_df = pd.read_csv('datasets/forecast_weather_suburb.csv', index_col=False)
    current_df = current_df.merge(forecast_df, left_on='suburb', right_on='suburb')

    # Load master suburbs list
    suburbs_df = pd.read_csv('../suburbs/suburbs.csv')
    current_df = current_df.merge(suburbs_df[['id', 'name']], left_on='suburb', right_on='name')
    current_df.drop(columns=['name'], inplace=True)
    current_df.rename(columns={'id': 'suburb_id'}, inplace=True)

    # Save to new file
    current_df.to_csv('weather.csv', index=False)


if __name__ == '__main__':
    main()
