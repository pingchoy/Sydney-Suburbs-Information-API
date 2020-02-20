"""
stations.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

An API endpoint which computes the 5 closest train stations in proximity to a given suburb
"""
import json
import pandas as pd
from flask import Flask
from flask_restplus import Resource, fields, inputs, reqparse, Namespace
from math import ceil
from ..haversine import distance
import re


app = Flask(__name__)
api = Namespace('train-stations', description="Information on Sydney trains proximity")

trains_model = api.model('Train Station', {
    'id': fields.Integer(description='Unique identifier of this train station'),
    'name': fields.String(description='Name of the train station'),
    'latitude': fields.Float(description='Latitude position'),
    'longitude': fields.Float(description='Longitude position'),
    'morning_peak': fields.String(description='Hours of morning peak usage'),
    'afternoon_peak': fields.String(description='Hours of afternoon peak usage')
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(trains_model))
})

pagination_arguments = reqparse.RequestParser()
pagination_arguments.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
pagination_arguments.add_argument('page', type=int, default=1, help='Page number to retrieve')
pagination_arguments.add_argument('per_page', type=int, choices=[25, 50, 100], default=25, help='Number of results to return per page')
pagination_arguments.add_argument('name', help="Name of the train station")


@api.route('/')
class TrainStations(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Retrieve a list of all Sydney train stations")
    @api.marshal_list_with(page_of_results)
    @api.expect(pagination_arguments, validate=True)
    def get(self):
        """
        Returns a list of train stations
        """
        page_args = pagination_arguments.parse_args()

        # Retrieve the argument parameters
        ascending = page_args.get('ascending', True)
        ascending = ascending if ascending is not None else True
        name = page_args.get('name')

        # Make a reference to the dataset
        return_df = trains_df

        # Filter by name
        if name:
            return_df = return_df[return_df['name'].str.contains(name, flags=re.IGNORECASE)]

        # Apply ordering
        return_df.sort_values(by='name', inplace=True, ascending=ascending)

        # Apply pagination
        page = page_args.get('page')
        per_page = page_args.get('per_page')
        count = len(return_df)
        pages = ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

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
            return_model['id'] = int(idx)
            ret.append(return_model)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, trains_model),
        }


@api.route('/<int:id>')
@api.param('id', 'The train station id')
class TrainStation(Resource):

    @api.response(200, 'Successful', trains_model)
    @api.response(404, 'Train station not found')
    @api.doc(description="Retrieve a train station by its ID")
    @api.marshal_with(trains_model)
    def get(self, id):
        """
        Returns a train station for a given id
        """
        if id not in trains_df.index:
            api.abort(404, "Train station with id {} doesn't exist".format(id))

        station = dict(trains_df.loc[id])
        station['id'] = id
        return station


position_parser = reqparse.RequestParser()
position_parser.add_argument('latitude', type=float, required=True, help='The latitude value of the coordinate')
position_parser.add_argument('longitude', type=float, required=True, help='The longitude value of the coordinate')


@api.route('/nearest')
class NearestStationList(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.doc(description="Find nearest 5 train stations from a given coordinate")
    @api.expect(position_parser, validate=True)
    def get(self):
        """
        Find and retrieve a list of the closest five train stations from a given coordinate
        """
        args = position_parser.parse_args()
        longitude = args.get('longitude')
        latitude = args.get('latitude')

        # Make a copy of the trains data frame in order to add an additional column based on queried suburb
        distance_df = trains_df

        # Iterate over each train station (row) and add an additional cell 'distance' by computing
        # the haversine distance between the suburb long/lat and train station long/lat
        distance_df['distance'] = distance_df.apply(lambda row: distance(row['latitude'], row['longitude'], latitude, longitude), axis=1)

        # Sort by the distance to each station in ascending order
        distance_df.sort_values(by='distance', inplace=True, ascending=True)

        # Convert to JSON format and return the 5 closest train stations for the given suburb
        json_str = distance_df.head().to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = idx
            ret.append(return_model)
        return ret


pd.options.mode.chained_assignment = None
# Load the suburbs and train_stations CSV files
trains_df = pd.read_csv('API/stations/stations.csv', index_col='id')

