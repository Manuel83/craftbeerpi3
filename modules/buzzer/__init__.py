import time
from thread import start_new_thread
from modules import cbpi

try:
    import RPi.GPIO as GPIO
except Exception as e:
    pass

class Buzzer(object):

# custom beep sounds

    sound = ["H", 0.1, "L"]
    melodie1 = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    melodie2 = ["H", 0.1, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.1, "L"]
    melodie3 = ["H", 0.4, "L", 0.1, "H", 0.4, "L", 0.1, "H", 0.4, "L"]
    melodie4 = ["H", 0.4, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.4, "L", 0.1, "H", 0.1, "L", 0.1, "H", 0.4, "L"]
    melodie5 = ["H", 0.6, "L", 0.3, "H", 0.6, "L", 0.3, "H", 0.6, "L"]
    melodie6 = ["H", 0.2, "L", 0.4, "H", 0.2, "L", 0.3, "H", 0.2, "L", 0.2, "H", 0.2, "L", 0.1, "H", 0.2, "L", 0.1, "H", 0.2, "L"]
    def __init__(self, gpio):
        try:
            cbpi.app.logger.info("INIT BUZZER NOW GPIO%s" % gpio)
            self.gpio = int(gpio)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio, GPIO.OUT)
            self.state = True
            cbpi.app.logger.info("BUZZER SETUP OK")
        except Exception as e:
            cbpi.app.logger.info("BUZZER EXCEPTION %s" % str(e))
            self.state = False

			
			
		
			
			
    def beep(self):  # beeps once when you boot up your Pi with CBPi -- beeps at Brewing finished
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie2,))


    def MashStepEndBeep(self):   # beeps at end of step
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie1,))
		


    def MashInStepEndBeep(self):   # beeps at end of step
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie3,))
		
		
    def ChilStepEndBeep(self):   # beeps at end of step
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie4,))		
		
		
    def PumpStepEndBeep(self):   # beeps at end of step
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie5,))		
		
		
    def BoilStepEndBeep(self):   # beeps at end of step
        if self.state is False:
            cbpi.app.logger.error("BUZZER not working")
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

        start_new_thread(play, (self.melodie6,))			
		
		
@cbpi.initalizer(order=1)
def init(cbpi):
    gpio = cbpi.get_config_parameter("buzzer", 16)
    cbpi.buzzer = Buzzer(gpio)
    cbpi.beep()
    cbpi.MashStepEndBeep()
    cbpi.MashInStepEndBeep()
    cbpi.ChilStepEndBeep()
    cbpi.PumpStepEndBeep()
    cbpi.BoilStepEndBeep()
    cbpi.app.logger.info("INIT OK")
