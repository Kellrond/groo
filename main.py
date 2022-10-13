# Local
import config
from database import Db
from modules import documentation 
from modules.documentation import export_docs, py_parser

# documentation.generateDocumentation()
# export_docs.toTxt(config.modules.Documentation.export_file_path)

documentation.generateDocumentation()
parser = py_parser.PyParser()
db = Db()
export_docs.toTxt(config.modules.Documentation.export_file_path)
export_docs.toDb(db)


# [ print(x) for x in parser.todo]

# # print(parser.file_docs[0])
# # print()
# print(parser.imports)


