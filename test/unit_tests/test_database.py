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
        def drop_test_table():
            sql = 'DROP TABLE IF EXISTS test_table;'
            self.db.execute(sql)
            self.db.close()

        # Test that you can query the new table
        def query_len_test_table() -> int:      
            sql = 'SELECT * FROM test_table;'
            result = self.db.query(sql)
            return len(result)

        # First drop the table if it exists
        drop_test_table()

        # Test selecting from a non existent table
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
        result = query_len_test_table()
        self.assertEqual(result, 0, "Results for querying empty table don't match expectations of nothing")
        drop_test_table()

        # Tests creating the table via a dictionary

        # No tablename in the dictionary should raise an exception
        no_tablename = {
            'id': 'SERIAL PRIMARY KEY',
            'test': 'TEXT'
        }
        with self.assertRaises(Exception):
            self.db.createTable(no_tablename)
        self.db.close()

        table_dict = {
            '__table_name__': 'test_table',
            'id': 'SERIAL PRIMARY KEY',
            'txt': 'TEXT',
            'int_numb': 'INTEGER',
            'real_numb': 'REAL'
        }
        self.db.createTable(table_dict)
        result = query_len_test_table()
        self.assertEqual(result, 0, "Results for querying empty table don't match expectations of nothing")
        
        # Prep the table to test drop if exists
        sql = ''' 
            INSERT INTO test_table (txt, int_numb, real_numb)
            VALUES ('test', 1, 1.5);
        '''
        self.db.execute(sql)
        result = query_len_test_table()
        self.assertEqual(result, 1, 'Query length does not match expectation')

        table_dict['__table_name__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=False)
        result = query_len_test_table()
        self.assertEqual(result, 1, 'drop_if_exists dropped the new table incorrectly')

        table_dict['__table_name__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        result = query_len_test_table()
        self.assertEquals(result, 0, 'drop_if_exists did not drop table before creating new table')

       
        