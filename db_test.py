from config import db_config

from database import Db
from database.__schema__ import buildTables

db = Db(db_config.garden_db_connect)
result = db.query("SELECT * FROM test WHERE 1 = 1")

buildTables()
print(result)
