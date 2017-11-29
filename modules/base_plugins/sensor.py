# -*- coding: utf-8 -*-
import os

from os.path import join

from modules.core.basetypes import Actor, Sensor, Action
from modules import cbpi
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

    @cbpi.addon.sensor.action(label="Set Dummy Temp", parameters={
        "p1":Property.Select(label="Temp",options=[1,2,3]),

    })
    def myaction(self, p1):
        self.text = p1
        self.update_value(int(p1))



    def execute(self):
        while True:
            try:
                self.update_value(int(self.text))
            except:
                pass
            self.api.sleep(5)


@cbpi.addon.core.action(name="Delete All Logs")
class ParameterAction(Action):

    p1 = Property.Number("P1", configurable=True, description="Target Temperature of Mash Step", unit="C")
    p2 = Property.Number("P2", configurable=True, description="Target Temperature of Mash Step", unit="C")


    def execute(self, p1, p2, **kwargs):
        for i in range(5):
            cbpi.sleep(1)
            cbpi.notify(headline="Woohoo", message="%s %s" % (p1, p2))


@cbpi.addon.core.action(name="Delete All Logs")
class DeleteAllLogs(Action):
    def execute(self, **kwargs):
        dir = "./logs"
        test = os.listdir(dir)

        for item in test:

            if item.endswith(".log"):
                os.remove(join(dir, item))
        cbpi.notify(headline="Logs Deleted", message="All Logs Cleared")