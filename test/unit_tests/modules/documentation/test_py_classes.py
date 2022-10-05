import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
import  modules.documentation.py_classes as py_classes

from modules import logging
from test import t_config

class TestDocsPyClasses(unittest.TestCase):
    ''' Test the Python documentation 
        
        The following can be handy to debug and test this
        `self.classDoc.debug_file_lines('class start', 58, 134)`
    '''
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.classDoc = py_classes.PyClassesDocs.from_test_conf(t_config.modules.Documentation)
        cls.classDoc.readLines()
        cls.classDoc.processPyClassFlags()

    @classmethod
    def tearDownClass(cls):
        ''' file_lines is a class variable and we don't want to pollute tests after they have run '''
        for file in cls.classDoc.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

    # Helper functions
    def find_flags(self, flag:str) -> int:
        '''Looks for a parsing flag '''
        file = [ file for file in self.classDoc.file_lines if file.get('file_path') == 'test/test_data/documentation/demo.py' ]
        if len(file) >= 1:
            file = file[0]
        count = 0
        for line in file.get('lines'):
            if flag in line.get('flags'):
                count += 1
        return count

    def test_find_classes(self):
        result = self.find_flags('cls start')
        self.assertEqual(result, 3, 'There should be 3 class start flags')
        result = self.find_flags('cls end')
        self.assertEqual(result, 3, 'There should be 3 class end flags')
        # Now look for Superclasses
        result = self.find_flags('super cls')
        self.assertEqual(result, 2, 'There should be 2 super class flags')


    def test_find_class_docs(self):
        result = self.find_flags('cls docs start')
        self.assertEqual(result, 2, 'There should be 2 docs start flags')
        result = self.find_flags('cls docs end')
        self.assertEqual(result, 2, 'There should be 2 docs end flags')

    def test_find_class_methods(self):
        result = self.find_flags('meth start')
        self.assertEqual(result, 12, 'There should be 12 method start flags')
        result = self.find_flags('meth end')
        self.assertEqual(result, 12, 'There should be 12 method end flags')

    def test_find_method_parameters(self):
        result = self.find_flags('meth param start')
        self.assertEqual(result, 12, 'There should be 3 method parameter start flags')
        result = self.find_flags('meth param end')
        self.assertEqual(result, 12, 'There should be 3 method parameter end flags')

    def test_find_method_docs(self):
        result = self.find_flags('meth docs start')
        self.assertEqual(result, 10, 'There should be 10 method docstring start flags')
        result = self.find_flags('meth docs end')
        self.assertEqual(result, 10, 'There should be 10 method docstring end flags')

    def test_find_method_return(self):
        result = self.find_flags('meth return')
        self.assertEqual(result, 11, 'There should be 11 method return flags')

    def test_find_method_decorators(self):
        result = self.find_flags('decorated')
        self.assertEqual(result, 2, 'There should be 2 method decorated flags')

    def test_find_nested_methods(self):
        result = self.find_flags('nest meth start')
        self.assertEqual(result, 3, 'There should be 3 nested method start flags')
        result = self.find_flags('nest meth param start')
        self.assertEqual(result, 3, 'There should be 3 nested method param start flags')
        result = self.find_flags('nest meth docs start')
        self.assertEqual(result, 2, 'There should be 2 nested method docs start flags')
        result = self.find_flags('nest meth end')
        self.assertEqual(result, 3, 'There should be 3 nested method end flags')
        result = self.find_flags('nest meth param end')
        self.assertEqual(result, 3, 'There should be 3 nested method param end flags')
        result = self.find_flags('nest meth docs end')
        self.assertEqual(result, 2, 'There should be 2 nested method docs end flags')
