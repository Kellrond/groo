from glob import glob
import os
import unittest

import  modules.documentation as documentation
from    modules.documentation import export_docs
from    modules import logging
from    test import t_config

class TestDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally
        logging.Log.test_mode = True 


    @classmethod
    def tearDownClass(cls):
        pass

    def test_generate_txt_file(self): 
        # Clear out the old file 
        glob_list = glob('test/test_data/**', recursive=True)
        file_exists = t_config.modules.Documentation.file_export in glob_list
        if file_exists:
            os.remove(t_config.modules.Documentation.file_export)
        # Create a new file
        export_docs.toTxt(t_config.modules.Documentation.file_export)

        glob_list = glob('test/test_data/**', recursive=True)
        file_exists = t_config.modules.Documentation.file_export in glob_list
        self.assertTrue(file_exists, 'Doc exporter did not create flat file properly')

    # def test_read_lines(self):
    #     self.assertEqual(len(self.docs.file_lines), 0, 'file_lines should be empty')
    #     self.docs.readLines()
    #     # Check that the test file got read into the list
    #     numb_files = len(self.docs.file_paths)
    #     self.docs.readLines()
    #     self.assertEqual(len(self.docs.file_lines), numb_files, 'Entries in file_lines does not match the number of files')
