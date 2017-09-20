import time
from flask_classy import route
from modules.core.core import cbpi
from modules.core.db import DBModel
from modules.core.baseview import BaseView
from modules.database.dbmodel import Sensor


class SensorView(BaseView):
    model = Sensor
    cache_key = "sensors"

    @route('<int:id>/action/<method>', methods=["POST"])
    def action(self, id, method):
        """
        Sensor Action 
        ---
        tags:
          - sensor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the sensor
          - in: path
            name: method
            schema:
              type: string
            required: true
            description: action method name
        responses:
          200:
            description: Sensor Action called
        """
        cbpi.cache.get("sensors").get(id).instance.__getattribute__(method)()
        return ('', 204)

    def _post_post_callback(self, m):

        cbpi.sensor.init_one(m.id)

    def _post_put_callback(self, m):
        cbpi.sensor.stop_one(m.id)
        cbpi.sensor.init_one(m.id)

    def _pre_delete_callback(self, m):
        cbpi.sensor.stop_one(m.id)

@cbpi.addon.core.initializer(order=1000)
def init(cbpi):

    SensorView.register(cbpi._app, route_base='/api/sensor')
    SensorView.init_cache()


#@cbpi.backgroundtask(key="read_passiv_sensor", interval=5)
def read_passive_sensor(api):
    """
    background process that reads all passive sensors in interval of 1 second
    :return: None

    """
    for key, value in cbpi.cache.get("sensors").iteritems():
        if value.mode == "P":
            value.instance.read()
