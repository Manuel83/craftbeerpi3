import time
from flask import json, request
from flask_classy import route

from modules.core.db import DBModel
from modules.core.baseview import BaseView
from modules.core.core import cbpi
from modules.database.dbmodel import Step


class StepView(BaseView):
    model = Step
    def _pre_post_callback(self, data):
        order = self.model.get_max_order()
        data["order"] = 1 if order is None else order + 1
        data["state"] = "I"

    @route('/sort', methods=["POST"])
    def sort_steps(self):
        """
        Sort all steps
        ---
        tags:
          - steps
        responses:
          204:
            description: Steps sorted. Update delivered via web socket
        """
        Step.sort(request.json)
        cbpi.ws_emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    @route('/', methods=["DELETE"])
    def deleteAll(self):
        """
        Delete all Steps
        ---
        tags:
          - steps
        responses:
          204:
            description: All steps deleted
        """
        self.model.delete_all()
        self.api.emit("ALL_BREWING_STEPS_DELETED")
        self.api.set_config_parameter("brew_name", "")
        cbpi.ws_emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    @route('/action/<method>', methods=["POST"])
    def action(self, method):
        """
        Call Step Action 
        ---
        tags:
          - steps
        responses:
          204:
            description: Step action called
        """
        self.api.emit("BREWING_STEP_ACTION_INVOKED", method=method)
        cbpi.cache["active_step"].__getattribute__(method)()
        return ('', 204)

    @route('/reset', methods=["POST"])
    def reset(self):

        """
        Reset All Steps
        ---
        tags:
          - steps
        responses:
          200:
            description: Steps reseted
        """
        self.model.reset_all_steps()
        self.stop_step()
        self.api.emit("ALL_BREWING_STEPS_RESET")
        cbpi.ws_emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    def stop_step(self):
        '''
        stop active step
        :return:
        '''
        step = cbpi.cache.get("active_step")
        cbpi.cache["active_step"] = None
        self.api.emit("BREWING_STEPS_STOP")
        if step is not None:
            step.finish()

    @route('/reset/current', methods=['POST'])
    def resetCurrentStep(self):
        """
        Reset current Steps
        ---
        tags:
          - steps
        responses:
          200:
            description: Current Steps reseted
        """
        step = cbpi.cache.get("active_step")

        if step is not None:
            step.reset()
            if step.is_dirty():

                state = {}
                for field in step.managed_fields:
                    state[field] = step.__getattribute__(field)
                Step.update_step_state(step.id, state)
                step.reset_dirty()
                self.api.emit("BREWING_STEPS_RESET_CURRENT")
                cbpi.ws_emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    def init_step(self, step):

        cbpi.brewing.log_action("Start Step %s" % step.name)
        type_cfg = cbpi.cache.get("step_types").get(step.type)
        if type_cfg is None:
            # if type not found
            return

        # copy config to stepstate
        # init step
        cfg = step.config.copy()
        cfg.update(dict(name=step.name, api=cbpi, id=step.id, timer_end=None, managed_fields=get_manged_fields_as_array(type_cfg)))
        instance = type_cfg.get("class")(**cfg)
        instance.init()
        # set step instance to ache
        cbpi.cache["active_step"] = instance

    @route('/next', methods=['POST'])
    @route('/start', methods=['POST'])
    def start(self):

        """
        Next Step
        ---
        tags:
          - steps
        responses:
          200:
            description: Next Step
        """
        active = Step.get_by_state("A")
        inactive = Step.get_by_state('I')

        if (active is not None):
            active.state = 'D'
            active.end = int(time.time())
            self.stop_step()
            Step.update(**active.__dict__)
            self.api.emit("BREWING_STEP_DONE")

        if (inactive is not None):
            self.init_step(inactive)
            inactive.state = 'A'
            inactive.stepstate = inactive.config
            inactive.start = int(time.time())
            Step.update(**inactive.__dict__)
            self.api.emit("BREWING_STEP_STARTED")
        else:
            cbpi.brewing.log_action("Brewing Finished")
            self.api.emit("BREWING_FINISHED")
            cbpi.notify("Brewing Finished", "You are done!", timeout=None)


        cbpi.ws_emit("UPDATE_ALL_STEPS", Step.get_all())

        return ('', 204)

def get_manged_fields_as_array(type_cfg):

    result = []
    for f in type_cfg.get("properties"):

        result.append(f.get("name"))

    return result


def init_after_startup():
    '''
    Restart after startup. Check is a step is in state A and reinitialize
    :return: None
    '''
    step = Step.get_by_state('A')
    # We have an active step
    if step is not None:
        # get the type
        type_cfg = cbpi.cache.get("step_types").get(step.type)

        if type_cfg is None:
            # step type not found. cant restart step
            return
        cfg = step.stepstate.copy()
        cfg.update(dict(api=cbpi, id=step.id, managed_fields=get_manged_fields_as_array(type_cfg)))
        instance = type_cfg.get("class")(**cfg)
        instance.init()
        cbpi.cache["active_step"] = instance

@cbpi.addon.core.initializer(order=2000)
def init(cbpi):

    StepView.register(cbpi._app, route_base='/api/step')

    def get_all():
        with cbpi._app.app_context():
            return Step.get_all()

    with cbpi._app.app_context():
        init_after_startup()

    cbpi.add_cache_callback("steps", get_all)

@cbpi.addon.core.backgroundjob(key="step_task", interval=0.1)
def execute_step(api):
    '''
    Background job which executes the step
    :return:
    '''
    with cbpi._app.app_context():
        step = cbpi.cache.get("active_step")
        if step is not None:
            step.execute()

            if step.is_dirty():

                state = {}
                for field in step.managed_fields:
                    state[field] = step.__getattribute__(field)

                Step.update_step_state(step.id, state)
                step.reset_dirty()
                cbpi.ws_emit("UPDATE_ALL_STEPS", Step.get_all())

            if step.n is True:

                StepView().start()
                cbpi.ws_emit("UPDATE_ALL_STEPS", Step.get_all())
