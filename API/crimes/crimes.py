"""
crimes.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

API for crime rates.
"""
import pandas as pd
from flask import Flask
from flask_restplus import Resource
from flask_restplus import inputs, fields
from flask_restplus import reqparse
from flask_restplus import Namespace
import math
import re

app = Flask(__name__)
api = Namespace('crimes', description="Crime rates and statistics for Sydney suburbs")

parser = reqparse.RequestParser()
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('page', type=int, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, choices=[25, 50, 100], default=25, help='Number of results to return per page')
parser.add_argument('suburb', help="Name of the suburb")
parser.add_argument('suburb_id', type=int, help="ID of the suburb")

@api.route('/')
class Crimes(Resource):

    @api.response(200, 'Successful', api.model('Crime rate', {
        'suburb_id': fields.Integer(description='Suburb id that these rates refer to'),
        'suburb': fields.String(description='Suburb name that these rates refer to'),
        'data': fields.List(fields.Integer(description='Number of reported offenses for a given year'))
    }))
    @api.response(400, 'Invalid request parameters')
    @api.doc(description="Retrieve a list of total crimes reported for each suburb, per year")
    @api.expect(parser, validate=True)
    def get(self):
        """
        Returns a list of number imes reported per year for each suburb
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
        crimes_df = df.copy()

        crimes_df.drop(columns=['id', 'offence_category'], inplace=True)
        crimes_df = df.groupby(['suburb', 'suburb_id']).sum()
        crimes_df.reset_index(inplace=True)

        # Filter by suburb
        if suburb:
            crimes_df = crimes_df[crimes_df['suburb'].str.contains(suburb, flags=re.IGNORECASE)]

        # Filter by suburb_id
        if suburb_id:
            crimes_df = crimes_df[crimes_df['suburb_id'] == suburb_id]

        # Apply ordering
        crimes_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(crimes_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            crimes_df = crimes_df[slice_from:slice_to]

        ret = []

        for index, row in crimes_df.iterrows():
            model = dict()
            model['suburb'] = row['suburb']
            model['suburb_id'] = row['suburb_id']
            model['data'] = row['1995':].to_dict()
            ret.append(model)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': ret,
        }


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/crimes/crimes.csv', index_col=None)
