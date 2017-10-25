from modules.logs import LogView
from tests.testlib import utils


class TestLogView(object):

    def test_get_all_logfiles(self):
        LogView._log_directory = utils.get_base_path() + "/logs"

        logfiles = LogView().get_all_logfiles()

        # if no log file is found then two square brackets "[]" are returned and string length is 2
        assert (len(logfiles) > 2)
