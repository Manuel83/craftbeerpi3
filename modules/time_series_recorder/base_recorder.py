import abc


class BaseRecorder:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load_time_series(self, ts_type, ts_id):
        raise NotImplementedError("Method not implemented")

    @abc.abstractmethod
    def check_status(self):
        raise NotImplementedError("Method not implemented")

    @abc.abstractmethod
    def store_datapoint(self, name, value, tags):
        raise NotImplementedError("Method not implemented")
