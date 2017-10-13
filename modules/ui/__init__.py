from flask import Blueprint,render_template

from modules.core.core import cbpi

import logging

react = Blueprint('ui', __name__, template_folder='templates', static_folder='static')
__logger = logging.getLogger(__name__)

@cbpi.addon.core.initializer(order=10)
def init(cbpi):
    cbpi._app.register_blueprint(react, url_prefix='/ui')


@react.route('/',  methods=["GET"])
def index():
    # return react.send_static_file("index.html")

    js_files = []
    for key, value in cbpi.cache["js"].iteritems():
        js_files.append(value)

    __logger.info(js_files)
    return render_template('index.html', js_files=js_files)



@cbpi._app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404





