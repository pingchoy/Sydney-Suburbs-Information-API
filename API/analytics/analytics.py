"""
analytics.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

API usage analytics.
"""
from flask import Flask
from flask_restplus import Resource, Namespace
from flask_restplus import fields
from flask_restplus import reqparse
from flask import send_file
from flask import request
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import math
from ..auth import RequiresAuth

app = Flask(__name__)
api = Namespace('analytics', description='API usage stats')

analytics_model = api.model('analytics', {
    'id': fields.Integer,
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_results = api.inherit('Page of results', pagination, {
    'results': fields.List(fields.Nested(analytics_model))
})

parser = reqparse.RequestParser()
parser.add_argument('page', type=int, required=False, default=1, help='Page number to retrieve')
parser.add_argument('per_page', type=int, required=False, choices=[25, 50, 100], default=25, help='Number of results to return per page')


@api.route('/')
class Analytics(Resource):

    @api.response(200, 'Successful')
    @api.response(400, 'Invalid request parameters')
    @api.response(401, 'Not authorised')
    @api.response(404, 'Not found')
    @api.doc(description="API usage stats")
    @api.produces(['application/json', 'image/png'])
    @api.expect(parser, validate=True)
    @RequiresAuth('admin')
    def get(self):
        """
        Returns a list or graph of API activity
        """
        args = parser.parse_args()

        mimetype = request.accept_mimetypes.best_match(['application/json', 'image/png'])

        data = generate_analytics()

        if mimetype == 'application/json':
            # Apply pagination
            page = args.get('page')
            per_page = args.get('per_page')
            count = len(data)
            pages = math.ceil(count / per_page) if count else 1

            # Throw 404 when page is out of range
            if count and page > pages:
                api.abort(404, 'Page not found')

            if count:
                slice_from = (page - 1) * per_page
                slice_to = slice_from + per_page
                data = data[slice_from:slice_to]

            return {
                'page': page,
                'total': count,
                'pages': pages,
                'per_page': per_page,
                'results': data,
            }

        csv_file = 'parsed_log.csv'
        df = pd.read_csv(csv_file, names=['request_id'
                                          'request_time',
                                          'host',
                                          'request_type',
                                          'endpoint',
                                          'bin_number'])
        return generate_graph(df)


def add_record(request_id, request_time, host, request_type, endpoint):
    record = {
        'request_id': request_id,
        'request_time': request_time,
        'host': host,
        'request_type': request_type,
        'endpoint': endpoint
    }
    return record


TIME_INTERVAL = 60
CONSUMER_ENDPOINTS = ['crimes',
                      'fuel', 'food',
                      'property',
                      'restaurants',
                      'schools',
                      'stations',
                      'weather']


def generate_analytics():
    all_requests = []

    # Parse log file for valid API calls.
    try:
        log_file = open('log.log', 'r+')
        csv_file = open('parsed_log.csv', 'w+')
    except FileNotFoundError:
        # Create files if they dont exit
        open('log.log', 'a').close()
        open('parsed_log.csv', 'a').close()
        log_file = open('log.log', 'r+')
        csv_file = open('parsed_log.csv', 'w+')

    bin_number = 0
    first_line_read = False

    request_id = 0
    for line in log_file:
        if 'HTTP' in line and '200' in line:
            try:
                record = line.split()
                del record[2:6]
                del record[-3:]

                request_time, host, request_type, request_content = record
                request_time = float(request_time)

                if not first_line_read:
                    initial_time = float(request_time)
                    bin_threshold = initial_time + TIME_INTERVAL
                    first_line_read = True

                if request_time > bin_threshold:
                    bin_number += 1
                    bin_threshold += TIME_INTERVAL

                request_type = request_type.strip('"')
                endpoint = request_content.split('/')[1]

                if any(endpoint in line for endpoint in CONSUMER_ENDPOINTS):
                    csv_file.write(f'{request_id}, {request_time}, {host}, {request_type}, {endpoint}, {bin_number}\n')
                    request_id += 1
                    all_requests.append(add_record(request_id, request_time, host, request_type, endpoint))
            except:
                continue

    csv_file.close()

    return all_requests


def generate_graph(df):
    if len(df != 0):
        grouped = df['bin_number'].value_counts()
        lists = sorted(grouped.items())
        bin, requests = zip(*lists)

        f, ax = plt.subplots(2, 2, figsize = (10, 10))
        f.set_figheight(5)
        f.set_figwidth(15)
        plt.style.use('seaborn')
        plt.subplot(1, 2, 1)
        plt.plot(bin, requests)
        plt.xlabel('Uptime (1 minute intervals)', fontsize = 12)
        plt.ylabel('# API Requests', fontsize=12)
        plt.title('API Usage', fontsize=12)
        number_of_endpoints = len(df['endpoint'].unique())
        explode = tuple([0.05 for x in range(number_of_endpoints)]) if number_of_endpoints > 1 else None

        plt.subplot(1, 2, 2)
        wedges, texts, autotexts = plt.pie(df['endpoint'].value_counts(normalize=True) * 100,
                                           explode = explode,
                                           shadow=True,
                                           autopct='%1.1f%%')
        plt.legend(wedges,
                   df['endpoint'].unique(),
                   title="Endpoints",
                   loc="center left",
                   bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title(f"Endpoint distribution\n\nTotal requests: {len(df)}")
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        return send_file(buffer, as_attachment=False, mimetype='image/png', cache_timeout=-1)


