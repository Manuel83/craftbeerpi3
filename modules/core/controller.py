from modules import cbpi


class ActorController(object):

    @cbpi.try_catch(None)
    def actor_on(self, power=100, id=None):

        if id is None:
            id = self.heater
        self.api.switch_actor_on(int(id), power=power)

    @cbpi.try_catch(None)
    def actor_off(self, id=None):
        if id is None:
            id = self.heater

        self.api.switch_actor_off(int(id))

    @cbpi.try_catch(None)
    def actor_power(self, power, id=None):
        if id is None:
            id = self.heater
        self.api.actor_power(int(id), power)


class SensorController(object):

    @cbpi.try_catch(None)
    def get_sensor_value(self, id=None):

        if id is None:
            id = self.sensor

        return cbpi.get_sensor_value(id)



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
        self.api.socketio.sleep(seconds)

    def stop(self):
        self.__running = False


    def __init__(self, *args, **kwds):
        for a in kwds:
            super(ControllerBase, self).__setattr__(a, kwds.get(a))
        self.api = kwds.get("api")
        self.heater = kwds.get("heater")
        self.sensor = kwds.get("sensor")


    def run(self):
        pass

class KettleController(ControllerBase, ActorController, SensorController):

    @staticmethod
    def chart(kettle):
        result = []
        result.append({"name": "Temp", "data_type": "sensor", "data_id": kettle.sensor})
        result.append({"name": "Target Temp", "data_type": "kettle", "data_id": kettle.id})

        return result

    def __init__(self, *args, **kwds):
        ControllerBase.__init__(self, *args, **kwds)
        self.kettle_id = kwds.get("kettle_id")

    @cbpi.try_catch(None)
    def heater_on(self, power=100):
        k = self.api.cache.get("kettle").get(self.kettle_id)
        if k.heater is not None:
            self.actor_on(power, int(k.heater))




    @cbpi.try_catch(None)
    def heater_off(self):
        k = self.api.cache.get("kettle").get(self.kettle_id)
        if k.heater is not None:
            self.actor_off(int(k.heater))

    @cbpi.try_catch(None)
    def get_temp(self, id=None):
        if id is None:
            id = self.kettle_id
        return self.get_sensor_value(int(self.api.cache.get("kettle").get(id).sensor))

    @cbpi.try_catch(None)
    def get_target_temp(self, id=None):
        if id is None:
            id = self.kettle_id
        return self.api.cache.get("kettle").get(id).target_temp

class FermenterController(ControllerBase, ActorController, SensorController):

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



    @cbpi.try_catch(None)
    def get_target_temp(self, id=None):
        if id is None:
            id = self.fermenter_id
        return self.api.cache.get("fermenter").get(id).target_temp

    @cbpi.try_catch(None)
    def heater_on(self, power=100):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.heater is not None:
            self.actor_on(power, int(f.heater))

    @cbpi.try_catch(None)
    def heater_off(self):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.heater is not None:
            self.actor_off(int(f.heater))

    @cbpi.try_catch(None)
    def cooler_on(self, power=100):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.cooler is not None:
            self.actor_on(power, int(f.cooler))

    @cbpi.try_catch(None)
    def cooler_off(self):
        f = self.api.cache.get("fermenter").get(self.fermenter_id)
        if f.cooler is not None:
            self.actor_off(int(f.cooler))

    @cbpi.try_catch(None)
    def get_temp(self, id=None):

        if id is None:
            id = self.fermenter_id
        return self.get_sensor_value(int(self.api.cache.get("fermenter").get(id).sensor))

