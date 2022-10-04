import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
from  modules.documentation import py_functions

from modules import logging
from test import t_config

class TestDocsPyFunctions(unittest.TestCase):
    ''' Test the Python documentation 
        
        The following can be handy to debug and test this
        `self.classDoc.debug_file_lines('class start', 58, 134)`
    '''
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.funcDoc = py_functions.PyFunctionDocs.from_test_conf(t_config.modules.Documentation)
        cls.funcDoc.readLines()
        cls.funcDoc.processPyFunctionFlags()

    @classmethod
    def tearDownClass(cls):
        ''' file_lines is a class variable and we don't want to pollute tests after they have run '''
        for file in cls.funcDoc.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

    # Helper functions
    def find_flags(self, flag:str) -> int:
        '''Looks for a parsing flag '''
        file = [ file for file in self.funcDoc.file_lines if file.get('file_path') == 'test/test_data/documentation/demo.py' ]
        if len(file) >= 1:
            file = file[0]
        count = 0
        for line in file.get('lines'):
            if flag in line.get('flags'):
                count += 1
        return count

    def test_func_defs(self):
        result = self.find_flags('func start')
        self.assertEqual(result, 3, 'There should be 3 function start flags')
        result = self.find_flags('func end')
        self.assertEqual(result, 3, 'There should be 3 function end flags')

    def test_func_params(self):
        result = self.find_flags('func param start')
        self.assertEqual(result, 3, 'There should be 3 function parameter start flags')
        result = self.find_flags('func param end')
        self.assertEqual(result, 3, 'There should be 3 function parameter end flags')
        result = self.find_flags('func return')
        self.assertEqual(result, 1, 'There should be 1 function return flags')

    def test_func_docs(self):
        result = self.find_flags('func docs start')
        self.assertEqual(result, 3, 'There should be 3 function docstring start flags')
        result = self.find_flags('func docs end')
        self.assertEqual(result, 3, 'There should be 3 function docstring end flags')
       
    def test_nested_func(self):
        result = self.find_flags('nest func start')
        self.assertEqual(result, 3, 'There should be 3 nested function start flags')
        result = self.find_flags('nest func end')
        self.assertEqual(result, 3, 'There should be 3 nested function end flags')
        result = self.find_flags('nest func param start')
        self.assertEqual(result, 3, 'There should be 3 nested function parameter start flags')
        result = self.find_flags('nest func param end')
        self.assertEqual(result, 3, 'There should be 3 nested function parameter end flags')
        
        result = self.find_flags('nest func return')
        self.assertEqual(result, 2, 'There should be 2 nested function return flags')




    def test_decorators(self):
        result = self.find_flags('decorated')
        self.assertEqual(result, 2, 'Function decorators failed')