"""
template.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Joining the suburbs data set with current weather data
"""
import json
import pandas as pd
from flask import Flask
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
import re

app = Flask(__name__)
api = Api(app,
          default="default",
          title="Sydney Data Services API - Property Prices",
          description="Property Analytics data in the city of Sydney, Australia")

# TODO: update to reflect the fields of your model
property_model = api.model('Property', {
    'id': fields.Integer,
    'name': fields.String,
    'state': fields.String,
    'post_code': fields.Integer,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'sqkm': fields.Float,
    'population_male': fields.Integer,
    'population_female': fields.Integer,
    'population_total': fields.Integer,
    
})

parser = reqparse.RequestParser()
parser.add_argument('order', choices=list(column for column in property_model.keys()))
parser.add_argument('ascending', type=inputs.boolean)
parser.add_argument('query')

def mergewithsuburbs(weatherdf,inputdf):
    my_df = weatherdf.merge(inputdf, left_on='suburb', right_on="name")
    return my_df
    




@api.route('/suburbs/PropertyPrice')
class Suburbs(Resource):

    @api.response(200, 'Successful')
    @api.doc(description="Retrieve a list of suburbs")
    @api.marshal_list_with(property_model)
    def get(self):
        args = parser.parse_args()

        # Retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        query = args.get('query')

        # Clean the query param (strip any non-alpha characters)
        # TODO: update the query parameter to the field you can search on or remove completely
        if query:
            query = re.sub(r'[^0-9A-Za-z- ]+', '', query)

        # Set default args
        order_by = order_by if order_by else 'id'
        ascending = ascending if ascending else True

        # Make a reference to the dataset
        return_df = df

        # Search by postcode or suburb name
        if query:
            print(query)
            if query.isdigit():
                # Search full post code
                post_code = int(query)
                return_df = return_df[return_df['post_code'] == post_code]
            else:
                # Search name
                return_df = return_df[return_df['name'].str.contains(query, flags=re.IGNORECASE)]

        # Apply ordering
        return_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Convert data frame to JSON then to a dictionary
        json_str = return_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = int(idx)
            ret.append(return_model)

        return ret

# TODO: update any references to suburb with your model
@api.route('/suburbs/<int:id>')
@api.param('id', 'The suburb identifier')
class Suburb(Resource):
    @api.response(404, 'Suburb was not located')
    @api.response(200, 'Successful')
    @api.doc(description="Retrieve a suburb by its ID")
    @api.marshal_with(property_model)
    def get(self, id):
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        suburb = dict(df.loc[id])
        suburb['id'] = id
        return suburb


if __name__ == '__main__':
    # TODO: Load your dataset
    weatherdf = pd.read_csv('suburb_property_prices_201909_final.csv')
    # Load the suburbs csv
    inputdf = pd.read_csv('suburbs.csv')
    df = mergewithsuburbs(weatherdf,inputdf)
    print(df)

    # run the application
    app.run(debug=True)