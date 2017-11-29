import json

from flask import request
from flask_classy import FlaskView, route
from modules import cbpi

class ActionView(FlaskView):

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
        data = request.json

        obj = self.cbpi.cache["actions"][action]["class"](self.cbpi)
        obj.execute(**data)
        return ('',204)

@cbpi.addon.core.initializer()
def init(cbpi):
    """
    Initializer for the message module
    :param app: the flask app
    :return: None
    """
    ActionView.cbpi = cbpi
    ActionView.register(cbpi.web, route_base='/api/action')
