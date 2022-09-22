import  config 
# External dependancies
import  datetime as dt
from    glob import glob
import  os

class Log():
    ''' Handles logging throughout the app
    '''

    log_files = ['groo.log']
    log_files_exist = False

    def __init__(self, src_name: str) -> None:
        self.src_name = src_name
        self.config = config.logging 

        if not self.log_files_exist:
            self.log_files_exist = (self.__check_for_log_folder() and self.__check_for_logs())
            if not self.log_files_exist:
                self.init_logs()
                self.log_files_exist = True
        
    @classmethod
    def from_test_conf(cls, config, src_name:str):
        ''' Instantiates a class using the test configuration passed in. 
            
            Params: 
                - config: a config file loaded from the test/config dir or otherise
                - src_name: __name__. Use that every time. 
        '''
        temp_class = cls(src_name)
        temp_class.config = config
        return temp_class


    def fatal(self, txt: str) -> None:
        ''' Log level: 0'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 0,
            'name': 'FATAL',
            'source': self.src_name,
            'body': str(txt),
        }
        self.consoleLog(log)
        self.fileLog(log)
        

    def error(self, txt: str) -> None:
        ''' Log level: 1'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 1,
            'name': 'ERROR',
            'source': self.src_name,
            'body': str(txt),
        }
        self.consoleLog(log)
        self.fileLog(log)

    def warn(self, txt: str) -> None:
        ''' Log level: 2'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 2,
            'name': 'WARN',
            'source': self.src_name,
            'body': str(txt),
        }
        self.consoleLog(log)
        self.fileLog(log)

    def info(self, txt: str) -> None:
        ''' Log level: 3'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 3,
            'name': 'INFO',
            'source': self.src_name,
            'body': str(txt),
        }
        self.consoleLog(log)
        self.fileLog(log)

    def debug(self, txt: str) -> None:
        ''' Log level: 4'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 4,
            'name': 'DEBUG',
            'source': self.src_name,
            'body': str(txt),
        }
        self.consoleLog(log)
        self.fileLog(log)

    def __check_for_log_folder(self) -> bool:
        folder_list = glob('**/', recursive=True)
        return (f'{self.config.log_dir}/' in folder_list)

    def __check_for_logs(self) -> bool:
        file_list = glob(f'{self.config.log_dir}/**/*.*', recursive=True)
        x = [ 1 for file in file_list if file in self.log_files]
        return sum(x) > 0

    def init_logs(self) -> None:
        ''' Ensure that the required folders and files are in place to start logging '''
        if self.__check_for_log_folder() == False:
            os.makedirs(self.config.log_dir)
        # Appending will create a file if there is none
        for file in self.log_files:
            with open(f'{self.config.log_dir}/{file}', 'a'):
                pass 
        
    def delete_dot_logs(self) -> None:
        ''' Remove all .log files created '''
        for file_path in self.log_files:
            os.remove(f'{self.config.log_dir}/{file_path}')

    # Output logs
    def consoleLog(self, log: dict):
        ''' Outputs the log information to terminal. '''
        if log.get('level') <= self.config.terminal_level:
            log_lines = log.get('body','').split('\n')
            for line in log_lines:
                if line != '': 
                    print(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('source')}\t{line}")
 
    def fileLog(self, log: dict): 
        ''' Writes the log to flat file '''
        if log.get('level') <= self.config.flatfile_level:
            with open(f'{self.config.log_dir}/groo.log', 'a') as file:
                log_lines = log.get('body','').split('\n')
                for line in log_lines: 
                    file.write(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('source')}\t{line}\n")