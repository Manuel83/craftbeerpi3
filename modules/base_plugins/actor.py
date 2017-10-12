import logging
from modules.core.baseapi import Buzzer
from modules.core.basetypes import Actor, KettleController, FermenterController
from modules.core.core import cbpi


@cbpi.addon.actor.type("Dummy Actor")
class Dummy(Actor):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @cbpi.addon.actor.action("WOHOO")
    def myaction(self):
        self.logger.debug("HALLO!!!")

    def on(self, power=100):
        '''
        Code to switch on the actor
        :param power: int value between 0 - 100
        :return: 
        '''
        self.logger.info("ON")

    def off(self):
        self.logger.info("OFF")



@cbpi.addon.kettle.controller()
class MyController(KettleController):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run(self):
        while self.is_running():
            self.logger.debug("HALLO")
            self.sleep(1)

@cbpi.addon.fermenter.controller()
class MyController2(FermenterController):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def run(self):
        while self.is_running():
            self.logger.debug("HALLO")
            self.sleep(1)

@cbpi.addon.core.initializer(order=200)
def init(cbpi):

    class MyBuzzer(Buzzer):
        def __init__(self):
            self.logger = logging.getLogger(__name__)

        def beep(self):
            self.logger.info("BEEEEEEP")

    cbpi.buzzer = MyBuzzer()
