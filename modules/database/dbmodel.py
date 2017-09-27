from modules.core.db import DBModel, get_db
from flask import json

class Kettle(DBModel):
    __fields__ = ["name","sensor", "heater", "automatic", "logic", "config", "agitator", "target_temp"]
    __table_name__ = "kettle"
    __json_fields__ = ["config"]

class Sensor(DBModel):
    __fields__ = ["name","type", "config", "hide"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]

class Config(DBModel):
    __fields__ = ["type", "value", "description", "options"]
    __table_name__ = "config"
    __json_fields__ = ["options"]
    __priamry_key__ = "name"

class Actor(DBModel):
    __fields__ = ["name","type", "config", "hide"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]

class Step(DBModel):
    __fields__      = ["name","type", "stepstate", "state", "start", "end", "order", "config"]
    __table_name__  = "step"
    __json_fields__ = ["config", "stepstate"]
    __order_by__    = "order"
    __as_array__    = True

    @classmethod
    def get_max_order(cls):
        cur = get_db().cursor()
        cur.execute("SELECT max(step.'order') as 'order' FROM %s" % cls.__table_name__)
        r = cur.fetchone()
        return r.get("order")

    @classmethod
    def get_by_state(cls, state, order=True):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM %s WHERE state = ? ORDER BY %s.'order'" % (cls.__table_name__,cls.__table_name__,), state)
        r = cur.fetchone()
        if r is not None:
            return cls(r)
        else:
            return None

    @classmethod
    def delete_all(cls):
        cur = get_db().cursor()
        cur.execute("DELETE FROM %s" % cls.__table_name__)
        get_db().commit()

    @classmethod
    def reset_all_steps(cls):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = 'I', stepstate = NULL , start = NULL, end = NULL " % cls.__table_name__)
        get_db().commit()

    @classmethod
    def update_state(cls, id, state):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = ? WHERE id =?" % cls.__table_name__, (state, id))
        get_db().commit()

    @classmethod
    def update_step_state(cls, id, state):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET stepstate = ? WHERE id =?" % cls.__table_name__, (json.dumps(state),id))
        get_db().commit()

    @classmethod
    def sort(cls, new_order):
        cur = get_db().cursor()

        for e in new_order:

            cur.execute("UPDATE %s SET '%s' = ? WHERE id = ?" % (cls.__table_name__, "order"), (e[1], e[0]))
        get_db().commit()


class Fermenter(DBModel):
    __fields__ = ["name", "brewname", "sensor", "sensor2", "sensor3", "heater", "cooler",  "logic",  "config",  "target_temp"]
    __table_name__ = "fermenter"
    __json_fields__ = ["config"]

class FermenterStep(DBModel):
    __fields__ = ["name", "days", "hours", "minutes", "temp", "direction", "order", "state", "start", "end", "timer_start", "fermenter_id"]
    __table_name__ = "fermenter_step"

    @classmethod
    def get_by_fermenter_id(cls, id):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM %s WHERE fermenter_id = ?" % cls.__table_name__,(id,))
        result = []
        for r in cur.fetchall():
            result.append(cls(r))
        return result

    @classmethod
    def get_max_order(cls,id):
        cur = get_db().cursor()
        cur.execute("SELECT max(fermenter_step.'order') as 'order' FROM %s WHERE fermenter_id = ?" % cls.__table_name__, (id,))
        r = cur.fetchone()
        return r.get("order")

    @classmethod
    def update_state(cls, id, state):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = ? WHERE id =?" % cls.__table_name__, (state, id))
        get_db().commit()

    @classmethod
    def update_timer(cls, id, timer):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET timer_start = ? WHERE id =?" % cls.__table_name__, (timer, id))
        get_db().commit()

    @classmethod
    def get_by_state(cls, state):
        cur = get_db().cursor()
        cur.execute("SELECT * FROM %s WHERE state = ?" % cls.__table_name__, state)
        r = cur.fetchone()
        if r is not None:
            return cls(r)
        else:
            return None

    @classmethod
    def reset_all_steps(cls,id):
        cur = get_db().cursor()
        cur.execute("UPDATE %s SET state = 'I', start = NULL, end = NULL, timer_start = NULL WHERE fermenter_id = ?" % cls.__table_name__, (id,))
        get_db().commit()