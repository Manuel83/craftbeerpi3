import json
from flask_classy import FlaskView, route
from modules import cbpi
class NotificationView(FlaskView):

    @route('/', methods=['GET'])
    def getMessages(self):
        """
        Get all messages
        :return: current messages
        """

        return json.dumps(cbpi.cache["messages"])

    @route('/<id>', methods=['DELETE'])
    def dismiss(self, id):
        """
        Delete message from cache by id
        :param id: message id to be deleted
        :return: empty response HTTP 204
        """
        for idx, m in enumerate(cbpi.cache.get("messages", [])):
            if (m.get("id") == id):
                cbpi.cache["messages"].pop(idx)
        return ('', 204)

@cbpi.event("MESSAGE", async=True)
def messageEvent(message, **kwargs):
    """
    React on message event. add the message to the cache and push the message to the clients
    :param message: the message
    :param kwargs: other parameter
    :return: None
    """
    if message["timeout"] is None:
        cbpi.cache["messages"].append(message)
    cbpi.emit("NOTIFY", message)

@cbpi.initalizer(order=2)
def init(cbpi):
    """
    Initializer for the message module
    :param app: the flask app
    :return: None
    """
    if cbpi.get_config_parameter("donation_notification", "YES") == "YES":
        msg = {"id": len(cbpi.cache["messages"]), "type": "info", "headline": "Support CraftBeerPi with your donation", "message": "You will find the PayPay Donation button in the system menu" , "read": False}
        cbpi.cache["messages"].append(msg)

    NotificationView.register(cbpi.app, route_base='/api/notification')
