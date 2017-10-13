from flask import Blueprint

from modules.core.core import cbpi, addon
from flask_swagger import swagger
from flask import json
from flask import Blueprint

import logging

@addon.core.initializer(order=22)
def web(cbpi):
    logger = logging.getLogger(__name__)

    s = Blueprint('webviewreact', __name__, template_folder='templates', static_folder='static')

    @s.route('/',  methods=["GET"])
    def index():
        return s.send_static_file("index.html")

    logger.info("REGISTER")
    cbpi.addon.core.add_menu_link("ReactJS View", "/webviewreact")
    cbpi._app.register_blueprint(s, url_prefix='/webviewreact')
