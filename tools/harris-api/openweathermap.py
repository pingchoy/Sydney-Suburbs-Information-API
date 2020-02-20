from flask import Flask, request
from flask_restplus import Resource, Api, fields
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests, datetime, re
import operator, functools
import urllib.request

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
api = Api(app,
          title = "Assignment 2 - Harris Phan's Section",
          description = """Aim:  to develop a Flask-Restplus data service 
          that allows a client to read
          and store some open weather data for Sydney suburbs, and allow the consumers to 
          access the data through a REST API. """
)


suburb_model = api.model('suburb', {
  'suburb': fields.String(),
})

def URL_api(city):
    URLstring = 'http://api.openweathermap.org/data/2.5/weather?q='f'{city},AU&appid=8098818c915438db8392de41103274cd'.format(city=city)
    return URLstring

def URL_forecast(city):
    URLforecast = 'http://api.openweathermap.org/data/2.5/forecast?q='f'{city},AU&cnt=7&appid=8098818c915438db8392de41103274cd'.format(city=city)
    return URLforecast    
    
    

@api.route('/suburb')
#@api.param('suburb','suburb')
class Weather(Resource):
    @api.doc(description = "Get Categories")
    @api.response(200, 'Successful retrieval')
    @api.response(201, 'Successful creation')
    @api.response(400, 'Unable to retrieve or create')
    @api.expect(suburb_model)
    def post(self):
        suburb = request.json['suburb']

        response = requests.get(URL_api(suburb)).json()

        data_collection = {
        "suburb": str(response['name']),
        "temp": str(round(response['main']['temp'] - 273.15,2)) + ' degrees Celsius',
        "pressure": str(response['main']['pressure']),
        "humidity": str(response['main']['humidity']),
        }
      
        return data_collection

@api.route('/suburbForecast')
class WeatherForecast(Resource):
    @api.doc(description = "Get Categories")
    @api.response(200, 'Successful retrieval')
    @api.response(201, 'Successful creation')
    @api.response(400, 'Unable to retrieve or create')
    @api.expect(suburb_model)
    def post(self):
        suburb = request.json['suburb']

        response = requests.get(URL_forecast(suburb)).json()
        #suburb_dict = {}
        min_temp = []
        max_temp = []
        conditions = []
        
        for j in range(7):
            min_temp.append(round(response['list'][j]['main']['temp_min'] - 273.15, 2))
            max_temp.append(round(response['list'][j]['main']['temp_max'] - 273.15, 2))
            conditions.append(response['list'][j]['weather'][0]['main'])
        data_collection = {
        "suburb": str(response['city']['name']),
        "Minimum Temperature": min_temp,
        "Maximum Temperature": max_temp,
        "Conditions": conditions
        }
        return data_collection
        




if __name__ == '__main__':

    app.run(debug=True)
