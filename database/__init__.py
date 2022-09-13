import  psycopg2

import appConfig

class Db:
    ''' Database class that handles connection to the database '''
    def __init__(self) -> None:
        self.host     = appConfig.db.host
        self.user     = appConfig.db.user
        self.password = appConfig.db.password
        self.dbname   = appConfig.db.dbname
        self.port     = appConfig.db.port
        self.conn     = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port,
                    dbname=self.dbname
                )
            except psycopg2.DatabaseError as e:
                raise e

    def execute(self, sql: str) -> bool:
        ''' Execute a SQL statement which does not return a result. ie. DELETE, UPDATE, etc. '''
        self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql)            

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

    # Add or update records
    def add(self, table: str, dbo: dict):
        ''' Add a single new record '''
        pass

    def upsert(self, table: str, dbo: dict):
        ''' Insert or updates a record as necessary 
                Params:
                    - table: the table name you want to add / update 
                    - dbo: a dictionary containing the column names you want to add
        '''
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

        dbo_has_keys = False
        for pk in primary_keys:

        print(primary_keys)

db = Db()