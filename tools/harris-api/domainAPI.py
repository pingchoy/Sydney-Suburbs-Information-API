from flask import Flask, request
from flask_restplus import Resource, Api, fields
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests, datetime, re
import operator, functools
import urllib.request
import json

app = Flask(__name__)
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
api = Api(app,
          title = "Assignment 2 - Harris Phan's Section - Properties")
          
suburb_model = api.model('suburb', {
  'suburb': fields.String(),
})

suburb_model = api.model('suburb', {
  'suburb': fields.Integer(),
})

params = {
    'api_key': 'key_2ea69bf3540b176b4b95eb87e6e97d67',
}

def AddressLocator(suburb):
    url_endpoint = 'https://api.domain.com.au/v1/addressLocators?searchLevel=Suburb&suburb='f'{suburb}&state=NSW'.format(suburb=suburb)
    return url_endpoint
    
def PropertyPrices(suburbId):
    url_endpoint = 'https://api.domain.com.au/v1/suburbPerformanceStatistics?state=nsw&suburbId='f'{suburbId}&propertyCategory=house&chronologicalSpan=12&tPlusFrom=1&tPlusTo=3&values=HighestSoldPrice%2CLowestSoldPrice'.format(suburbId=suburbId)
    return url_endpoint

@api.route('/addressLocators')
class Suburb(Resource):
    @api.doc(description = "Get Suburb IDs")
    @api.response(200, 'Successful retrieval')
    @api.response(201, 'Successful creation')
    @api.response(400, 'Unable to retrieve or create')
    @api.expect(suburb_model)
    def post(self):
        suburb = request.json['suburb']
        if ' ' in suburb == True:
            suburb_name = suburb.replace(' ', '%20')
            suburb_name = suburb_name.strip()
        response = requests.get(AddressLocator(suburb),params=params).json()[0]
        
        data_collection = {
            #"suburb": str(response['addressComponents'][0]['shortName']),
            "suburb": response['addressComponents'][0]['shortName'],
            "suburb_id": response['ids'][0]['id']
        }
        
        return data_collection

#@api.route('/suburbPerformanceStatistics')
#class HousePrices(Resource):
#    @api.doc(description = "Get House prices for a suburb ID")
#    @api.response(200, 'Successful retrieval')
#    @api.response(201, 'Successful creation')
#    @api.response(400, 'Unable to retrieve or create')
#    @api.expect(suburb_id)
#       def post(self):
#       suburb_id = request.json['suburb_id']
        
        

if __name__ == '__main__':

    app.run(debug=True)


 