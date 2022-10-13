''' Houses the PyMeta class for parsing Python documentation'''
# Internal
from    modules.documentation import Docs
from    modules import logging


log = logging.Log(__name__)


class PyMeta(Docs):
    ''' Adds Python meta flags to Docs class variable file_lines  '''
    def __init__(self) -> None:
        super().__init__()
        # Ensure that the Doc class variables are filled
        self.readLines()

    @classmethod
    @log.performance
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    @log.performance
    def processPyFileFlags(self):
        ''' Runs the flagging in the correct order. Though in this case order does not matter as much. '''
        log.verbose('Start flagging Python file metadata')
        self.__flag_file_comments()
        self.__flag_file_imports()
        self.__flag_todos()
        log.verbose('Stop flagging Python file metadata')

    @log.performance
    def __flag_file_comments(self):
        ''' Adds flags for file docstring'''
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if not self.isFileOfExtension(file.get('file_path'),'py'):
                continue

            in_comment = False        
            finished_with_docs = False
            is_hashtag_comment = False
            prev_non_empty_line = 0

            for line in file.get('lines'):
                if finished_with_docs == True:
                    break

                single_q = False
                double_q = False
                hashtag  = False
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
                    # If not a hashtag comment
                    else:
                        line['flags'].append('file docs') 
                        # Check for single liner
                        if single_q or double_q:
                            closing_quotes = max([ line.get('line')[3:].find("'''"), line.get('line')[+3:].find('"""') ])
                        else:
                            closing_quotes = max([ line.get('line').find("'''"), line.get('line').find('"""') ])

                        if closing_quotes > -1:
                            in_comment = False
                            finished_with_docs = True
                            line['flags'] = [ x for x in line['flags'] if x != 'docs']
                            line['flags'].append('file docs end')

                if len(line.get('line').strip()) > 0: 
                    prev_non_empty_line = line.get('line_no')

    @log.performance
    def __flag_file_imports(self):
        ''' Adds flags for file imports'''
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if not self.isFileOfExtension(file.get('file_path'),'py'):
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

    @log.performance
    def __flag_todos(self):
        ''' Adds flags for file todos'''
        for file in self.file_lines: 
            # if the file isn't a .py continue to next file
            if not self.isFileOfExtension(file.get('file_path'),'py'):
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