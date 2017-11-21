import os
import re
import time

import datetime
from flask import json, request, send_from_directory
from flask_classy import route, FlaskView

from modules.core.db import DBModel
from modules.core.baseview import BaseView
from modules.core.core import cbpi
from modules.database.dbmodel import Step
from yaml import Loader, Dumper
from yaml import load, dump

from modules.step import StepView


class RecipeBook(FlaskView):


    @route('/load', methods=["POST"])
    def load(self):

        data = request.json
        recipe_name = data.get("name")
        if re.match("^[A-Za-z0-9_-]*$", recipe_name) is None:
            return ('Recipie Name contains not allowed characters', 500)

        with open("./recipes/%s.json" % recipe_name) as json_data:
            d = json.load(json_data)
            Step.delete_all()
            StepView().reset()
            for s in d["steps"]:
                Step.insert(**{"name": s.get("name"), "type": s.get("type"), "config": s.get("config")})

        self.api.ws_emit("UPDATE_ALL_STEPS", Step.get_all())
        self.api.notify(headline="Recipe %s loaded successfully" % recipe_name, message="")

        return ('', 204)

    @route('/download/<name>', methods=["GET"])
    def download(self, name):

        """
                Download a log file by name
                ---
                tags:
                  - logs
                parameters:
                  - in: path
                    name: file
                    schema:
                      type: string
                    required: true
                    description: filename
                responses:
                  200:
                    description: Log file downloaded
                """
        file = "%s.json" % name
        print file
        if not self.check_filename(file):
            return ('File Not Found111', 404)
        return send_from_directory('../../recipes', file, as_attachment=True, attachment_filename=file)

    def check_filename(self, name):
        import re
        print "CHECK"
        pattern = re.compile('^([A-Za-z0-9-_])+.json$')
        return True if pattern.match(name) else False

    @route('/<name>', methods=["DELETE"])
    def remove(self, name):


        recipe_name = name
        if re.match("^[A-Za-z0-9_-]*$", recipe_name) is None:
            return ('Recipie Name contains not allowed characters', 500)

        filename = "./recipes/%s.json" % recipe_name
        if os.path.isfile(filename) == True:
            os.remove(filename)
            self.api.notify(headline="Recipe %s deleted successfully" % recipe_name, message="")
            return ('', 204)
        else:
            self.api.notify(headline="Faild to delete Recipe %s deleted" % recipe_name, message="")
            return ('', 404)

        return ('', 204)


    @route('/', methods=["GET"])
    def get_all(self):
        result = []
        for filename in os.listdir("./recipes"):
            if filename.endswith(".json"):

                result.append({"id":filename.split(".")[0], "name": filename.split(".")[0], "change_date": self._modification_date('./recipes/%s' % filename)})
        return json.dumps(result)


    def _modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')

    @route('/save', methods=["POST"])
    def save(self):
        """
        Save Recepie
        ---
        tags:
          - steps
        responses:
          204:
            description: Recipe saved
        """



        recipe_name = self.api.get_config_parameter("brew_name")

        if recipe_name is None or len(recipe_name) <= 0:
            self.api.notify(headline="Please set brew name", message="Recipe not saved!", type="danger")
            return ('Recipie Name contains not allowed characters', 500)

        if re.match("^[\sA-Za-z0-9_-]*$", recipe_name) is None:
            self.api.notify(headline="Only alphanummeric charaters are allowd for recipe name", message="", type="danger")
            return ('Recipie Name contains not allowed characters', 500)

        recipe_data = {"name": recipe_name, "steps": Step.get_all()}

        file_name = recipe_name.replace(" ", "_")
        with open('./recipes/%s.json' % file_name, 'w') as outfile:
            json.dump(recipe_data, outfile, indent=4)

        self.api.notify(headline="Recipe %s saved successfully" % recipe_name, message="")


        return ('', 204)


@cbpi.addon.core.initializer(order=2000)
def init(cbpi):
    RecipeBook.api = cbpi
    RecipeBook.register(cbpi._app, route_base='/api/recipebook')