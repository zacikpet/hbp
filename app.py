import os
from datetime import timedelta

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.routing import BaseConverter

from api import api
from commands import connect_command, fill_command, update_command, erase_command, classify_command, stats_command
from encoders import MongoJSONEncoder, ObjectIdConverter

app = Flask(__name__, static_url_path='/static/', static_folder='build')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config["JWT_COOKIE_SAMESITE"] = 'None'

jwt = JWTManager(app)

CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'
app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter

app.register_blueprint(api, url_prefix='/api')


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

'''
@app.route('/', defaults={'path': ''})
@app.route('/<regex(".*"):path>/')
def root(path):
    return app.send_static_file('index.html')
'''

app.cli.add_command(fill_command)
app.cli.add_command(update_command)
app.cli.add_command(erase_command)
app.cli.add_command(classify_command)
app.cli.add_command(stats_command)
app.cli.add_command(connect_command)

if __name__ == '__main__':
    app.run()
