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

class BeerXMLImport(FlaskView):
    BEER_XML_FILE = "./upload/beer.xml"
    @route('/', methods=['GET'])
    def get(self):
        if not os.path.exists(self.BEER_XML_FILE):
            self.api.notify(headline="File Not Found", message="Please upload a Beer.xml File",
                            type="danger")
            return ('', 404)
        result = []

        e = xml.etree.ElementTree.parse(self.BEER_XML_FILE).getroot()
        result = []
        for idx, val in enumerate(e.findall('RECIPE')):
            result.append({"id": idx+1, "name": val.find("NAME").text})
        return json.dumps(result)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in set(['xml'])

    @route('/upload', methods=['POST'])
    def upload_file(self):
        try:
            if request.method == 'POST':
                file = request.files['file']
                if file and self.allowed_file(file.filename):
                    file.save(os.path.join(self.api.app.config['UPLOAD_FOLDER'], "beer.xml"))
                    self.api.notify(headline="Upload Successful", message="The Beer XML file was uploaded succesfully")
                    return ('', 204)
                return ('', 404)
        except Exception as e:
            self.api.notify(headline="Upload Failed", message="Failed to upload Beer xml", type="danger")
            return ('', 500)

    @route('/<int:id>', methods=['POST'])
    def load(self, id):


        steps = self.getSteps(id)
        name = self.getRecipeName(id)
        self.api.set_config_parameter("brew_name", name)
        boil_time = self.getBoilTime(id)
        mashstep_type = cbpi.get_config_parameter("step_mash", "MashStep")
        mash_kettle = cbpi.get_config_parameter("step_mash_kettle", None)

        boilstep_type = cbpi.get_config_parameter("step_boil", "BoilStep")
        boil_kettle = cbpi.get_config_parameter("step_boil_kettle", None)
        boil_temp = 100 if cbpi.get_config_parameter("unit", "C") == "C" else 212

        # READ KBH DATABASE
        Step.delete_all()
        StepView().reset()

        try:

            for row in steps:
                Step.insert(**{"name": row.get("name"), "type": mashstep_type, "config": {"kettle": mash_kettle, "temp": float(row.get("temp")), "timer": row.get("timer")}})
            Step.insert(**{"name": "ChilStep", "type": "ChilStep", "config": {"timer": 15}})
            ## Add cooking step
            Step.insert(**{"name": "Boil", "type": boilstep_type, "config": {"kettle": boil_kettle, "temp": boil_temp, "timer": boil_time}})
            ## Add Whirlpool step
            Step.insert(**{"name": "Whirlpool", "type": "ChilStep", "config": {"timer": 15}})
            self.api.emit("UPDATE_ALL_STEPS", Step.get_all())
            self.api.notify(headline="Recipe %s loaded successfully" % name, message="")
        except Exception as e:
            self.api.notify(headline="Failed to load Recipe", message=e.message, type="danger")
            return ('', 500)

        return ('', 204)

    def getRecipeName(self, id):
        e = xml.etree.ElementTree.parse(self.BEER_XML_FILE).getroot()
        return e.find('./RECIPE[%s]/NAME' % (str(id))).text

    def getBoilTime(self, id):
        e = xml.etree.ElementTree.parse(self.BEER_XML_FILE).getroot()
        return float(e.find('./RECIPE[%s]/BOIL_TIME' % (str(id))).text)

    def getSteps(self, id):



        e = xml.etree.ElementTree.parse(self.BEER_XML_FILE).getroot()
        steps = []
        for e in e.findall('./RECIPE[%s]/MASH/MASH_STEPS/MASH_STEP' % (str(id))):

            if self.api.get_config_parameter("unit", "C") == "C":
                temp = float(e.find("STEP_TEMP").text)
            else:
                temp = round(9.0 / 5.0 * float(e.find("STEP_TEMP").text) + 32, 2)
            steps.append({"name": e.find("NAME").text, "temp": temp, "timer": float(e.find("STEP_TIME").text)})

        return steps

@cbpi.initalizer()
def init(cbpi):

    BeerXMLImport.api = cbpi
    BeerXMLImport.register(cbpi.app, route_base='/api/beerxml')
