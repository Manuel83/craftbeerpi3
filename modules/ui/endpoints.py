from flask import Blueprint

from modules import cbpi

react = Blueprint('react', __name__, template_folder='templates', static_folder='static')

@cbpi.initalizer(order=10)
def init(cbpi):
    cbpi.app.register_blueprint(react, url_prefix='/ui')




@react.route('/',  methods=["GET"])
def index():
    return react.send_static_file("index.html")









