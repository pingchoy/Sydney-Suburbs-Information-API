
"""
parsing.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

- Parse locally stored Zomato website HTML files
- Obtain suburb_id form master list
- Obtain restaurant ratings using google places API
- Export to JSON

Datasets used:
    Locally stored Zomato website HTML files.
"""


from bs4 import BeautifulSoup
import json
import pandas as pd
import requests

API_KEY = '' #Enter your google API key.

# CSS selectors
address_selector = "div > div.content > div > article > div.pos-relative.clearfix > div > div.col-s-16.col-m-12.pl0 > div:nth-child(2) > div"
cuisine_selector = "div > div.content > div > article > div.search-page-text.clearfix.row > div:nth-child(1) > span.col-s-11.col-m-12.nowrap.pl0 > a"
name_selector = "div > div.content > div > article > div.pos-relative.clearfix > div > div.col-s-16.col-m-12.pl0 > div:nth-child(1) > div.col-s-12 > a.result-title.hover_feedback.zred.bold.ln24.fontsize0"
cost_selector = 'div > div > div:nth-child(1) > article:nth-child(1) > div:nth-child(3) > div:nth-child(2) > span:nth-child(2)'
phone_selector = 'div > div.ui.two.item.menu.search-result-action.mt0 > a.item.res-snippet-ph-info'
price_selector = 'div.rating-popup:nth-child(2)'
container_selector = "#orig-search-list > div"

soup = BeautifulSoup(open('all_output.html'), "html.parser")
containers = soup.select(container_selector)
all_restaurants = []

csv_file = open('backup_data.csv', 'a')


def create_restaurant( id, name, address, cuisines, cost, suburb_id, rating, places_id):
    df = {
          'id': id,
          'name': name,
          'address': address,
          'cuisines': cuisines,
          'cost': int(cost.split('$')[1]),
          'rating': rating,
          'suburb_codde': suburb_id,
          'places_id': places_id
    }
    return df


def contains_digit(street_address):
    return any(char.isdigit() for char in street_address)


def add_new_restaurant(restaurant):
    all_restaurants.append(restaurant)


# Use google places API to get restaurant rating.
def get_restaurant_rating(restaurant):
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

    params = {'input': restaurant,
              'inputtype': 'textquery',
              'locationbias': 'ipbias',
              'key': API_KEY,
              'fields': 'rating,place_id'
              }

    r = requests.get(url, params=params)
    data = r.json()
    rating = data['candidates'][0]['rating']
    place_id = data['candidates'][0]['place_id']

    return [place_id, rating]


# Load master suburbs CSV
df_suburbs = pd.read_csv('../suburbs/suburbs.csv')

# Parse each restaurant
for i in range(len(containers)):
    try:
        sp = BeautifulSoup(str(containers[i]), "html.parser")
        cost = sp.select_one(cost_selector).text.strip()
        phone_number = sp.select_one(phone_selector)['data-phone-no-str']
        name = sp.select_one(name_selector).text.strip()

        address = sp.select_one(address_selector).text.strip().split(',')

        # Remove unnecessary address fields
        if not len(address) >= 3:
            continue
        address = address if len(address) == 3 else address[len(address)-3:]
        address_street, address_suburb, address_city = address[0].strip(), address[1].strip(), address[2].strip()

        if address_suburb == 'CBD':
            address_suburb = 'Sydney'

        # Skip if suburb isn't in suburbs df
        if not df_suburbs['name'].str.contains(address_suburb).any():
            continue

        # Skip if address doens't contain street number
        if not contains_digit(address_street):
            continue

        # get suburb code from suburbs_df
        try:
            suburb_id = int(df_suburbs[df_suburbs['name'] == address_suburb]['id'].values[0])
        except:
            continue

        address_string = f'{address_street.strip()} {address_suburb.strip()} Sydney NSW Australia'

        cuisines = []
        for x in sp.select(cuisine_selector):
            cuisines.append(x.text)

        places_api_results = get_restaurant_rating(name)
        place_id, rating = places_api_results[0], places_api_results[1]

        add_new_restaurant(create_restaurant(i, name, address_string, cuisines, cost, suburb_id, rating, place_id))
    except:
        continue

with open('food.json', 'w', encoding='utf-8') as f:
    json.dump(all_restaurants, f, ensure_ascii=False, indent=4)



