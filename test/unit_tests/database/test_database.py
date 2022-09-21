import glob, os, sys
import unittest
import psycopg2
from psycopg2.errors import UndefinedTable
from unittest.mock import patch

import database
from test import config

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_db = database.Db.from_test_conf(config.db)
        setup_db.connect()
        with open(config.db.test_data_file_apth, 'r') as file:
            sql_statements = file.read().split(';')
            
        # for sql in sql_statements:
        #     if sql != '':
        #         setup_db.execute(sql)

        del setup_db

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.db = database.Db.from_test_conf(config.db)

    def tearDown(self):
        del self.db

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

    def test_create_table(self):
        # First drop the table if it exists
        sql = 'DROP TABLE IF EXISTS test_table;'
        self.db.execute(sql)
        self.db.close()

        # Test selecting from a non existant table
        sql = 'SELECT * FROM test_table'
        with self.assertRaises(UndefinedTable):
            _ = self.db.query(sql)
        self.db.close()

        # Create the test table with SQL
        sql = ''' 
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                txt TEXT,
                int_numb INTEGER,
                real_numb REAL
            )
        '''
        self.db.execute(sql)

        # Test that you can query the new table
        sql = 'SELECT * FROM test_table'
        result = self.db.query(sql)
        self.assertEqual(len(result), 0, "Results for querying empty table don't match expectations of nothing")

        # Create the table via a dictionary
        table_dict = {
            '__table_name__': 'test_table',
            'id': 'SERIAL PRIMARY KEY',
            'txt': 'TEXT',
            'int_numb': 'INTEGER',
            'real_numb': 'REAL'
        }
        
        