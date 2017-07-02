from flask import json, request
from flask_classy import FlaskView, route
from git import Repo, Git
import sqlite3
from modules.app_config import cbpi
from werkzeug.utils import secure_filename
import pprint
import time
import os
from modules.steps import Step, StepView


class KBH(FlaskView):

    @route('/', methods=['GET'])
    def get(self):
        conn = None
        try:
            if not os.path.exists(self.api.app.config['UPLOAD_FOLDER'] + '/kbh.db'):
                self.api.notify(headline="File Not Found", message="Please upload a Kleiner Brauhelfer Database", type="danger")
                return ('', 404)

            conn = sqlite3.connect(self.api.app.config['UPLOAD_FOLDER'] + '/kbh.db')
            c = conn.cursor()
            c.execute('SELECT ID, Sudname, BierWurdeGebraut FROM Sud')
            data = c.fetchall()
            result = []
            for row in data:
                result.append({"id": row[0], "name": row[1], "brewed": row[2]})
            return json.dumps(result)
        except Exception as e:
            print e
            self.api.notify(headline="Failed to load KHB database", message="ERROR", type="danger")
            return ('', 500)
        finally:
            if conn:
                conn.close()

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in set(['sqlite'])

    @route('/upload', methods=['POST'])
    def upload_file(self):
        try:
            if request.method == 'POST':
                file = request.files['file']
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(self.api.app.config['UPLOAD_FOLDER'], "kbh.db"))
                    self.api.notify(headline="Upload Successful", message="The Kleiner Brauhelfer Database was uploaded succesfully")
                    return ('', 204)
                return ('', 404)
        except Exception as e:
            self.api.notify(headline="Upload Failed", message="Failed to upload Kleiner Brauhelfer", type="danger")

            return ('', 500)

    @route('/<int:id>', methods=['POST'])
    def load(self, id):
        mashstep_type = cbpi.get_config_parameter("step_mash", "MashStep")
        mashinstep_type = cbpi.get_config_parameter("step_mashin", "MashInStep")
        chilstep_type = cbpi.get_config_parameter("step_chil", "ChilStep")
        boilstep_type = cbpi.get_config_parameter("step_boil", "BoilStep")
        mash_kettle = cbpi.get_config_parameter("step_mash_kettle", None)
        boil_kettle = cbpi.get_config_parameter("step_boil_kettle", None)
        boil_temp = 100 if cbpi.get_config_parameter("unit", "C") == "C" else 212

        # READ KBH DATABASE
        Step.delete_all()
        StepView().reset()
        conn = None
        try:
            conn = sqlite3.connect(self.api.app.config['UPLOAD_FOLDER'] + '/kbh.db')
            c = conn.cursor()
            c.execute('SELECT EinmaischenTemp, Sudname FROM Sud WHERE ID = ?', (id,))
            row = c.fetchone()
            name = row[1]

            self.api.set_config_parameter("brew_name", name)
            Step.insert(**{"name": "MashIn", "type": mashinstep_type, "config": {"kettle": mash_kettle, "temp": row[0]}})
            ### add rest step
            for row in c.execute('SELECT * FROM Rasten WHERE SudID = ?', (id,)):
                Step.insert(**{"name": row[5], "type": mashstep_type, "config": {"kettle": mash_kettle, "temp": row[3], "timer": row[4]}})
            Step.insert(**{"name": "Chil", "type": chilstep_type, "config": {"timer": 15}})
            ## Add cooking step
            c.execute('SELECT max(Zeit) FROM Hopfengaben WHERE SudID = ?', (id,))
            row = c.fetchone()
            Step.insert(**{"name": "Boil", "type": boilstep_type, "config": {"kettle": boil_kettle, "temp": boil_temp, "timer": row[0]}})
            ## Add Whirlpool step
            Step.insert(**{"name": "Whirlpool", "type": chilstep_type, "config": {"timer": 15}})

            #setBrewName(name)
            self.api.emit("UPDATE_ALL_STEPS", Step.get_all())
            self.api.notify(headline="Recipe %s loaded successfully" % name, message="")
        except Exception as e:
            self.api.notify(headline="Failed to load Recipe", message=e.message, type="danger")
            return ('', 500)
        finally:
            if conn:
                conn.close()
        return ('', 204)



@cbpi.initalizer()
def init(cbpi):

    KBH.api = cbpi
    KBH.register(cbpi.app, route_base='/api/kbh')
