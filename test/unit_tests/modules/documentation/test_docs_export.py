from    glob import glob
import  os
import  unittest
# External
from    psycopg2.errors import UndefinedTable
# Local
from    database import Db
import  modules.documentation as documentation
from    modules.documentation import export_docs, py_classes, py_functions, py_meta, py_parser
from    modules import logging
from    test import t_config

class TestDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Turn off logging globally

        cls.db = Db.from_test_conf(t_config.db.GrowDb)

        logging.Log.test_mode = True 
        py_meta.Docs.file_lines  = []
        py_meta.Docs.file_paths  = []
        py_meta.Docs.folder_list = []
        py_parser.PyParser.folders = []
        py_parser.PyParser.files   = [] 
        py_parser.PyParser.classes = []
        py_parser.PyParser.functions = []
        py_parser.PyParser.file_docs = []
        py_parser.PyParser.imports = []
        py_parser.PyParser.todo = []

        cls.docs = documentation.Docs.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc = py_meta.PyMeta.from_test_conf(t_config.modules.Documentation)
        cls.classDoc = py_classes.PyClasses.from_test_conf(t_config.modules.Documentation)
        cls.funcDoc = py_functions.PyFunctions.from_test_conf(t_config.modules.Documentation)
        cls.parser = py_parser.PyParser.from_test_conf(t_config.modules.Documentation)
        cls.fileDoc.readLines()

        for file in cls.docs.file_lines:
            for line in file.get('lines'):
                line['flags'] = []

        cls.fileDoc.processPyFileFlags()
        cls.classDoc.processPyClassFlags()
        cls.funcDoc.processPyFunctionFlags()
        cls.parser.parsePython()
        export_docs.toTxt(t_config.modules.Documentation.export_file_path)
        export_docs.toDb(cls.db)

    @classmethod
    def tearDownClass(cls):
        # Clear out the old file 
        glob_list = glob('test/test_data/**', recursive=True)
        file_exists = t_config.modules.Documentation.export_file_path in glob_list
        if file_exists:
            os.remove(t_config.modules.Documentation.export_file_path)

        del cls.db

    def test_generate_docs_txt_file(self): 
        glob_list = glob('test/test_data/**', recursive=True)
        file_exists = t_config.modules.Documentation.export_file_path in glob_list
        self.assertTrue(file_exists, 'Doc exporter did not create flat file properly')

    def test_read_docs_txt_file(self):
        with open(t_config.modules.Documentation.export_file_path, 'r') as file:
            content = file.read()

        self.assertGreater(content.find('config.modules'), -1, 'doc file export did not write import correctly')
        self.assertGreater(content.find('Class1'), -1, 'doc file export did not write class name correctly')
        self.assertGreater(content.find('line 2 should line up with above'), -1, 'doc file export did not write documentation correctly')
        self.assertGreater(content.find('param1:dict, param2=False'), -1, 'doc file export did not write parameters correctly')
        self.assertGreater(content.find('c1func2'), -1, 'doc file export did not write method name correctly')
        self.assertGreater(content.find('nestedDef1'), -1, 'doc file export did not write nested function in method correctly')
        self.assertGreater(content.find('new_line='), -1, 'doc file export did not write nested function param correctly')
        self.assertGreater(content.find('-> str'), -1, 'doc file export did not write return hint correctly')

    def test_docs_db_tables_exist(self):
        tables = ['doc_classes','doc_file_docs','doc_files','doc_folders','doc_functions','doc_imports','doc_todos']
        for table in tables:
            try:
                sql = f'SELECT * FROM { table }'
                _ = self.db.query(sql)
                self.db.close()
            except:
                self.assertTrue(False, f'Failed to find { table } in db')


    def test_read_docs_db(self):
        tables = ['doc_classes','doc_file_docs','doc_files','doc_folders','doc_functions','doc_imports','doc_todos']
        for table in tables:
            sql = f'SELECT * FROM { table }'
            _ = self.db.query(sql)
            self.assertGreater(len(_), 0, f'Failed to find { table } in db')
            self.db.close()

        sql = f"SELECT * FROM doc_classes WHERE name = 'Class1' AND superclass IS NULL AND docstring IS NOT NULL AND parameters IS NOT NULL AND line_start > 10 AND line_count >10 "
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write class correctly')
        self.db.close()

        sql = f"SELECT * FROM doc_file_docs WHERE file_id = 0 AND docs IS  NOT NULL"
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write file docs correctly')
        self.db.close()

        sql = f"SELECT * FROM doc_files WHERE file_id = 0 AND folder_id IS NOT NULL AND folder_id IS NOT NULL AND folder_id IS NOT NULL AND folder_id IS NOT NULL AND lines > 10"
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write files correctly')
        self.db.close()

        sql = f"SELECT * FROM doc_functions WHERE function_id = 0 AND parent_id IS NULL AND file_id IS NOT NULL AND class_id IS NOT NULL AND name IS NOT NULL AND parameters IS NOT NULL AND returns IS NOT NULL AND decorators IS NULL AND line_start > 10 and line_count > 1"
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write functions correctly')
        self.db.close()

        sql = f"SELECT * FROM doc_imports WHERE import_id = 0 AND file_id = 0 AND module IS NOT NULL AND object IS NOT NULL AND alias IS NOT NULL AND line_start > 10 "
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write imports correctly')
        self.db.close()

        sql = f"SELECT * FROM doc_todos WHERE todo_id = 0 AND file_id = 0 AND todo IS NOT NULL AND line_start > 10 AND line_count = 1"
        _ = self.db.query(sql)
        self.assertEqual(len(_), 1, f'Docs db failed to write todo correctly')
        self.db.close()