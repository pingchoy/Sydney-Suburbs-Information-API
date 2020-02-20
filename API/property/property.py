"""
property.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

API for property statistics.
"""
import pandas as pd
from flask import Flask
from flask_restplus import Resource
from flask_restplus import inputs
from flask_restplus import fields
from flask_restplus import reqparse
from flask_restplus import Namespace
import math
import json

app = Flask(__name__)
api = Namespace('property', description="Statistics on Sydney property by suburb")

property_model = api.model('Property', {
    'suburb': fields.String(description='Suburb of the statistics'),
    'median_sold_price': fields.Float(description='Median sold price'),
    'lowest_sold_price': fields.Float(description='Lowest sold price'),
    'highest_sold_price': fields.Float(description='Highest sold price'),
    'median_rent_price': fields.Float(description='Median rent price'),
    'suburb_id': fields.Integer(description='Suburb id of these statistics'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(property_model))
})

parser = reqparse.RequestParser()
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('page', type=int, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, choices=[25, 50, 100], default=25, help='Number of results to return per page')
parser.add_argument('suburb_id', type=int, help="ID of the suburb")

@api.route('/')
class Property(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Retrieve statistics on property by suburb")
    @api.expect(parser, validate=True)
    @api.marshal_list_with(page_of_results)
    def get(self):
        """
        Returns property statistics
        """
        args = parser.parse_args()

        # Retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        suburb_id = args.get('suburb_id')

        # Set default args
        order_by = order_by if order_by else 'suburb'
        ascending = ascending if ascending is not None else True

        # Make a reference to the dataset
        property_df = df.copy()

        # Filter by suburb_id
        if suburb_id:
            property_df = property_df[property_df['suburb_id'] == suburb_id]

        # Apply ordering
        property_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(property_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            property_df = property_df[slice_from:slice_to]

        ret = []

        # Convert data frame to JSON then to a dictionary
        json_str = property_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []
        for idx in ds:
            return_model = ds[idx]
            ret.append(return_model)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, property_model),
        }


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/property/property.csv', index_col=None)
