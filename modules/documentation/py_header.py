from urllib.parse import quote_plus
from xml.dom import HierarchyRequestErr
from modules.documentation import Docs
from modules import logging
# from database import docs_db

log = logging.Log(__name__)

class PyFileComments(Docs):
    ''' File comments reside at the top of a file before the imports 
    '''
    def __init__(self) -> None:
        super().__init__()
        self.readLines()

    @classmethod
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    def flagFileComments(self):
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if file.get('file_path')[-3:] != '.py':
                continue

            in_comment = False        
            past_docs = False
            for line in file.get('lines'):
                if past_docs == True:
                    break

                single_q = line.get('line')[:3] == "'''"
                double_q = line.get('line')[:3] == '"""'
                hashtag  = line.get('line')[:1] == '#'

                if (single_q or double_q or hashtag) and not in_comment:
                    in_comment = True
                    line['flags'].append('file docs start')

                if in_comment:
                    line['flags'].append('file docs')

                Add prev line with text and then look for an import or end of quotes 
                Maybe put in somethin where it notes what type of comment it is. hashtag or quotes
        