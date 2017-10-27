import logging
import time
from flask import request
from flask_classy import route

from modules.core.core import  cbpi
from modules.core.db import get_db, DBModel
from modules.core.baseview import BaseView
from modules.database.dbmodel import Fermenter, FermenterStep


class FermenterView(BaseView):
    model = Fermenter
    cache_key = "fermenter"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _post_post_callback(self, m):
        m.state = False
        m.steps = []

    def _pre_put_callback(self, m):
        m.state = False
        try:
            m.instance.stop()
        except:
            pass

    def _post_put_callback(self, m):
        m.state = False

    @route('/<int:id>/targettemp/<temp>', methods=['POST'])
    def postTargetTemp(self, id, temp):
        if temp is None or not temp:
            return ('', 500)
        id = int(id)
        temp = float(temp)
        cbpi.cache.get(self.cache_key)[id].target_temp = float(temp)
        self.model.update(**self.api.cache.get(self.cache_key)[id].__dict__)
        cbpi.ws_emit("UPDATE_FERMENTER_TARGET_TEMP", {"id": id, "target_temp": temp})
        return ('', 204)

    @route('/<int:id>/brewname', methods=['POST'])
    def postBrewName(self, id):
        data = request.json
        brewname = data.get("brewname")
        cbpi.cache.get(self.cache_key)[id].brewname = brewname
        self.model.update(**self.api.cache.get(self.cache_key)[id].__dict__)
        cbpi.ws_emit("UPDATE_FERMENTER_BREWNAME", {"id": id, "brewname": brewname})
        return ('', 204)

    @classmethod
    def post_init_callback(cls, obj):
        obj.steps = FermenterStep.get_by_fermenter_id(obj.id)
        obj.state = False

    @route('/<int:id>/step', methods=['POST'])
    def postStep(self, id):
        data = request.json
        order_max = FermenterStep.get_max_order(id)
        order = order_max + 1 if order_max is not None else 1
        data["order"] = order
        data["days"] = 0 if data["days"] == "" else data["days"]
        data["hours"] = 0 if data["hours"] == "" else data["hours"]
        data["minutes"] = 0 if data["minutes"] == "" else data["minutes"]
        data["temp"] = 0 if data["temp"] == "" else data["temp"]
        data["state"] = "I"
        data["name"] = "NO NAME" if data["name"] == "" else data["name"]
        f = FermenterStep.insert(**data)

        cbpi.cache.get(self.cache_key)[id].steps.append(f)

        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])

        return ('', 204)

    @route('/<int:id>/step/<int:stepid>', methods=["PUT"])
    def putStep(self, id, stepid):
        data = request.json
        # Select modal

        data["id"] = stepid
        data["fermenter_id"] = id

        data["days"] = 0 if data["days"] == "" else data["days"]
        data["hours"] = 0 if data["hours"] == "" else data["hours"]
        data["minutes"] = 0 if data["minutes"] == "" else data["minutes"]

        for s in cbpi.cache.get(self.cache_key)[id].steps:
            if s.id == stepid:
                s.__dict__.update(**data)

                FermenterStep.update(**s.__dict__)
                break
        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])
        return ('', 204)

    @route('/<int:id>/step/<int:stepid>', methods=["DELETE"])
    def deleteStep(self, id, stepid):

        for idx, s in enumerate(cbpi.cache.get(self.cache_key)[id].steps):
            if s.id == stepid:
                del cbpi.cache.get(self.cache_key)[id].steps[idx]
                FermenterStep.delete(s.id)
                break
        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])
        return ('', 204)

    @route('/<int:id>/start', methods=['POST'])
    def start_fermentation(self, id):
        active = None
        for idx, s in enumerate(cbpi.cache.get(self.cache_key)[id].steps):
            if s.state == 'A':
                active = s
                break

        inactive = None
        for idx, s in enumerate(cbpi.cache.get(self.cache_key)[id].steps):
            if s.state == 'I':
                inactive = s
                break

        if active is not None:

            active.state = 'D'
            active.end = time.time()
            FermenterStep.update(**active.__dict__)

            del cbpi.cache["fermenter_task"][id]

        if inactive is not None:
            fermenter = self.get_fermenter(inactive.fermenter_id)

            current_temp = cbpi.sensor.get_value(int(fermenter.sensor))

            inactive.state = 'A'
            inactive.start = time.time()
            inactive.direction = "C" if current_temp >= inactive.temp else "H"
            FermenterStep.update(**inactive.__dict__)

            self.postTargetTemp(id, inactive.temp)

            cbpi.cache["fermenter_task"][id] = inactive

        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])
        return ('', 204)

    @route('/<int:id>/reset', methods=["POST"])
    def reset(self, id):
        FermenterStep.reset_all_steps(id)

        cbpi.cache[self.cache_key][id].steps = FermenterStep.get_by_fermenter_id(id)

        if id in cbpi.cache["fermenter_task"]:
            del cbpi.cache["fermenter_task"][id]

        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])
        return ('', 204)

    @route('/<int:id>/automatic', methods=['POST'])
    def toggle(self, id):
        fermenter = cbpi.cache.get(self.cache_key)[id]
        try:

            if fermenter.state is False:
                # Start controller
                if fermenter.logic is not None:
                    cfg = fermenter.config.copy()
                    cfg.update(
                        dict(api=cbpi, fermenter_id=fermenter.id, heater=fermenter.heater, sensor=fermenter.sensor))
                    instance = cbpi.fermentation.get_controller(fermenter.logic).get("class")(**cfg)
                    instance.init()
                    fermenter.instance = instance

                    def run(instance):
                        instance.run()

                    t = cbpi._socketio.start_background_task(target=run, instance=instance)
                fermenter.state = not fermenter.state
                cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key).get(id))
                cbpi.emit("FERMENTER_CONTROLLER_STARTED", id=id)
            else:
                # Stop controller
                fermenter.instance.stop()
                fermenter.state = not fermenter.state
                cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key).get(id))
                cbpi.emit("FERMENTER_CONTROLLER_STOPPED", id=id)

        except Exception as e:

            cbpi.notify("Toogle Fementer Controller failed", "Pleae check the %s configuration" % fermenter.name,
                        type="danger", timeout=None)
            return ('', 500)

        return ('', 204)

    def get_fermenter(self, id):
        return cbpi.cache["fermenter"].get(id)

    def target_temp_reached(self,id, step):
        timestamp = time.time()

        days = step.days * 24 * 60 * 60
        hours = step.hours * 60 * 60
        minutes = step.minutes * 60
        target_time = days + hours + minutes + timestamp

        FermenterStep.update_timer(step.id, target_time)

        step.timer_start = target_time

        cbpi.ws_emit("UPDATE_FERMENTER", cbpi.cache.get(self.cache_key)[id])

    def check_step(self):
        for key, value in cbpi.cache["fermenter_task"].iteritems():

            try:
                fermenter = self.get_fermenter(key)
                current_temp = current_temp = cbpi.get_sensor_value(int(fermenter.sensor))

                if value.timer_start is None:

                    if value.direction == "H" :

                        if current_temp >= value.temp:
                            self.target_temp_reached(key,value)
                    else:
                        if current_temp <= value.temp:
                            self.target_temp_reached(key, value)
                else:
                    if time.time() >= value.timer_start:
                        self.start_fermentation(key)
                    else:
                        pass
            except Exception as e:
                pass


@cbpi.addon.core.backgroundjob(key="read_target_temps_fermenter", interval=5)
def read_target_temps(cbpi):
    """
    background process that reads all passive sensors in interval of 1 second
    :return: None
    """
    for key, value in cbpi.cache.get("fermenter").iteritems():
        cbpi.sensor.write_log(key, value.target_temp, prefix="fermenter")



instance = FermenterView()

@cbpi.addon.core.backgroundjob(key="fermentation_task", interval=1)
def execute_fermentation_step(cbpi):
    with cbpi._app.app_context():
        instance.check_step()


def init_active_steps():
    pass



@cbpi.addon.core.initializer(order=1)
def init(cbpi):

    cbpi.cache["fermenter_task"] = {}
    FermenterView.register(cbpi._app, route_base='/api/fermenter')
    FermenterView.init_cache()
