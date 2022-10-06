from config.modules import Documentation, Logging 

Logging.log_dir = "test/test_data/logs"

Logging.performance_to_db   = False
Logging.performance_to_file = False

Documentation.docs_folder_list = ['test/test_data/documentation']
Documentation.file_export = 'test/test_data/documentation/source_code_docs'