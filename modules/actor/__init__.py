import time
from flask_classy import route
from modules.core.db import DBModel
from modules.core.core import cbpi
from modules.core.baseview import BaseView
from modules.database.dbmodel import Actor


class ActorView(BaseView):
    model = Actor
    cache_key = "actors"

    @classmethod
    def post_init_callback(self, obj):
        obj.state = 0
        obj.power = 100

    def _post_post_callback(self, m):
        self.api.actor.init_one(m.id)

    def _post_put_callback(self, m):
        self.api.actor.init_one(m.id)

    @route("<int:id>/switch/on", methods=["POST"])
    def on(self, id):
        """
        Switch actor on
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
        responses:
          200:
            description: Actor switched on
        """
        self.api.actor.on(id)
        return ('', 204)

    @route("<int:id>/switch/off", methods=["POST"])
    def off(self, id):
        """
        Switch actor off
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
        responses:
          200:
            description: Actor switched off
        """
        self.api.actor.off(id)
        return ('', 204)

    @route("<int:id>/power/<int:power>", methods=["POST"])
    def power(self, id, power):
        """
        Set Actor Power 
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
          - in: path
            name: power
            schema:
              type: integer
            required: true
            description: Power value between 0 - 100
        responses:
          200:
            description: Actor power set
        """
        self.api.actor.power(id, power)
        return ('', 204)

    @route("<int:id>/toggle", methods=["POST"])
    def toggle(self, id):
        """
        Toggle Actor 
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
        responses:
          200:
            description: Actor toggled
        """
        if self.api.cache.get("actors").get(id).state == 0:
            self.on(id)
        else:
            self.off(id)
        return ('', 204)

    def toggleTimeJob(self, id, t):
        self.api.cache.get("actors").get(int(id)).timer = int(time.time()) + int(t)
        self.toggle(int(id))
        self.api._socketio.sleep(t)
        self.api.cache.get("actors").get(int(id)).timer = None
        self.toggle(int(id))

    @route("/<id>/toggle/<int:t>", methods=["POST"])
    def toggleTime(self, id, t):
        """
        Toggle Actor for a defined time
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
          - in: path
            name: time
            schema:
              type: integer
            required: true
            description: time in seconds
        responses:
          200:
            description: Actor toggled
        """
        t = self.api._socketio.start_background_task(target=self.toggleTimeJob, id=id, t=t)
        return ('', 204)

    @route('<int:id>/action/<method>', methods=["POST"])
    def action(self, id, method):
        """
        Actor Action 
        ---
        tags:
          - actor
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the actor
          - in: path
            name: method
            schema:
              type: string
            required: true
            description: action method name
        responses:
          200:
            description: Actor Action called
        """
        cbpi.cache.get("actors").get(id).instance.__getattribute__(method)()
        return ('', 204)


@cbpi.addon.core.initializer(order=1000)
def init(cbpi):
    ActorView.register(cbpi._app, route_base='/api/actor')
    ActorView.init_cache()
    #cbpi.init_actors()
