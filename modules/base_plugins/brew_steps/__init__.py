# -*- coding: utf-8 -*-
import time


from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi


@cbpi.step
class MashStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True)
    kettle = StepProperty.Kettle("Kettle")
    timer = Property.Number("Timer in Minutes", configurable=True)

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return: 
        '''
        # set target tep
        self.set_target_temp(self.temp, self.kettle)

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        Custom Action which can be execute form the brewing dashboard.
        All method with decorator @cbpi.action("YOUR CUSTOM NAME") will be available in the user interface
        :return: 
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.temp, self.kettle)

    def finish(self):
        self.set_target_temp(0, self.kettle)

    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''

        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= int(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.next()


@cbpi.step
class MashInStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True)
    kettle = StepProperty.Kettle("Kettle")
    s = False

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return: 
        '''
        # set target tep
        self.s = False
        self.set_target_temp(self.temp, self.kettle)



    def execute(self):
        '''
        This method is execute in an interval
        :return: 
        '''

        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= int(self.temp) and self.s is False:
            self.s = True
            self.notify("Step Temp Reached!", "Please press the next button to continue", timeout=None)



