from modules.core.basetypes import Step
from modules.core.core import cbpi
from modules.core.proptypes import Property


@cbpi.addon.step.type("Dummy Step")
class Dummy(Step):


    @cbpi.addon.step.action("WOHOO")
    def myaction(self):
        self.stop_timer()
        self.start_timer(10)
        print "HALLO"

    text = Property.Text(label="Text", configurable=True, description="WOHOOO")
    time = Property.Text(label="Text", configurable=True, description="WOHOOO")

    def execute(self):
        #print self.text
        pass

    def reset(self):
        print "RESET STEP!!!"
        self.stop_timer()