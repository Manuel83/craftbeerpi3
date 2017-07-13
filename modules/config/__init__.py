import time

from flask import json, request
from flask_classy import route
from modules import DBModel, cbpi, get_db
from modules.core.baseview import BaseView

class Config(DBModel):
    __fields__ = ["type", "value", "description", "options"]
    __table_name__ = "config"
    __json_fields__ = ["options"]
    __priamry_key__ = "name"


class ConfigView(BaseView):
    model = Config
    cache_key = "config"

    @route('/<name>', methods=["PUT"])
    def put(self, name):

        data = request.json
        data["name"] = name
        update_data = {"name": data["name"], "value": data["value"]}

        if self.api.cache.get(self.cache_key) is not None:
            self.api.cache.get(self.cache_key)[name].__dict__.update(**update_data)
        m = self.model.update(**self.api.cache.get(self.cache_key)[name].__dict__)
        self._post_put_callback(self.api.cache.get(self.cache_key)[name])
        return json.dumps(self.api.cache.get(self.cache_key)[name].__dict__)

    @route('/<id>', methods=["GET"])
    def getOne(self, id):
        return ('NOT SUPPORTED', 400)

    @route('/<id>', methods=["DELETE"])
    def delete(self, id):
        return ('NOT SUPPORTED', 400)

    @route('/', methods=["POST"])
    def post(self):
        return ('NOT SUPPORTED', 400)

    @classmethod
    def init_cache(cls):

        with cls.api.app.app_context():
            cls.api.cache[cls.cache_key] = {}
            for key, value  in cls.model.get_all().iteritems():
                cls.post_init_callback(value)
                cls.api.cache[cls.cache_key][value.name] = value

@cbpi.initalizer(order=0)
def init(cbpi):

    ConfigView.register(cbpi.app, route_base='/api/config')
    ConfigView.init_cache()
