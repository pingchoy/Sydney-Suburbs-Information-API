"""
schools.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Sydney school information
"""
import pandas as pd
from flask import Flask
from flask_restplus import Resource, Namespace
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from sklearn import linear_model
from sklearn.utils import shuffle
import json
import math

app = Flask(__name__)
api = Namespace('schools', description='Information on Sydney schools')

school_model = api.model('School', {
    'id': fields.Integer(description='The unique identifier for the school'),
    'name': fields.String(description='Name of the school'),
    'street': fields.String(description='Street of address'),
    'suburb': fields.String(description='Suburb of address'),
    'postcode': fields.Integer(description='Postcode of address'),
    'suburb_id': fields.Integer(description='Id of the suburb of this school'),
    'type': fields.String(description='School type (public or private)'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(school_model))
})

parser = reqparse.RequestParser()
parser.add_argument('order', choices=list(column for column in school_model.keys()), help='Field to order by')
parser.add_argument('ascending', type=inputs.boolean, help='Sort in ascending or descending order')
parser.add_argument('page', type=int, required=False, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, required=False, choices=[25, 50, 100], default=25, help='Number of results to return per page')
parser.add_argument('postcode', type=int, help="Post code of the school")
parser.add_argument('type', choices=['public', 'private'], help="School type (public or private)")


@api.route('/')
class SchoolsList(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(404, 'Page not found')
    @api.doc(description="Get a list of all public and private schools")
    @api.marshal_list_with(page_of_results)
    @api.expect(parser, validate=True)
    def get(self):
        """
        Returns a list of schools in Sydney
        """
        # get Schools as JSON string
        args = parser.parse_args()

        # retrieve the query parameters
        order_by = args.get('order')
        ascending = args.get('ascending', True)
        postcode = args.get('postcode')
        school_type = args.get('type')

        # Set default args
        order_by = order_by if order_by else 'id'
        ascending = ascending if ascending is not None else True

        # Make a reference to the dataset
        schools_df = df

        # Filter by post code
        if postcode:
            schools_df = schools_df[schools_df['postcode'] == postcode]

        if school_type:
            schools_df = schools_df[schools_df['type'] == school_type]

        # Apply ordering
        schools_df.sort_values(by=order_by, inplace=True, ascending=ascending)

        # Apply pagination
        page = args.get('page')
        per_page = args.get('per_page')
        count = len(schools_df)
        pages = math.ceil(count / per_page) if count else 1

        # Throw 404 when page is out of range
        if count and page > pages:
            api.abort(404, 'Page not found')

        if count:
            slice_from = (page - 1) * per_page
            slice_to = slice_from + per_page
            schools_df = schools_df[slice_from:slice_to]

        json_str = schools_df.to_json(orient='index')

        # convert the string JSON to a real JSON
        ds = json.loads(json_str)
        ret = []

        # add prediction to return
        for idx in ds:
            school = ds[idx]
            school['id'] = int(idx)
            ret.append(school)

        return {
            'page': page,
            'total': count,
            'pages': pages,
            'per_page': per_page,
            'results': api.marshal(ret, school_model),
        }


@api.route('/<int:id>')
@api.param('id', 'The school id')
class Schools(Resource):

    @api.response(200, 'Successful', school_model)
    @api.response(404, 'School was not found')
    @api.doc(description="Get a school by its ID")
    @api.marshal_with(school_model)
    def get(self, id):
        """
        Returns a school by its id
        """
        if id not in df.index:
            api.abort(404, "School with id {} doesn't exist".format(id))

        school = dict(df.loc[id])
        school['id'] = id

        return school


@api.route('/<int:id>/predict/')
@api.param('id', 'The school id')
class Predict(Resource):

    @api.response(200, 'Successful')
    @api.response(404, 'School was not found')
    @api.doc(description="Predict school size")
    def get(self, id):
        """
        Predict the number of students at a school
        """
        if id not in df.index:
            api.abort(404, "Unable to find school with id {}").format(id)

        school = df.loc[id]
        name = school['name']

        predict = Predict()
        ret = predict.predict(name)
        return {'size': ret}


pd.options.mode.chained_assignment = None
df = pd.read_csv('API/schools/schools.csv', index_col=0)


class Predict(object):
    """
    Class for predicting school sizes in Sydney
    """
    def predict(self, school_name):
        """
        Make a prediction
        """
        csv_file = "API/schools/headcount.csv"
        df = pd.read_csv(csv_file, index_col=0)
        head_X_train, head_y_train, head_X_test, head_y_test = self.load_headcount(split_percentage=0.7)
        model = linear_model.LinearRegression()
        model.fit(head_X_train, head_y_train)
        school_data_x = self.get_school_data(school_name)
        if df['School_Name'].str.contains(school_name).any():
            y_pred = model.predict(school_data_x)
            return y_pred[0]
        else:
            return "N/A"


    def load_headcount(self, split_percentage):
        """
        Load headcount data
        """
        csv_file = "API/schools/headcount.csv"
        df = pd.read_csv(csv_file, index_col=0)

        df = shuffle(df)
        row = df.iloc[:, 2:]
        row.astype(int)

        head_count_x = df.iloc[:, 2:16].values
        head_count_y = df.iloc[:, 16].values

        # Split the dataset in train and test data
        # A random permutation, to split the data randomly
        split_point = int(len(head_count_x) * split_percentage)
        head_X_train = head_count_x[:split_point]
        head_y_train = head_count_y[:split_point]
        head_X_test = head_count_x[split_point:]
        head_y_test = head_count_y[split_point:]

        return head_X_train, head_y_train, head_X_test, head_y_test


    def get_school_data(self, name):
        """
        Load school data for training the ML Model
        """
        csv_file = "API/schools/headcount.csv"
        df = pd.read_csv(csv_file, index_col=0)
        school_data = df.loc[df['School_Name'] == name]
        school_data_x = school_data.iloc[:, 2:16].values

        return school_data_x
