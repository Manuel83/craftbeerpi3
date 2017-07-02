from flask import request
from flask_classy import FlaskView, route
from modules import cbpi, socketio
from modules.core.baseview import BaseView
from modules.core.db import DBModel

class Kettle(DBModel):
    __fields__ = ["name","sensor", "heater", "automatic", "logic", "config", "agitator", "target_temp"]
    __table_name__ = "kettle"
    __json_fields__ = ["config"]


class Kettle2View(BaseView):
    model = Kettle
    cache_key = "kettle"

    @classmethod
    def _pre_post_callback(self, data):
        data["target_temp"] = 0

    @classmethod
    def post_init_callback(cls, obj):
        obj.state = False


    def _post_post_callback(self, m):
        m.state = False

    def _pre_put_callback(self, m):
        try:
            m.instance.stop()
        except:
            pass

    def _post_put_callback(self, m):
        m.state = False

    @route('/<int:id>/targettemp/<temp>', methods=['POST'])
    def postTargetTemp(self, id, temp):
        id = int(id)
        temp = float(temp)
        cbpi.cache.get("kettle")[id].target_temp = float(temp)
        self.model.update(**self.api.cache.get(self.cache_key)[id].__dict__)
        cbpi.emit("UPDATE_KETTLE_TARGET_TEMP", {"id": id, "target_temp": temp})
        return ('', 204)

    @route('/<int:id>/automatic', methods=['POST'])
    def toggle(self, id):
        kettle = cbpi.cache.get("kettle")[id]

        if kettle.state is False:
            # Start controller
            if kettle.logic is not None:
                cfg = kettle.config.copy()
                cfg.update(dict(api=cbpi, kettle_id=kettle.id, heater=kettle.heater, sensor=kettle.sensor))
                instance = cbpi.get_controller(kettle.logic).get("class")(**cfg)
                instance.init()
                kettle.instance = instance
                def run(instance):
                    instance.run()
                t = self.api.socketio.start_background_task(target=run, instance=instance)
            kettle.state = not kettle.state
            cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
        else:
            # Stop controller
            kettle.instance.stop()
            kettle.state = not kettle.state
            cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle").get(id))
        return ('', 204)

@cbpi.event("SET_TARGET_TEMP")
def set_target_temp(id, temp):
    '''
    Change Taget Temp Event
    :param id: kettle id
    :param temp: target temp to set
    :return: None
    '''

    Kettle2View().postTargetTemp(id,temp)

@cbpi.backgroundtask(key="read_target_temps", interval=5)
def read_target_temps(api):
    """
    background process that reads all passive sensors in interval of 1 second
    :return: None
    """
    result = {}
    for key, value in cbpi.cache.get("kettle").iteritems():
        cbpi.save_to_file(key, value.target_temp, prefix="kettle")

@cbpi.initalizer()
def init(cbpi):
    Kettle2View.api = cbpi
    Kettle2View.register(cbpi.app,route_base='/api/kettle')
    Kettle2View.init_cache()
