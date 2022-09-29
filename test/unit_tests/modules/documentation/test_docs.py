import glob, os
import unittest

import  modules.documentation as documentation
from    modules import logging
from    test import t_config

class TestDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 
        cls.docs = documentation.Docs.from_test_conf(t_config.modules.Documentation)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_folder_and_file_lists(self): 
        self.docs.generateFolderList()
        find_test_path = sum([ 1 for x in self.docs.folders if x.get('file_path') == 'test/test_data/documentation/' ]) 
        self.assertEqual(find_test_path, 1, 'Did not locate test folder')
        
        self.docs.generateFilePaths()
        self.assertTrue('test/test_data/documentation/demo.py' in self.docs.file_paths, 'demo.py not located in test/test_data/documentation/')
        self.assertTrue('test/test_data/documentation/example.bad' not in self.docs.file_paths, 'example.bad was not ignored because of file extension')

    def test_read_lines(self):
        self.assertEqual(len(self.docs.file_lines), 0, 'file_lines should be empty')
        self.docs.readLines()
        # Check that the test file got read into the list
        numb_files = len(self.docs.file_paths)
        self.docs.readLines()
        self.assertEqual(len(self.docs.file_lines), numb_files, 'Entries in file_lines does not match the number of files')
