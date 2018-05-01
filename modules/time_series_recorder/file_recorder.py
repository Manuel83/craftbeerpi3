from modules.time_series_recorder.base_recorder import BaseRecorder


class FileRecorder(BaseRecorder):
    def check_status(self):
        pass

    def load_time_series(self, ts_type, ts_id):
        pass

    def store_datapoint(self, name, value, tags):
        pass
