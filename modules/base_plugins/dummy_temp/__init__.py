# -*- coding: utf-8 -*-
import subprocess
import time

from modules import cbpi, socketio
from modules.core.hardware import  SensorActive
from modules import cbpi
from modules.core.props import Property


@cbpi.sensor
class DummyTempSensor(SensorActive):

    temp = Property.Number("Temperature", configurable=True, default_value=5, description="Dummy Temperature as decimal value")

    @cbpi.action("My Custom Action")
    def my_action(self):
        print "HELLO WORLD"
        pass

    def get_unit(self):
        '''
        :return: Unit of the sensor as string. Should not be longer than 3 characters
        '''
        return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"

    def stop(self):
        SensorActive.stop(self)

    def execute(self):
        '''
        Active sensor has to handle his own loop
        :return: 
        '''
        while self.is_running() is True:
            self.data_received(self.temp)
            self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''









