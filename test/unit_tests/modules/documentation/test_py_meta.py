import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
from  modules.documentation import py_meta

from modules import logging
from test import t_config

class TestDocsPyHeader(unittest.TestCase):
    ''' Test the Python documentation 
        
        The following can be handy to debug and test this
        `self.classDoc.debug_file_lines('class start', 58, 134)`
    '''
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.fileDoc = py_meta.PyFileDocs.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc.readLines()
        cls.fileDoc.processPyFileFlags()

    @classmethod
    def tearDownClass(cls):
        ''' file_lines is a class variable and we don't want to pollute tests after they have run '''
        for file in cls.fileDoc.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

    # Helper functions
    def find_flags(self, flag:str) -> int:
        '''Looks for a parsing flag '''
        file = [ file for file in self.fileDoc.file_lines if file.get('file_path') == 'test/test_data/documentation/demo.py' ]
        if len(file) >= 1:
            file = file[0]
        count = 0
        for line in file.get('lines'):
            if flag in line.get('flags'):
                count += 1
        return count

    def test_file_comments(self):
        result = self.find_flags('file docs start')
        self.assertEqual(result, 1, 'There should be 1 file docstring start flags')
        result = self.find_flags('file docs end')
        self.assertEqual(result, 1, 'There should be 1 file docstring end flags')

    def test_file_imports(self):
        result = self.find_flags('import')
        self.assertEqual(result, 7, 'There should be 7 file import flags')

    def test_file_todos(self):
        result = self.find_flags('todo')
        # There are 2 todo's but one is a 2 liner
        self.assertEqual(result, 3, 'There should be 3 todo flags')

       