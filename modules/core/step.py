from modules import cbpi
from modules.core.props import StepProperty, Property
import time


class NotificationAPI(object):
    def notify(self, headline, message, type="success", timeout=5000):
        self.api.notify(headline, message, type, timeout)

class ActorAPI(NotificationAPI):

    @cbpi.try_catch(None)
    def actor_on(self, id, power=100):
        self.api.switch_actor_on(int(id), power=power)

    @cbpi.try_catch(None)
    def actor_off(self, id):
        self.api.switch_actor_off(int(id))

    @cbpi.try_catch(None)
    def actor_power(self, id, power):
        self.api.actor_power(int(id), power)

class SensorAPI(NotificationAPI):

    @cbpi.try_catch(None)
    def get_sensor_value(self, id):
        return cbpi.get_sensor_value(id)

class KettleAPI(NotificationAPI):

    @cbpi.try_catch(None)
    def get_kettle_temp(self, id=None):
        id = int(id)
        if id is None:
            id = self.kettle_id
        return cbpi.get_sensor_value(int(self.api.cache.get("kettle").get(id).sensor))

    @cbpi.try_catch(None)
    def get_target_temp(self, id=None):
        id = int(id)
        if id is None:
            id = self.kettle_id
        return self.api.cache.get("kettle").get(id).target_temp

    def set_target_temp(self, temp, id=None):
        temp = float(temp)

        try:
            if id is None:
                self.api.emit_event("SET_TARGET_TEMP", id=self.kettle_id, temp=temp)
            else:
                self.api.emit_event("SET_TARGET_TEMP", id=id, temp=temp)
        except Exception as e:

            self.notify("Faild to set Target Temp", "", type="warning")

class Timer(object):
    timer_end = Property.Number("TIMER_END", configurable=False)

    def start_timer(self, timer):

        if self.timer_end is not None:
            return
        self.timer_end = int(time.time()) + timer


    def stop_timer(self):
        if self.timer_end is not None:
            self.timer_end = None

    def is_timer_running(self):
        if self.timer_end is not None:
            return True
        else:
            return False

    def timer_remaining(self):
        if self.timer_end is not None:
            return self.timer_end - int(time.time())
        else:
            return None

    def is_timer_finished(self):
        if self.timer_end is None:
            return None
        if self.timer_end <= int(time.time()):
            return True
        else:
            return False


class StepBase(Timer, ActorAPI, SensorAPI, KettleAPI):

    __dirty = False
    managed_fields = []
    n = False

    def next(self):
        self.n = True

    def init(self):
        pass

    def finish(self):
        pass

    def reset(self):
        pass

    def execute(self):
        print "-------------"
        print "Step Info"
        print "Kettle ID: %s" % self.kettle_id
        print "ID: %s" % self.id


    def __init__(self, *args, **kwds):

        for a in kwds:

            super(StepBase, self).__setattr__(a, kwds.get(a))


        self.api = kwds.get("api")
        self.id = kwds.get("id")
        self.name = kwds.get("name")
        self.kettle_id = kwds.get("kettleid")
        self.value = None
        self.__dirty = False


    def is_dirty(self):
        return self.__dirty

    def reset_dirty(self):
        self.__dirty = False

    def __setattr__(self, name, value):

        if name != "_StepBase__dirty" and name in self.managed_fields:
            self.__dirty = True
            super(StepBase, self).__setattr__(name, value)
        else:
            super(StepBase, self).__setattr__(name, value)

