
import appConfig


class Db:
    def __init__(self, connect_string) -> None:
        self.__name__ = "garden"
        self.engine = create_engine(connect_string)
        self.session = Session(self.engine)


    def connect(self):
        return self.engine.connect()

    def test_connection(self) -> bool:
        try:
            with self.connect() as c:
                is_connected = True
        except:
            is_connected = False
        return is_connected

    def query(self, sql):
        with self.connect() as c:
            results = c.execute(sql)
        return [ str(row) for row in results ]
    
    def execute(self, sql):
        ''' Executes a SQL statement where there is no value returned'''
        try:
            with self.connect() as c:
                c.execute(sql)
            return True
        except Exception as e:
            print(e)
            return False

    def nextUniqueId(self, db_class) -> int:
        ''' Get the next id for inserting into database. '''
        maxId  = self.session.query(func.max(db_class)).first()[0]
        nextId = maxId + 1 if maxId != None else 0
        return nextId

    def returnDictFromDboObject(self, db_object) -> dict:
        ''' If there is a db_object it will convert from sqlalchemy object to dict else return None'''
        if db_object:
            object_dict = db_object.__dict__
            object_dict.pop('_sa_instance_state', None)
            return object_dict
        else:
            return None
 
db = Db(appConfig.db.garden_connect)