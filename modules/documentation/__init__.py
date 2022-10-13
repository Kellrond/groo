'''
    Overall the design on this is inefficient. It loops through files many many times over.
    A single pass over a file to create all the flags would be a more efficient way to do it. 
    But this function wont be run often as it really needs to be done after a major update. 
    Doing it in a single pass per flag is easier to debug. The only gotchas in this approach 
    are that some methods require others to be run before hand.  
'''
from    glob     import glob
# Local
import  config
from    database import Db
from    modules  import logging

log = logging.Log(__name__)

class Docs:
    ''' Superclass for other documentation classes. Primarily builds and maintains a file list 
        which is shared by the classes. 

        Notes:
            - file lines start on zero to make math easy in python. If it's ever going to be displayed 
              as code this should be adjusted only then. 
    ''' 
    file_paths  = []
    file_lines  = []
    folder_list = []

    @log.performance
    def __init__(self) -> None:
        self.config = config.modules.Documentation

    @classmethod
    @log.performance
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the Docs class'''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    @log.performance
    def generateFolderList(self):
        ''' Globs a list of folders and sub folders based on the config Documentation.docs_folder_list. 
        ''' 
        log.verbose('Start glob documentation folder list')
        
        folder_list = []
        glob_list = glob(f"./**/", recursive=True)
        for folder in glob_list:
            second_slash = folder[2:].find('/') + 2
            if folder[:second_slash] in self.config.docs_folder_list or folder in self.config.docs_folder_list:
                folder_list.append(folder)

        folder_list = [ x for x in folder_list if x.find('__pycache__') == -1 ]
        folder_list = [ {'file_path': x, 'split_file_path': [ sq for sq in x.split('/') if sq != '' ], 'folder_id': i + 1} for i, x in enumerate(folder_list) ]
        
        # If we are testing we dont want to add the root directory
        if self.config.docs_folder_list != ['./test/test_data/documentation/']:
            folder_list.append({'file_path': './', 'split_file_path': [ '.' ], 'folder_id': 0, 'parent_id': None })

        # Find parents for folders
        for folder in folder_list:
            if len(folder.get('split_file_path')) > 1:
                parent_folder_path = '/'.join(folder.get('split_file_path')[:-1]) + '/'
                folder['parent_id'] = None
                result_of_parent_search = [ x for x in folder_list if x.get('file_path') == parent_folder_path]
                if len(result_of_parent_search) > 0:
                    folder['parent_id'] = result_of_parent_search[0].get('folder_id')

            name = folder.get('file_path')[:-1]
            while name.find('/') != -1:
                name = name[name.find('/')+1:]

            folder['name'] = name

        Docs.folder_list = folder_list

    @log.performance
    def generateFilePaths(self):
        ''' Globs files with the extensions listed in the config file from the folder list
            gathered in self.generateFolderList()
        '''
        # Check that the folder class variable has been set
        if len(self.folder_list) == 0:
            self.generateFolderList()

        if len(self.file_paths) == 0: # Don't waste cycles
            for folder in self.folder_list:
                for ext in self.config.docs_ext_list:
                    glob_list = glob(f"{ folder.get('file_path') }*.{ ext }")
                    for fp in glob_list:
                        Docs.file_paths.append(
                            {
                            'folder_id': folder.get('folder_id'),
                            'file_path': fp
                            }
                        )
            log.verbose('Read file paths into class')

    @log.performance
    def readLines(self): 
        ''' Reads the lines of the files generated in self.generateFilePaths '''
        
        # Check that the prerequisites are met
        if len(self.file_paths) == 0:
            self.generateFilePaths()

        if len(self.file_lines) == 0: # Don't waste cycles
            log.verbose('Start reading file content from file_paths')
            for i, fp in enumerate(self.file_paths):
                with open(fp.get('file_path'), 'r') as file:
                    lines = file.readlines()
              
                line_list = []
                for n, line in enumerate(lines):
                    # Each line should have the line numbers, line and flags
                    line_list.append({
                        'line_no': n,
                        'whitespace': len(line) - len(line.lstrip()),
                        'flags': [],
                        'line': line.replace('\n',''),
                    })

                # Extract the file extension 
                extension = fp.get('file_path')
                while extension.find('.') != -1:
                    extension = extension[extension.find('.') + 1:]

                name = fp.get('file_path')
                while name.find('/') != -1:
                    name =  name[name.find('/') + 1:]

                temp_dict = { 
                    'file_path': fp.get('file_path'),
                    'folder_id': fp.get('folder_id'),
                    'file_id': i,
                    'name': name,
                    'ext': extension,
                    'length': len(line_list),
                    'lines': line_list
                }
                Docs.file_lines.append(temp_dict)

    @log.performance
    def debug_file_lines(self, find_filter=None, start_pos=0, end_pos=None, file='test/test_data/documentation/demo.py'):
        ''' Used to debug / view the output of the function

            Params:
                - find_filter: `[ f for f in line.get('flags') if f.find(find_filter)]`
                  to get all class flags just used 'class' else be specific 'class start'
                - start_pos: defaults to 0 as the line to start printing on 
                - end_pos: defaults as None for end_pos as the line to stop printing on 
                - file: defaults to the demo python documentation file
        '''
        if type(find_filter) == str:
            find_filter = [find_filter]

        # This bit is for printing the result of this function   
        for file in [ f for f in self.file_lines if f.get('file_path') == file ]:
            line_no = []
            whitespace = []
            flags = []
            lines = []
            for line in file.get('lines'):
                filtered_flags = []
                if find_filter != None and len(find_filter) > 0:
                    for filter in find_filter:
                        filtered_flags += [ f for f in line.get('flags') if f == filter ]
                else:
                    filtered_flags = line.get('flags')

                line_no.append(str(line.get('line_no')))
                whitespace.append(str(line.get('whitespace')))
                flags.append(", ".join(filtered_flags))
                lines.append(line.get('line'))

            max_len_flags = max([len(x) for x in flags])

        print(file.get('file_path'))
        print('No. Wspc. Flags')
        if end_pos == None:
            end_pos = len(line_no)
        for i in range(start_pos, end_pos):
            print(f'''{line_no[i].ljust(4)}  {whitespace[i].rjust(2)} {flags[i].ljust(max_len_flags)}:{lines[i]}''')

    @log.performance
    def isFileOfExtension(self, file_path:str, ext:str) -> bool:
        ''' Returns True or False if the file is of the desired extension 
        
            Params:
                - file_path: full path or just the filename
                - ext: the extension you want to match
        '''
        dot_pos = 1
        while dot_pos > -1:
            dot_pos = file_path.find('.')
            file_path = file_path[dot_pos + 1:]
        return file_path == ext
        
@log.performance
def generateDocumentation():
    ''' Loads and runs all the documentation parts. When new file flaggers and parsers added
        ensure they get added to this function.
    '''
    from modules.documentation import py_classes, py_functions, py_meta, py_parser

    # Python documentation
    classes = py_classes.PyClasses()
    funct   = py_functions.PyFunctions()
    meta    = py_meta.PyMeta()
    parser  = py_parser.PyParser()

    classes.processPyClassFlags()
    funct.processPyFunctionFlags()
    meta.processPyFileFlags()
    parser.parsePython()

    log.info('documentation generated')
    
def exportAllDocumentation():
    ''' Export the documentation to file and database. This will overwrite the file and database
        but this is okay. Since we are generating the documentation from scratch   
    '''
    from modules.documentation import export_docs, Docs

    if len(Docs.file_paths) == 0:
        generateDocumentation()

    export_docs.toTxt(config.modules.Documentation.export_file_path)
    db = Db()
    export_docs.toDb(db)