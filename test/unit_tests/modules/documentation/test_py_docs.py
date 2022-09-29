import glob, os
from mailbox import linesep
import unittest

import  modules.documentation as documentation
import  modules.documentation.py_classes as py_classes

from modules import logging
from test import config

class TestPyDocumentation(unittest.TestCase):
    ''' Test the Python documentation '''
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.classDoc = py_classes.ClassesDocs.from_test_conf(config.modules.Documentation)
        cls.classDoc.readLines()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
    
    def tearDown(self):
        for file in self.classDoc.file_lines:
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
        # Make sure we are empty to begin with
        result = self.find_flags('class start')
        self.assertEqual(result, 0, 'There should be zero class start flags')
        result = self.find_flags('class end')
        self.assertEqual(result, 0, 'There should be zero class end flags')
        
        self.classDoc.flagClasses()
        result = self.find_flags('class start')
        self.assertEqual(result, 3, 'There should be 3 class start flags')
        result = self.find_flags('class end')
        self.assertEqual(result, 3, 'There should be 3 class end flags')

    def test_find_class_docstr(self):
        self.classDoc.flagClasses()
        result = self.find_flags('docstr start')
        self.assertEqual(result, 0, 'There should be zero docstring start flags')
        result = self.find_flags('docstr end')
        self.assertEqual(result, 0, 'There should be zero docstring end flags')

        self.classDoc.flagClassDocstring()
        result = self.find_flags('docstr start')
        self.assertEqual(result, 3, 'There should be 3 docstr start flags')
        result = self.find_flags('docstr end')
        self.assertEqual(result, 3, 'There should be 3 docstr end flags')

    def test_find_class_methods(self):
        self.classDoc.flagClasses()
        self.classDoc.flagClassDocstring()
        result = self.find_flags('method start')
        self.assertEqual(result, 0, 'There should be zero method start flags')
        result = self.find_flags('method end')
        self.assertEqual(result, 0, 'There should be zero method end flags')

        self.classDoc.flagClassMethods()
        self.classDoc.debug_file_lines()
        result = self.find_flags('method start')
        self.assertEqual(result, 12, 'There should be 12 method start flags')
        result = self.find_flags('method end')
        self.assertEqual(result, 12, 'There should be 12 method end flags')