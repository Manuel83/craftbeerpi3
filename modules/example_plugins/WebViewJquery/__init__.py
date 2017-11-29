from flask import Blueprint

from modules import cbpi
from flask_swagger import swagger
from flask import json
from flask import Blueprint

@cbpi.addon.core.initializer(order=22)
def web(cbpi):

    s = Blueprint('web_view', __name__, template_folder='templates', static_folder='static')

    @s.route('/',  methods=["GET"])
    def index():
        return s.send_static_file("index.html")


    cbpi.addon.core.add_menu_link("JQuery View", "/web_view")
    cbpi.web.register_blueprint(s, url_prefix='/web_view')
