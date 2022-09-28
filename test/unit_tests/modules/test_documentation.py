import glob, os
import unittest

import modules.logging as logging
from test import config

class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Turn of logging globally
        logging.Log.test_mode = True 

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.log = logging.Log.from_test_conf(config.modules.Logging, __name__)

    def tearDown(self):
        pass
