#domain 
import pandas as pd
from flask import Flask, request
import requests, datetime, re
import csv

params = {
    'api_key': 'key_4bb3b3b55069d1cfb935829a3edbf399',
}

def getsuburbs(csv):
    suburbsData = pd.read_csv(csv_file)
    #print(suburbsData['name'].ravel())
    return suburbsData['name'].ravel()
    
def AddressLocator(suburb):
    url_endpoint = 'https://api.domain.com.au/v1/addressLocators?searchLevel=Suburb&suburb='f'{suburb}&state=NSW'.format(suburb=suburb)
    return url_endpoint
    
def PropertyPrices(suburbId):
    url_endpoint = 'https://api.domain.com.au/v1/suburbPerformanceStatistics?state=NSW&suburbId='f'{suburbId}&propertyCategory=house&chronologicalSpan=12&tPlusFrom=1&tPlusTo=1'.format(suburbId=suburbId)
    return url_endpoint

def getids(suburblist):
    idlist = []
    for j in range(len(suburblist)):
        suburb = suburblist[j]
        print(suburb)
        if ' ' in suburb == True:
            suburb_name = suburb.replace(' ', '%20')
            suburb_name = suburb_name.strip()
        response = requests.get(AddressLocator(suburb),params=params)
        if response.status_code != 404:
            responsejson = response.json()[0]
            idlist.append(str(responsejson['ids'][0]['id']))
    
    return idlist
    
def arraywriter(idlist):
    wtr = csv.writer(open ('suburbIds.csv', 'w'), delimiter=',', lineterminator='\n')
    for x in idlist : wtr.writerow ([x])
    
def get_details():
    suburbsID = pd.read_csv('suburbIds.csv')
    suburbIDlist = suburbsID['suburbID'].ravel()
    #response = requests.get(PropertyPrices(suburbIDlist[1]),params=params)
    #responsejson = response.json()
    suburbprices = {}
    #Important... loop through limited amount of suburbs otherwise you will go over the 500 call limit;
    #379 - start at the 379th element all to way to the 579th. 
    for j in range(379,579 + 1):
        suburbID = suburbIDlist[j]

        response = requests.get(PropertyPrices(suburbID),params=params)
        #print(response.status_code)
        print('Suburb ID: ' + str(suburbID))
        if response.status_code != 404:
            responsejson = response.json()
            if responsejson:
                suburbprices[responsejson['header']['suburb']] = [responsejson['series']['seriesInfo'][0]['values']['medianSoldPrice'],responsejson['series']['seriesInfo'][0]['values']['lowestSoldPrice'],
                                                                     responsejson['series']['seriesInfo'][0]['values']['highestSoldPrice'],responsejson['series']['seriesInfo'][0]['values']['medianRentListingPrice']]

            
            
    return suburbprices
     
            
def return_csvs(csv_name,sdict):
    df = pd.DataFrame.from_dict(sdict,orient='index')
    print(df)
    df.to_csv(csv_name)
    
        
    
    
    
    


if __name__ == '__main__':
    #csv_file = 'suburbs.csv'
    #suburblist = getsuburbs(csv_file)
    #idlist = getids(suburblist)
    #print(idlist)
    #arraywriter(idlist)
    suburbprices = get_details()
    return_csvs('suburb_property_prices_201909_pt3.csv',suburbprices)

    
    
    
    