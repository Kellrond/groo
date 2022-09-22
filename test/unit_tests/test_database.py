import datetime, glob, os, sys
import json
import unittest
import psycopg2
from psycopg2.errors import UndefinedTable
from unittest.mock import patch

import database
from test import config

class TestDatabase(unittest.TestCase):
    # Setups and teardowns
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

    # Helper functions
    def drop_test_table(self):
        sql = 'DROP TABLE IF EXISTS test_table;'
        self.db.execute(sql)
        self.db.close()

    def query_len_test_table(self) -> int:      
        sql = 'SELECT * FROM test_table;'
        result = self.db.query(sql)
        return len(result)

    # The tests
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
        self.drop_test_table()

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
        result = self.query_len_test_table()
        self.assertEqual(result, 0, "Results for querying empty table don't match expectations of nothing")
        self.drop_test_table()

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
        result = self.query_len_test_table()
        self.assertEqual(result, 0, "Results for querying empty table don't match expectations of nothing")
        
        # Prep the table to test drop if exists statement
        sql = ''' 
            INSERT INTO test_table (txt, int_numb, real_numb)
            VALUES ('test', 1, 1.5);
        '''
        self.db.execute(sql)
        result = self.query_len_test_table()
        self.assertEqual(result, 1, 'Query length does not match expectation')

        table_dict['__table_name__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=False)
        result = self.query_len_test_table()
        self.assertEqual(result, 1, 'drop_if_exists dropped the new table incorrectly')

        table_dict['__table_name__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        result = self.query_len_test_table()
        self.assertEqual(result, 0, 'drop_if_exists did not drop table before creating new table')

       
    def test_insert(self):
        # Drop and insert a test table 
        table_dict = {
            '__table_name__':  'test_table',
            'test_id':           'SERIAL PRIMARY KEY',
            'test_bigint':       'BIGINT',
            'test_bool':         'BOOLEAN',
            'test_bytea':        'BYTEA',
            'test_char5':        'CHAR(5)',
            'test_date':         'DATE',
            'test_double':       'DOUBLE PRECISION',
            'test_int':          'INTEGER',
            'test_json':         'JSON',
            'test_numeric':      'NUMERIC',
            'test_real':         'REAL',
            'test_smallint':     'SMALLINT',
            'test_time':         'TIME',
            'test_time_w_tz':    'TIMETZ',
            'test_text':         'TEXT',
            'test_timestamp':    'TIMESTAMP',
            'test_timestamp_tz': 'TIMESTAMPTZ',
            'test_varchar5':     'VARCHAR(5)'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        
        # Test a manual insert
        sql = '''   
            insert into test_table (
                test_id,    test_bigint,    test_bool,      test_bytea, test_char5,     test_date,  test_double, 
                test_int,   test_json,      test_numeric,   test_real,  test_smallint,  test_time,  test_time_w_tz, 
                test_text,  test_timestamp, test_timestamp_tz, test_varchar5
            ) VALUES (
                0,
                9223372036854775800,    --bigint 
                true,                   -- boolean
                decode('013d7d16d7ad4fefb61bd95b765c8ceb', 'hex'), --bytea
                'abcde',                -- char(5)
                '1984-12-16',           -- date,
                0.1234567890123,        -- double precision
                123,                    -- integer
                '[1,2,3]'::json,        -- json
                1/3,                    -- numeric
                1.123456,               -- real
                32767,                  -- smallint
                '13:13:13',             -- time
                '13:13:13 -8:00',       --  timetz
                'test_text',            -- text
                TIMESTAMP '2004-01-01 13:13:13',  -- timestamp
                TIMESTAMP WITH TIME ZONE '2004-01-01 13:13:13+08',  -- timestamptz
                'abc'                   -- varchar(5)
            )
        '''

        self.db.execute(sql)
        self.assertEqual(self.query_len_test_table(),1,"Manual insert statement failed insert")
        
        # Now test the insert from dictionary
        table_dict['__table_name__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table_name__': 'test_table',
            'test_id': 0, 
            'test_bigint': 9223372036854775800, 
            'test_bool': True, 
            'test_bytea': b'El ni\xc3\xb1o come camar\xc3\xb3n' , 
            'test_char5': 'abcde', 
            'test_date': datetime.date(1984, 12, 16), 
            'test_double': 0.1234567890123, 
            'test_int': 123,
            'test_json': json.dumps([1, 2, 3]), 
            'test_numeric': 0.0123456789123456789, 
            'test_real': 1.123456, 
            'test_smallint': 32767, 
            'test_time': datetime.time(13, 13, 13), 
            'test_time_w_tz': datetime.time(13, 13, 13, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=57600))), 
            'test_text': 'test_text', 
            'test_timestamp': datetime.datetime(2004, 1, 1, 13, 13, 13), 
            'test_timestamp_tz': datetime.datetime(2004, 1, 1, 5, 13, 13, tzinfo=datetime.timezone.utc), 
            'test_varchar5': 'abc'
            }
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),1,"Db.add() method failed insert")
