import json
import logging
from flask_classy import FlaskView, route
from modules.core.core import cbpi


class ActionView(FlaskView):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @route('/<action>', methods=['POST'])
    def action(self, action):
        """
        Call global action button
        ---
        tags:
          - action
        responses:
          200:
            description: action invoked
        """

        self.cbpi.cache["actions"][action]["function"](self.cbpi)

        return ('',204)

@cbpi.addon.core.initializer()
def init(cbpi):
    """
    Initializer for the message module
    :param app: the flask app
    :return: None
    """
    ActionView.cbpi = cbpi
    ActionView.register(cbpi._app, route_base='/api/action')
