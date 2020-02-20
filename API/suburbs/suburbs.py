"""
suburbs.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Suburbs API.
"""
import io
import json
import pandas as pd
import numpy as np
from flask import Flask
from flask import request
from flask import send_file
from flask_restplus import Resource
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from flask_restplus import Namespace
from sklearn.linear_model import LinearRegression
import re
import math
import matplotlib.pyplot as plt
import urllib.parse
import requests
from ..haversine import distance
from ..schools.schools import school_model
from ..stations.stations import trains_model
from ..restaurants.restaurants import restaurant_model
from ..property.property import property_model

app = Flask(__name__)
api = Namespace('suburbs', description="Information and statistics on Sydney suburbs")

suburb_model = api.model('Suburb', {
    'id': fields.Integer(description='Unique identifier of the suburb'),
    'name': fields.String(description='Name of the suburb'),
    'locality': fields.String(description='Local council name'),
    'state': fields.String(description='State'),
    'post_code': fields.Integer(description='Post code for this suburb'),
    'latitude': fields.Float(description='Latitude'),
    'longitude': fields.Float(description='Longitude'),
    'sqkm': fields.Float(description='Area of suburb'),
    'population_male': fields.Integer(description='Number of male residents'),
    'population_female': fields.Integer(description='Numer of female residents'),
    'population_total': fields.Integer(description='Total residents'),
    'avg_income': fields.Float(description='Average yearly income')
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(suburb_model))
})

parser = reqparse.RequestParser()
parser.add_argument('order', choices=list(column for column in suburb_model.keys()), help='Field to order by')
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('post_code', type=int, required=False, help='Post code to filter by')
parser.add_argument('page', type=int, required=False, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, required=False, choices=[25, 50, 100], default=25, help='Number of results to return per page')


@api.route('/')
class Suburbs(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Retrieve a list of suburbs")
    @api.marshal_list_with(page_of_results)
    @api.expect(parser, validate=True)
    def get(self):
        """
        Retrieve a list of Sydney suburbs
        """
        args = parser.parse_args()

        # Retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        post_code = args.get('post_code')

        # Set default args
        order_by = order_by if order_by else 'id'
        ascending = ascending if ascending is not None else True

        # Make a reference to the dataset
        suburbs_df = df

        if post_code:
            suburbs_df = suburbs_df[suburbs_df['post_code'] == post_code]

        # Apply ordering
        suburbs_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(suburbs_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page out of range.')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            suburbs_df = suburbs_df[slice_from:slice_to]

        # Convert data frame to JSON then to a dictionary
        json_str = suburbs_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            suburb = ds[idx]
            suburb['id'] = int(idx)
            ret.append(suburb)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, suburb_model),
        }


search_parser = parser.copy()
search_parser.add_argument('query', required=True, help="Query must be provided")
search_parser.remove_argument('post_code')


@api.route('/search')
class SuburbSearch(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Could not find any matching suburbs')
    @api.doc(description="Find suburbs using postcode or name")
    @api.doc(params={'query': 'Search by post code or name'})
    @api.marshal_list_with(page_of_results)
    @api.expect(search_parser, validate=True)
    def get(self):
        """
        Search for a suburb by its name or postcode
        """
        args = search_parser.parse_args()
        query = args.get('query')
        order = args.get('order')
        ascending = args.get('ascending')

        # Clean the query param (strip any non-alpha characters)
        query = re.sub(r'[^0-9A-Za-z- ]+', '', query)

        # Make a reference to the dataset
        suburbs_df = df

        # Search by postcode or suburb name
        if query:
            if query.isdigit():
                # Search full post code
                post_code = int(query)
                suburbs_df = suburbs_df[suburbs_df['post_code'] == post_code]
            else:
                # Search suburb name
                suburbs_df = suburbs_df[suburbs_df['name'].str.contains(query, flags=re.IGNORECASE)]

        # Set default args
        order = order if order else 'id'
        ascending = ascending if ascending is not None else True

        # Apply ordering
        suburbs_df.sort_values(by=order, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(suburbs_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            suburbs_df = suburbs_df[slice_from:slice_to]

        # Convert data frame to JSON then to a dictionary
        json_str = suburbs_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            suburb = ds[idx]
            suburb['id'] = int(idx)
            ret.append(suburb)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, suburb_model),
        }


@api.route('/<int:id>')
@api.param('id', 'The suburb id')
class Suburb(Resource):

    @api.response(200, 'Successful', suburb_model)
    @api.response(404, 'Suburb not found')
    @api.doc(description="Retrieve a suburb by its ID")
    @api.marshal_with(suburb_model)
    def get(self, id):
        """
        Retrieve a suburb by its id
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        suburb = dict(df.loc[id])
        suburb['id'] = id
        return suburb


@api.route('/<int:id>/nearest')
@api.param('id', 'The suburb id')
class NearestSuburbs(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb could not be retrieved')
    @api.doc(description="Retrieve the 5 nearest suburbs")
    @api.marshal_list_with(suburb_model)
    def get(self, id):
        """
        Returns a list of the five nearest suburbs for a given suburb id
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        # Load the suburb
        suburb = dict(df.loc[id])

        # Make a copy of the data frame
        distance_df = df

        # Compute Haversine distance to other suburbs
        distance_df['distance'] = distance_df.apply(lambda row: distance(row['latitude'], row['longitude'], suburb['latitude'], suburb['longitude']), axis=1)

        # Filter out current suburb
        distance_df = distance_df[distance_df['distance'] > 0]
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


@api.route('/<int:id>/schools')
@api.param('id', 'The suburb id')
class SuburbSchools(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb could not be retrieved')
    @api.doc(description="List the schools in a suburb")
    @api.marshal_list_with(school_model)
    def get(self, id):
        """
        Returns a list of schools in a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        # Load schools
        schools_df = pd.read_csv('API/schools/schools.csv', index_col='id')

        schools_df = schools_df[schools_df['suburb_id'] == id]

        # Convert to JSON format and return the 5 closest train stations for the given suburb
        json_str = schools_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = idx
            ret.append(return_model)
        return ret


@api.route('/<int:id>/train-stations')
@api.param('id', 'The suburb id')
class SuburbTrainStations(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb could not be retrieved')
    @api.doc(description="Retrieve five nearest stations to a train station by its ID")
    @api.produces(['application/json', 'image/png'])
    def get(self, id):
        """
        Returns a list or map of the five closest train stations to a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        # Load the suburb
        suburb = dict(df.loc[id])

        # Load the train stations data frame
        trains_df = pd.read_csv('API/stations/stations.csv', index_col='id')

        # Iterate over each train station (row) and add an additional cell 'distance' by computing
        # the haversine distance between the suburb long/lat and train station long/lat
        trains_df['distance'] = trains_df.apply(lambda row: distance(row['latitude'], row['longitude'], suburb['latitude'], suburb['longitude']), axis=1)

        # Sort by the distance to each station in ascending order
        trains_df.sort_values(by='distance', inplace=True, ascending=True)

        # Convert to JSON format and return the 5 closest train stations for the given suburb
        json_str = trains_df.head().to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = idx
            ret.append(return_model)

        mime = request.accept_mimetypes.best_match(['application/json', 'image/png'])

        with open('credentials.json') as credential_file:
            credentials = json.load(credential_file)
            gmaps_key = credentials['maps_api_key']

        # Send a plot of the data if mime-type is image/png
        if mime == 'image/png':
            # Generate map URL
            api_params = {
                'center': "+".join(suburb["name"].split()) + ',NSW,AU',
                'size': '600x400',
                'maptype': 'roadmap',
                'style': 'feature:transit.station.rail|visibility:off',
                'markers': [],
                'key': gmaps_key
            }

            for station in ret:
                marker = [
                    'color:blue',
                    'label:T',
                    f'{station["latitude"]},{station["longitude"]}',
                ]
                api_params['markers'].append('|'.join(marker))

            marker = [
                'color:red',
                'label:S',
                f'{suburb["latitude"]},{suburb["longitude"]}',
            ]
            api_params['markers'].append('|'.join(marker))
            map_url = f'https://maps.googleapis.com/maps/api/staticmap?{urllib.parse.urlencode(api_params, doseq=True)}'

            # Load the map
            response = requests.get(map_url)
            if response.status_code != 200:
                api.abort(404, 'No map for this suburb')
            buffer = io.BytesIO(response.content)
            # Send the map image response
            buffer.seek(0)
            return send_file(buffer, as_attachment=False, mimetype='image/png', cache_timeout=-1)

        return api.marshal(ret, trains_model)


crime_parser = reqparse.RequestParser()
crime_parser.add_argument('start_year', type=int, default=1990, help='The year the data will be filtered from (inclusive)')
crime_parser.add_argument('end_year', type=int, default=2019, help='The year the data will be filtered to (inclusive)')


@api.route('/<int:id>/crime-rates')
@api.param('id', 'The suburb id')
class SuburbCrimeRates(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve crime rate statistics for a suburb. This can be returned as JSON or a graph image")
    @api.produces(['application/json', 'image/png'])
    @api.expect(crime_parser, validate=True)
    def get(self, id):
        """
        Returns a graph or json object showing the number of crimes reported per year for a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        args = crime_parser.parse_args()
        start_year = args.get('start_year')
        end_year = args.get('end_year')

        # Check year filters
        if start_year > end_year:
            api.abort(400, 'Start year must be less than or equal to end year')

        # Make a reference to the dataset
        crimes_df = pd.read_csv('API/crimes/crimes.csv')

        # Group and sum data for suburbs by year
        crimes_df.drop(columns=['id', 'offence_category'], inplace=True)
        crimes_df = crimes_df.groupby(['suburb', 'suburb_id']).sum()
        crimes_df.reset_index(inplace=True)
        crimes_df.set_index('suburb_id', inplace=True)

        crimes_df = crimes_df[crimes_df.index == id]

        if not len(crimes_df):
            api.abort(404, "Cannot load data for suburb with id {}".format(id))

        # Load row for this suburb
        model = crimes_df.to_dict(orient='records')[0]

        # Convert years data and filter based on start/end year
        data = {int(x): model[x] for x in model if x.isdigit()}
        data = {x: data[x] for x in data if x >= start_year and x <= end_year}

        # Create return model
        ret = dict()
        ret['suburb'] = model['suburb']
        ret['suburb_id'] = int(id)
        ret['data'] = data

        mime = request.accept_mimetypes.best_match(['application/json', 'image/png'])

        # Send a plot of the data if mime-type is image/png
        if mime == 'image/png':
            # Create memory buffer
            buffer = io.BytesIO()

            # Generate a graph and save it to the buffer
            plt.figure(figsize=(7, 5))
            plt.style.use('seaborn')
            plt.subplots_adjust(bottom=0.20)
            plt.plot([str(key) for key in ret['data']], [ret['data'][key] for key in ret['data']])
            plt.ylabel('Number of reported crimes', fontdict={'fontsize': 14})
            plt.xlabel('Year', fontdict={'fontsize': 14})
            plt.xticks(rotation=45)
            plt.title(f'Crimes reported in {model["suburb"]}', y=1.1, fontdict={'fontsize': 20, 'verticalalignment': 'top'})
            plt.savefig(buffer, format='png')
            plt.close()

            # Send the graph
            buffer.seek(0)
            return send_file(buffer, as_attachment=False, mimetype='image/png', cache_timeout=-1)

        return ret


@api.route('/<int:id>/weather')
@api.param('id', 'The suburb id')
class SuburbWeather(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve a list of weather statistics for a suburb")
    def get(self, id):
        """
        Returns weather statistics for a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        weather_df = pd.read_csv('API/weather/weather.csv')

        # Filter by suburb id
        weather_df = weather_df[weather_df['suburb_id'] == id]

        # Convert data frame to JSON then to a dictionary
        json_str = weather_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            ret.append(return_model)

        return ret

restaurant_parser = reqparse.RequestParser()
restaurant_parser.add_argument('order', default='rating', choices=list(column for column in restaurant_model.keys()), help='Field to order by')
restaurant_parser.add_argument('ascending', type=inputs.boolean, default=False, help='Sort in ascending or descending order')
restaurant_parser.add_argument('page', type=int, required=False, default=1, help='Page number to retrieve')
restaurant_parser.add_argument('per_page', type=int, required=False, choices=[10, 25, 100], default=10, help='Number of results to return per page')


@api.route('/<int:id>/restaurants')
@api.param('id', 'The suburb id')
class SuburbRestaurants(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve a list of restaurants located in this suburb")
    @api.expect(restaurant_parser, validate=True)
    def get(self, id):
        """
        Returns resturants that are located in a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        restaurants_df = pd.read_csv('API/restaurants/restaurants.csv', index_col='id', converters={'cuisines': eval})

        args = restaurant_parser.parse_args()
        order_by = args.get('order')
        ascending = args.get('ascending', True)

        # Filter by suburb id
        restaurants_df = restaurants_df[restaurants_df['suburb_id'] == id]

        # Apply ordering
        restaurants_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(restaurants_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page out of range.')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            restaurants_df = restaurants_df[slice_from:slice_to]

        # Convert data frame to JSON then to a dictionary
        json_str = restaurants_df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            return_model = ds[idx]
            return_model['id'] = idx
            ret.append(return_model)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, restaurant_model),
        }

        return ret


@api.route('/<int:id>/property')
@api.param('id', 'The suburb id')
class SuburbProperty(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve property statistics for a suburb")
    @api.marshal_with(property_model)
    def get(self, id):
        """
        Returns property statistics for a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        property_df = pd.read_csv('API/property/property.csv')

        # Filter by suburb id
        property_df = property_df[property_df['suburb_id'] == id]

        if not len(property_df):
            api.abort(404, "Property statistics for suburb {} not found".format(id))

        property = property_df.iloc[0]
        property = json.loads(property.to_json(orient='index'))




        # Convert data frame to JSON then to a dictionary
        return property


                      
@api.route('/<int:id>/fuel-prices')
@api.param('id', 'The suburb id')
class SuburbFuelPrices(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve monthly fuel prices for a suburb")
    @api.produces(['application/json', 'image/png'])
    def get(self, id):
        """
        Returns a JSON object showing the average monthly fuel prices per fuel type for a given suburb
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        # Make a reference to the dataset
        fuel_df = pd.read_csv('API/fuel/fuel.csv')

        # Filter for the given suburb
        fuel_df.drop(columns=['id'], inplace=True)
        fuel_df.set_index('suburb_id', inplace=True)
        fuel_df = fuel_df[fuel_df.index == id]
        
        # Save the suburb name for plotting purposes
        suburb = fuel_df.suburb.unique()

        if not len(fuel_df):
            api.abort(404, "Cannot load data for suburb with id {}".format(id))

        # Make a copy of the dataframe in order to preserve shape
        prices_df = fuel_df.copy()
        prices_df.drop(columns=['suburb', 'fuel_code'], inplace=True)
        model = prices_df.to_dict(orient='records')

        # Create a return model
        ret = {}
        i = 0
        for fuel_code in fuel_df['fuel_code'].tolist():
            ret[fuel_code] = model[i]
            i += 1
        
        mime = request.accept_mimetypes.best_match(['application/json', 'image/png'])

        # Send a plot of the data if mime-type is image/png
        plot_df = fuel_df.copy()
        plot_df.drop(columns=['suburb'], inplace=True)
        plot_df.set_index('fuel_code', inplace=True)
        
        # Replace all zeroes with NaN to avoid troublesome data points
        for code in plot_df.index:
            plot_df.loc[code].replace(0, pd.np.nan, inplace=True)
        
        # Transpose the dataframe in order to have an accurate representation in the line graph
        plot_df = plot_df.T
        plot_df.index.rename('month', inplace=True)
        if mime == 'image/png':
            # Create memory buffer
            buffer = io.BytesIO()
            # Generate a graph and save it to the buffer
            plt.style.use('ggplot')
            fig, ax = plt.subplots()
            for col in plot_df.columns:
                ax = plot_df[col].plot(ax=ax, kind='line', x='month', y=col, label=col)
            plt.xticks(np.arange(len(plot_df.index)), plot_df.index, rotation=90)
            plt.subplots_adjust(bottom=0.20)
            plt.ylabel('Price', fontdict={'fontsize': 14})
            plt.xlabel('Month/Year', fontdict={'fontsize': 14})
            plt.title(f'Monthly fuel price data per fuel type for {suburb[0]}', y=1.1,\
                        fontdict={'fontsize': 14, 'verticalalignment': 'top'})
            plt.legend(loc='best')
            plt.tight_layout()
            plt.savefig(buffer, format='png')
            plt.close()

            # Send the graph
            buffer.seek(0)
            return send_file(buffer, as_attachment=False, mimetype='image/png', cache_timeout=-1)
                      
        return ret
                      

@api.route('/<int:id>/fuel-prices/forecast/<string:fuel_code>')
@api.param('id', 'The suburb id')
@api.param('fuel_code', 'The fuel type out of [P98, P95, U91, E10]')
class SuburbFuelPrices(Resource):

    @api.response(201, 'Successfully generated forecast')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Suburb was not located')
    @api.doc(description="Retrieve a forecast for monthly fuel price for a given suburb and fuel type")
    def post(self, id, fuel_code):
        """
        Returns a JSON object showing the average monthly fuel price forecast for a given suburb and fuel type
        """
        if id not in df.index:
            api.abort(404, "Suburb {} doesn't exist".format(id))

        if fuel_code not in ['P98', 'P95', 'U91', 'E10']:
            api.abort(400, "Fuel type must be one of ['P98', 'P95', 'U91', 'E10']".format(fuel_code))
        
        # Make a reference to the dataset
        fuel_df = pd.read_csv('API/fuel/fuel.csv', index_col='id')
        
        # Filter for the given suburb
        fuel_df = fuel_df[fuel_df['suburb_id'] == id]
        fuel_df = fuel_df[fuel_df['fuel_code'] == fuel_code]
        fuel_df.set_index('suburb_id', drop=True, inplace=True)
        
        # Create a forecast object which will compute a fuel price forecast
        fuel_model = FuelForecast(id, fuel_df)
        ret = fuel_model.forecast()
        
        return {'forecast': ret}, 201


class FuelForecast(object):
    """
    An object used for forecasting monthly fuel price for a given fuel type in a Sydney suburb
    """
    def __init__(self, id, df):
        self.query_cols = df.columns.values[2:]
        self.query_vals = df.loc[id].values[2:]
        self.query_frame = {}
        self.forecast_lags = None

    def forecast(self):
        """
        Call to forecast a fuel price given a fuel type
        """
        nonzero_count = np.count_nonzero(self.query_vals)
        if nonzero_count in range(0, 11):
            return "No data"
        model = self.create_model()
        y_hat = model.predict(self.forecast_lags)
        if len(y_hat) > 1:
            return y_hat[0]
        else:
            return "N/A"

    def create_model(self):
        """
        Create forecast model (trained based on split percentage)
        """
        self.query_frame = { 'price': self.query_vals }
        query_df = pd.DataFrame(self.query_frame, index=self.query_cols)
        query_df.index.rename('month', inplace=True)
        
        # Remove any rows containing zeroes as price
        query_df.price.replace(0, pd.np.nan, inplace=True)
        query_df.dropna(axis=0, how='any', inplace=True)
        
        # Simulate an auto-regressive time series with 3 lags AR(3)
        query_x = []
        query_y = []
        for i in range(3,query_df.shape[0]):
            '''
            creates a set of independent x variables for each y value
            which are equal to the first 3 lags of the current (ith) y value
            '''
            x = query_df.iloc[i-3:i].values.reshape(-1)
            y = query_df.iloc[i].values[0]
            query_x.append(x)
            query_y.append(y)

        query_x = np.array(query_x)
        query_y = np.array(query_y)
        
        '''
        Create three lagged values which will be used as the auto-regressive variables
           AR(3)  ;  Y(t+1) = b0Y(t=0) + b1Y(t-1) + b2Y(t-2) + e
        '''
        final_array = query_y.tolist()[-3:]
        forecast_x_list = query_x.tolist()
        forecast_x_list[-1] = final_array
        self.forecast_lags = np.array(forecast_x_list)
        
        forecast_model = self.train_model(query_x, query_y, split_percentage = 0.8)
        
        return forecast_model

    def train_model(self, query_x, query_y, split_percentage):
        """
        Trains the time-series ML Model based on the split percentage
        """
        split_point = int(len(query_y) * split_percentage)
        
        query_X_train = query_x[:split_point]
        query_y_train = query_y[:split_point]
        
        model = LinearRegression()
        model.fit(query_X_train, query_y_train)
        
        return model


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/suburbs/suburbs.csv', index_col='id')
