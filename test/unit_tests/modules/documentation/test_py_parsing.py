import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
from  modules.documentation import py_classes, py_functions, py_parser

from modules import logging
from modules.documentation import py_meta
from test import t_config

class TestDocsPyParsing(unittest.TestCase):
    ''' Test the Python documentation 
        
        The following can be handy to debug and test this
        `self.classDoc.debug_file_lines('class start', 58, 134)`
    '''
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.docs = documentation.Docs.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc = py_meta.PyFileDocs.from_test_conf(t_config.modules.Documentation)
        cls.classDoc = py_classes.PyClassesDocs.from_test_conf(t_config.modules.Documentation)
        cls.funcDoc = py_functions.PyFunctionDocs.from_test_conf(t_config.modules.Documentation)
        cls.parser = py_parser.PyDocsParser.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc.readLines()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        for file in self.docs.file_lines:
            for line in file.get('lines'):
                line['flags'] = []    # Helper functions
    
    def tearDown(self):
        for file in self.docs.file_lines:
            for line in file.get('lines'):
                line['flags'] = []    # Helper functions

    def find_flags(self, flag:str) -> int:
        '''Looks for a parsing flag '''
        file = [ file for file in self.docs.file_lines if file.get('file_path') == 'test/test_data/documentation/demo.py' ]
        if len(file) >= 1:
            file = file[0]
        count = 0
        for line in file.get('lines'):
            if flag in line.get('flags'):
                count += 1
        return count

    def run_all_docs(self):
        ''' Run everything to prep for parsing '''
        self.fileDoc.processPyFileDocs()
        self.classDoc.processPyClassDocs()
        self.funcDoc.processPyFunctionDocs()

    def test_parse_folders(self):
        self.run_all_docs()
        self.parser.parseFilesToParts()

        