
from modules.logs import LogView


class TestLogView(object):

    def test_get_all_logfiles(self):

        LogView._log_directory = "./logs"

        log_view = LogView()
        logfiles = log_view.get_all_logfiles()

        print(logfiles)
        assert (len(logfiles) == 2)
