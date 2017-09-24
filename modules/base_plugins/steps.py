from modules.core.basetypes import Step
from modules.core.core import cbpi
from modules.core.proptypes import Property


@cbpi.addon.step.type("Dummy Step")
class Dummy(Step):


    @cbpi.addon.step.action("WOHOO")
    def myaction(self):
        print "HALLO"

    text = Property.Text(label="Text", configurable=True, description="WOHOOO")

    def execute(self):
        #print self.text
        pass