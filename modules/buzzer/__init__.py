import time
from thread import start_new_thread
from modules import cbpi

try:
    import RPi.GPIO as GPIO
except Exception as e:
    pass

class Buzzer(object):

    sound = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    def __init__(self, gpio, buzzer_type, beep_level):
        try:
            cbpi.app.logger.info("INIT BUZZER NOW GPIO%s" % gpio)
            self.gpio = int(gpio)
            self.beep_level = beep_level
            self.buzzer_type = buzzer_type
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio, GPIO.OUT)
            if buzzer_type == "PASSIVE":
                self.p = GPIO.PWM(int(gpio), 5000)
            self.state = True
            cbpi.app.logger.info("BUZZER SETUP OK")
        except Exception as e:
            cbpi.app.logger.info("BUZZER EXCEPTION %s" % str(e))
            self.state = False

    def beep(self):
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
            return

        def play(sound):
            def output(level):
                if self.buzzer_type == "PASSIVE" and level == GPIO.LOW:
                    self.p.stop()
                elif self.buzzer_type == "PASSIVE":
                    self.p.start(50)
                else:
                    GPIO.output(int(self.gpio), level)

            try:
                for i in sound:
                    if (isinstance(i, str)):
                        if i == "H" and self.beep_level == "HIGH":
                            output(GPIO.HIGH)
                        elif i == "H" and self.beep_level != "HIGH":
                            output(GPIO.LOW)
                        elif i == "L" and self.beep_level == "HIGH":
                            output(GPIO.LOW)
                        else:
                            output(GPIO.HIGH)
                    else:
                        time.sleep(i)
                if self.buzzer_type == "PASSIVE":
                    self.p.stop()
            except Exception as e:
                pass

        start_new_thread(play, (self.sound,))

@cbpi.initalizer(order=1)
def init(cbpi):
    gpio = cbpi.get_config_parameter("buzzer", 16)
    beep_level = cbpi.get_config_parameter("buzzer_beep_level", "HIGH")
    buzzer_type = cbpi.get_config_parameter("buzzer_type", "ACTIVE")

    cbpi.buzzer = Buzzer(gpio, buzzer_type, beep_level)
    cbpi.beep()
    cbpi.app.logger.info("INIT OK")
