import unittest

from modules.logs import LogView


class TestLogView(unittest.TestCase):

    def test_get_all_logfiles(self):
        LogView._log_directory = "../../logs"

        log_view = LogView()
        logfiles = log_view.get_all_logfiles()

        print(logfiles)
        self.assertTrue(len(logfiles) > 0)


if __name__ == '__main__':
    unittest.main()
