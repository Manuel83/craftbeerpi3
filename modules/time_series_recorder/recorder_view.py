import logging

from flask import jsonify
from flask_api import status
from flask_classy import FlaskView
from flask_classy import route

from modules.time_series_recorder.recorder_service import RecorderService


class RecorderView(FlaskView):
    _logger = logging.getLogger(__name__)
    _service = None

    def __init__(self):
        if RecorderView._service is None:
            RecorderView._service = RecorderService()

    @route('/status', methods=["GET"])
    def check_status(self):
        recorder_status = RecorderView._service.check_status()
        return self.make_json_response(recorder_status)

    @route('/<type_short>/<int:type_id>', methods=["GET"])
    def load_time_series(self, type_short, type_id):
        acceptable_types = ("s", "k", "f")

        if type_short in acceptable_types:
            time_series = RecorderView._service.load_time_series(type_short, type_id)
            return self.make_json_response(time_series)
        else:
            content = "Invalid type. Only {0} are allowed.".format(acceptable_types)
            return content, status.HTTP_400_BAD_REQUEST

    @staticmethod
    def make_json_response(content):
        response = jsonify(content)
        response.headers["content-type"] = "application/json; charset=UTF-8"

        return response
