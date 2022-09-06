from flask_sqlalchemy import SQLAlchemy
from sqlalchemy       import func

from www import app

db = SQLAlchemy(app)

def nextUniqueId(Class) -> int:
    ''' Get the next id for inserting into database. '''
    maxId = db.session.query(func.max(Class)).first()[0]
    nextId =  maxId + 1 if maxId != None else 0
    return nextId

def returnDictFromDboObject(db_object) -> dict:
    ''' If there is a db_object it will convert from sqlalchemy object to dict else return None'''
    if db_object:
        object_dict = db_object.__dict__
        object_dict.pop('_sa_instance_state', None)
        return object_dict
    else:
        return None
