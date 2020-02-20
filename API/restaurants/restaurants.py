"""
restaurants.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Sydney restaurant information.
"""
import pandas as pd
from flask import Flask
from flask_restplus import Resource, Namespace
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
import json
import math

app = Flask(__name__)
api = Namespace('restaurants', description='Information on Sydney restaurants')

restaurant_model = api.model('Restaurant', {
    'id': fields.Integer(description='Unique identifier of this restaurant'),
    'rating': fields.Float(description='Rating out of 5'),
    'cuisines': fields.List(fields.String(), description='Type of cuisine served by this restaurant'),
    'name': fields.String(description='Name of the restaurant'),
    'address': fields.String(description=''),
    'cost': fields.Float(description='Average cost per meal for 2 people'),
    'suburb_id': fields.Integer(description='Suburb identifier')
})

restaurant_cuisines = ['Afghan', 'African', 'American', 'Arabian', 'Argentine', 'Asian', 'Asian Fusion', 'Australian',
                       'Austrian', 'BBQ', 'Bakery', 'Bangladeshi', 'Bar Food', 'Basque', 'Belgian', 'Beverages',
                       'Brasserie', 'Brazilian', 'British', 'Bubble Tea', 'Burger', 'Burmese', 'Cafe Food', 'Cambodian', 'Cantonese', 'Caribbean', 'Charcoal Chicken', 'Chinese', 'Coffee and Tea', 'Colombian', 'Contemporary', 'Continental', 'Creole', 'Crepes', 'Cuban', 'Danish', 'Deli', 'Desserts', 'Diner', 'Drinks Only', 'Dumplings', 'Eastern European', 'Egyptian', 'Ethiopian', 'European', 'Falafel', 'Fast Food', 'Fijian', 'Filipino', 'Finger Food', 'Fish and Chips', 'French', 'Fried Chicken', 'Frozen Yogurt', 'Fusion', 'German', 'Greek', 'Grill', 'Hawaiian', 'Healthy Food', 'Hot Pot', 'Hungarian', 'Ice Cream', 'Indian', 'Indonesian', 'International', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Japanese', 'Japanese BBQ', 'Juices', 'Kebab', 'Korean', 'Korean BBQ', 'Laotian', 'Latin American', 'Lebanese', 'Malatang', 'Malaysian', 'Meat Pie', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Modern Australian', 'Modern European', 'Mongolian', 'Moroccan', 'Nepalese', 'North Indian', 'Oriental', 'Pakistani', 'Pan Asian', 'Patisserie', 'Pho', 'Pizza', 'Poké', 'Polish', 'Portuguese', 'Pub Food', 'Ramen', 'Roast', 'Russian', 'Salad', 'Sandwich', 'Satay', 'Scandinavian', 'Seafood', 'Shanghai', 'Sichuan', 'Singaporean', 'Soul Food', 'South Indian', 'Spanish', 'Sri Lankan', 'Steak', 'Street Food', 'Sushi', 'Swedish', 'Swiss', 'Taiwanese', 'Tapas', 'Tea', 'Teppanyaki', 'Teriyaki', 'Tex-Mex', 'Thai', 'Tibetan', 'Turkish', 'Uruguayan', 'Uyghur', 'Vegan', 'Vegetarian', 'Venezuelan', 'Vietnamese', 'Yum Cha']


pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(restaurant_model))
})

parser = reqparse.RequestParser()
parser.add_argument('order', choices=list(column for column in restaurant_model.keys()), help='Field to order by')
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('page', type=int, required=False, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, required=False, choices=[25, 50, 100], default=25, help='Number of results to return per page')
parser.add_argument('cuisine', choices=restaurant_cuisines, help='Cuisine the restaurant serves')
parser.add_argument('suburb_id', type=int, help='Suburb id of the restaurant')
parser.add_argument('min_rating', type=int, choices=[x for x in range(1, 6)], help='Filter by minimum rating')


@api.route('/')
class Restaurants(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Get a list of all restaurants")
    @api.marshal_list_with(page_of_results)
    @api.expect(parser, validate=True)
    def get(self):
        """
        Returns a list of restaurants
        """
        # get restaurants as JSON string
        args = parser.parse_args()

        # retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        cuisine = args.get('cuisine')
        suburb_id = args.get('suburb_id')
        min_rating = args.get('min_rating')

        # Set default args
        order_by = order_by if order_by else 'id'
        ascending = ascending if ascending is not None else True

        # Make a reference to the dataset
        restaurants_df = df

        # Filter by suburb_id
        if suburb_id:
            restaurants_df = restaurants_df[restaurants_df['suburb_id'] == suburb_id]

        # Filter by cuisine
        if cuisine:
            restaurants_df = restaurants_df[restaurants_df['cuisines'].apply(lambda x: cuisine in x)]

        if min_rating:
            restaurants_df = restaurants_df[restaurants_df['rating'] >= min_rating]

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

        json_str = restaurants_df.to_json(orient='index')

        # convert the string JSON to a real JSON
        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            restaurant = ds[idx]
            restaurant['id'] = int(idx)
            ret.append(restaurant)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, restaurant_model),
        }


@api.route('/<int:id>')
@api.param('id', 'The restaurant id')
class Restaurant(Resource):

    @api.response(200, 'Successful', restaurant_model)
    @api.response(404, 'Restaurant not found')
    @api.doc(description="Retrieve a restaurant by its ID")
    @api.marshal_with(restaurant_model)
    def get(self, id):
        """
        Retrieve a Restaurant by its id
        """
        if id not in df.index:
            api.abort(404, "Restaurant with id {} doesn't exist".format(id))

        restaurant = dict(df.loc[id])
        restaurant['id'] = id
        return restaurant


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/restaurants/restaurants.csv', index_col='id', converters={'cuisines': eval})
