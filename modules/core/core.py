import json
import logging
import logging.config
import os
import sqlite3
import uuid
import yaml
from datetime import datetime
from functools import wraps, update_wrapper
from importlib import import_module
from time import localtime, strftime
import time

from flask import Flask, redirect, json, g, make_response
from flask_socketio import SocketIO

from baseapi import *
from db import DBModel
from modules.core.basetypes import Sensor, Actor
from modules.database.dbmodel import Kettle



class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        try:

            if isinstance(obj, DBModel):
                return obj.__dict__
            elif isinstance(obj, Actor):
                return {"state": obj.value}
            elif isinstance(obj, Sensor):
                return {"value": obj.value, "unit": obj.unit}
            elif hasattr(obj, "callback"):
                return obj()
            else:
                return None

            return None
        except TypeError as e:
            pass
        return None


class Addon(object):
    def __init__(self, cbpi):
        self.step = StepAPI(cbpi)
        self.actor = ActorAPI(cbpi)
        self.sensor = SensorAPI(cbpi)
        self.kettle = KettleAPI(cbpi)
        self.fermenter = FermenterAPI(cbpi)
        self.core = CoreAPI(cbpi)

    def init(self):
        self.core.init()
        self.step.init()
        self.actor.init()
        self.sensor.init()
        # self.kettle.init()
        # self.fermenter.init()


class ActorCore(object):
    key = "actor_types"

    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)

        self.cbpi = cbpi
        self.cbpi.cache["actors"] = {}
        self.cbpi.cache[self.key] = {}

    def init(self):
        for key, value in self.cbpi.cache["actors"].iteritems():
            self.init_one(key)

    def init_one(self, id):
        try:
            self.logger.info("INIT ONE ACTOR [%s]", id)
            actor = self.cbpi.cache["actors"][id]
            clazz = self.cbpi.cache[self.key].get(actor.type)["class"]
            cfg = actor.config.copy()
            cfg.update(dict(cbpi=self.cbpi, id=id))
            self.cbpi.cache["actors"][id].instance = clazz(**cfg)
            actor.state = 0
            actor.power = 100
            self.cbpi.emit("INIT_ACTOR", id=id)
        except Exception as e:
            self.logger.error(e)

    def stop_one(self, id):
        self.cbpi.cache["actors"][id]["instance"].stop()
        self.cbpi.emit("STOP_ACTOR", id=id)

    def on(self, id, power=100):
        try:
            actor = self.cbpi.cache["actors"].get(int(id))
            actor.instance.on()
            actor.state = 1
            actor.power = power
            self.cbpi.ws_emit("SWITCH_ACTOR", actor)
            self.cbpi.emit("SWITCH_ACTOR_ON", id=id, power=power)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def off(self, id):
        try:
            actor = self.cbpi.cache["actors"].get(int(id))
            actor.instance.off()
            actor.state = 0
            self.cbpi.ws_emit("SWITCH_ACTOR", actor)
            self.cbpi.emit("SWITCH_ACTOR_OFF", id=id)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def toggle(self, id):
        if self.cbpi.cache.get("actors").get(id).state == 0:
            self.on(id)
        else:
            self.off(id)

    def power(self, id, power):
        try:
            actor = self.cbpi.cache["actors"].get(int(id))
            actor.instance.power(power)
            actor.power = power
            self.cbpi.ws_emit("SWITCH_ACTOR", actor)
            self.cbpi.emit("SWITCH_ACTOR_POWER_CHANGE", id=id, power=power)
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def action(self, id, method):
        self.cbpi.cache.get("actors").get(id).instance.__getattribute__(method)()


    def toggle_timeout(self, id, seconds):

        def toggle( id, seconds):
            self.cbpi.cache.get("actors").get(int(id)).timer = int(time.time()) + int(seconds)
            self.toggle(int(id))
            self.cbpi.sleep(seconds)
            self.cbpi.cache.get("actors").get(int(id)).timer = None
            self.toggle(int(id))
        job = self.cbpi._socketio.start_background_task(target=toggle, id=id, seconds=seconds)

    def get_state(self, actor_id):
        self.logger.debug(actor_id)
        self.logger.debug(self.cbpi)


class SensorCore(object):
    key = "sensor_types"

    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)

        self.cbpi = cbpi
        self.cbpi.cache["sensors"] = {}
        self.cbpi.cache["sensor_instances"] = {}
        self.cbpi.cache["sensor_types"] = {}

    def init(self):
        for key, value in self.cbpi.cache["sensors"].iteritems():
            self.init_one(key)

    def init_one(self, id):
        try:
            sensor = self.cbpi.cache["sensors"][id]
            clazz = self.cbpi.cache[self.key].get(sensor.type)["class"]
            cfg = sensor.config.copy()
            cfg.update(dict(cbpi=self.cbpi, id=id))
            self.cbpi.cache["sensors"][id].instance = clazz(**cfg)
            self.cbpi.cache["sensors"][id].instance.init()
            self.logger.debug(self.cbpi.cache["sensors"][id].instance)
            self.cbpi.emit("INIT_SENSOR", id=id)

            def job(obj):
                obj.execute()

            t = self.cbpi._socketio.start_background_task(target=job, obj=self.cbpi.cache["sensors"][id].instance)
            self.cbpi.emit("INIT_SENSOR", id=id)

        except Exception as e:
            self.logger.error(e)

    def stop_one(self, id):
        self.logger.info("OBJ [%s]", self.cbpi.cache["sensors"][id])
        self.cbpi.cache["sensors"][id].instance.stop()
        self.cbpi.emit("STOP_SENSOR", id=id)

    def get_value(self, sensorid):
        try:
            return self.cbpi.cache["sensors"][sensorid].instance.value
        except:
            return None

    def get_state(self, actor_id):
        self.logger.info("Get state actor id [%s]", actor_id)
        self.logger.debug(self.cbpi)

    def write_log(self, id, value, prefix="sensor"):
        filename = "./logs/%s_%s.log" % (prefix, str(id))
        formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        msg = str(formatted_time) + "," + str(value) + "\n"

        with open(filename, "a") as file:
            file.write(msg)

    def action(self, id, method):
        self.cbpi.cache.get("sensors").get(id).instance.__getattribute__(method)()



class BrewingCore(object):
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.cache["step_types"] = {}
        self.cbpi.cache["controller_types"] = {}

    def log_action(self, text):
        filename = "./logs/action.log"
        formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        with open(filename, "a") as file:
            text = text.encode("utf-8")
            file.write("%s,%s\n" % (formatted_time, text))

    def get_controller(self, name):
        return self.cbpi.cache["controller_types"].get(name)

    def set_target_temp(self, id, temp):
        self.cbpi.cache.get("kettle")[id].target_temp = float(temp)
        Kettle.update(**self.cbpi.cache.get("kettle")[id].__dict__)
        self.cbpi.ws_emit("UPDATE_KETTLE_TARGET_TEMP", {"id": id, "target_temp": temp})
        self.cbpi.emit("SET_KETTLE_TARGET_TEMP", id=id, temp=temp)


    def toggle_automatic(self, id):
        kettle = self.cbpi.cache.get("kettle")[id]
        if kettle.state is False:
            # Start controller
            if kettle.logic is not None:
                cfg = kettle.config.copy()
                cfg.update(dict(api=cbpi, kettle_id=kettle.id, heater=kettle.heater, sensor=kettle.sensor))
                instance = self.get_controller(kettle.logic).get("class")(**cfg)
                instance.init()
                kettle.instance = instance

                def run(instance):
                    instance.run()

                t = self.cbpi._socketio.start_background_task(target=run, instance=instance)
            kettle.state = not kettle.state
            self.cbpi.ws_emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
            self.cbpi.emit("KETTLE_CONTROLLER_STARTED", id=id)
        else:
            # Stop controller
            kettle.instance.stop()
            kettle.state = not kettle.state
            self.cbpi.ws_emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
            self.cbpi.emit("KETTLE_CONTROLLER_STOPPED", id=id)


class FermentationCore(object):
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.cache["fermenter"] = {}
        self.cbpi.cache["fermentation_controller_types"] = {}

    def get_controller(self, name):
        return self.cbpi.cache["fermentation_controller_types"].get(name)


class CraftBeerPI(object):
    cache = {}
    eventbus = {}

    def __init__(self):
        #FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
        #logging.basicConfig(filename='./logs/app.log', level=logging.INFO, format=FORMAT)
        logging.config.dictConfig(yaml.load(open('./config/logger.yaml', 'r')))
        self.logger = logging.getLogger(__name__)

        self.cache["messages"] = []
        self.cache["version"] = "3.1"
        self.modules = {}

        self.addon = Addon(self)
        self.actor = ActorCore(self)
        self.sensor = SensorCore(self)
        self.brewing = BrewingCore(self)
        self.fermentation = FermentationCore(self)
        self._app = Flask(__name__)
        self._app.secret_key = 'Cr4ftB33rP1'
        self._app.json_encoder = ComplexEncoder
        self._socketio = SocketIO(self._app, json=json, logging=False)

        @self._app.route('/')
        def index():
            return redirect('ui')

    def run(self):
        self.__init_db()
        self.loadPlugins()
        self.addon.init()
        self.sensor.init()
        self.actor.init()
        self.beep()
        try:
            port = int(cbpi.get_config_parameter('port', '5000'))
        except ValueError:
            port = 5000
        self._socketio.run(self._app, host='0.0.0.0', port=port)

    def beep(self):
        self.buzzer.beep()

    def sleep(self, seconds):
        self._socketio.sleep(seconds)

    def notify(self, headline, message, type="success", timeout=5000):
        msg = {"id": str(uuid.uuid1()), "type": type, "headline": headline, "message": message, "timeout": timeout}
        self.ws_emit("NOTIFY", msg)

    def ws_emit(self, key, data):
        self._socketio.emit(key, data, namespace='/brew')

    def __init_db(self, ):
        self.logger.info("INIT DB")
        with self._app.app_context():
            db = self.get_db()
            try:
                with self._app.open_resource('../../config/schema.sql', mode='r') as f:
                    db.cursor().executescript(f.read())
                db.commit()
            except Exception as e:
                self.logger.error(e)
                pass

    def nocache(self, view):
        @wraps(view)
        def no_cache(*args, **kwargs):
            response = make_response(view(*args, **kwargs))
            response.headers['Last-Modified'] = datetime.now()
            response.headers[
                'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response

        return update_wrapper(no_cache, view)

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d

            db = g._database = sqlite3.connect('craftbeerpi.db')
            db.row_factory = dict_factory
        return db

    def add_cache_callback(self, key, method):
        method.callback = True
        self.cache[key] = method

    def get_config_parameter(self, key, default):
        cfg = self.cache["config"].get(key)
        if cfg is None:
            return default
        else:
            return cfg.value

    def emit(self, key, **kwargs):

        if self.eventbus.get(key) is not None:
            for value in self.eventbus[key]:
                if value["async"] is False:
                    value["function"](**kwargs)
                else:
                    t = self.cbpi._socketio.start_background_task(target=value["function"], **kwargs)

    def loadPlugins(self):
        for filename in os.listdir("./modules/plugins"):
            self.logger.info("Loading plugin [%s]", filename)
            if os.path.isdir("./modules/plugins/" + filename) is False:
                continue
            try:
                self.modules[filename] = import_module("modules.plugins.%s" % (filename))
            except Exception as e:
                self.logger.error(e)
                self.notify("Failed to load plugin %s " % filename, str(e), type="danger", timeout=None)


cbpi = CraftBeerPI()
addon = cbpi.addon
