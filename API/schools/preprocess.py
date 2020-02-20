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
    NSW Public School Dataset
        https://data.cese.nsw.gov.au/data/dataset/nsw-public-schools-master-dataset/resource/2ac19870-44f6-443d-a0c3-4c867f04c305
    NSW Private School Dataset
        https://data.cese.nsw.gov.au/data/dataset/nsw-non-government-school-locations-and-descriptions/resource/a5871783-7dd8-4b25-be9e-7d8b9b85422f
"""
import pandas as pd


def main():

    csv_file = "datasets/master_dataset.csv"
    public_df = pd.read_csv(csv_file)

    # Only use the 5 columns  -  AgeID, Name, Street, Suburb, Postcode
    public_df = public_df.iloc[:, 1:6]

    # Rename Columns
    public_df = public_df.rename(columns={"AgeID": "id", "Town_suburb" : "Suburb"})

    # get rid of all NaN values and convert to integer
    public_df['id'] = public_df['id'].fillna(-1)
    public_df = public_df[public_df.id != -1]
    public_df['id'] = public_df['id'].astype(int)

    # add type column
    public_df.loc[:,'type'] = 'public'
    # replace spaces in the name of columns
    public_df.columns = [c.replace(' ', '_') for c in public_df.columns]
    # remove white space from suburb column
    public_df['Suburb'] = public_df['Suburb'].str.strip()


    # set the index column; this will help us to find books with their ids
    public_df.set_index('id', inplace=True)

    csv_file = "datasets/datahub_nongov_locations-2017.csv"

    # Need to change encoding format for this file
    private_df = pd.read_csv(csv_file, encoding = "ISO-8859-1")

    # Only use the 5 columns  - AgeID, Name, Street, Suburb, Postcode
    private_df = private_df.iloc[:, :6]
    # Drop AgeId Column

    private_df.drop(['head_campus_ageID'], inplace=True, axis=1)
    # Rename columns
    private_df = private_df.rename(columns = {"ageID": "id",  "school_name": "School_name", "street" : "Street",
                                              "postcode": "Postcode", "town_suburb": "Suburb"})

    # Add type column
    private_df.loc[:, 'type'] = 'private'

    # replace spaces in the name of columns
    private_df.columns = [c.replace(' ', '_') for c in private_df.columns]
    # remove white space from suburb column
    private_df['Suburb'] = private_df['Suburb'].str.strip()
    # set the index column; this will help us to find books with their ids
    private_df.set_index('id', inplace=True)

    merged_df = pd.concat([public_df, private_df])

    # Merge schools df with suburb df
    merged_df['Suburb'] = merged_df['Suburb'].str.title()
    suburbs_df = pd.read_csv('../suburbs/suburbs.csv')
    merged_df = merged_df.merge(suburbs_df[['id', 'name']], left_on='Suburb', right_on="name")
    # Rename id to suburb_id
    merged_df = merged_df.rename(columns={"id": "suburb_id"})
    merged_df = merged_df.drop(['name'], axis = 1)

    # Rename columns
    merged_df.rename(columns={'School_name': 'name'}, inplace=True)
    merged_df.columns = merged_df.columns.str.lower()

    # Reset index
    merged_df.index.rename('id', inplace=True)
    merged_df.index += 10000

    csv_file = "datasets/masterdatasetnightlybatchheadcount.csv"
    head_count_df = pd.read_csv(csv_file)
    # replace spaces in the name of columns
    head_count_df.columns = [c.replace(' ', '_') for c in head_count_df.columns]
    #rename column
    # head_count_df = head_count_df.rename(columns={'School_Name' : 'name'})
    # fill NaN Columns with 0
    head_count_df= head_count_df.fillna(0)
    #replace SP with 0
    head_count_df.replace({'SP' : 0}, inplace = True)

    head_count_df.to_csv("headcount.csv")
    # merged_df = pd.merge(merged_df, head_count_df, on = 'name')
    merged_df.to_csv('schools.csv')


if __name__ == '__main__':
    main()
    print('Preprocessing complete')