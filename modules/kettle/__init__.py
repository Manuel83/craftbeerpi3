from flask import request
from flask_classy import FlaskView, route
from modules import cbpi
from modules.core.baseview import RestApi
from modules.core.db import DBModel
from modules.database.dbmodel import Kettle

class KettleView(RestApi):
    model = Kettle
    cache_key = "kettle"

    @route('/', methods=["GET"])
    def getAll(self):
        """
        Get all Kettles
        ---
        tags:
          - kettle
        responses:
          200:
            description: List auf all Kettles
        """
        return super(KettleView, self).getAll()

    @route('/', methods=["POST"])
    def post(self):
        """
        Create a new kettle
        ---
        tags:
          - kettle
        parameters:
          - in: body
            name: body
            schema:
              id: Kettle
              required:
                - name
              properties:
                name:
                  type: string
                  description: name for user
                sensor:
                  type: string
                  description: name for user
                heater:
                  type: string
                  description: name for user
                automatic:
                  type: string
                  description: name for user
                logic:
                  type: string
                  description: name for user
                config:
                  type: string
                  description: name for user
                agitator:
                  type: string
                  description: name for user
                target_temp:
                  type: string
                  description: name for user
        responses:
          200:
            description: User created
        """
        return super(KettleView, self).post()


    @route('/<int:id>', methods=["PUT"])
    def put(self, id):
        """
        Update a kettle
        ---
        tags:
          - kettle
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the Kettle
          - in: body
            name: body
            schema:
              id: Kettle
              required:
                - name
              properties:
                name:
                  type: string
                  description: name for user
                sensor:
                  type: string
                  description: name for user
                heater:
                  type: string
                  description: name for user
                automatic:
                  type: string
                  description: name for user
                logic:
                  type: string
                  description: name for user
                config:
                  type: string
                  description: name for user
                agitator:
                  type: string
                  description: name for user
                target_temp:
                  type: string
                  description: name for user
        responses:
          200:
            description: User created
        """
        return super(KettleView, self).put(id)

    @route('/<int:id>', methods=["DELETE"])
    def delete(self, id):
        """
        Delete a kettle
        ---
        tags:
          - kettle
        parameters:
          - in: path
            name: id
            schema:
              type: integer
            required: true
            description: Numeric ID of the Kettle

        responses:
          200:
            description: User created
        """
        return super(KettleView, self).delete(id)

    @classmethod
    def _pre_post_callback(self, data):
        data["target_temp"] = 0

    @classmethod
    def post_init_callback(cls, obj):
        obj.state = False


    def _post_post_callback(self, m):
        m.state = False

    def _pre_put_callback(self, m):
        try:
            m.instance.stop()
        except:
            pass

    def _post_put_callback(self, m):
        m.state = False

    @route('/<int:id>/targettemp/<temp>', methods=['POST'])
    def postTargetTemp(self, id, temp):

        """
        Set Target Temp
        ---
        tags:
          - kettle
        parameters:
          - required: true
            type: string
            description: ID of pet to return
            in: path
            name: id
          - required: true
            type: string
            description: Temperature you like to set
            in: path
            name: temp
        responses:
          201:
            description: User created
        """

        id = int(id)
        temp = float(temp)
        cbpi.brewing.set_target_temp(id, temp)
        return ('', 204)

    @route('/<int:id>/automatic', methods=['POST'])
    def toggle(self, id):

        """
                Set Target Temp
                ---
                tags:
                  - kettle
                parameters:
                  - required: true
                    type: string
                    description: ID of pet to return
                    in: path
                    name: id
                  - required: true
                    type: string
                    description: Temperature you like to set
                    in: path
                    name: temp
                responses:
                  201:
                    description: User created
                """

        self.api.brewing.toggle_automatic(id)
        return ('', 204)


@cbpi.addon.core.listen("SET_TARGET_TEMP")
def set_target_temp(id, temp):
    '''
    Change Taget Temp Event
    :param id: kettle id
    :param temp: target temp to set
    :return: None
    '''
    KettleView().postTargetTemp(id,temp)

@cbpi.addon.core.backgroundtask(key="read_target_temps", interval=5)
def read_target_temps(api):
    """
    background process that reads all passive sensors in interval of 1 second
    :return: None
    """
    result = {}
    for key, value in cbpi.cache.get("kettle").iteritems():
        cbpi.sensor.write_log(key, value.target_temp, prefix="kettle")

@cbpi.addon.core.initializer()
def init(cbpi):
    KettleView.api = cbpi
    KettleView.register(cbpi.web, route_base='/api/kettle')
    KettleView.init_cache()
