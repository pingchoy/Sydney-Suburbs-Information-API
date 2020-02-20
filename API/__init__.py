from flask_restplus import Api
from .suburbs.suburbs import api as suburbs_ns
from .users.users import api as users_ns
from .schools.schools import api as schools_ns
from .restaurants.restaurants import api as restaurants_ns
from .stations.stations import api as stations_ns
from .crimes.crimes import api as crimes_ns
from .weather.weather import api as weather_ns
from .property.property import api as property_ns
from .fuel.fuel import api as fuel_ns
from .analytics.analytics import api as analytics_ns

api = Api(
    title='Sydney Data Services API',
    version='1.0',
    description='Analytics data on the city of Sydney, Australia',
    authorizations={
        'API-KEY': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'AUTH-TOKEN'
        }},
    security='API-KEY'
)

api.add_namespace(users_ns, path='')
api.add_namespace(suburbs_ns, path='/suburbs')
api.add_namespace(schools_ns, path='/schools')
api.add_namespace(restaurants_ns, path='/restaurants')
api.add_namespace(stations_ns, path='/train-stations')
api.add_namespace(crimes_ns, path='/crime-rates')
api.add_namespace(weather_ns, path='/weather')
api.add_namespace(property_ns, path='/property')
api.add_namespace(fuel_ns, path='/fuel-prices')
api.add_namespace(analytics_ns, path='/analytics')
