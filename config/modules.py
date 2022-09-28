class Documentation:
    docs_ext_list = ['py', 'html', 'txt', 'sh', 'sql', 'js', 'css', 'md', 'wsgi', 'yml']
    docs_folder_list = ['config', 'database', 'modules', 'test'] 

class Logging:
    # Set what level of logging you want. Level 2 includes 0 and 1 etc. 
    #   0 = Fatal   1 = Error   2 = Warn    3 = Info    4 = Debug   5 = Verbose
    log_terminal_level = 4
    log_database_level = 4
    log_flatfile_level = 4
    # Location of gro.log and any other log flat files
    log_dir  = "logs"
    log_file = 'grow.log'

