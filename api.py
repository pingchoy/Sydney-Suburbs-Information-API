"""
api.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Load and run the API modules.
"""
from flask import Flask
from API import api
import logging.config
import yaml

# Logging configuration
logging.config.dictConfig(yaml.load(open('logging.conf')))
log_file = logging.getLogger('file')
log_console = logging.getLogger('console')
log_file.debug("Debug FILE")
log_console.debug("Debug CONSOLE")

# Initialise app
app = Flask(__name__)
api.init_app(app)
app.config['RESTPLUS_MASK_SWAGGER'] = False


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


app.run(debug=True)
