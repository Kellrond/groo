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

        for file in cls.docs.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

        cls.fileDoc.processPyFileFlags()
        cls.classDoc.processPyClassFlags()
        cls.funcDoc.processPyFunctionFlags()
        cls.parser.parseFilesToParts()

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
        count = len([ x for x in self.parser.imports if x.get('alias') != ''])
        self.assertEqual(count, 3, 'Parser did not catch the aliases correctly on python imports')
        count = len([ x for x in self.parser.imports if x.get('object') != ''])
        self.assertEqual(count, 5, 'Parser did not get the objects right in a from import')

    def test_parse_file_docs(self):
        self.assertEqual(len(self.parser.file_docs), 1, 'Parser did not get the file docstring')

    def test_parse_functions(self):
        ''' Here functions will be function and nested functions. Not method functions or nested
            method functions. Those are tested separately
        '''
        self.assertEqual(len(self.parser.functions), 6, 'Functions not parsed properly. Wrong numbers')
        count = sum([1 for x in self.parser.functions if x.get('parent_id') != None])
        self.assertEqual(count, 3, 'Parser did not get the nested functions right')
        count = len(self.parser.functions[0].get('parameters'))
        self.assertEqual(count, 3, 'Parser got function parameters wrong')
        result = len(self.parser.functions[1].get('docstring'))
        self.assertEqual(result, 1,'Parser trimmed docstring wrong')
        result = len(self.parser.functions[-1].get('docstring'))
        self.assertEqual(result, 2,'Parser got multi-line docstring wrong')        
        result = self.parser.functions[-1].get('returns')
        self.assertEqual(result, 'str','Parser got function return wrong')  
        result = len(self.parser.functions[-1].get('decorators'))
        self.assertEqual(result, 2,'Parser got function decorators wrong')  


    def test_parse_classes(self):
        # self.print_docs()

        # self.parser.debug_file_lines()

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
        self.assertEqual(result, 3,'Parser got number of methods wrong') 


        # result = len(self.parser.classes[-1].get(''))
        # self.assertEqual(result, 2,'') 
        # result = len(self.parser.classes[-1].get(''))
        # self.assertEqual(result, 2,'') 
        # result = len(self.parser.classes[-1].get(''))
        # self.assertEqual(result, 2,'') 
        # result = len(self.parser.classes[-1].get(''))
        # self.assertEqual(result, 2,'') 
        # result = len(self.parser.classes[-1].get(''))
        # self.assertEqual(result, 2,'') 










    def print_docs(self):
        print("TEST PARSE OUTPUT")
        print()
        # print(self.parser.file_docs[0].get('docs'))
        print("\n=== FOLDERS")
        for line in self.parser.folder_list:
            for k,v in line.items():
                print(k,v,sep=": ", end="\t")
            print()
        print("\n=== FILES")
        for line in self.parser.file_lines:
            for k,v in line.items():
                if k == 'lines':
                    continue
                print(k,v,sep=": ", end="\t")
            print()
        # print('\n=== IMPORTS')
        # for line in self.parser.imports:
        #     for k,v in line.items():
        #         print(k,v,sep=": ", end="\t")
        #     print()

        print("\n=== Classes")
        for line in self.parser.classes:
            for k,v in line.items():
                if k == 'lines':
                    continue
                if k == 'docstring':
                    continue
                    if len(v) > 0:
                        print(k,v[0],sep=": ", end="\t")
                    else:
                        print(k, end=':\t')
                    continue
                
                print(k,v,sep=": ", end="\t")
            print()


        # print('\n=== FUNCTIONS')
        # for fn in [x for x in self.parser.functions if x.get('class_id') == None]:
        #     if fn.get('returns') != None:
        #         return_str = f' -> {fn.get("returns")}:'
        #     else:
        #         return_str = ':'
        #     print(f'''file id: {fn.get('file_id')} function_id: {fn.get('function_id')} class_id: {fn.get('class_id')} parent_id: {fn.get('parent_id')} line start: {fn.get('line_start')} line count: {fn.get('line_count')}\n''')
        #     if len(fn.get('decorators')) > 0:
        #         for decorator in fn.get('decorators'):
        #             print(f'@{decorator}')
        #     print(f'''{ fn.get('name') }({', '.join(fn.get('parameters'))}){ return_str }''')
        #     [print(f"\t{x.get('line')}") for x in fn.get('docstring') ]
        #     print('\n---------------------------------------')
