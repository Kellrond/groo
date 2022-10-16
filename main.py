# Local
import config
from database import Db

from modules import camera

camera.runCameraTest()

# # Generate the documentation. 
# from modules import documentation 
# from modules.documentation import export_docs, py_parser
# documentation.generateDocumentation()
# export_docs.toTxt(config.modules.Documentation.export_file_path)
# db = Db()
# export_docs.toDb(db)
# # Help with debugging
# parser = py_parser.PyParser()
# parser.debug_file_lines(start_pos=600,file='./modules/documentation/py_parser.py')



