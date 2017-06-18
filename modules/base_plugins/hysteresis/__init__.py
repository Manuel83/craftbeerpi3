from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property


@cbpi.controller
class Hysteresis(KettleController):

    # Custom Properties

    on = Property.Number("Offset On", True, 0)
    off = Property.Number("Offset Off", True, 0)

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

            self.actor_power(50)

            if self.get_temp() < self.get_target_temp() - int(self.on):
                self.heater_on(100)
            elif self.get_temp() >= self.get_target_temp() - int(self.off):
                self.heater_off()
            else:
                self.heater_off()
            self.sleep(1)

