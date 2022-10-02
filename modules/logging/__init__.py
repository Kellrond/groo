import  config
# External dependancies
import  datetime as dt
from    functools import wraps
from    glob import glob
from    time import perf_counter
import  os, psycopg2

def generatePerformanceExecNumber() -> int:
    ''' By creating a generator function we can generate a chain of executions in the performance log and 
        get a form of stack trace out of it. 
    '''
    i = -1
    while True:
        i += 1
        yield str(i)

# The generator object should be in the files scope so that all the log instances share the generator
perf_exec_start = generatePerformanceExecNumber()
perf_exec_end   = generatePerformanceExecNumber()

class Log():
    ''' Handles logging throughout the app. There are 6 levels of logging currently

            - 0: Fatal
            - 1: Error
            - 2: Warn
            - 3: Info
            - 4: Debug
            - 5: Verbose

        There is a database connection in the dbLog method. This is here because the database will
        create logs when writing and depending on configuration it would be possible to end up in 
        an endless loop. Python will throw a maximum recursion error before you fill up the storage
        so it's not going to destroy your machine, but should be left. 

        Usage: 
            `log = logging.Log(__name__)`
    '''

    log_files_exist = False
    # While testing we want to silence logging globally except when testing logging 
    test_mode = False

    def __init__(self, src_name: str) -> None:
        self.src_name = src_name
        self.config = config.modules.Logging
        self.db_config = config.db.GrowDb

        if not Log.log_files_exist:
            Log.log_files_exist = (self.__check_for_log_folder() and self.__check_for_logs())
            if not Log.log_files_exist:
                self.init_logs()
                Log.log_files_exist = True
        
    @classmethod
    def from_test_conf(cls, config, db_config, src_name:str):
        ''' Instantiates a class using the test configuration passed in. Normal or test instances
            of Log will check for their files at instantiation. 

            
            Params: 
                - config: a config file loaded from the test/config dir or otherwise
                - db_config: since the logger writes to the db and the db logs, it's better to pass
                  in a connection config
                - src_name: __name__. Use that every time. 
        '''
        test_class = cls(src_name)
        test_class.config = config
        test_class.db_config = db_config
        # Set logger to testing to mute all output 
        cls.test_mode = True
        
        # Make sure the directory structure exists
        glob_list = glob('./test/**/', recursive=True)
        if './test/test_data/logs/' not in glob_list:
            os.mkdir('test/test_data/logs')
        # Make sure the test log file is there
        with open(f'{config.log_dir}/{config.log_file}', 'a'):
            pass 
        with open(f'{config.log_dir}/{config.performance_file}', 'a'):
            pass 

        return test_class

    def fatal(self, txt: str) -> None:
        ''' Log level: 0'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 0,
            'name': 'FATAL',
            'module': self.src_name,
            'log': str(txt),
        } 
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)
        
    def error(self, txt: str) -> None:
        ''' Log level: 1'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 1,
            'name': 'ERROR',
            'module': self.src_name,
            'log': str(txt),
        }
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)

    def warn(self, txt: str) -> None:
        ''' Log level: 2'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 2,
            'name': 'WARN',
            'module': self.src_name,
            'log': str(txt),
        }
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)

    def info(self, txt: str) -> None:
        ''' Log level: 3'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 3,
            'name': 'INFO',
            'module': self.src_name,
            'log': str(txt),
        }
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)

    def debug(self, txt: str) -> None:
        ''' Log level: 4'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 4,
            'name': 'DEBUG',
            'module': self.src_name,
            'log': str(txt),
        }
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)

    def verbose(self, txt: str) -> None:
        ''' Log level: 5 '''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 5,
            'name': 'VERBOSE',
            'module': self.src_name,
            'log': str(txt),
        }
        if self.test_mode == False:
            self.__log_console_write(log)
            self.__log_db_write(log)
            self.__log_file_write(log)   
    
    def performance(self, func):
        ''' This function is a decorator. At some point it might be worth splitting it into it's own class 
            that way we can include logger performance. 

            Usage:
                `@log.performance`
        '''
        def performance_wrapper(*args, **kwargs):
            ''' Performance testing is an expensive operation and can slow the operation of the system.
                However the knowledge you can gleam from this is worth the expense. But it doesn't need
                to run all the time.  
            ''' 
            if not self.config.test_performance:
                return func(*args, **kwargs)

            is_minimal_log = kwargs.get('minimal', False)
            if self.config.minimal_test and not is_minimal_log:
                return func(*args, **kwargs)

            # Setup
            start_time = perf_counter()
            start_id   = next(perf_exec_start)
            # Function
            result = func(*args, **kwargs)
            # Wrap up
            end_time = perf_counter()
            end_id   = next(perf_exec_end)
            duration = end_time - start_time
            log = {
                'start_id': start_id,
                'end_id': end_id,
                'timestamp': dt.datetime.now(),
                'module': self.src_name,
                'name': func.__name__,
                'duration': duration,
                } 
            
            self.__perf_db_write(log)
            self.__perf_file_write(log)
            return result
        return performance_wrapper


    def __check_for_log_folder(self) -> bool:
        folder_list = glob('**/', recursive=True)
        return (f'{self.config.log_dir}/' in folder_list)

    def __check_for_logs(self) -> bool:
        file_list = glob(f'{self.config.log_dir}/**/*.*', recursive=True)
        x = [ 1 for file in file_list if file == self.config.log_file ]
        return sum(x) > 0

    def init_logs(self) -> None:
        ''' Ensure that the required folders and files are in place to start logging '''
        if self.__check_for_log_folder() == False:
            os.makedirs(self.config.log_dir)
        log_list = [self.config.log_file, self.config.performance_file]
        for log in log_list:
            with open(f'{self.config.log_dir}/{log}', 'a'):
                pass         

    def delete_dot_logs(self) -> None:
        ''' Remove all .log files created '''
        os.remove(f'{self.config.log_dir}/{self.config.log_file}')
        os.remove(f'{self.config.log_dir}/{self.config.performance_file}')

    # Output logs
    def __log_console_write(self, log: dict):
        ''' Outputs the log information to terminal. 

            Params:
                - log: a dictionary created from the methods above
        '''
        if log.get('level') <= self.config.log_terminal_level:
            log_lines = log.get('log','').split('\n')
            for line in log_lines:
                if line != '': 
                    print(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('module')}\t{line}")
 
    def __log_file_write(self, log: dict): 
        ''' Writes the log to flat file 
        
            Params:
                - log: a dictionary created from the methods above
        '''
        if log.get('level') <= self.config.log_flatfile_level:
            with open(f'{self.config.log_dir}/{self.config.log_file}', 'a') as file:
                log_lines = log.get('log','').split('\n')
                for line in log_lines: 
                    file.write(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('module')}\t{line}\n")

    def __log_db_write(self, log: dict): 
        ''' Writes the log to the database. This has a basic pattern to create the db connection and
            should be left this way. The database creates logs and can end up in a recursive loop.

            Params:
                - log: a dictionary created from the methods above
        '''
        if log.get('level') <= self.config.log_database_level:
            # Log must be manually input to avoid a feedback loop of db adds triggering logs which get added to db
            db_conn = psycopg2.connect(
                    host=self.db_config.host,
                    user=self.db_config.user,
                    password=self.db_config.password,
                    port=self.db_config.port,
                    dbname=self.db_config.dbname
                )

            tempLog = { k:v for k, v in log.items() if k != 'name'}

            columns = ", ".join(tempLog.keys())
            placeholders = ", ".join([ '%s' for x in tempLog.values() ])  
            values = tuple(tempLog.values())
            sql = f'''
                INSERT INTO logs ({ columns })
                VALUES ({ placeholders })
            '''
            try:
                with db_conn.cursor() as cursor:
                    cursor.execute(sql, values)   
                    db_conn.commit()    
                db_conn.close()
            except Exception as e:
                db_conn.close()
                raise e

    def __perf_db_write(self, log:dict):
        if self.config.performance_to_db:
            # Log must be manually input to avoid a feedback loop of db adds triggering logs which get added to db
            db_conn = psycopg2.connect(
                    host=self.db_config.host,
                    user=self.db_config.user,
                    password=self.db_config.password,
                    port=self.db_config.port,
                    dbname=self.db_config.dbname
                )

            tempLog = { k:v for k, v in log.items() if k != 'name'}

            columns = ", ".join(tempLog.keys())
            placeholders = ", ".join([ '%s' for x in tempLog.values() ])  
            values = tuple(tempLog.values())
            sql = f'''
                INSERT INTO performance_logs ({ columns })
                VALUES ({ placeholders })
            '''
            try:
                with db_conn.cursor() as cursor:
                    cursor.execute(sql, values)   
                    db_conn.commit()    
                db_conn.close()
            except Exception as e:
                db_conn.close()
                raise e

    def __perf_file_write(self, log:dict):
        if self.config.performance_to_file:
            line = f"{log.get('timestamp')}\t{log.get('start_id')}\t{log.get('end_id')}\t{log.get('module')}\t{log.get('name')}\t{log.get('duration'):10.10f}\n"
            with open(f'{self.config.log_dir}/{self.config.performance_file}', 'a') as file:
                file.write(line)


