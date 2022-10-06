import config
from modules import documentation 
from modules.documentation import export_docs

documentation.generateDocumentation()
export_docs.toTxt(config.modules.Documentation.file_export)