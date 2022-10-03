import config
from modules.documentation import Docs
from modules import logging
# from database import docs_db

log = logging.Log(__name__)

class PyDocsParser(Docs):
    ''' File comments reside at the top of a file before the imports 
    '''    

    folders = []
    files = [] 
    classes = []
    functions = []
    meta = []

    def __init__(self) -> None:
        self.config = config.modules.Documentation
        super().__init__()

    @classmethod
    @log.performance
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    @log.performance
    def parsePyDocs(self):
        ''' Runs the flagging in the correct order. Though in this case order does not matter as much. '''
        self.prepFolders()

    @log.performance
    def processFolders(self):
        print('\n\n\n\n\n')
        [print(x) for x in self.folder_list ]
        [print(x) for x in self.file_paths ]

    @log.performance
    def parseFilesToParts(self):
        ''' Takes the flagged lines and converts them into objects'''

        for file in self.file_lines:
            py_class_lines = []
            py_meta_lines  = []
            py_func_lines  = []
            for line in file.get('lines'):
                ln = line.get('line')
                flags = line.get('flags')

                if 'cls' in flags:
                    py_class_lines.append(ln)
                if 'func' in flags:
                    py_func_lines.append(ln)
                if 'import' in flags or 'file docs' in flags or 'todo' in flags:
                    py_meta_lines.append(ln)

            self.parseClasses(py_class_lines)
            self.parseFunctions(py_func_lines)
            self.parseMeta(py_meta_lines)

    @log.performance
    def parseClasses(self, lines:list):
        pass

    @log.performance
    def parseFunctions(self, lines:list):
        pass

    @log.performance
    def parseMeta(self, lines:list):
        pass
