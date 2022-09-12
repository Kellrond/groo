import appConfig

from database import Db
from database.__schema__ import buildTables

db = Db(appConfig.db.garden_connect)
buildTables(db)
