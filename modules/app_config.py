
import json
import sys, os
from flask import Flask, render_template, redirect, json, g


from flask_socketio import SocketIO, emit

import logging



from modules.core.core import CraftBeerPi, ActorBase, SensorBase
from modules.core.db import DBModel

app = Flask(__name__)

FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'

logging.basicConfig(filename='./logs/app.log',level=logging.INFO, format=FORMAT)
app.config['SECRET_KEY'] = 'craftbeerpi'
app.config['UPLOAD_FOLDER'] = './upload'


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, DBModel):
                return obj.__dict__
            elif isinstance(obj, ActorBase):
                return obj.state()
            elif isinstance(obj, SensorBase):
                return obj.get_value()
            elif hasattr(obj, "callback"):
                return obj()
            else:
                return None
        except TypeError as e:
            pass
        return None

app.json_encoder = ComplexEncoder
socketio = SocketIO(app, json=json, logging=False)
cbpi   = CraftBeerPi(app, socketio)

app.logger.info("##########################################")
app.logger.info("### NEW STARTUP Version 3.0")
app.logger.info("##########################################")