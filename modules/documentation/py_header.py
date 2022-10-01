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
            if not self.isFileOfExtension(file, 'py'):
                continue

            in_comment = False        
            finished_with_docs = False
            is_hashtag_comment = False
            prev_non_empty_line = 0

            for line in file.get('lines'):
                if finished_with_docs == True:
                    break
                
                if not in_comment: # The first line must have the comment or it breaks                       
                    single_q = line.get('line')[:3] == "'''"
                    double_q = line.get('line')[:3] == '"""'
                    hashtag  = line.get('line')[:1] == '#'

                    if (single_q or double_q or hashtag):
                        in_comment = True
                        is_hashtag_comment = hashtag
                        line['flags'].append('file docs start')

                if in_comment:
                    if is_hashtag_comment:
                        if line.get('line')[0:1] == '#':
                            line['flags'].append('file docs')
                        else:
                            file['lines'][prev_non_empty_line]['flags'].append('file docs end')
                            in_comment = False
                            finished_with_docs = True
                            is_hashtag_comment = False

                if len(line.get('line').strip()) > 0: 
                    prev_non_empty_line = line.get('line_no')

    def flagFileImports(self):
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue
            in_multiline_import = False
            # Imports can happen anywhere in the file. So check each line. 
            for line in file.get('lines'):
                # Imports can happen in function, method, loops etc. so deal with 
                whtSpc    = line.get('whitespace')
                is_from   = line.get('line')[whtSpc:whtSpc+4] == 'from'
                is_import = line.get('line')[whtSpc:whtSpc+6] == 'import'
                if is_from or is_import:
                    line['flags'].append('import')
                    # An import can span multiple lines so look for \
                    in_multiline_import = line.get('line').find('\\') > -1
                elif in_multiline_import:
                    line['flags'].append('import')
                    # Check if it continues to yet another line
                    in_multiline_import = line.get('line').find('\\') > -1                    


    def flagTodos(self):
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            in_multiline_todo = False
            for line in file.get('lines'):
                whtSpc    = line.get('whitespace')
                is_comment = line.get('line')[whtSpc:whtSpc+1] == '#'
                if is_comment:
                    if line.get('line')[whtSpc:whtSpc+8].lower().find('todo') > -1:
                        in_multiline_todo = True
                    if in_multiline_todo:
                        line['flags'].append('todo')
                else:
                    is_comment = False
                    in_multiline_todo = False