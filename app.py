"""
Flask App entrypoint
"""

import os
from datetime import timedelta

from flask import Flask, request
from flask_jwt_extended import JWTManager

from encoders import MongoJSONEncoder, ObjectIdConverter
from api import api
from cli import (
    connect_command, fill_command, update_command,
    erase_command, classify_command, stats_command,
    classify_one_command
)


app = Flask(__name__, static_url_path='/static/', static_folder='client')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_COOKIE_SECURE'] = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_COOKIE_SAMESITE'] = "Strict"

JWTManager(app)

app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter

app.register_blueprint(api, url_prefix='/api')


@app.route('/')
@app.errorhandler(404)
def _root(error=None):
    if request.path.startswith('/api/'):
        return error, 404

    return app.send_static_file('index.html')


app.cli.add_command(fill_command)
app.cli.add_command(update_command)
app.cli.add_command(erase_command)
app.cli.add_command(classify_command)
app.cli.add_command(classify_one_command)
app.cli.add_command(stats_command)
app.cli.add_command(connect_command)

if __name__ == '__main__':
    app.run()
