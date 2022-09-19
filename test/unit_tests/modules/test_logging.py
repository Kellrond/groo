import glob, os, sys
import unittest
from unittest.mock import patch

import modules.logging as logging
from test import config

class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.log = logging.Log.from_test_conf(config.logging)

    def tearDown(self):
        pass

    def test_create_log_files(self):
        # Glob and delete all files in the test_data/logs folder
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        if len(glob_logs) > 0:
            for log_filepath in glob_logs:
                os.remove(log_filepath)

        # Check that all files where removed
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        self.assertEqual(len(glob_logs), 0, "File was unsuccessfully removed from test_data/logs")

        # Create empty log files and check they all got created
        self.log.init_logs()
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        self.assertEqual(len(glob_logs),len(self.log.log_files), "Number of log files does not match log file list of class")

    def test_delete_logs(self):
        # Make sure there are log files there to start with
        self.log.init_logs()

        # Check that log files where added
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        self.assertGreaterEqual(len(glob_logs), 1, "Files were not added to test_data/logs")        

        # Delete logs and assert they are gone
        self.log.delete_dot_logs()
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        self.assertEqual(len(glob_logs),0,"Log files where not removed")

    def test_logging(self):
        self.log.debug('Test', __name__)


    # def test_apply_raise(self):
    #     print('test_apply_raise')
    #     self.emp_1.apply_raise()
    #     self.emp_2.apply_raise()

    #     self.assertEqual(self.emp_1.pay, 52500)
    #     self.assertEqual(self.emp_2.pay, 63000)

    # def test_monthly_schedule(self):
    #     with patch('employee.requests.get') as mocked_get:
    #         mocked_get.return_value.ok = True
    #         mocked_get.return_value.text = 'Success'

    #         schedule = self.emp_1.monthly_schedule('May')
    #         mocked_get.assert_called_with('http://company.com/Schafer/May')
    #         self.assertEqual(schedule, 'Success')

    #         mocked_get.return_value.ok = False

    #         schedule = self.emp_2.monthly_schedule('June')
    #         mocked_get.assert_called_with('http://company.com/Smith/June')
    #         self.assertEqual(schedule, 'Bad Response!')

if __name__ == '__main__':
    unittest.main()
