from flask import Blueprint

from modules.core.core import cbpi

react = Blueprint('ui', __name__, template_folder='templates', static_folder='static')

@cbpi.addon.core.initializer(order=10)
def init(cbpi):
    cbpi._app.register_blueprint(react, url_prefix='/ui')


@react.route('/',  methods=["GET"])
def index():
    return react.send_static_file("index.html")









