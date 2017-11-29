import flask_login
from flask import request

from modules import cbpi

class User(flask_login.UserMixin):
    pass

@cbpi.addon.core.initializer(order=0)
def log(cbpi):


    cbpi._login_manager = flask_login.LoginManager()
    cbpi._login_manager.init_app(cbpi.web)

    @cbpi.web.route('/login', methods=['POST'])
    def login():

         data = request.json
         password = cbpi.get_config_parameter("password", None)

         if password is None:
             return ('',500)

         if password == data.get("password",""):
            user = User()
            user.id = "craftbeerpi"
            flask_login.login_user(user)
            return ('',204)
         else:
            return ('',401)


    @cbpi.web.route('/logout', methods=['POST'])
    def logout():
        flask_login.logout_user()
        return 'Logged out'

    @cbpi._login_manager.request_loader
    def load_user_from_request(request):


        api_key = request.args.get('api_key')

        if cbpi.get_config_parameter("password_security", "NO") == "NO":
            user = User()
            user.id = "craftbeerpi"
            return user
        elif api_key == "123":
            user = User()
            user.id = "craftbeerpi"
            return user
        return None

    @cbpi._login_manager.user_loader
    def user_loader(user):

        if cbpi.get_config_parameter("password_security", "NO") == "YES":
            if user != "craftbeerpi":
                return
            user = User()
            user.id = user
            return user
        else:
            user = User()
            user.id = user
            return user

    @cbpi._login_manager.unauthorized_handler
    def unauthorized_handler():


        return ('Please login',401)
