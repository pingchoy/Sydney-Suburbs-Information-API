"""
fuel.py
University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates
An API endpoint for fuel prices
"""
import re
import math
import json
import pandas as pd
from flask import Flask
from flask_restplus import Resource, Namespace, inputs, reqparse, fields

app = Flask(__name__)
api = Namespace('fuel-prices', description='Information on Sydney fuel prices')

parser = reqparse.RequestParser()
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('page', type=int, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, choices=[25, 50, 100], default=25, help='Number of results to return per page')
parser.add_argument('suburb', help="Name of the suburb")
parser.add_argument('suburb_id', type=int, help="ID of the suburb")

@api.route('/')
class FuelPrices(Resource):

    @api.response(200, 'Successful', api.model('Fuel price', {
        "suburb_id": fields.Integer(description='Suburb id'),
        "suburb": fields.String(description='Suburb this price refers to'),
        "fuel_code": fields.Integer(description='Unique code for this fuel type'),
    }))
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Retrieve a list of all Sydney fuel prices for each suburb, per month")
    @api.expect(parser, validate=True)
    def get(self):
        """
        Returns a list of monthly fuel prices for each suburb
        """
        args = parser.parse_args()

        # Retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        suburb = args.get('suburb')
        suburb_id = args.get('suburb_id')

        # Set default args
        order_by = order_by if order_by else 'suburb'
        ascending = ascending if ascending is not None else True

        # Make a reference to the dataset
        fuel_df = df.copy()

        # Filter by suburb
        if suburb:
            fuel_df = fuel_df[fuel_df['suburb'].str.contains(suburb, flags=re.IGNORECASE)]

        # Filter by suburb_id
        if suburb_id:
            fuel_df = fuel_df[fuel_df['suburb_id'] == suburb_id]

        # Apply ordering
        fuel_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(fuel_df)
        pages = math.ceil(count / per_page) if count else 1
        
        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            fuel_df = fuel_df[slice_from:slice_to]

        ret = []

        # Convert data frame to JSON then to a dictionary
        json_str = fuel_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            fuel = ds[idx]
            fuel['id'] = int(idx)
            ret.append(fuel)
        
        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': ret,
        }


@api.route('/<int:id>')
@api.param('id', 'The fuel prices row id')
class FuelPrices(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Fuel price row was not found')
    @api.doc(description="Get fuel prices by their row ID")
    def get(self, id):
        """
        Returns a fuel price row by its id
        """
        if id not in df.index:
            api.abort(404, "Fuel price row {} doesn't exist".format(id))

        fuel_price = df.loc[id].to_json()
        fuel_price = json.loads(fuel_price)
        fuel_price['id'] = int(id)

        return fuel_price


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/fuel/fuel.csv', index_col='id')