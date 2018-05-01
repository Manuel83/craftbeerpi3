import logging

from modules.core.core import cbpi
from modules.time_series_recorder.file_recorder import FileRecorder
from modules.time_series_recorder.kairosdb_recorder import KairosdbRecorder


class RecorderService:

    _logger = logging.getLogger(__name__)

    def __init__(self):
        print "init"
        self.config_event_listener()
        self.recorder = self.determine_recorder_impl()

    def check_status(self):
        return self.recorder.check_status()

    def load_time_series(self, type_short, type_id):

        if type_short == "s":
            type_full = "sensors"
            sensor = cbpi.cache.get(type_full).get(type_id)
            chart = cbpi.sensor.get_sensors(sensor.type).get("class").chart(sensor)
        elif type_short == "k":
            type_full = "kettle"
            kettle = cbpi.cache.get(type_full).get(type_id)
            chart = cbpi.brewing.get_controller(kettle.logic).get("class").chart(kettle)
        elif type_short == "f":
            type_full = "fermenter"
            fermenter = cbpi.cache.get(type_full).get(type_id)
            chart = cbpi.fermentation.get_controller(fermenter.logic).get("class").chart(fermenter)
        else:
            chart = []

        return map(self.convert_chart_data_to_json, chart)

    def convert_chart_data_to_json(self, chart_data):
        return {"name": chart_data["name"],
                "data": self.recorder.load_time_series(chart_data["data_type"], chart_data["data_id"])}

    def hallo2(self, **kwargs):
        print kwargs
        cbpi.beep()
        # if name == "kairos_db" or name == "kairos_db_port":
        #   print name
        #    print cbpi.cache["config"][name].__dict__["value"]

    def config_event_listener(self):
        if "CONFIG_UPDATE" not in cbpi.eventbus:
            cbpi.eventbus["CONFIG_UPDATE"] = []
        cbpi.eventbus["CONFIG_UPDATE"].append({"function": self.hallo2, "async": False})

    @staticmethod
    def determine_recorder_impl():
        use_kairosdb = cbpi.cache["config"]["kairos_db"].__dict__["value"]
        kairosdb_port = cbpi.cache["config"]["kairos_db_port"].__dict__["value"]

        if use_kairosdb:
            recorder = KairosdbRecorder(kairosdb_port)
        else:
            recorder = FileRecorder()

        return recorder
