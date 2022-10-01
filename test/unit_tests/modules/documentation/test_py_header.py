import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
from  modules.documentation import py_header

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
        cls.fileDoc = py_header.PyFileComments.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc.readLines()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

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
        # Make sure we are empty to begin with
        result = self.find_flags('file docs start')
        self.assertEqual(result, 0, 'There should be zero file docstring start flags')
        
        self.fileDoc.flagFileComments()
        result = self.find_flags('file docs start')
        self.assertEqual(result, 1, 'There should be 1 file docstring start flags')
        result = self.find_flags('file docs end')
        self.assertEqual(result, 1, 'There should be 1 file docstring end flags')

    def test_file_imports(self):
        # Make sure we are empty to begin with
        result = self.find_flags('import')
        self.assertEqual(result, 0, 'There should be zero file import flags')
        
        self.fileDoc.flagFileImports()
        result = self.find_flags('import')
        self.assertEqual(result, 7, 'There should be 7 file import flags')

    def test_file_todos(self):
        # Make sure we are empty to begin with
        result = self.find_flags('todo')
        self.assertEqual(result, 0, 'There should be zero todo flags')
        
        self.fileDoc.flagTodos()
        result = self.find_flags('todo')
        self.assertEqual(result, 2, 'There should be 2 todo flags')

       