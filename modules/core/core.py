import inspect
import pprint

import sqlite3
from flask import make_response, g
import datetime
from datetime import datetime
from flask.views import MethodView
from flask_classy import FlaskView, route

from time import localtime, strftime
from functools import wraps, update_wrapper


from props import *

from hardware import *

import time
import uuid


class NotificationAPI(object):
    pass

class ActorAPI(object):

    def init_actors(self):
        self.app.logger.info("Init Actors")
        t = self.cache.get("actor_types")
        for key, value in t.iteritems():
            value.get("class").api = self
            value.get("class").init_global()

        for key in self.cache.get("actors"):
            self.init_actor(key)

    def init_actor(self, id):
        try:
            value = self.cache.get("actors").get(int(id))
            cfg = value.config.copy()
            cfg.update(dict(api=self, id=id, name=value.name))
            clazz = self.cache.get("actor_types").get(value.type).get("class")
            value.instance = clazz(**cfg)
            value.instance.init()
            value.state = 0
            value.power = 100
        except Exception as e:
            self.notify("Actor Error", "Failed to setup actor %s. Please check the configuraiton" % value.name,
                        type="danger", timeout=None)
            self.app.logger.error("Initializing of Actor %s failed" % id)

    def switch_actor_on(self, id, power=None):
        actor = self.cache.get("actors").get(id)

        if actor.state == 1:
            return

        actor.instance.on(power=power)
        actor.state = 1
        if power is not None:

            actor.power = power
        self.emit("SWITCH_ACTOR", actor)

    def actor_power(self, id, power=100):
        actor = self.cache.get("actors").get(id)
        actor.instance.set_power(power=power)
        actor.power = power
        self.emit("SWITCH_ACTOR", actor)

    def switch_actor_off(self, id):
        actor = self.cache.get("actors").get(id)

        if actor.state == 0:
            return
        actor.instance.off()
        actor.state = 0
        self.emit("SWITCH_ACTOR", actor)

class SensorAPI(object):

    def init_sensors(self):
        '''
        Initialize all sensors
        :return: 
        '''

        self.app.logger.info("Init Sensors")

        t = self.cache.get("sensor_types")
        for key, value in t.iteritems():
            value.get("class").init_global()

        for key in self.cache.get("sensors"):
            self.init_sensor(key)

    def stop_sensor(self, id):

        try:
            self.cache.get("sensors").get(id).instance.stop()
        except Exception as e:

            self.app.logger.info("Stop Sensor Error")
            pass


    def init_sensor(self, id):
        '''
        initialize sensor by id
        :param id: 
        :return: 
        '''

        def start_active_sensor(instance):
            '''
            start active sensors as background job
            :param instance: 
            :return: 
            '''
            instance.execute()

        try:
            if id in self.cache.get("sensor_instances"):
                self.cache.get("sensor_instances").get(id).stop()
            value = self.cache.get("sensors").get(id)

            cfg = value.config.copy()
            cfg.update(dict(api=self, id=id, name=value.name))
            clazz = self.cache.get("sensor_types").get(value.type).get("class")
            value.instance = clazz(**cfg)
            value.instance.init()
            if isinstance(value.instance, SensorPassive):
                # Passive Sensors
                value.mode = "P"
            else:
                # Active Sensors
                value.mode = "A"
                t = self.socketio.start_background_task(target=start_active_sensor, instance=value.instance)

        except Exception as e:

            self.notify("Sensor Error", "Failed to setup Sensor %s. Please check the configuraiton" % value.name, type="danger", timeout=None)
            self.app.logger.error("Initializing of Sensor %s failed" % id)

    def receive_sensor_value(self, id, value):
        self.emit("SENSOR_UPDATE", self.cache.get("sensors")[id])
        self.save_to_file(id, value)

    def save_to_file(self, id, value, prefix="sensor"):
        filename = "./logs/%s_%s.log" % (prefix, str(id))
        formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        msg = str(formatted_time) + "," +str(value) + "\n"

        with open(filename, "a") as file:
            file.write(msg)

    def log_action(self, text):
        filename = "./logs/action.log"
        formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        with open(filename, "a") as file:
            text = text.encode("utf-8")
            file.write("%s,%s\n" % (formatted_time, text))

    def shutdown_sensor(self, id):
        self.cache.get("sensors")[id].stop()


    def get_sensor_value(self, id):
        try:
            id = int(id)
            return float(self.cache.get("sensors")[id].instance.last_value)
        except Exception as e:

            return None

class CacheAPI(object):

    def get_sensor(self, id):
        try:
            return self.cache["sensors"][id]
        except:
            return None

    def get_actor(self, id):
        try:
            return self.cache["actors"][id]
        except:
            return None

class CraftBeerPi(ActorAPI, SensorAPI):

    cache = {
        "init": {},
        "config": {},
        "actor_types": {},
        "sensor_types": {},
        "sensors": {},
        "sensor_instances": {},
        "init": [],
        "background":[],
        "step_types": {},
        "controller_types": {},
        "messages": [],
        "plugins": {},
        "fermentation_controller_types": {},
        "fermenter_task": {}
    }
    buzzer = None
    eventbus = {}


    # constructor
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio


    def emit(self, key, data):
        self.socketio.emit(key, data, namespace='/brew')

    def notify(self, headline, message, type="success", timeout=5000):
        self.beep()
        msg = {"id": str(uuid.uuid1()), "type": type, "headline": headline, "message": message, "timeout": timeout}
        self.emit_message(msg)

    def beep(self):
        if self.buzzer is not None:
            self.buzzer.beep()


    def add_cache_callback(self, key,  method):
        method.callback = True
        self.cache[key] = method

    def get_config_parameter(self, key, default):
        cfg = self.cache.get("config").get(key)

        if cfg is None:
            return default
        else:
            return cfg.value

    def set_config_parameter(self, name, value):
        from modules.config import Config
        with self.app.app_context():
            update_data = {"name": name, "value": value}
            self.cache.get("config")[name].__dict__.update(**update_data)
            c = Config.update(**update_data)
            self.emit("UPDATE_CONFIG", c)


    def add_config_parameter(self, name, value, type, description, options=None):
        from modules.config import Config
        with self.app.app_context():
            c = Config.insert(**{"name":name, "value": value, "type": type, "description": description, "options": options})
            if self.cache.get("config") is not None:
                self.cache.get("config")[c.name] = c

    def clear_cache(self, key, is_array=False):
        if is_array:
            self.cache[key] = []
        else:
            self.cache[key] = {}

    # helper method for parsing props
    def __parseProps(self, key, cls):
        name = cls.__name__
        self.cache[key][name] = {"name": name, "class": cls, "properties": [], "actions": []}
        tmpObj = cls()
        members = [attr for attr in dir(tmpObj) if not callable(getattr(tmpObj, attr)) and not attr.startswith("__")]
        for m in members:
            if isinstance(tmpObj.__getattribute__(m), Property.Number):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append(
                    {"name": m, "label": t.label, "type": "number", "configurable": t.configurable, "description": t.description, "default_value": t.default_value})
            elif isinstance(tmpObj.__getattribute__(m), Property.Text):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append(
                    {"name": m, "label": t.label, "type": "text", "configurable": t.configurable, "default_value": t.default_value, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Select):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append(
                    {"name": m, "label": t.label, "type": "select",  "configurable": True, "options": t.options, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Actor):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "actor",  "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Sensor):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "sensor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Kettle):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "kettle", "configurable": t.configurable, "description": t.description})

        for name, method in cls.__dict__.iteritems():
            if hasattr(method, "action"):
                label = method.__getattribute__("label")
                self.cache[key][cls.__name__]["actions"].append({"method": name, "label": label})


        return cls


    def actor(self, cls):
        return self.__parseProps("actor_types", cls)



    def actor2(self, description="", power=True, **options):

        def decorator(f):
            print f()
            print f
            print options
            print description
            return f
        return decorator

    def sensor(self, cls):
        return self.__parseProps("sensor_types", cls)

    def controller(self, cls):
        return self.__parseProps("controller_types", cls)

    def fermentation_controller(self, cls):
        return self.__parseProps("fermentation_controller_types", cls)

    def get_controller(self, name):
        return self.cache["controller_types"].get(name)

    def get_fermentation_controller(self, name):
        return self.cache["fermentation_controller_types"].get(name)


    # Step action
    def action(self,label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator

    # step decorator
    def step(self, cls):

        key = "step_types"
        name = cls.__name__
        self.cache[key][name] = {"name": name, "class": cls, "properties": [], "actions": []}

        tmpObj = cls()
        members = [attr for attr in dir(tmpObj) if not callable(getattr(tmpObj, attr)) and not attr.startswith("__")]
        for m in members:
            if isinstance(tmpObj.__getattribute__(m), StepProperty.Number):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "number", "configurable": t.configurable, "default_value": t.default_value, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), StepProperty.Text):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "text", "configurable": t.configurable, "default_value": t.default_value, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), StepProperty.Select):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "select", "configurable": True, "options": t.options, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), StepProperty.Actor):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "actor",  "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), StepProperty.Sensor):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "sensor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), StepProperty.Kettle):
                t = tmpObj.__getattribute__(m)
                self.cache[key][name]["properties"].append({"name": m, "label": t.label, "type": "kettle", "configurable": t.configurable, "description": t.description})

        for name, method in cls.__dict__.iteritems():
            if hasattr(method, "action"):
                label = method.__getattribute__("label")
                self.cache[key][cls.__name__]["actions"].append({"method": name, "label": label})

        return cls


    # Event Bus
    def event(self, name, async=False):

        def real_decorator(function):
            if self.eventbus.get(name) is None:
                self.eventbus[name] = []
            self.eventbus[name].append({"function": function, "async": async})
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)
            return wrapper
        return real_decorator

    def emit_message(self, message):
        self.emit_event(name="MESSAGE", message=message)

    def emit_event(self, name, **kwargs):
        for i in self.eventbus.get(name, []):
            if i["async"] is False:
                i["function"](**kwargs)
            else:
                t = self.socketio.start_background_task(target=i["function"], **kwargs)

    # initializer decorator
    def initalizer(self, order=0):
        def real_decorator(function):
            self.cache["init"].append({"function": function, "order": order})
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)
            return wrapper
        return real_decorator



    def try_catch(self, errorResult="ERROR"):
        def real_decorator(function):
            def wrapper(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except:
                    self.app.logger.error("Exception in function %s. Return default %s" % (function.__name__, errorResult))
                    return errorResult
            return wrapper

        return real_decorator

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

    def init_kettle(self, id):
        try:
            value = self.cache.get("kettle").get(id)
            value["state"] = False
        except:
            self.notify("Kettle Setup Faild", "Please check %s configuration" % value.name, type="danger", timeout=None)
            self.app.logger.error("Initializing of Kettle %s failed" % id)


    def run_init(self):
        '''
        call all initialziers after startup
        :return: 
        '''
        self.app.logger.info("Invoke Init")
        self.cache["init"] = sorted(self.cache["init"], key=lambda k: k['order'])
        for i in self.cache.get("init"):
            self.app.logger.info("INITIALIZER - METHOD %s PAHT %s: " % (i.get("function").__name__, str(inspect.getmodule(i.get("function")).__file__) ))
            i.get("function")(self)



    def backgroundtask(self, key, interval, config_parameter=None):

        '''
        Background Task Decorator
        :param key: 
        :param interval: 
        :param config_parameter: 
        :return: 
        '''
        def real_decorator(function):
            self.cache["background"].append({"function": function, "key": key, "interval": interval, "config_parameter": config_parameter})
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)
            return wrapper
        return real_decorator

    def run_background_processes(self):
        '''
        call all background task after startup
        :return: 
        '''
        self.app.logger.info("Start Background")

        def job(interval, method):
            while True:
                try:
                    method(self)
                except Exception as e:
                    self.app.logger.error("Exception" + method.__name__ + ": " + str(e))
                self.socketio.sleep(interval)


        for  value in self.cache.get("background"):
            t = self.socketio.start_background_task(target=job,  interval=value.get("interval"),  method=value.get("function"))
