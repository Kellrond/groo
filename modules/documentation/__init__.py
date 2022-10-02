'''
    Overall the design on this is inefficient. It loops through files many many times over.
    A single pass over a file to create all the flags would be a more efficient way to do it. 
    But this function wont be run often as it really needs to be done after a major update. 
    Doing it in a single pass per flag is easier to debug. The only gotchas in this approach 
    are that some methods require others to be run before hand.  
    been run already  flag orders will be. 
'''
from config  import modules
from modules import logging

from glob import glob

log = logging.Log(__name__)

class Docs:
    ''' Superclass for other documentation classes. Primarily builds and maintains a file list 
        which is shared by the classes. 

        Notes:
            - file lines start on zero to make math easy in python. If it's ever going to be displayed 
              as code this should be adjusted only then. 
    ''' 
    file_paths = []
    file_lines = []
    folders    = []

    def __init__(self) -> None:
        log.performance('Docs.__init__')
        self.config = modules.Documentation
        log.performance('Docs.__init__')

    @classmethod
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class'''
        log.performance('Docs.from_test_conf')
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        log.performance('Docs.from_test_conf')
        return test_class

    def generateFolderList(self):
        ''' Loads a list of folders and sub folders to the folder list based on the folders listed
            in the config file. 
        ''' 
        log.performance('Docs.generateFolderList')
        folder_list = []
        for folder in self.config.docs_folder_list:
            folder_list += glob(f"./{folder}/**/", recursive=True)
        # Remove the ./ in front
        folder_list = [ x[2:] for x in folder_list ]

        ignore_folders_list = ['venv']
        for ignored_folder in ignore_folders_list:
            folder_list  = [ x for x in folder_list if x[:len(ignored_folder)] != ignored_folder ]

        folder_list = [ x for x in folder_list if x.find('__pycache__') == -1 ]
        folder_list = [ {'file_path': x, 'split_file_path': [ sq for sq in x.split('/') if sq != '' ], 'folder_id': i } for i, x in enumerate(folder_list) ]

        Docs.folders = folder_list
        log.performance('Docs.generateFolderList')

    def generateFilePaths(self):
        ''' Globs the files with the extensions listed in the config file from the folder list
            gathered in self.generateFolderList()
        '''
        log.performance('Docs.generateFilePaths')
        # Check that the folder class variable has been set
        if len(self.folders) == 0:
            self.generateFolderList()

        if len(self.file_paths) == 0: # Don't waste cycles
            for folder in self.folders:
                for ext in self.config.docs_ext_list:
                    Docs.file_paths += glob(f"{ folder.get('file_path') }*.{ ext }")
            log.verbose('Read file paths into class')
        log.performance('Docs.generateFilePaths')

    def readLines(self): 
        ''' Reads the lines of the files generated in self.generateFilePaths '''
        log.performance('Docs.readLines')
        # Check that the file_paths class variable is not empty and try to fill it
        if len(self.file_paths) == 0:
            self.generateFilePaths()

        if len(self.file_lines) == 0: # Don't waste cycles
            for fp in self.file_paths:
                with open(fp, 'r') as file:
                    lines = file.readlines()
              
                line_list = []
                for i, line in enumerate(lines):
                    # Each line should have the line numbers, line and flags
                    line_list.append({
                        'line_no': i,
                        'whitespace': len(line) - len(line.lstrip()),
                        'flags': [],
                        'line': line.replace('\n',''),
                    })

                temp_dict = { 
                    'file_path': fp,
                    'lines': line_list
                }
                Docs.file_lines.append(temp_dict)
        log.performance('Docs.readLines')

    def debug_file_lines(self, find_filter=None, start_pos=0, end_pos=None, file='test/test_data/documentation/demo.py'):
        ''' Used to debug / view the output of the function

            Params:
                - find_filter: `[ f for f in line.get('flags') if f.find(find_filter)]`
                  to get all class flags just used 'class' else be specific 'class start'
                - start_pos: defaults to 0 as the line to start printing on 
                - end_pos: defaults as None for end_pos as the line to stop printing on 
                - file: defaults to the demo python documentation file
        '''
        log.performance('Docs.debug_file_lines')
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
        log.performance('Docs.debug_file_lines')

    def isFileOfExtension(self, file:dict, ext:str) -> bool:
        ''' Returns True or False if the file is of the desired extension '''
        log.performance('Docs.isFileOfExtension')
        filtered_file_path = file.get('file_path')
        dot_pos = 1
        while dot_pos > -1:
            dot_pos = filtered_file_path.find('.')
            filtered_file_path = filtered_file_path[dot_pos + 1:]
        log.performance('Docs.isFileOfExtension')
        return filtered_file_path == ext
        

    def generateDocumentation(self, param_func) -> list:
        log.performance('Docs.generateDocumentation')
        document_list = []
        for file_path in self.file_paths:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                routes_in_file = param_func(lines, file_path)
                if len(routes_in_file) > 0:
                    document_list += routes_in_file 
        log.performance('Docs.generateDocumentation')
        return document_list 

