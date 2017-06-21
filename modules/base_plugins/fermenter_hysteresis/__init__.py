from modules import cbpi
from modules.core.controller import KettleController, FermenterController
from modules.core.props import Property


@cbpi.fermentation_controller
class Hysteresis(FermenterController):

    heater_offset_min = Property.Number("Heater Offset min", True, 0)
    heater_offset_max = Property.Number("Heater Offset max", True, 0)
    cooler_offset_min = Property.Number("Cooler Offset min", True, 0)
    cooler_offset_max = Property.Number("Cooler Offset max", True, 0)

    def stop(self):
        super(FermenterController, self).stop()

        self.heater_off()
        self.cooler_off()

    def run(self):
        while self.is_running():

            target_temp = self.get_target_temp()
            temp = self.get_temp()

            if temp + float(self.heater_offset_min) < target_temp:
                self.heater_on(100)

            if temp + float(self.heater_offset_max) > target_temp:
                self.heater_off()

            if temp > target_temp + float(self.cooler_offset_min):
                self.cooler_on(100)

            if temp < target_temp + float(self.cooler_offset_max):
                self.cooler_off()

            self.sleep(1)
