
class Base(object):

    def __init__(self, *args, **kwds):
        for a in kwds:

            super(Base, self).__setattr__(a, kwds.get(a))
        self.api = kwds.get("cbpi")
        self.id = kwds.get("id")
        self.value = None
        self.__dirty = False

class Actor(Base):

    @classmethod
    def init_global(cls):
        print "GLOBAL INIT ACTOR"
        pass

    def init(self):
        pass

    def shutdown(self):
        pass

    def on(self, power=100):
        print "SWITCH ON"
        pass

    def off(self):
        print "SWITCH OFF"
        pass

    def power(self, power):
        print "SET POWER", power
        pass

    def state(self):
        pass


class Sensor(Base):

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
        self.cbpi.sensor.write_log(self.id, value)
        self.cbpi.emit("SENSOR_UPDATE", id=self.id, value=value)
        self.cbpi.ws_emit("SENSOR_UPDATE", self.cbpi.cache["sensors"][self.id])

    def execute(self):
        print "EXECUTE"
        pass




class ControllerBase(object):
    __dirty = False
    __running = False

    @staticmethod
    def init_global():
        print "GLOBAL CONTROLLER INIT"

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



class Step(Base):


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
        print "-------------"
        print "Step Info"
        print "Kettle ID: %s" % self.kettle_id
        print "ID: %s" % self.id

    def __init__(self, *args, **kwds):

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

