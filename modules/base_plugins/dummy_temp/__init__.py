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
    inc = Property.Number("Auto increase", configurable=True, default_value=0.5, description="Dummy Temperature increase as decimal value")
    max_temp = Property.Number("Max temperature", configurable=True, default_value='100', description="Dummy Max. Temperature as decimal value")
    min_temp = Property.Number("Min temperature", configurable=True, default_value='0', description="Dummy Min. Temperature as decimal value")
    current_temp = None

    @cbpi.action("My Custom Action")
    def my_action(self):
        print("HELLO WORLD")
        pass

    @cbpi.action("Reset")
    def reset(self):
        self.current_temp = None

    @cbpi.action("Toogle Up/Down")
    def toogle(self):
        self.inc *= -1

    def stop(self):
        SensorActive.stop(self)

    def execute(self):
        '''
        Active sensor has to handle his own loop
        :return:
        '''
        while self.is_running() is True:
            if not self.current_temp:
                self.current_temp = self.temp
            self.data_received(self.current_temp)
            new_temp = float(self.current_temp) + float(self.inc)
            if float(self.min_temp) <= new_temp <= float(self.max_temp):
                self.current_temp = '%.2f' % new_temp
            self.sleep(5)

    @classmethod
    def init_global(cls):
        '''
        Called one at the startup for all sensors
        :return:
        '''
