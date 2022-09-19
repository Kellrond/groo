import config

from database import Db
from database.__schema__ import buildTables

db = Db(config.db.garden_connect)
buildTables(db)
