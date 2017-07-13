import time
from flask import json, request
from flask_classy import route

from modules import DBModel, cbpi, get_db
from modules.core.baseview import BaseView


class Step(DBModel):
    __fields__ = ["name","type", "stepstate", "state", "start", "end", "order", "config"]
    __table_name__ = "step"
    __json_fields__ = ["config", "stepstate"]
    __order_by__ = "order"
    __as_array__ = True

    @classmethod
    def get_max_order(cls):
        cur = get_db().cursor()
        cur.execute("SELECT max(step.'order') as 'order' FROM %s" % cls.__table_name__)
        r = cur.fetchone()
        return r.get("order")

    @classmethod
    def get_by_state(cls, state, order=True):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM %s WHERE state = ? ORDER BY %s.'order'" % (cls.__table_name__,cls.__table_name__,), state)
        r = cur.fetchone()
        if r is not None:
            return cls(r)
        else:
            return None

    @classmethod
    def delete_all(cls):
        cur = get_db().cursor()
        cur.execute("DELETE FROM %s" % cls.__table_name__)
        get_db().commit()

    @classmethod
    def reset_all_steps(cls):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = 'I', stepstate = NULL , start = NULL, end = NULL " % cls.__table_name__)
        get_db().commit()

    @classmethod
    def update_state(cls, id, state):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = ? WHERE id =?" % cls.__table_name__, (state, id))
        get_db().commit()

    @classmethod
    def update_step_state(cls, id, state):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET stepstate = ? WHERE id =?" % cls.__table_name__, (json.dumps(state),id))
        get_db().commit()

    @classmethod
    def sort(cls, new_order):
        cur = get_db().cursor()

        for e in new_order:

            cur.execute("UPDATE %s SET '%s' = ? WHERE id = ?" % (cls.__table_name__, "order"), (e[1], e[0]))
        get_db().commit()


class StepView(BaseView):
    model = Step
    def _pre_post_callback(self, data):
        order = self.model.get_max_order()
        data["order"] = 1 if order is None else order + 1
        data["state"] = "I"

    @route('/sort', methods=["POST"])
    def sort_steps(self):
        Step.sort(request.json)
        cbpi.emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    @route('/', methods=["DELETE"])
    def deleteAll(self):
        self.model.delete_all()
        cbpi.emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    @route('/action/<method>', methods=["POST"])
    def action(self, method):
        cbpi.cache["active_step"].__getattribute__(method)()
        return ('', 204)

    @route('/reset', methods=["POST"])
    def reset(self):
        self.model.reset_all_steps()
        self.stop_step()
        cbpi.emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    def stop_step(self):
        '''
        stop active step
        :return: 
        '''
        step = cbpi.cache.get("active_step")
        cbpi.cache["active_step"] = None

        if step is not None:
            step.finish()

    @route('/reset/current', methods=['POST'])
    def resetCurrentStep(self):
        '''
        Reset current step
        :return: 
        '''
        step = cbpi.cache.get("active_step")

        if step is not None:
            step.reset()
            if step.is_dirty():

                state = {}
                for field in step.managed_fields:
                    state[field] = step.__getattribute__(field)
                Step.update_step_state(step.id, state)
                step.reset_dirty()
                cbpi.emit("UPDATE_ALL_STEPS", self.model.get_all())
        return ('', 204)

    def init_step(self, step):
        cbpi.log_action("Start Step %s" % step.name)
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
        active = Step.get_by_state("A")
        inactive = Step.get_by_state('I')

        if (active is not None):
            active.state = 'D'
            active.end = int(time.time())
            self.stop_step()
            Step.update(**active.__dict__)

        if (inactive is not None):
            self.init_step(inactive)
            inactive.state = 'A'
            inactive.stepstate = inactive.config
            inactive.start = int(time.time())
            Step.update(**inactive.__dict__)
        else:
            cbpi.log_action("Brewing Finished")
            cbpi.notify("Brewing Finished", "You are done!", timeout=None)

        cbpi.emit("UPDATE_ALL_STEPS", Step.get_all())
        return ('', 204)

def get_manged_fields_as_array(type_cfg):

    result = []
    for f in type_cfg.get("properties"):

        result.append(f.get("name"))

    return result

@cbpi.try_catch(None)
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

@cbpi.initalizer(order=2000)
def init(cbpi):

    StepView.register(cbpi.app, route_base='/api/step')

    def get_all():
        with cbpi.app.app_context():
            return Step.get_all()

    with cbpi.app.app_context():
        init_after_startup()
    cbpi.add_cache_callback("steps", get_all)

@cbpi.backgroundtask(key="step_task", interval=0.1)
def execute_step(api):
    '''
    Background job which executes the step 
    :return: 
    '''
    with cbpi.app.app_context():
        step = cbpi.cache.get("active_step")
        if step is not None:
            step.execute()
            if step.is_dirty():
                state = {}
                for field in step.managed_fields:
                    state[field] = step.__getattribute__(field)
                Step.update_step_state(step.id, state)
                step.reset_dirty()
                cbpi.emit("UPDATE_ALL_STEPS", Step.get_all())

            if step.n is True:

                StepView().start()
                cbpi.emit("UPDATE_ALL_STEPS", Step.get_all())
