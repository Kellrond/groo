import datetime
import json
from decimal import Decimal
import unittest
from psycopg2.errors import UndefinedTable


import database
from test import config

class TestDatabase(unittest.TestCase):
    # Setups and teardowns
    @classmethod
    def setUpClass(cls):
        ## The following is if we want to populate a bunch of data on the test_db
        # setup_db = database.Db.from_test_conf(config.db.GrowDb)
        # setup_db.connect()
        # with open(config.db.test_data_file_path, 'r') as file:
        #     sql_statements = file.read().split(';')
        # for sql in sql_statements:
        #     if sql != '':
        #         setup_db.execute(sql)
        # del setup_db
        cls.db = database.Db.from_test_conf(config.db.GrowDb)

    @classmethod
    def tearDownClass(cls):
        del cls.db

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
            '__table__': 'test_table',
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

        table_dict['__table__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=False)
        result = self.query_len_test_table()
        self.assertEqual(result, 1, 'drop_if_exists dropped the new table incorrectly')

        table_dict['__table__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        result = self.query_len_test_table()
        self.assertEqual(result, 0, 'drop_if_exists did not drop table before creating new table')
       
    def test_add(self):
        # Drop and insert a test table 
        table_dict = {
            '__table__':  'test_table',
            'test_id':         'SERIAL PRIMARY KEY',
            'test_text':       'TEXT'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        
        # Test a manual insert
        sql = '''   
            insert into test_table ( test_text ) VALUES ('test_text' )
        '''
        self.db.execute(sql)
        self.assertEqual(self.query_len_test_table(),1,"Manual insert statement failed insert")
        
        # Now test the insert from dictionary
        table_dict['__table__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table__': 'test_table',
            'test_text': 'test_text', 
            }
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),1,"Db.add() method failed insert")
     
    def test_add_datatypes(self):
        # Drop and insert a test table 
        table_dict = {
            '__table__':  'test_table',
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
        table_dict['__table__'] = 'test_table'
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table__': 'test_table',
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

    def test_add_constraints(self):
        # Drop and insert a test table 
        table_dict = {
            '__table__':  'test_table',
            'test_id':         'SERIAL PRIMARY KEY',
            'test_text':       'TEXT'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        
        # Check auto-incrementing table with and without keys
        insert_dict = {
            '__table__': 'test_table',
            'test_text': 'test_text', 
            }
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),1,"Db.add() failed insert without key in dict")

        insert_dict['test_id'] = 99
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),2,"Db.add() failed insert with key in dict")


        # Check non-auto-incrementing tables with and without keys 
        table_dict = {
            '__table__':  'test_table',
            'test_id':         'INTEGER PRIMARY KEY',
            'test_text':       'TEXT'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table__': 'test_table',
            'test_text': 'test_text', 
            }
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),1,"Db.add() failed insert without key in dict")

        insert_dict['test_id'] = 99
        self.db.add(insert_dict)
        self.assertEqual(self.query_len_test_table(),2,"Db.add() failed insert with key in dict")

        # Test with multiple keys
        sql = f'''
            CREATE TABLE test_table (
                test_id     char(5),
                test_id2    varchar(5),
                test_text   TEXT,
                PRIMARY KEY (test_id, test_id2)
            );
        '''
        self.drop_test_table()
        self.db.execute(sql)

        insert_dict = {
            '__table__': 'test_table',
            'test_text': 'test_text', 
            }
        # This should raise an assertion. Composite keys MUST be passed into the dictionary
        with self.assertRaises(Exception):
            self.db.add(insert_dict)

        insert_dict['__table__'] = 'test_table'
        insert_dict['test_id'] = 'abcde'
        with self.assertRaises(Exception):
            self.db.add(insert_dict)

        insert_dict['__table__'] = 'test_table'
        insert_dict['test_id2'] = 'zyxwv'
        self.db.add(insert_dict)

        result = self.query_len_test_table()
        self.assertEqual(result, 1, "There should be 1 record in the Db")

    def test_add_multiple(self):
        table_dict = {
            '__table__':  'test_table',
            'test_id':         'SERIAL PRIMARY KEY',
            'test_text':       'TEXT'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        add_list = []

        number_of_records = 20
        for i in range(number_of_records):
            add_list.append({'__table__': 'test_table','test_text': 'test_text'})

        self.db.add(add_list)
        result = self.query_len_test_table()
        self.assertEqual(result, number_of_records, f"There should be {number_of_records} record in the Db") 

    def test_next_id(self):
        # Create an auto-incrementing table and test that it returns None
        table_dict = {
            '__table__': 'test_table',
            'id': 'SERIAL PRIMARY KEY',
            'txt': 'TEXT'
        }
    
        self.db.createTable(table_dict, drop_if_exists=True)
        result = self.query_len_test_table()
        self.assertEqual(result, 0, "There should be no records in the Db")

        next_id = self.db.nextId('test_table')
        self.assertEqual(next_id, None, 'Primary key is auto-incrementing or serial. Should not return next id')

        # Create and prime the table for the test
        table_dict = {
            '__table__': 'test_table',
            'id': 'INTEGER PRIMARY KEY',
            'txt': 'TEXT'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        next_id = self.db.nextId('test_table')
        self.assertEqual(next_id, 1, 'No records in Db, next_id should be 1')

        self.db.add({'__table__': 'test_table','id':1, 'txt': 'test'})
        result = self.query_len_test_table()
        self.assertEqual(result, 1, "There should be a record in the Db")

        next_id = self.db.nextId('test_table')
        self.assertEqual(next_id,2,'With 1 record in the Db the next id should be 2')

    def test_query(self):
        table_dict = {
            '__table__':  'test_table',
            'test_id':           'INTEGER PRIMARY KEY',
            'test_bigint':       'BIGINT',
            'test_bool':         'BOOLEAN',
            'test_char5':        'CHAR(5)',
            'test_date':         'DATE',
            'test_double':       'DOUBLE PRECISION',
            'test_int':          'INTEGER',
            'test_numeric':      'NUMERIC',
            'test_real':         'REAL',
            'test_smallint':     'SMALLINT',
            'test_time':         'TIME',
            'test_time_w_tz':    'TIMETZ',
            'test_text':         'TEXT',
            'test_timestamp':    'TIMESTAMP',
            'test_varchar5':     'VARCHAR(5)'
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table__': 'test_table',
            'test_id': 1, 
            'test_bigint': 9223372036854775800, 
            'test_bool': True, 
            'test_char5': 'abcde', 
            'test_date': datetime.date(1984, 12, 16), 
            'test_double': 0.1234567890123, 
            'test_int': 123,
            'test_numeric': Decimal('0.012345678912345679'), 
            'test_real': 1.123456, 
            'test_smallint': 32767, 
            'test_time': datetime.time(13, 13, 13), 
            'test_time_w_tz': datetime.time(13, 13, 13, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=57600))), 
            'test_text': 'test_text', 
            'test_timestamp': datetime.datetime(2004, 1, 1, 13, 13, 13), 
            'test_varchar5': 'abc'
            }
        self.db.add(insert_dict)
        result = self.db.query('SELECT * FROM test_table')
        for k,v in result[0].items():
            self.assertEqual(v,insert_dict[k], 'Data does not match between insert dict and results')

        # Bad query
        sql = 'INSERT INTO test_table ( doesnt matter I just want to test for SELECT )'
        with self.assertRaises(Exception):
            self.db.query(sql)

    def test_query_one(self):
        table_dict = {
            '__table__':  'test_table',
            'test_id':           'INTEGER PRIMARY KEY',
            'test_text':         'TEXT',
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        insert_dict = {
            '__table__': 'test_table',
            'test_id': 1, 
            'test_text': 'test_text', 
            }
        self.db.add(insert_dict)

        result = self.db.queryOne('SELECT * FROM test_table')
        for k,v in result.items():
            self.assertEqual(v,insert_dict[k], 'Data does not match between insert dict and results')

        # Bad query
        sql = 'INSERT INTO test_table ( doesnt matter I just want to test for SELECT )'
        with self.assertRaises(Exception):
            self.db.query(sql)

    def test_scalar(self):
        table_dict = {
            '__table__':  'test_table',
            'test_id':         'SERIAL PRIMARY KEY',
            'test_int':        'INTEGER',
        }
        self.db.createTable(table_dict, drop_if_exists=True)
        
        sum_total = 0
        for i in range(1, 20):
            sum_total += i
            self.db.add({'__table__': 'test_table', 'test_int': i})

        result = self.db.scalar('SELECT test_int FROM test_table WHERE test_id = 13')
        self.assertEqual(result, 13, 'Single scalar returned incorrect result')

        result = self.db.scalar('SELECT sum(test_int) FROM test_table')
        self.assertEqual(result, sum_total, 'Aggregate scalar results failed')

        # Test an invalid query
        with self.assertRaises(Exception):
            self.db.scalar('SELECT * FROM test_table')

    def test_upsert(self):
        table_dict = {
            '__table__':  'test_table',
            'test_id':   'INTEGER PRIMARY KEY',
            'test_text': 'TEXT',
        }
        self.db.createTable(table_dict, drop_if_exists=True)

        for i in range(0,20):
            self.db.upsert({'__table__': 'test_table', 'test_id': i, 'test_text':'FIRST PASS'})

        self.assertEqual(self.query_len_test_table(), 20, 'Upsert() did not add rows with unique pk''s properly')

        for i in range(10,30):
            self.db.upsert({'__table__': 'test_table', 'test_id': i, 'test_text':'SECOND PASS'})

        self.assertEqual(self.query_len_test_table(), 30, 'Upsert() did not update rows with matching pk''s properly')

        sql = "SELECT count(*) FROM test_table t WHERE t.test_text = 'FIRST PASS'"

        self.assertEqual(self.db.scalar(sql), 10, 'upsert() did not overwrite rows correctly')