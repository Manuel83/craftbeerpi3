import time

from flask import json, request
from flask_classy import route
from modules import cbpi
from modules.core.db import DBModel
from modules.core.baseview import RestApi
from modules.database.dbmodel import Config


class ConfigView(RestApi):
    model = Config
    cache_key = "config"

    @route('/<name>', methods=["PUT"])
    def put(self, name):
        """
        Set new config value
        ---
        tags:
          - config
        responses:
          204:
            description: New config value set
        """
        data = request.json
        data["name"] = name
        update_data = {"name": data["name"], "value": data["value"]}

        if self.api.cache.get(self.cache_key) is not None:
            self.api.cache.get(self.cache_key)[name].__dict__.update(**update_data)
        m = self.model.update(**self.api.cache.get(self.cache_key)[name].__dict__)
        self._post_put_callback(self.api.cache.get(self.cache_key)[name])

        self.api.emit("CONFIG_UPDATE", name=name, data=data["value"])
        return json.dumps(self.api.cache.get(self.cache_key)[name].__dict__)

    @route('/<id>', methods=["GET"])
    def getOne(self, id):
        """
        Get config parameter
        ---
        tags:
          - config
        responses:
          400:
            description: Get one config parameter via web api is not supported
        """
        return ('NOT SUPPORTED', 400)

    @route('/<id>', methods=["DELETE"])
    def delete(self, id):
        """
        Delete config parameter
        ---
        tags:
          - config
        responses:
          400:
            description: Deleting config parameter via web api is not supported
        """
        return ('NOT SUPPORTED', 400)

    @route('/', methods=["POST"])
    def post(self):
        """
        Get config parameter
        ---
        tags:
          - config
        responses:
          400:
            description: Adding new config parameter via web api is not supported
        """
        return ('NOT SUPPORTED', 400)

    @classmethod
    def init_cache(cls):

        with cls.api.web.app_context():
            cls.api.cache[cls.cache_key] = {}
            for key, value  in cls.model.get_all().iteritems():
                cls.post_init_callback(value)
                cls.api.cache[cls.cache_key][value.name] = value

@cbpi.addon.core.initializer(order=0)
def init(cbpi):
    ConfigView.register(cbpi.web, route_base='/api/config')
    ConfigView.init_cache()
