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
        for idx, r in enumerate(self.getDict().get("RECIPES").get("RECIPE")):
            result.append({"id": idx, "name": r.get("NAME")})
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

        recipe = self.getDict().get("RECIPES").get("RECIPE")[id]
        steps = recipe.get("MASH",{}).get("MASH_STEPS",{}).get("MASH_STEP",[])
        name = recipe.get("NAME")

        self.api.set_config_parameter("brew_name", name)
        boil_time = recipe.get("BOIL_TIME", 90)
        mashstep_type = cbpi.get_config_parameter("step_mash", "MashStep")
        mash_kettle = cbpi.get_config_parameter("step_mash_kettle", None)

        boilstep_type = cbpi.get_config_parameter("step_boil", "BoilStep")
        boil_kettle = cbpi.get_config_parameter("step_boil_kettle", None)
        boil_temp = 100 if cbpi.get_config_parameter("unit", "C") == "C" else 212

        # READ KBH DATABASE
        Step.delete_all()
        StepView().reset()

        conn = None
        try:
            conn = sqlite3.connect(self.api.app.config['UPLOAD_FOLDER'] + '/kbh.db')
            c = conn.cursor()
            for row in steps:
                Step.insert(**{"name": row.get("NAME"), "type": mashstep_type, "config": {"kettle": mash_kettle, "temp": float(row.get("STEP_TEMP")), "timer": row.get("STEP_TIME")}})
            Step.insert(**{"name": "ChilStep", "type": "ChilStep", "config": {"timer": 15}})
            ## Add cooking step
            Step.insert(**{"name": "Boil", "type": boilstep_type, "config": {"kettle": boil_kettle, "temp": boil_temp, "timer": boil_time}})
            ## Add Whirlpool step
            Step.insert(**{"name": "Whirlpool", "type": "ChilStep", "config": {"timer": 15}})
            # setBrewName(name)
            self.api.emit("UPDATE_ALL_STEPS", Step.get_all())
            self.api.notify(headline="Recipe %s loaded successfully" % name, message="")
        except Exception as e:
            self.api.notify(headline="Failed to load Recipe", message=e.message, type="danger")
            return ('', 500)
        finally:
            if conn:
                conn.close()
        return ('', 204)


    def getDict(self):
        '''
        Beer XML file to dict
        :return: beer.xml file as dict
        '''
        try:
            import xmltodict
            with open(self.BEER_XML_FILE) as fd:
                doc = xmltodict.parse(fd.read())
                return doc
        except:
            self.api.notify(headline="Failed to load Beer.xml", message="Please check if you uploaded an beer.xml", type="danger")



@cbpi.initalizer()
def init(cbpi):

    BeerXMLImport.api = cbpi
    BeerXMLImport.register(cbpi.app, route_base='/api/beerxml')
