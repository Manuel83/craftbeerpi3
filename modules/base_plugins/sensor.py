# -*- coding: utf-8 -*-
import os

from os.path import join

from modules.core.basetypes import Sensor
from modules.core.core import cbpi
from modules.core.proptypes import Property

import logging


@cbpi.addon.sensor.type("Dummy Sensor")
class Dummy(Sensor):

    text = Property.Text(label="Text", required=True, description="This is a parameter", configurable=True)
    p = Property.Select(label="hallo",options=[1,2,3])

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("INIT SENSOR")

    def init(self):
        if self.api.get_config_parameter("unit","C") == "C":
            self.unit = "°C"
        else:
            self.unit = "°F"

    @cbpi.addon.sensor.action("WOHOO")
    def myaction(self):
        self.logger.info(self.text)
        self.logger.debug("SENSOR ACTION HALLO!!!")

    def execute(self):
        while True:
            try:
                self.update_value(int(self.text))
            except:
                pass
            self.api.sleep(1)

@cbpi.addon.core.action(key="clear", label="Clear all Logs")
def woohoo(cbpi):
    logger = logging.getLogger(__name__)
    logger.info("COOL")

    dir = "./logs"
    test = os.listdir(dir)

    for item in test:

        if item.endswith(".log"):
            os.remove(join(dir, item))
    cbpi.notify(headline="Logs Deleted",message="All Logs Cleared")
