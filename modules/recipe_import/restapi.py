from flask import json, request
from flask_classy import FlaskView, route
from git import Repo, Git
import sqlite3
from modules.app_config import cbpi
from werkzeug.utils import secure_filename
import pprint
import time
import os
from modules.steps import Step,StepView
import xml.etree.ElementTree


class RESTImport(FlaskView):


    @route('/', methods=['POST'])
    def load(self):

        try:
            data = request.json

            name = data.get("name", "No Name")

            self.api.set_config_parameter("brew_name", name)
            chilstep_type = cbpi.get_config_parameter("step_chil", "ChilStep")
            mashstep_type = cbpi.get_config_parameter("step_mash", "MashStep")
            mash_kettle = cbpi.get_config_parameter("step_mash_kettle", None)

            boilstep_type = cbpi.get_config_parameter("step_boil", "BoilStep")
            boil_kettle = cbpi.get_config_parameter("step_boil_kettle", None)
            boil_temp = 100 if cbpi.get_config_parameter("unit", "C") == "C" else 212

            # READ KBH DATABASE
            Step.delete_all()
            StepView().reset()


            for step in data.get("steps"):
                if step.get("type", None) == "MASH":
                    Step.insert(**{"name": step.get("name","Mash Step"), "type": mashstep_type, "config": {"kettle": mash_kettle, "temp": step.get("temp",0), "timer": step.get("timer",0)}})
                elif step.get("type", None) == "CHIL":
                    Step.insert(**{"name": step.get("name","Chil"), "type": chilstep_type, "config": {"timer": step.get("timer")}})
                elif step.get("type", None) == "BOIL":
                    Step.insert(**{"name": step.get("name", "Boil"), "type": boilstep_type, "config": {"kettle": boil_kettle, "timer": step.get("timer"), "temp": boil_temp}})
                else:
                    pass

            self.api.emit("UPDATE_ALL_STEPS", Step.get_all())
            self.api.notify(headline="Recipe %s loaded successfully" % name, message="")
        except Exception as e:
            self.api.notify(headline="Failed to load Recipe", type="danger", message=str(e))
            m = str(e.message)
            return (str(e), 500)

        return ('', 204)


@cbpi.initalizer()
def init(cbpi):
    RESTImport.api = cbpi
    RESTImport.register(cbpi.app, route_base='/api/recipe/import/v1')
