import glob, os, sys, time
import unittest
from unittest.mock import patch

import modules.logging as logging
import database
from test import t_config

class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = logging.Log.from_test_conf(t_config.modules.Logging, t_config.db.GrowDb, __name__)

    @classmethod
    def tearDownClass(cls):
        # Glob and delete all files in the test_data/logs folder
        glob_logs = glob.glob(f'{t_config.modules.Logging.log_dir}/*.*')
        if len(glob_logs) > 0:
            for log_filepath in glob_logs:
                os.remove(log_filepath)

    def fileLineCount(self, file_name:str) -> int:
        ''' Counts the number of lines in a log returns the number 
        
            Param:
                - file_name: `grow.log` for example. No '/'
        '''
        with open(f'{self.log.config.log_dir}/{file_name}', 'r') as file:
            lines = file.readlines()
            log_lines = len(lines)
        return log_lines

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
        self.assertEqual(len(glob_logs),2, "Wrong number of log files")

    def test_delete_logs(self):
        # Make sure there are log files there to start with
        self.log.init_logs()

        # Check that log files where added
        glob_logs = glob.glob(f'{self.log.config.log_dir}/*.*')
        self.assertGreaterEqual(len(glob_logs), 2, "Files were not added to test_data/logs")        

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

        # Create a db object with the test configuration so it's connected to the test database
        db = database.Db.from_test_conf(t_config.db.GrowDb)
        drop_sql = 'DELETE FROM logs WHERE 1=1;'
        db.execute(drop_sql)

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
            with open(f'{self.log.config.log_dir}/{t_config.modules.Logging.log_file}', 'r') as file:
                log_lines = len(file.readlines())
            self.assertEqual(lvl+1, log_lines - prev_log_lines, f"Lines written in log file do not match logging level { lvl }")
            prev_log_lines = log_lines

            # Query the database and check for records
            count_sql = 'SELECT COUNT(*) FROM logs;'
            count = db.scalar(count_sql)
            self.assertEqual(lvl + 1, count, f"Records written to database to not match log level { lvl }")

            # Now delete all the rows
            drop_sql = 'DELETE FROM logs WHERE 1=1;'
            db.execute(drop_sql)

        # Check multi-line logs print across multiple lines. 
        self.log.fatal('Line 1  \nLine 2  \nLine 3')
        log_lines = self.fileLineCount(t_config.modules.Logging.log_file)
        self.assertEqual(log_lines - prev_log_lines, 3, f"Lines written in log file do not match logging level { lvl }")            
        with open(f'{self.log.config.log_dir}/{t_config.modules.Logging.log_file}', 'r') as file:
            last_line = file.readlines()[-1]
        self.assertGreaterEqual(len(last_line), 25, "Multi-line logs do not have log meta data on new lines")
        # Turn test mode back on to silence output
        self.log.test_mode = True
        
    def test_performance_testing(self):
        ''' This is a busier test. Might be worth splitting up if it gets added to more '''

        @self.log.performance
        def time_tester():
            pass

        # Clear the performance file
        db = database.Db.from_test_conf(t_config.db.GrowDb)
        drop_sql = 'DELETE FROM performance_logs WHERE 1=1;'
        db.execute(drop_sql)
        with open(t_config.modules.Logging.performance_file, 'w') as perf_log:
            pass

        # Test single timer
        log_lines = self.fileLineCount(t_config.modules.Logging.performance_file)
        self.assertEqual(log_lines, 0, 'Performance log should be empty')
        
        # Turn on the performance
        self.log.config.performance_to_db = True
        self.log.config.performance_to_file = True

        time_tester()

        log_lines = self.fileLineCount(t_config.modules.Logging.performance_file)
        self.assertEqual(log_lines, 1, 'Performance log should have one line')

        # Test overlapping timers

        # log_lines = self.fileLineCount(t_config.modules.Logging.performance_file)
        # self.assertEqual(log_lines, 5, 'Performance log should have one line')

        # # Db check
        # sql = 'SELECT COUNT(*) FROM performance_logs;'
        # count = db.scalar(sql)
        # self.assertEqual(count, 5, 'Performance log count in DB is wrong')

        # # Time check
        # self.log.performance('timer test')
        # time.sleep(0.010)
        # self.log.performance('timer test')

        # Performance is a hog, turn it off
        self.log.config.performance_to_db = False
        self.log.config.performance_to_file = False        
        
        # with open(f"{self.log.config.log_dir}/{self.log.config.performance_file}", 'r') as file:
        #     last_line = file.readlines()[-1]

        # last_col = float(last_line.split('\t')[-1])
        # self.assertAlmostEqual(last_col, 0.0101, 3, 'Time should be around 10 ms')

