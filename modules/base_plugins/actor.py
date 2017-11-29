from modules.core.baseapi import Buzzer
from modules.core.basetypes import Actor, KettleController, FermenterController
from modules import cbpi
from modules.core.proptypes import Property

@cbpi.addon.actor.type("Dummy Actor")
class Dummy(Actor):


    # Decorator to create a parameter based action
    @cbpi.addon.actor.action("Run until Temp reached", parameters={"t": Property.Text(label="Target Temp")})
    def check_sensor_value(self, t=1):

        def check(api, id, value):
            '''
            Background Prozess which checks the sensor value every second
            :param api: 
            :param id: 
            :param value: 
            :return: 
            '''
            while api.sensor.get_value(1) < value:
                api.sleep(1)
            api.actor.off(id)

        target_value = int(t)

        # Create notificaiton
        self.api.notify(headline="Waiting", message="Waiting for temp %s" % target_value)
        # Switch actor on
        self.api.actor.on(self.id, 100)
        # Start Background task
        self.api.start_background_task(check, self.api, id=self.id, value=target_value)


    def on(self, power=100):
        '''
        Code to switch on the actor
        :param power: int value between 0 - 100
        :return: 
        '''
        print "ID %s ON" % self.id

    def off(self):
        print "ID %s OFF" % self.id


@cbpi.addon.kettle.controller()
class MyController(KettleController):

    def run(self):
        while self.is_running():
            print "HALLO"

            self.sleep(1)

@cbpi.addon.fermenter.controller()
class MyController2(FermenterController):


    def run(self):
        while self.is_running():
            print "HALLO"

            self.get_target_temp()
            self.sleep(1)

@cbpi.addon.core.initializer(order=200)
def init(cbpi):

    class MyBuzzer(Buzzer):
        def beep(self):
            print "BEEEEEP"
            pass

    cbpi.buzzer = MyBuzzer()
