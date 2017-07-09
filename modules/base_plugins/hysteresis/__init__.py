from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property


@cbpi.controller
class Hysteresis(KettleController):

    # Custom Properties

    on = Property.Number("Offset On", True, 0, description="Offset below target temp when heater should switched on. Should be bigger then Offset Off")
    off = Property.Number("Offset Off", True, 0, description="Offset below target temp when heater should switched off. Should be smaller then Offset Off")

    def stop(self):
        '''
        Invoked when the automatic is stopped.
        Normally you switch off the actors and clean up everything
        :return: None
        '''
        super(KettleController, self).stop()
        self.heater_off()




    def run(self):
        '''
        Each controller is exectuted in its own thread. The run method is the entry point
        :return: 
        '''
        while self.is_running():

            if self.get_temp() < self.get_target_temp() - float(self.on):
                self.heater_on(100)
            elif self.get_temp() >= self.get_target_temp() - float(self.off):
                self.heater_off()
            else:
                self.heater_off()
            self.sleep(1)

