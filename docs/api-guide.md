# API Guide

### Setting up

Make a copy of the `API/template` directory and rename it to your endpoint name.  
Set the name to a simple object plural (eg, suburbs, restaurants).  
Rename the `template.py` file to the name you used for the directory.

### Loading datasets

Paste any datasets you'll be using in the `datasets` directory.  
Edit the `preprocess.py` file and implement any data cleaning there. When
its run, it should output a `[name].csv` file which will be the data source for the API.    
Each row needs to be attached to a `suburb id`, to do this you need to load the
master suburbs csv and merge the `id` column. 

Example
```python
# Your dataset
my_df = pd.read_csv('datasets/my-dataset.csv')

# Make sure the suburb name in your dataset it titled (eg, "MOSS VALE" to "Moss Vale")
my_df['suburb'] = my_df['suburb'].str.title()

# Load master suburbs csv
suburbs_df = pd.read_csv('../suburbs/suburbs.csv', index_col='id')

# Merge suburbs based on name
my_df = my_df.merge(suburbs_df[['id', 'name']], left_on='suburb', right_on="name")
```

### Configure the API

Edit the `[name].py` file and change any references from `template` to `[name]`.  
Update the `model` to match the model of your data.  
Test that your API works by running it.