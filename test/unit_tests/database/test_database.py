import glob, os, sys
import unittest
import psycopg2
from unittest.mock import patch

import database
from test import config

class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.db = database.Db.from_test_conf(config.db)

    def tearDown(self):
        pass

    def test_database_connection(self):
        if self.db.conn != None:
            self.db.conn.close()

        self.db.connect()


        self.assertNotEqual(self.db.conn, None, "Database connection failed")
