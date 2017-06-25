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
        '''
        :return: Unit of the sensor as string. Should not be longer than 3 characters
        '''
        return "°C" if self.get_config_parameter("unit", "C") == "C" else "°F"

    def stop(self):
        '''
        Stop the sensor. Is called when the sensor config is updated or the sensor is deleted
        :return: 
        '''
        pass

    def execute(self):
        '''
        Active sensor has to handle his own loop
        :return: 
        '''
        while self.is_running():
            self.data_received(self.temp)
            socketio.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return: 
        '''









