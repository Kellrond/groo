import  config
from    modules import logging
# External dependencies
import  psycopg2, traceback

log = logging.Log(__name__)

class Db:
    ''' Database class that handles connection to the database. Much of this is
        a wrapper around psycopg2 so some methods are just mirroring 
        
        By default commits occur after every method call where needed. We want to 
        capture as much data as we can. A bad output from one function or sensor 
        should not prevent other data from being written. Transactions should be 
        as small as possible.

        conn:
            connection to the database. Or more accurately a connection to psycopg2
            This abstraction exists to make switching to another database vendor a 
            little easier. 

            `conn == None` is the tell that there is no connection to the database.
            That is not how to close a connection. Please use the close() method.

    '''
    def __init__(self) -> None:
        self.config = config.db
        self.conn = None
        log.debug('Class instantiated')

    def __del__(self):
        ''' If the object is deleted via `del db` close the connection to avoid 
            leftover database connections. 
        '''
        if self.conn is not None:
            self.conn.close()

    @classmethod
    def from_test_conf(cls, config):
        ''' Instantiates a class using the test configuration passed in. '''
        temp_class = cls()
        temp_class.config = config
        log.debug('Test class instantiated')
        return temp_class

    # Connection controls
    def commit(self):
        ''' Commit the last set of statements to the database '''
        if self.conn is not None:
            self.conn.commit()
            log.debug('Transaction committed')

    def connect(self):
        ''' If inactive open a connection to the database '''
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.config.host,
                    user=self.config.user,
                    password=self.config.password,
                    port=self.config.port,
                    dbname=self.config.dbname
                )
                log.debug('Connected')       
            except Exception as e:
                log.error(traceback.format_exc())
                raise e

    def close(self):
        ''' If active close the database connection '''
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            log.debug('Connection closed')

    # Table functions
    
    def createTable(self, table: dict, drop_if_exists=False) -> None:
        ''' Create a table from the dictionary passed in 
        
            The dictionary must contain the key value pair of
            `'__table_name__': 'example_name'`

            The rest of the items in the dictionary should be in key value pairs. 

            Usage:
                `dict = { 
                    '__table_name__': 'example_name',
                    'id': 'SERIAL PRIMARY KEY',
                    'col1': INTEGER,
                    'col2': TEXT  
                }
                db.createTable(dict)
                `

            Params:
                - table: the dictionary as described above 
                - drop_if_exists: drops an existing table. False by default to prevent 
                  accidental data loss
        '''
        table_name = ''     
        if table.get('__table_name__'):
            table_name = table.pop('__table_name__')
        else:
            raise Exception('Create table dict requires "__table_name__"')

        if drop_if_exists:
            sql = f"DROP TABLE IF EXISTS {table_name};"
            self.execute(sql)
        else:
            # If not dropping table check if table exists and leave if it exists
            sql = f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            results = self.query(sql)
            results = [v.get('table_name') for v in results]
            if table_name in results:
                return

        # Build the create table statement
        sql = f'CREATE TABLE {table_name} ( '
        for column_name,meta in table.items():
            sql += f' {column_name} {meta},'
        
        # Remove the trailing comma or postgres throws error
        sql = sql[:-1] + ');'
        self.execute(sql)
        log.info(f'Table { table_name } created')

    def nextId(self, table_name: str): 
        ''' Get the next id in a sequence. Be aware of table with serial or
            auto-incrementing primary keys. They do not get passed keys as they generate
            their own.  

            Returns None if passed a table with multiple primary keys, a serialized key,
            or the table does not exist.

            Params:
                - table_name: just pass in the table name and the rest will get discovered
        '''

        primary_keys = self.getPrimaryKeyNamesFromTable(table_name)
        
        # Check for serialized and return non if found
        if sum([1 for pk in primary_keys if pk.get('autoInc') == True]) > 0:
            return None

        # If there is more than one key, it's a composite and the key is likely put together 
        # from two other primary keys 
        if len(primary_keys) == 1:
            sql = f'SELECT MAX({ primary_keys[0].get("col_name") }) FROM { table_name }'
            max_id = self.scalar(sql)
            # If no records exist then return 1 as the starting id
            if max_id == None:
                return 1
            return max_id + 1

    def getPrimaryKeyNamesFromTable(self, table_name: str) -> list:
        ''' The primary keys a good details to have when working with a table
        
            Params:
                - table_name: just the name of a table
        '''
        self.connect()
        # Find the primary keys of the table
        sql = f'''
            SELECT c.column_name, c.data_type, c.column_default
            FROM information_schema.table_constraints tc 
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) 
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
            AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{ table_name }';
            '''
        result = self.query(sql)

        primary_keys = []
        for pk in result:
            auto_inc_key = str(pk.get('column_default','')).find(table_name) != -1 
            primary_keys.append({
                'col_name': pk.get('column_name'),
                'data_type': pk.get('data_type'),
                'autoInc': auto_inc_key
            })
            
        return primary_keys

    # Queries with a return
    def query(self, sql: str) -> list:
        ''' Query the database, returns a dictionary'''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            records = [ dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return records

    def queryOne(self, sql: str) -> dict:
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            records = dict(zip(columns, cursor.fetchone()))
            cursor.close()
            return records        
 
    def scalar(self, sql):
        ''' Returns a scalar result'''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            records = cursor.fetchone()
            cursor.close()
            return records[0] 

    # Add or update records, execute statement
    def execute(self, sql: str, autoCommit=True) -> bool:
        ''' Execute a SQL statement which does not return a result. ie. DELETE, UPDATE, etc. '''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
        if autoCommit:
            self.commit()

    def add(self, data: dict or list, single_transaction=True):
        ''' Add one or many row. Rows are inserted individually so in a list of
            records you may insert to multiple rows at a time. 

            Security note:
                Using `add()` will avoid SQL injection attacks due to the parameterization of the input values.
                If you are exposing this to the internet, you should always consider injection attacks. Taking 
                a reading from a sensor and writing that value directly to an insert statement is not dangerous.
                But you should think twice if dealing with anything with human input.  

            Params:
                - data: either a dict or a list of dicts. DICTIONARIES MUST HAVE '__table_name__': 'table_name'
                - single_transaction: when left at the True default, commits at the end of all the inserts
                  this is to help ensure data integrity. If keeping all data at all cost is your preference 
                  set this to False.       
        '''
        if type(data) == dict:
            data =[data]

        for row in data:
            table_name = ''     
            if row.get('__table_name__'):
                table_name = row.pop('__table_name__')
            else:
                raise Exception('Create table dict requires "__table_name__"')        
            columns = ", ".join(row.keys())
            placeholders = ", ".join([ '%s' for x in row.values() ])  
            values = tuple(row.values())

            sql = f'''
                INSERT INTO { table_name } ({ columns })
                VALUES ({ placeholders })
            '''
            self.connect()
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(sql, values)  
                if not single_transaction:
                    self.commit()
                log.debug(f'Db.add() inserted row in {table_name}')
            except Exception as e:
                log.error(f'Db.add() failed to add data to table {table_name}')
                log.error(traceback.format_exc())
                self.close()
                raise e

        if single_transaction: 
            self.commit()   
        log.info(f'Db.add() {len(data)} row(s) to database')  

    def upsert(self, table: str, dbo: dict):
        ''' Insert or updates a record as necessary 
                Params:
                    - table: the table name you want to add / update 
                    - dbo: a dictionary containing the column names you want to add
        '''

        # Prepare the strings for insertion into query
        primary_keys = self.getPrimaryKeyNamesFromTable(table)
        primary_keys = ", ".join(primary_keys)
        columns = ", ".join(dbo.keys())
        excluded_cols = ", ".join([ f"EXCLUDED.{col}" for col in dbo.keys() ])
        placeholders = ", ".join([ '%s' for x in dbo.values() ])  
        values = tuple(dbo.values())
        
        # If upserting only a single column the () would break the statement. Putting them back is len > 1
        if len(dbo) > 1:
            columns = f'({ columns })'
            excluded_cols = f'({ excluded_cols })'

        sql = f'''
            INSERT INTO { table } ({ columns })
            VALUES ({ placeholders })
            ON CONFLICT ({ primary_keys }) DO UPDATE SET
            { columns } = { excluded_cols }
        '''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)  
