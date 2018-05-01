

from modules.core.core import cbpi
from modules.time_series_recorder.recorder_service import RecorderService
from modules.time_series_recorder.recorder_view import RecorderView


@cbpi.addon.core.initializer(order=1000)
def init(cbpi):
    RecorderView.register(cbpi._app, route_base='/api/recorder')
