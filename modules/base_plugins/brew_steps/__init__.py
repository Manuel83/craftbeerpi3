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
    temp = Property.Number("Temperature", configurable=True, description="Target Temperature of Mash Step")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, description="Timer is started when the target temperature is reached")

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
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Mash Step Completed!", "Starting the next step", timeout=None)
            self.next()


@cbpi.step
class MashInStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True,  description="Target Temperature of Mash Step")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    s = False

    @cbpi.action("Change Power")
    def change_power(self):
        self.actor_power(1, 50)

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
        if self.get_kettle_temp(self.kettle) >= float(self.temp) and self.s is False:
            self.s = True
            self.notify("Step Temp Reached!", "Please press the next button to continue", timeout=None)



@cbpi.step
class ChilStep(StepBase):

    timer = Property.Number("Timer in Minutes", configurable=True, default_value=0, description="Timer is started immediately")

    @cbpi.action("Stat Timer")
    def start(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()


    def finish(self):
        pass

    def execute(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

        if self.is_timer_finished() == True:
            self.next()

@cbpi.step
class PumpStep(StepBase):

    pump = StepProperty.Actor("Pump", description="Pump actor gets toogled")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=0, description="Timer is started immediately")

    @cbpi.action("Stat Timer")
    def start(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()


    def finish(self):
        self.actor_off(int(self.pump))

    def init(self):
        self.actor_on(int(self.pump))

    def execute(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

        if self.is_timer_finished() == True:
            self.next()

@cbpi.step
class BoilStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True, default_value=100, description="Target temperature for boiling")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")
    hop_1 = Property.Number("Hop 1 Addition", configurable=True, description="Fist Hop alert")
    hop_1_added = Property.Number("",default_value=None)
    hop_2 = Property.Number("Hop 2 Addition", configurable=True, description="Second Hop alert")
    hop_2_added = Property.Number("", default_value=None)
    hop_3 = Property.Number("Hop 3 Addition", configurable=True)
    hop_3_added = Property.Number("", default_value=None, description="Third Hop alert")
    hop_4 = Property.Number("Hop 4 Addition", configurable=True)
    hop_4_added = Property.Number("", default_value=None, description="Fourth Hop alert")
    hop_5 = Property.Number("Hop 5 Addition", configurable=True)
    hop_5_added = Property.Number("", default_value=None, description="Fives Hop alert")

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


    def check_hop_timer(self, number, value):

        if self.__getattribute__("hop_%s_added" % number) is not True and time.time() > (
            self.timer_end - (int(self.timer) * 60 - int(value) * 60)):
            self.__setattr__("hop_%s_added" % number, True)
            self.notify("Hop Alert", "Please add Hop %s" % number, timeout=None)

    def execute(self):
        '''
        This method is execute in an interval
        :return:
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)
            else:
                self.check_hop_timer(1, self.hop_1)
                self.check_hop_timer(2, self.hop_2)
                self.check_hop_timer(3, self.hop_3)
                self.check_hop_timer(4, self.hop_4)
                self.check_hop_timer(5, self.hop_5)
        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Boil Step Completed!", "Starting the next step", timeout=None)
            self.next()
