import  config
from    modules import logging
# External dependencies
import  psycopg2, traceback

log = logging.Log(__name__)

class Db:
    ''' Database class that handles connection to the database '''
    def __init__(self) -> None:
        self.config   = config.db
        self.conn     = None

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    @classmethod
    def from_test_conf(cls, config):
        ''' Instantiates a class using the test configuration passed in. '''
        temp_class = cls()
        temp_class.config = config
        return temp_class

    # Connection controls
    def commit(self):
        ''' Commit the last set of statements to the database '''
        if self.conn is not None:
            log.debug('DB commit')
            self.conn.commit()

    def connect(self):
        ''' If inactive open a connection to the database '''
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.config.host3,
                    user=self.config.user,
                    password=self.config.password,
                    port=self.config.port,
                    dbname=self.config.dbname
                )
                log.debug('DB connected')       
            except Exception as e:
                log.error(traceback.format_exc())
                raise e

    def close(self):
        ''' If active close the database connection '''
        if self.conn is not None:
            self.conn.close()
            self.conn = None

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
                - table: the dictionary as desccribed above 
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

        sql = f'CREATE TABLE {table_name} ( '

        for column_name,meta in table.items():
            sql += f' {column_name} {meta},'
        
        # Remove the trailing comma or postgres throws error
        sql = sql[:-1] + ');'
        self.execute(sql)

    def nextId(self, table):
        primary_keys = self.getPrimaryKeyNamesFromTable(table)
        if len(primary_keys) == 1:
            sql = f'SELECT MAX({ primary_keys[0] }) FROM { table }'
            max_id = self.scalar(sql)
            return max_id + 1

    def getPrimaryKeyNamesFromTable(self, table: str) -> list:
        self.connect()
        # Find the primary keys of the table
        sql = f'''
            SELECT c.column_name, c.data_type
            FROM information_schema.table_constraints tc 
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) 
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
            AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{ table }';
            '''
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            primary_keys = [ row[0] for row in cursor.fetchall() ]
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

    def add(self, table: str, dbo: dict):
        ''' Add a single new record '''
        columns = ", ".join(dbo.keys())
        placeholders = ", ".join([ '%s' for x in dbo.values() ])  
        values = tuple(dbo.values())

        sql = f'''
            INSERT INTO { table } ({ columns })
            VALUES ({ placeholders })
        '''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, values)        

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
