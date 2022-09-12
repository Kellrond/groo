# This initialization script is to be run during instal or manual set up

# Build the database schema based on database/__schema__.py
from database import db
from database.__schema__ import buildTables

buildTables(db)
