from modules import cbpi
from modules.core.controller import KettleController, FermenterController
from modules.core.props import Property


@cbpi.fermentation_controller
class Hysteresis(FermenterController):

    on = Property.Number("Offset On", True, 0)
    off = Property.Number("Offset Off", True, 0)

    def stop(self):

        super(FermenterController, self).stop()
        self.heater_off()

    def run(self):
        while self.is_running():
            print "Temp %s" % self.get_temp()
            if self.get_temp() < self.get_target_temp() - int(self.on):
                self.heater_on(100)
            elif self.get_temp() >= self.get_target_temp() - int(self.off):
                self.heater_off()
            else:
                self.heater_off()
            if self.get_temp() > self.get_target_temp() + int(self.on):
                self.cooler_on()
            elif self.get_temp() <= self.get_target_temp() + int(self.off):
                self.cooler_off()
            else:
                self.cooler_off()
            self.sleep(1)

