from modules.core.baseapi import Buzzer
from modules.core.basetypes import Actor, KettleController, FermenterController
from modules.core.core import cbpi

@cbpi.addon.actor.type("Dummy Actor")
class Dummy(Actor):


    @cbpi.addon.actor.action("WOHOO")
    def myaction(self):
        pass

    def on(self, power=100):
        '''
        Code to switch on the actor
        :param power: int value between 0 - 100
        :return: 
        '''
        print "ON"

    def off(self):
        print "OFF"



@cbpi.addon.kettle.controller()
class MyController(KettleController):

    def run(self):
        while self.is_running():

            self.sleep(1)

@cbpi.addon.fermenter.controller()
class MyController2(FermenterController):


    def run(self):
        while self.is_running():
            print "HALLO"
            self.sleep(1)

@cbpi.addon.core.initializer(order=200)
def init(cbpi):

    class MyBuzzer(Buzzer):
        def beep(self):
            pass

    cbpi.buzzer = MyBuzzer()
