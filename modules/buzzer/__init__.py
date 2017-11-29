import time
from thread import start_new_thread

from modules.core.baseapi import Buzzer
from modules import cbpi

try:
    import RPi.GPIO as GPIO
except Exception as e:
    pass

class GPIOBuzzer(Buzzer):

    sound = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]


    def __init__(self, gpio):
        try:
            cbpi.web.logger.info("INIT BUZZER NOW GPIO%s" % gpio)
            self.gpio = int(gpio)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio, GPIO.OUT)
            self.state = True
            cbpi.web.logger.info("BUZZER SETUP OK")
        except Exception as e:
            cbpi.web.logger.info("BUZZER EXCEPTION %s" % str(e))
            self.state = False

    def beep(self):
        if self.state is False:
            cbpi.web.logger.error("BUZZER not working")
            return

        def play(sound):
            try:
                for i in sound:
                    if (isinstance(i, str)):
                        if i == "H":
                            GPIO.output(int(self.gpio), GPIO.HIGH)
                        else:
                            GPIO.output(int(self.gpio), GPIO.LOW)
                    else:
                        time.sleep(i)
            except Exception as e:
                pass

        start_new_thread(play, (self.sound,))

@cbpi.addon.core.initializer(order=1)
def init(cbpi):
    gpio = cbpi.get_config_parameter("buzzer", 16)
    cbpi.buzzer = GPIOBuzzer(gpio)

