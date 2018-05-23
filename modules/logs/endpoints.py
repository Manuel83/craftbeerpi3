import datetime
import os
import requests
import logging
from flask import request, send_from_directory, json
from flask_classy import FlaskView, route
from modules import cbpi


class LogView(FlaskView):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @route('/', methods=['GET'])
    def get_all_logfiles(self):
        result = []
        for filename in os.listdir("./logs"):
            if filename.endswith(".log"):
                result.append(filename)
        return json.dumps(result)

    @route('/actions')
    def actions(self):
        array = self.read_log_as_json("action")
        json_dumps = json.dumps(array)

        return json_dumps

    @route('/<file>', methods=["DELETE"])
    def clearlog(self, file):
        """
        Overload delete method to shutdown sensor before delete
        :param id: sensor id
        :return: HTTP 204
        """
        if not self.check_filename(file):
            return ('File Not Found', 404)

        filename = "./logs/%s" % file
        if os.path.isfile(filename) == True:
            os.remove(filename)
            cbpi.notify("log deleted succesfully", "")
        else:
            cbpi.notify("Failed to delete log", "", type="danger")
        return ('', 204)

    def query_tsdb(self, sensor_name):
        kairosdb_server = "http://127.0.0.1:" + cbpi.cache["config"]["kairos_db_port"].__dict__["value"]

        data = dict(metrics=[
            {
                "tags": {},
                "name": "cbpi.%s" % sensor_name,
                "aggregators": [
                    {
                        "name": "avg",
                        "align_sampling": True,
                        "sampling": {
                            "value": cbpi.cache["config"]["kairos_db_sampling_value"].__dict__["value"],
                            "unit": "seconds"
                        },
                        "align_start_time": True
                    }
                ]
            }
        ],
            cache_time=0,
            start_relative={
                "value": cbpi.cache["config"]["kairos_db_start_relative"].__dict__["value"],
                "unit": "days"
            })

        if cbpi.cache["active_brew"] != "none":
            data["metrics"][0]["tags"] = {"brew": [cbpi.cache["active_brew"]]}

        self.logger.debug("query: %s", json.dumps(data))

        response = requests.post(kairosdb_server + "/api/v1/datapoints/query", json.dumps(data))
        if response.ok:
            self.logger.debug("Fetching time series for [%s] took [%s]", sensor_name, response.elapsed)
            self.logger.debug("Time series for [%s] is [%s]", sensor_name, response.json())
            return response.json()["queries"][0]["results"][0]["values"]
        else:
            self.logger.warning("Failed to fetch time series for [%s]. Response [%s]", sensor_name, response)

    def query_log(self, filename, value_type):
        array = []

        if not os.path.isfile(filename):
            self.logger.warn("File does not exist [%s]", filename)
            return array

        import csv

        if value_type == "float":
            converter = float
        else:
            converter = str

        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    point_of_time = int((datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
                                         - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000
                    value = converter(row[1])
                    array.append([point_of_time, value])
                except:
                    self.logger.exception("error in reading logfile [%s]", filename)
                    pass
        return array

    def read_log_as_json(self, sensor_name):
        use_kairosdb = (cbpi.cache["config"]["kairos_db"].__dict__["value"] == "YES")

        if use_kairosdb:
            return self.query_tsdb(sensor_name)
        else:
            filename = "./logs/%s.log" % sensor_name
            return self.query_log(filename, "float")


    def convert_chart_data_to_json(self, chart_data):
        return {"name": chart_data["name"],
                "data": self.read_log_as_json(chart_data["data_type"] + "_" + str(chart_data["data_id"]))}

    @route('/<t>/<int:id>', methods=["POST"])
    def get_logs_as_json(self, t, id):
        data = request.json
        result = []
        if t == "s":
            name = cbpi.cache.get("sensors").get(id).name
            sensor_name = "%s_%s" % ("sensor", str(id))
            result.append({"name": name, "data": self.read_log_as_json(sensor_name)})

        if t == "k":
            kettle = cbpi.cache.get("kettle").get(id)
            result = map(self.convert_chart_data_to_json, cbpi.get_controller(kettle.logic).get("class").chart(kettle))

        if t == "f":
            fermenter = cbpi.cache.get("fermenter").get(id)
            result = map(self.convert_chart_data_to_json,
                         cbpi.get_fermentation_controller(fermenter.logic).get("class").chart(fermenter))

        return json.dumps(result)

    @route('/download/<file>')
    @cbpi.nocache
    def download(self, file):
        if not self.check_filename(file):
            return ('File Not Found', 404)
        return send_from_directory('../logs', file, as_attachment=True, attachment_filename=file)

    def check_filename(self, name):
        import re
        pattern = re.compile('^([A-Za-z0-9-_])+.log$')

        return True if pattern.match(name) else False


@cbpi.initalizer()
def init(app):
    """
    Initializer for the message module
    :param app: the flask app
    :return: None
    """
    LogView.register(cbpi.app, route_base='/api/logs')
