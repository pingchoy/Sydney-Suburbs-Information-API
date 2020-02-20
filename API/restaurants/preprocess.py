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
    Zomato API
        https://developers.zomato.com/api
"""
import pandas as pd


def main():
    df = pd.read_json('datasets/food.json', 'r', encoding='utf8')
    df.rename(columns={'suburb_codde': 'suburb_id'}, inplace=True)
    df.set_index('id', inplace=True)
    df.index += 10000
    df.to_csv('restaurants.csv')


if __name__ == '__main__':
    main()