from modules import cbpi
from modules.core.controller import KettleController, FermenterController
from modules.core.props import Property


@cbpi.fermentation_controller
class Hysteresis(FermenterController):

    heater_offset_min = Property.Number("Heater Offset ON", True, 0, description="Offset as decimal number when the heater is switched on. Should be geather then 'Heater Offset OFF'. For example 2 means the heater will be switched on if the current temperature is 2 degrees above the target temperature")
    heater_offset_max = Property.Number("Heater Offset OFF", True, 0, description="Offset as decimal number when the heater is switched off. Should be smaller then 'Heater Offset ON'. For example 1 means the heater will be switched off if the current temperature is 1 degrees above the target temperature")
    cooler_offset_min = Property.Number("Cooler Offset ON", True, 0, description="Offset as decimal number when the cooler is switched on. Should be geather then 'Cooler Offset OFF'. For example 2 means the cooler will be switched on if the current temperature is 2 degrees below the target temperature")
    cooler_offset_max = Property.Number("Cooler Offset OFF", True, 0, description="Offset as decimal number when the cooler is switched off. Should be less then 'Cooler Offset ON'. For example 1 means the cooler will be switched off if the current temperature is 1 degrees below the target temperature")

    def stop(self):
        super(FermenterController, self).stop()

        self.heater_off()
        self.cooler_off()

    def run(self):
        while self.is_running():

            target_temp = self.get_target_temp()
            temp = self.get_temp()

            if temp + float(self.heater_offset_min) <= target_temp:
                self.heater_on(100)

            if temp + float(self.heater_offset_max) >= target_temp:
                self.heater_off()

            if temp >= target_temp + float(self.cooler_offset_min):
                self.cooler_on(100)

            if temp <= target_temp + float(self.cooler_offset_max):
                self.cooler_off()

            self.sleep(1)
