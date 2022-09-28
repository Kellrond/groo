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
        # Glob and delete all files in the test_data/logs folder
        glob_logs = glob.glob(f'{config.modules.Logging.log_dir}/*.*')
        if len(glob_logs) > 0:
            for log_filepath in glob_logs:
                os.remove(log_filepath)

    def setUp(self):
        self.log = logging.Log.from_test_conf(config.modules.Logging, __name__)

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
        self.assertEqual(len(glob_logs),1, "Number of log files does not match log file list of class")

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
        self.log.init_logs()
        self.log.test_mode = False
        logging_levels = [0, 1, 2, 3, 4]
        log_lines = 0
        prev_log_lines = 0
        for lvl in logging_levels:    
            # Set the logging level
            self.log.config.log_database_level = lvl
            self.log.config.log_flatfile_level = lvl
            self.log.config.log_terminal_level = -1 # We dont want to print to terminal during tests
            # Log at every level
            self.log.fatal(f'Logging level:{lvl} Fatal:0')
            self.log.error(f'Logging level:{lvl} Error:1')
            self.log.warn(f'Logging level:{lvl} Warn:2')
            self.log.info(f'Logging level:{lvl} Info:3')
            self.log.debug(f'Logging level:{lvl} Debug:4')

            # Check the log length
            with open(f'{self.log.config.log_dir}/grow.log', 'r') as file:
                log_lines = len(file.readlines())
            self.assertEqual(lvl+1, log_lines - prev_log_lines, f"Lines written in log file do not match logging level { lvl }")
            prev_log_lines = log_lines

            # Once Database logging is created use that here
            # 
            #

        # Check multi-line logs print across multiple lines. 
        self.log.fatal('Line 1  \nLine 2  \nLine 3')
        with open(f'{self.log.config.log_dir}/grow.log', 'r') as file:
            lines = file.readlines()
            log_lines = len(lines)
        self.assertEqual(log_lines - prev_log_lines, 3, f"Lines written in log file do not match logging level { lvl }")            
        self.assertGreaterEqual(len(lines[-1]), 25, "Multi-line logs do not have log meta data on new lines")
        # Turn test mode back on to silence output
        self.log.test_mode = True
        