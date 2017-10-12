import logging

from proptypes import *

class BaseAPI(object):

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.cache[self.key] = {}


    def init(self):
        for name, value in self.cbpi.cache[self.key].iteritems():

            value["class"].init_global()

    def parseProps(self, key, cls, **options):

        name = cls.__name__
        tmpObj = cls()

        try:
            doc = tmpObj.__doc__.strip()
        except:
            doc = ""

        self.cbpi.cache.get(key)[name] = {"name": name, "class": cls, "description":doc, "properties": [], "actions": []}
        self.cbpi.cache.get(key)[name].update(options)
        members = [attr for attr in dir(tmpObj) if not callable(getattr(tmpObj, attr)) and not attr.startswith("__")]
        for m in members:
            t = tmpObj.__getattribute__(m)

            if isinstance(t, Property.Number):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "number", "configurable": t.configurable, "description": t.description, "default_value": t.default_value})
            elif isinstance(t, Property.Text):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "text", "required": t.required, "configurable": t.configurable, "description": t.description, "default_value": t.default_value})
            elif isinstance(tmpObj.__getattribute__(m), Property.Select):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "select",  "configurable": True, "options": t.options, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Actor):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "actor",  "configurable": True, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Sensor):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "sensor", "configurable": True, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Kettle):
                self.cbpi.cache.get(key)[name]["properties"].append({"name": m, "label": t.label, "type": "kettle", "configurable": True, "description": t.description})

        for method_name, method in cls.__dict__.iteritems():
            if hasattr(method, "action"):
                label = method.__getattribute__("label")
                self.cbpi.cache.get(key)[name]["actions"].append({"method": method_name, "label": label})

        return cls


class SensorAPI(BaseAPI):

    key = "sensor_types"

    def type(self, description="Step", **options):
       def decorator(f):
            BaseAPI.parseProps(self, self.key,f, description=description)
            return f
       return decorator

    def action(self, label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator


class StepAPI(BaseAPI):

    key = "step_types"

    def init(self):
        pass

    def type(self, description="Step", **options):
       def decorator(f):
            BaseAPI.parseProps(self, self.key,f, description=description)
            return f
       return decorator

    def action(self, label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator




class ActorAPI(BaseAPI):

    key = "actor_types"

    def type(self, description="", **options):
       def decorator(f):
            BaseAPI.parseProps(self, self.key, f, description=description)
            return f
       return decorator

    def action(self, label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator



class KettleAPI(BaseAPI):

    key = "controller_types"

    def controller(self, description="", **options):
       def decorator(f):
            BaseAPI.parseProps(self, self.key,f,description=description)
            return f
       return decorator

    def action(self, label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator

class FermenterAPI(BaseAPI):

    key = "fermentation_controller_types"

    def controller(self, description="Step", **options):
       def decorator(f):
            BaseAPI.parseProps(self, self.key,f,description=description)
            return f
       return decorator

    def action(self, label):
        def real_decorator(func):
            func.action = True
            func.label = label
            return func
        return real_decorator

class CoreAPI(BaseAPI):

    key = "core"

    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)

        self.cbpi = cbpi
        self.cbpi.cache["actions"] = {}
        self.cbpi.cache["init"] = []
        self.cbpi.cache["js"] = {}
        self.cbpi.cache["background"] = []
        self.cbpi.cache["web_menu"] =[]

    def init(self):

        self.cbpi.cache["init"] = sorted(self.cbpi.cache["init"], key=lambda k: k['order'])
        for value in self.cbpi.cache.get("init"):

            self.logger.debug(value)
            value["function"](self.cbpi)

        def job(interval, method):
            while True:
                try:
                    method(self.cbpi)
                except Exception as e:
                    self.logger.debug(e)
                self.cbpi._socketio.sleep(interval)

        for value in self.cbpi.cache.get("background"):
            t = self.cbpi._socketio.start_background_task(target=job,  interval=value.get("interval"),  method=value.get("function"))


    def add_js(self, name, file):
        self.cbpi.cache["js"][name] = file

    def add_menu_link(self, name, path):
        self.cbpi.cache["web_menu"].append(dict(name=name, path=path))

    def initializer(self, order=0, **options):
        def decorator(f):
             self.cbpi.cache.get("init").append({"function": f, "order": order})
             return f
        return decorator


    def action(self, key, label, **options):
        def decorator(f):
             self.cbpi.cache.get("actions")[key] = {"label": label, "function": f}
             return f
        return decorator


    def backgroundjob(self, key, interval, **options):
        def decorator(f):
             self.cbpi.cache.get("background").append({"function": f, "key": key, "interval": interval})
             return f
        return decorator

    def listen(self, name, method=None, async=False):

        if method is not None:
            if self.cbpi.eventbus.get(name) is None:
                self.cbpi.eventbus[name] = []
            self.cbpi.eventbus[name].append({"function": method, "async": async})
        else:
            def real_decorator(function):
                if self.cbpi.eventbus.get(name) is None:
                    self.cbpi.eventbus[name] = []
                self.cbpi.eventbus[name].append({"function": function, "async": async})
                def wrapper(*args, **kwargs):
                    return function(*args, **kwargs)
                return wrapper
            return real_decorator


class Buzzer(object):

    def beep():
        pass