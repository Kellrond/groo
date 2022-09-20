import glob, os, sys
import unittest
import psycopg2
from unittest.mock import patch

import database
from test import config

class TestLogging(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_db = database.Db.from_test_conf(config.db)
        setup_db.connect()
        with open(config.db.test_data_file_apth, 'r') as file:
            sql_statements = file.read().split(';')
            
        for sql in sql_statements:
            if sql != '':
                setup_db.execute(sql)

        del setup_db

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.db = database.Db.from_test_conf(config.db)

    def tearDown(self):
        pass

    def test_database_connection(self):
        # Ensure the connection is closed before testing 
        if self.db.conn != None:
            self.db.conn.close()

        # Connect to db and test for existence of connection
        self.db.connect()
        self.assertNotEqual(self.db.conn, None, "Database connection failed")

        # Close the connection and make sure it's closed
        self.db.close()
        self.assertEqual(self.db.conn, None, "Database connection failed to close")

        
