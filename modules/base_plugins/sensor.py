# -*- coding: utf-8 -*-
import os

from os.path import join

from modules.core.basetypes import Actor, Sensor
from modules.core.core import cbpi
from modules.core.proptypes import Property
import random

@cbpi.addon.sensor.type("Dummy Sensor")
class Dummy(Sensor):

    text = Property.Text(label="Text", required=True, description="This is a parameter", configurable=True)
    p = Property.Select(label="hallo",options=[1,2,3])

    def init(self):

        if self.api.get_config_parameter("unit","C") == "C":
            self.unit = "°C"
        else:
            self.unit = "°F"

    @cbpi.addon.sensor.action("WOHOO")
    def myaction(self):

        print "SENSOR ACTION HALLO!!!"

    def execute(self):
        while True:
            try:
                self.update_value(int(self.text))
            except:
                pass
            self.api.sleep(1)

@cbpi.addon.core.action(key="clear", label="Clear all Logs")
def woohoo(cbpi):

    dir = "./logs"
    test = os.listdir(dir)

    for item in test:

        if item.endswith(".log"):
            os.remove(join(dir, item))
    cbpi.notify(headline="Logs Deleted",message="All Logs Cleared")
