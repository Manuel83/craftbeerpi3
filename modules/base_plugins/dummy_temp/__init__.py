# -*- coding: utf-8 -*-
import subprocess
import time

from modules import cbpi, socketio
from modules.core.hardware import  SensorActive
from modules import cbpi
from modules.core.props import Property


@cbpi.sensor
class DummyTempSensor(SensorActive):
    temp = Property.Number("Temperature", configurable=True, default_value=5)

    def get_unit(self):
        return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"

    def stop(self):
        pass

    def execute(self):
        while self.is_running():

            self.data_received(self.temp)
            socketio.sleep(5)











