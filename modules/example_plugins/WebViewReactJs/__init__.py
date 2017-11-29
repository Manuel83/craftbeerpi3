from flask import Blueprint

from modules import cbpi
from flask_swagger import swagger
from flask import json
from flask import Blueprint

@cbpi.addon.core.initializer(order=22)
def web(cbpi):

    s = Blueprint('webviewreact', __name__, template_folder='templates', static_folder='static')

    @s.route('/',  methods=["GET"])
    def index():
        return s.send_static_file("index.html")


    cbpi.addon.core.add_menu_link("ReactJS View", "/webviewreact")
    cbpi.web.register_blueprint(s, url_prefix='/webviewreact')
