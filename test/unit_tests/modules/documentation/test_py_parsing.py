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
        py_meta.Docs.file_lines  = []
        py_meta.Docs.file_paths  = []
        py_meta.Docs.folder_list = []
        cls.docs = documentation.Docs.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc = py_meta.PyFileDocs.from_test_conf(t_config.modules.Documentation)
        cls.classDoc = py_classes.PyClassesDocs.from_test_conf(t_config.modules.Documentation)
        cls.funcDoc = py_functions.PyFunctionDocs.from_test_conf(t_config.modules.Documentation)
        cls.parser = py_parser.PyDocsParser.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc.readLines()

        for file in cls.docs.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

        cls.fileDoc.processPyFileFlags()
        cls.classDoc.processPyClassFlags()
        cls.funcDoc.processPyFunctionFlags()
        cls.parser.parsePython()

    @classmethod
    def tearDownClass(cls):
        ''' file_lines is a class variable and we don't want to pollute tests after they have run '''
        for file in cls.parser.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

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

    def find_dict_in_list(self, key:str, value:str, _list:list) -> dict:
        ''' Finds a dictionary from a list of dictionaries by a key value pair'''
        for obj in _list:
            if obj.get(key) == value:
                return obj

    # Meta python doc tests
    def test_parse_todos(self):
        todo2 = self.parser.todo[1]        
        self.assertEqual(len(self.parser.todo), 2, "Mismatched number of todo's parsed")
        self.assertEqual(todo2.get('line_count'),2,'Did not parse 2 line todo properly')
        self.assertGreater(todo2.get('line').find('\n'),-1, 'Did not insert newline in 2 line todo properly')
        found_hash = todo2.get('line').find('#')
        self.assertEqual(found_hash, -1, 'Parser did not remove "#" properly')

    def test_parse_imports(self):
        self.assertEqual(len(self.parser.imports), 9, 'Parser did not catch all the imports')
        count = len([ x for x in self.parser.imports if x.get('alias') != None])
        self.assertEqual(count, 3, 'Parser did not catch the aliases correctly on python imports')
        count = len([ x for x in self.parser.imports if x.get('object') != None])
        self.assertEqual(count, 5, 'Parser did not get the objects right in a from import')

    def test_parse_file_docs(self):
        self.assertEqual(len(self.parser.file_docs), 1, 'Parser did not get the file docstring')

    def test_parse_functions(self):
        ''' Here functions will be function and nested functions. Not method functions or nested
            method functions. Those are tested separately
        '''
        self.assertEqual(sum([1 for x in self.parser.functions if x.get('class_id') == None]), 6, 'Functions not parsed properly. Wrong numbers')
        count = sum([1 for x in self.parser.functions if x.get('parent_id') != None and x.get('class_id') == None])
        self.assertEqual(count, 3, 'Parser did not get the nested functions right')
        
        test_dict = self.find_dict_in_list('name', 'testImportInFunction', self.parser.functions)
        self.assertEqual(len(test_dict.get('parameters')), 3, 'Parser got function parameters wrong')
        test_dict = self.find_dict_in_list('name', 'testNestedDefInFunction', self.parser.functions)
        self.assertEqual(len(test_dict.get('docstring')), 1,'Parser trimmed docstring wrong')
        
        test_dict = self.find_dict_in_list('name', 'decoratedAndMultiLine', self.parser.functions)
        self.assertEqual(len(test_dict.get('docstring')), 2,'Parser got multi-line docstring wrong')        
        self.assertEqual(test_dict.get('returns'), 'str','Parser got function return wrong')  

        self.assertEqual(len(test_dict.get('decorators')), 2,'Parser got function decorators wrong')  


    def test_parse_classes(self):
        result = len(self.parser.classes)
        self.assertEqual(result, 3,'Parser got number of classes wrong')  
        result = len(self.parser.classes[0].get('docstring'))
        self.assertGreater(result, 10,'Parser got docstring length wrong') 
        result = len(self.parser.classes[0].get('parameters'))
        self.assertEqual(result, 4,'Parser got number of parameters wrong') 
        result = len(self.parser.classes[2].get('superclass'))
        self.assertEqual(result, 2,'Parser for superclasses wrong') 

        # Class methods and nested methogs
        result = len([x for x in self.parser.functions if x.get('class_id') == 0])
        self.assertEqual(result, 7,'Parser got number of methods wrong, __init__ counts as method') 

        test_dict = self.find_dict_in_list('name', 'c1func2', self.parser.functions)
        self.assertEqual(len(test_dict.get('parameters')), 2,'Parser got number of method parameters wrong')
        self.assertEqual(len(test_dict.get('docstring')), 1,'Parser got method docstring wrong')
        self.assertEqual(test_dict.get('returns'), 'str','Parser got method return wrong')

        test_dict = self.find_dict_in_list('name', 'nestedDef2', self.parser.functions)
        self.assertEqual(len(test_dict.get('parameters')), 2,'Parser got number of nested method parameters wrong')
        self.assertEqual(len(test_dict.get('docstring')), 1,'Parser got nested method docstring wrong')
        self.assertEqual(test_dict.get('returns'), 'int','Parser got nested method return wrong')
