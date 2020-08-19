# -*- coding: utf-8 -*-
""" base gpio actors """
import time

from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property

try:
    import RPi.GPIO as GPIO  # pylint: disable=import-error

    GPIO.setmode(GPIO.BCM)
except ImportError as exp:
    print(exp)


@cbpi.actor
class GPIOSimple(ActorBase):
    """
    Simple GPIO Actor
    """
    gpio = Property.Select("GPIO",
                           options=[
                               0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                               14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                               26, 27
                           ],
                           description="GPIO to which the actor is connected")

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 0)

    def on(self, power=0):
        print(("GPIO ON %s" % str(self.gpio)))
        GPIO.output(int(self.gpio), 1)

    def off(self):
        print("GPIO OFF")
        GPIO.output(int(self.gpio), 0)


@cbpi.actor
class GPIOPWM(ActorBase):
    """
    GPIO Actor with PWM support
    """
    gpio = Property.Select("GPIO",
                           options=[
                               0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                               14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                               26, 27
                           ],
                           description="GPIO to which the actor is connected")
    frequency = Property.Number("Frequency (Hz)", configurable=True)

    gpio_inst = None
    power = 100  # duty cycle

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 0)

    def on(self, power=None):
        if power is not None:
            self.power = int(power)

        if self.frequency is None:
            self.frequency = 0.5  # 2 sec

        if self.gpio_inst is None:
            self.gpio_inst = GPIO.PWM(int(self.gpio), float(self.frequency))
        self.gpio_inst.start(int(self.power))

    def set_power(self, power):
        '''
        Optional: Set the power of your actor
        :param power: int value between 0 - 100
        :return:
        '''
        if self.gpio_inst:
            if power is not None:
                self.power = int(power)
            self.gpio_inst.ChangeDutyCycle(self.power)

    def off(self):
        print("GPIO OFF")
        self.gpio_inst.stop()


@cbpi.actor
class RelayBoard(ActorBase):
    """
    Relay board Actor
    """
    gpio = Property.Select("GPIO",
                           options=[
                               0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                               14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                               26, 27
                           ],
                           description="GPIO to which the actor is connected")

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 1)

    def on(self, power=0):

        GPIO.output(int(self.gpio), 0)

    def off(self):

        GPIO.output(int(self.gpio), 1)


@cbpi.actor
class Dummy(ActorBase):
    """
    Simple Dummy Actor
    """

    def on(self, power=100):
        '''
        Code to switch on the actor
        :param power: int value between 0 - 100
        :return:
        '''
        print("ON")

    def off(self):
        print("OFF")


@cbpi.actor
class DummyPWM(ActorBase):
    """
    Dummy Actor with PWM support
    """
    power = 100

    def on(self, power=100):
        '''
        Code to switch on the actor
        :param power: int value between 0 - 100
        :return:
        '''
        self.power = int(power) if power is not None else 100
        print("DummyPWM ON %s" % self.power)

    def off(self):
        self.power = 100
        print("OFF")

    def set_power(self, power):
        self.power = int(power)
        print("DummyPWM POWER %s" % self.power)
