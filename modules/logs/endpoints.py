import datetime
import os
from flask import Blueprint, request, send_from_directory, json
from flask_classy import FlaskView, route
from modules import cbpi


class LogView(FlaskView):

    @route('/', methods=['GET'])
    def get_all_logfiles(self):
        result = []
        for filename in os.listdir("./logs"):
            if filename.endswith(".log"):
                result.append(filename)
        return json.dumps(result)

    @route('/actions')
    def actions(self):
        filename = "./logs/action.log"
        if os.path.isfile(filename) == False:
            return
        import csv
        array = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    array.append([int((datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000, row[1]])
                except:
                    pass
        return json.dumps(array)

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

    def read_log_as_json(self, type, id):
        filename = "./logs/%s_%s.log" % (type, id)
        if os.path.isfile(filename) == False:
            return

        import csv
        array = []
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    array.append([int((datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000, float(row[1])])
                except:
                    pass
        return array

    def convert_chart_data_to_json(self, chart_data):
        return {"name": chart_data["name"], "data": self.read_log_as_json(chart_data["data_type"], chart_data["data_id"])}

    @route('/<t>/<int:id>', methods=["POST"])
    def get_logs_as_json(self, t, id):
        data = request.json
        result = []
        if t == "s":
            name = cbpi.cache.get("sensors").get(id).name
            result.append({"name": name, "data": self.read_log_as_json("sensor", id)})

        if t == "k":
            kettle = cbpi.cache.get("kettle").get(id)
            result = map(self.convert_chart_data_to_json, cbpi.get_controller(kettle.logic).get("class").chart(kettle))

        if t == "f":
            fermenter = cbpi.cache.get("fermenter").get(id)
            result = map(self.convert_chart_data_to_json, cbpi.get_fermentation_controller(fermenter.logic).get("class").chart(fermenter))

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
