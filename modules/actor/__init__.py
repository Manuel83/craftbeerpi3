import time
from flask_classy import route
from modules import DBModel, cbpi
from modules.core.baseview import BaseView

class Actor(DBModel):
    __fields__ = ["name","type", "config", "hide"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]

class ActorView(BaseView):
    model = Actor
    cache_key = "actors"

    @classmethod
    def post_init_callback(self, obj):
        obj.state = 0
        obj.power = 100

    def _post_post_callback(self, m):
        self.api.init_actor(m.id)

    def _post_put_callback(self, m):

        self.api.init_actor(m.id)

    @route("<int:id>/switch/on", methods=["POST"])
    def on(self, id):
        self.api.switch_actor_on(id)
        return ('', 204)

    @route("<int:id>/switch/off", methods=["POST"])
    def off(self, id):
        self.api.switch_actor_off(id)
        return ('', 204)

    @route("<int:id>/power/<int:power>", methods=["POST"])
    def power(self, id, power):
        self.api.actor_power(id, power)
        return ('', 204)

    @route("<int:id>/toggle", methods=["POST"])
    def toggle(self, id):

        if self.api.cache.get("actors").get(id).state == 0:
            self.on(id)
        else:
            self.off(id)
        return ('', 204)

    def toggleTimeJob(self, id, t):
        self.api.cache.get("actors").get(int(id)).timer = int(time.time()) + int(t)
        self.toggle(int(id))
        self.api.socketio.sleep(t)
        self.api.cache.get("actors").get(int(id)).timer = None
        self.toggle(int(id))

    @route("/<id>/toggle/<int:t>", methods=["POST"])
    def toggleTime(self, id, t):
        t = self.api.socketio.start_background_task(target=self.toggleTimeJob, id=id, t=t)
        return ('', 204)

    @route('<int:id>/action/<method>', methods=["POST"])
    def action(self, id, method):

        cbpi.cache.get("actors").get(id).instance.__getattribute__(method)()
        return ('', 204)


@cbpi.initalizer(order=1000)
def init(cbpi):
    ActorView.register(cbpi.app, route_base='/api/actor')
    ActorView.init_cache()
    cbpi.init_actors()