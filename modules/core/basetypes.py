import logging

from modules.core.proptypes import Property
import time

class Base(object):

    def __init__(self, *args, **kwds):
        for a in kwds:

            super(Base, self).__setattr__(a, kwds.get(a))
        self.api = kwds.get("cbpi")
        self.id = kwds.get("id")
        self.value = None
        self.__dirty = False


class Actor(Base):
    __logger = logging.getLogger(__name__)

    @classmethod
    def init_global(cls):
        cls.__logger.info("GLOBAL INIT ACTOR")
        pass

    def init(self):
        pass

    def shutdown(self):
        pass

    def on(self, power=100):
        self._logger.info("SWITCH ON")
        pass

    def off(self):
        self._logger.info("SWITCH OFF")
        pass

    def power(self, power):
        self._logger.info("SET POWER TO [%s]", power)
        pass

    def state(self):
        pass


class Sensor(Base):
    __logger = logging.getLogger(__name__)

    unit = ""

    @classmethod
    def init_global(cls):
        pass

    def init(self):
        pass

    def get_unit(self):
        pass

    def stop(self):
        pass

    def update_value(self, value):
        self.value = value
        self.__logger.info("Updated value for sensor [%s] with value [%s].", self.id, value)
        self.cbpi.sensor.write_log(self.id, value)
        self.cbpi.emit("SENSOR_UPDATE", id=self.id, value=value)
        self.cbpi.ws_emit("SENSOR_UPDATE", self.cbpi.cache["sensors"][self.id])

    def execute(self):
        self.__logger.info("EXECUTE")
        pass




class ControllerBase(object):
    __dirty = False
    __running = False

    __logger = logging.getLogger(__name__)

    @staticmethod
    def init_global():
        ControllerBase.__logger.info("GLOBAL CONTROLLER INIT")

    def notify(self, headline, message, type="success", timeout=5000):
        self.api.notify(headline, message, type, timeout)

    def is_running(self):
        return self.__running

    def init(self):
        self.__running = True

    def sleep(self, seconds):
        self.api.sleep(seconds)

    def stop(self):
        self.__running = False

    def get_sensor_value(self, id):
        return self.api.sensor.get_sensor_value(id)

    def __init__(self, *args, **kwds):
        for a in kwds:
            super(ControllerBase, self).__setattr__(a, kwds.get(a))
        self.api = kwds.get("api")
        self.heater = kwds.get("heater")
        self.sensor = kwds.get("sensor")

    def actor_on(self,id, power=100):
        self.api.actor.on(id, power=power)

    def actor_off(self, id):
        self.api.actor.off(id)

    def actor_power(self, power, id=None):
        self.api.actor.power(id, power)

    def run(self):
        pass

class KettleController(ControllerBase):

    @staticmethod
    def chart(kettle):
        result = []
        result.append({"name": "Temp", "data_type": "sensor", "data_id": kettle.sensor})
        result.append({"name": "Target Temp", "data_type": "kettle", "data_id": kettle.id})
        return result

    def __init__(self, *args, **kwds):
        ControllerBase.__init__(self, *args, **kwds)
        self.kettle_id = kwds.get("kettle_id")

    def heater_on(self, power=100):
        k = self.api.cache.get("kettle").get(self.kettle_id)
        if k.heater is not None:
            self.actor_on(k.heater, power)

    def heater_off(self):
        k = self.api.cache.get("kettle").get(self.kettle_id)
        if k.heater is not None:
            self.actor_off(k.heater)

    def get_temp(self, id=None):
        if id is None:
            id = self.kettle_id
        return self.get_sensor_value(int(self.api.cache.get("kettle").get(id).sensor))

    def get_target_temp(self, id=None):
        if id is None:
            id = self.kettle_id
        return self.api.cache.get("kettle").get(id).target_temp

class FermenterController(ControllerBase):

    @staticmethod
    def chart(fermenter):
        result = []
        result.append({"name": "Temp", "data_type": "sensor", "data_id": fermenter.sensor})
        result.append({"name": "Target Temp", "data_type": "fermenter", "data_id": fermenter.id})
        return result

    def __init__(self, *args, **kwds):
        ControllerBase.__init__(self, *args, **kwds)
        self.fermenter_id = kwds.get("fermenter_id")
        self.cooler = kwds.get("cooler")

    def get_target_temp(self, id=None):
        if id is None:
            id = self.fermenter_id
        return self.api.cache.get("fermenter").get(id).target_temp

    def heater_on(self, power=100):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.heater is not None:
            self.actor_on(int(f.heater))

    def heater_off(self):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.heater is not None:
            self.actor_off(int(f.heater))

    def cooler_on(self, power=100):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.cooler is not None:
            self.actor_on(power, int(f.cooler))

    def cooler_off(self):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.cooler is not None:
            self.actor_off(int(f.cooler))

    def get_temp(self, id=None):
        if id is None:
            id = self.fermenter_id
        return self.get_sensor_value(int(self.api.cache.get("fermenter").get(id).sensor))


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


class Step(Base, Timer):

    @classmethod
    def init_global(cls):
        pass

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
        self.logger.info("-------------")
        self.logger.info("Step Info")
        self.logger.info("Kettle ID: %s" % self.kettle_id)
        self.logger.info("ID: %s" % self.id)

    def __init__(self, *args, **kwds):
        self.logger = logging.getLogger(__name__)

        for a in kwds:
            super(Step, self).__setattr__(a, kwds.get(a))
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
            super(Step, self).__setattr__(name, value)
        else:
            super(Step, self).__setattr__(name, value)

