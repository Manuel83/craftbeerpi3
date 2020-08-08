# -*- coding: utf-8 -*-
"""
enpoints for logging
"""
import csv
import datetime
import os
import re

from flask import send_from_directory, json
from flask_classy import FlaskView, route
from modules import cbpi


class LogView(FlaskView):
    """
    View for logging
    """

    @route('/', methods=['GET'])
    def get_all_logfiles(self):  # pylint: disable=no-self-use
        """
        get all log files

        :return: json for all logs
        """
        result = []
        for filename in os.listdir("./logs"):
            if filename.endswith(".log"):
                result.append(filename)
        return json.dumps(result)

    @route('/actions')
    def actions(self):  # pylint: disable=no-self-use
        """
        get actions log

        :return: json for actions log
        """
        filename = "./logs/action.log"
        if not os.path.isfile(filename):
            return ('File not found', 404)
        array = []
        with open(filename, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                try:
                    array.append([
                        int((datetime.datetime.strptime(
                            row[0], "%Y-%m-%d %H:%M:%S") -
                             datetime.datetime(1970, 1, 1)).total_seconds()) *
                        1000, row[1]
                    ])
                except IndexError:
                    pass
        return json.dumps(array)

    @route('/<file>', methods=["DELETE"])
    def clearlog(self, file):
        """
        log delete
        :param file: log file name
        :return: HTTP 204
        """
        if not self.check_filename(file):
            return ('File Not Found', 404)

        filename = "./logs/%s" % file
        if os.path.isfile(filename):
            os.remove(filename)
            cbpi.notify("log deleted succesfully", "")
        else:
            cbpi.notify("Failed to delete log", "", type="danger")
        return ('', 204)

    def read_log_as_json(self, log_type, log_id):  # pylint: disable=no-self-use
        """
        :param log_type: log type
        :param log_id: log id

        :return: log as array
        """
        filename = "./logs/%s_%s.log" % (log_type, log_id)
        if not os.path.isfile(filename):
            return ('File not found', 404)

        array = []
        with open(filename, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                try:
                    array.append([
                        int((datetime.datetime.strptime(
                            row[0], "%Y-%m-%d %H:%M:%S") -
                             datetime.datetime(1970, 1, 1)).total_seconds()) *
                        1000,
                        float(row[1])
                    ])
                except IndexError:
                    pass
        return array

    def convert_chart_data_to_json(self, chart_data):
        """
        :param chart_data: data for a chart

        :return: json for chart data
        """
        return {
            "name":
            chart_data["name"],
            "data":
            self.read_log_as_json(chart_data["data_type"],
                                  chart_data["data_id"])
        }

    @route('/<log_type>/<int:log_id>', methods=["POST"])
    def get_logs_as_json(self, log_type, log_id):
        """
        :param log_type: log type
        :param log_id: log id

        :return: log as array
        """
        result = []
        if log_type == "s":
            name = cbpi.cache.get("sensors").get(log_id).name
            result.append({
                "name": name,
                "data": self.read_log_as_json("sensor", log_id)
            })

        if log_type == "k":
            kettle = cbpi.cache.get("kettle").get(log_id)
            result = list(
                map(
                    self.convert_chart_data_to_json,
                    cbpi.get_controller(
                        kettle.logic).get("class").chart(kettle)))

        if log_type == "f":
            fermenter = cbpi.cache.get("fermenter").get(log_id)
            result = list(
                map(
                    self.convert_chart_data_to_json,
                    cbpi.get_fermentation_controller(
                        fermenter.logic).get("class").chart(fermenter)))

        return json.dumps(result)

    @route('/download/<file>')
    @cbpi.nocache
    def download(self, file):
        """
        :param file: log file name

        :return: log data
        """
        if not self.check_filename(file):
            return ('File Not Found', 404)
        return send_from_directory('../logs',
                                   file,
                                   as_attachment=True,
                                   attachment_filename=file)

    def check_filename(self, name):  # pylint: disable=no-self-use
        """
        :param name: log file name
        :return: bool
        """
        pattern = re.compile('^([A-Za-z0-9-_])+.log$')

        return bool(pattern.match(name))


@cbpi.initalizer()
def init(app):  # pylint: disable=unused-argument
    """
    Initializer for the message module
    :param app: the flask app
    :return: None
    """
    LogView.register(cbpi.app, route_base='/api/logs')
