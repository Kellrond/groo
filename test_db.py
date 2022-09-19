from database import Db

db = Db()

sql = '''CREATE TABLE IF NOT EXISTS tt (
    id int PRIMARY KEY,
    col1 text,
    col2 text
)'''

db.execute(sql)

dbo = {
    'id': 5,
}

db.upsert('tt', dbo)
db.commit()
