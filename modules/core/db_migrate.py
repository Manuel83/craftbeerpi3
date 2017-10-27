import sqlite3
import os
from modules.core.core import  cbpi
from modules.core.db import get_db

def execute_file(curernt_version, data):
    if curernt_version >= data["version"]:
        cbpi._app.logger.info("SKIP DB FILE: %s" % data["file"])
        return
    try:
        with sqlite3.connect("craftbeerpi.db") as conn:
            with open('./update/%s' % data["file"], 'r') as f:
                d = f.read()
                sqlCommands = d.split(";")
                cur = conn.cursor()
                for s in sqlCommands:
                    cur.execute(s)
                cur.execute("INSERT INTO schema_info (version,filename) values (?,?)", (data["version"], data["file"]))
                conn.commit()

    except sqlite3.OperationalError as err:
        cbpi._app.logger.error(err)

@cbpi.addon.core.initializer(order=-9999)
def init(cbpi):

    with cbpi._app.app_context():
        conn = get_db()
        cur = conn.cursor()
        current_version = None
        try:
            cur.execute("SELECT max(version) as m FROM schema_info")
            m = cur.fetchone()
            current_version =  m["m"]
        except:
            pass
        result = []
        for filename in os.listdir("./update"):

            if filename.endswith(".sql"):
                d = {"version": int(filename[:filename.index('_')]), "file": filename}
                result.append(d)
                execute_file(current_version, d)