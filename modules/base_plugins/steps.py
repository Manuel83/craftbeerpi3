import logging

from modules.core.basetypes import Step
from modules.core.core import cbpi
from modules.core.proptypes import Property


@cbpi.addon.step.type("Dummy Step")
class Dummy(Step):

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    @cbpi.addon.step.action("WOHOO")
    def myaction(self):
        self.stop_timer()
        self.start_timer(10)
        self.logger.debug("HALLO")

    text = Property.Text(label="Text", configurable=True, description="WOHOOO")
    time = Property.Text(label="Text", configurable=True, description="WOHOOO")

    def execute(self):
        self.logger.debug(self.text)
        pass

    def reset(self):
        self.logger.info("RESET STEP!!!")
        self.stop_timer()
