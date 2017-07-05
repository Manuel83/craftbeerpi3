import time
from flask_classy import route
from modules import DBModel, cbpi
from modules.core.baseview import BaseView

class Sensor(DBModel):
    __fields__ = ["name","type", "config", "hide"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]

class SensorView(BaseView):
    model = Sensor
    cache_key = "sensors"

    @route('<int:id>/action/<method>', methods=["POST"])
    def action(self, id, method):

        cbpi.cache.get("sensors").get(id).instance.__getattribute__(method)()
        return ('', 204)

    def _post_post_callback(self, m):
        cbpi.init_sensor(m.id)

    def _post_put_callback(self, m):
        cbpi.stop_sensor(m.id)
        cbpi.init_sensor(m.id)

    def _pre_delete_callback(self, m):
        cbpi.stop_sensor(m.id)

@cbpi.initalizer(order=1000)
def init(cbpi):

    SensorView.register(cbpi.app, route_base='/api/sensor')
    SensorView.init_cache()
    cbpi.init_sensors()


@cbpi.backgroundtask(key="read_passiv_sensor", interval=5)
def read_passive_sensor(api):
    """
    background process that reads all passive sensors in interval of 1 second
    :return: None

    """
    for key, value in cbpi.cache.get("sensors").iteritems():
        if value.mode == "P":
            value.instance.read()
