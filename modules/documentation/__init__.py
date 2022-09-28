from config  import modules
from modules import logging

from glob import glob

log = logging.Log(__name__)

class Docs:
    ''' Superclass for other documentation classes. Primarily builds and maintains a file list 
        which is shared by the classes. 
    ''' 
    file_paths = []
    folders    = []

    def __init__(self) -> None:
        # Since file_paths and folders are class variables this should only run once
        if len(self.file_paths) == 0:
            self.__generate_folder_list()
            self.__generate_file_paths()
            log.verbose('Generated doc folder and file_paths lists')
    
    def __generate_folder_list(self):
        folder_list = glob(f"./**/", recursive=True)

        # Remove the ./ in front
        folder_list = [ x[2:] for x in folder_list ]

        ignore_folders_list = ['venv']
        for ignored_folder in ignore_folders_list:
            folder_list  = [ x for x in folder_list if x[:len(ignored_folder)] != ignored_folder ]


        folder_list = [ x for x in folder_list if x.find('__pycache__') == -1 ]
        folder_list = [ {'file_path': x, 'split_file_path': [ sq for sq in x.split('/') if sq != '' ], 'folder_id': i } for i, x in enumerate(folder_list) ]

        self.folder_list = folder_list

    def __generate_file_paths(self):
        for folder in self.folder_list:
            for ext in self.ext_list:
                self.file_paths += glob(f"{ folder.get('file_path') }*.{ ext }")

    def generate_documentation(self, param_func) -> list:
        document_list = []
        for file_path in self.file_paths:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                routes_in_file = param_func(lines, file_path)
                if len(routes_in_file) > 0:
                    document_list += routes_in_file 
        return document_list 

