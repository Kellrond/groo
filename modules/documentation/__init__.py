from config  import modules
from modules import logging

from glob import glob

log = logging.Log(__name__)

class Docs:
    ''' Superclass for other documentation classes. Primarily builds and maintains a file list 
        which is shared by the classes. 
    ''' 
    file_paths = []
    file_lines = []
    folders    = []

    def __init__(self) -> None:
        self.config = modules.Documentation
 
    @classmethod
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class'''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    def generateFolderList(self):
        ''' Loads a list of folders and sub folders to the folder list based on the folders listed
            in the config file. 
        ''' 

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

    def generateFilePaths(self):
        ''' Globs the files with the extensions listed in the config file from the folder list
            gathered in self.generateFolderList()
        '''
        # Check that the folder class variable has been set
        if len(self.folders) == 0:
            self.generateFolderList()

        if len(self.file_paths) == 0: # Don't waste cycles
            for folder in self.folders:
                for ext in self.config.docs_ext_list:
                    Docs.file_paths += glob(f"{ folder.get('file_path') }*.{ ext }")
            log.verbose('Read file paths into class')

    def readLines(self): 
        ''' Reads the lines of the files generated in self.generateFilePaths '''
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
                

    def generateDocumentation(self, param_func) -> list:
        document_list = []
        for file_path in self.file_paths:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                routes_in_file = param_func(lines, file_path)
                if len(routes_in_file) > 0:
                    document_list += routes_in_file 
        return document_list 

