from modules import cbpi
from flask_swagger import swagger
from flask import json
from flask import Blueprint

@cbpi.addon.core.initializer(order=22)
def hello(cbpi):

    s = Blueprint('react', __name__, template_folder='templates', static_folder='static')

    @s.route('/',  methods=["GET"])
    def index():
        return s.send_static_file("index.html")

    @s.route('/swagger.json',  methods=["GET"])
    def spec():
        swag = swagger(cbpi.web)
        swag['info']['version'] = "3.0"
        swag['info']['title'] = "CraftBeerPi"
        return json.dumps(swag)

    cbpi.addon.core.add_menu_link("Swagger API", "/swagger")
    cbpi.web.register_blueprint(s, url_prefix='/swagger')
