import flask_login
from modules.core.core import cbpi, addon

class User(flask_login.UserMixin):
    pass

@addon.core.initializer(order=0)
def log(cbpi):


    cbpi._login_manager = flask_login.LoginManager()
    cbpi._login_manager.init_app(cbpi._app)
    @cbpi._app.route('/login', methods=['GET', 'POST'])
    def login():
         user = User()
         user.id = "manuel"
         flask_login.login_user(user)
         return "OK"

    @cbpi._app.route('/logout')
    def logout():
        flask_login.logout_user()
        return 'Logged out'

    @cbpi._login_manager.user_loader
    def user_loader(email):
        if email not in cbpi.cache["users"]:
            return

        user = User()
        user.id = email
        return user

    @cbpi._login_manager.unauthorized_handler
    def unauthorized_handler():
        return 'Unauthorized :-('
