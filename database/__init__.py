from sqlalchemy import create_engine, func, MetaData
from sqlalchemy.orm import Session
from config import db_config


class Db:
    def __init__(self, connect_string) -> None:
        self.__name__ = "garden"
        self.engine = create_engine(connect_string)
        self.session = Session(self.engine)
        self.meta = MetaData(self.engine)

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
 