"""
weather.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Weather API.
"""
import json
import pandas as pd
from flask import Flask
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse
import math

app = Flask(__name__)
api = Namespace('weather', description="Current weather statistics and forecasting")

parser = reqparse.RequestParser()
parser.add_argument('page', type=int, required=False, default=1, help='Page number of results')
parser.add_argument('per_page', type=int, required=False, choices=[25, 50, 100], default=25, help='Number of items per page')
parser.add_argument('suburb_id', type=int, required=False, help='Suburb id to filter by')


@api.route('/')
class Weather(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.expect(parser, validate=True)
    @api.doc(description="Retrieve a list of weather statistics")
    def get(self):
        """
        Returns a list of weather statistics for each suburb
        """
        args = parser.parse_args()
        suburb_id = args.get('suburb_id')

        # Make a copy of the dataset
        return_df = df

        if suburb_id:
            # Filter by suburb id
            return_df = return_df[return_df['suburb_id'] == suburb_id]

        # Apply ordering
        return_df.sort_values(by='suburb', inplace=True, ascending=True)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(return_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page out of range.')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            return_df = return_df[slice_from:slice_to]

        # Convert data frame to JSON then to a dictionary
        json_str = return_df.to_json(orient='index')
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
            'results': ret,
        }


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/weather/weather.csv', index_col=False)