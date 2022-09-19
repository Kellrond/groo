import  datetime as dt
import  os

import  config 

class Log():
    ''' Handles logging throughout the app
    '''

    log_files = ['groo.log']

    def __init__(self) -> None:
        self.config = config.logging 
        
    @classmethod
    def from_test_conf(cls, config):
        ''' Instantiates a class using the test configuration passed in. '''
        temp_class = cls()
        temp_class.config = config
        return temp_class


    def fatal(self, txt: str, py) -> None:
        ''' Log level: 0'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 0,
            'name': 'FATAL',
            'source': py,
            'body': txt,
        }
        self.consoleLog(log)
        self.fileLog(log)
        

    def error(self, txt: str, py) -> None:
        ''' Log level: 1'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 1,
            'name': 'ERROR',
            'source': py,
            'body': txt,
        }
        self.consoleLog(log)
        self.fileLog(log)

    def warn(self, txt: str, py) -> None:
        ''' Log level: 2'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 2,
            'name': 'WARN',
            'source': py,
            'body': txt,
        }
        self.consoleLog(log)
        self.fileLog(log)

    def info(self, txt: str, py) -> None:
        ''' Log level: 3'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 3,
            'name': 'INFO',
            'source': py,
            'body': txt,
        }
        self.consoleLog(log)
        self.fileLog(log)

    def debug(self, txt: str, py) -> None:
        ''' Log level: 4'''
        log = {
            'timestamp': dt.datetime.now(),
            'level': 4,
            'name': 'DEBUG',
            'source': py,
            'body': txt,
        }
        self.consoleLog(log)
        self.fileLog(log)

    # Log file control
    def init_logs(self) -> None:
        ''' Check if the log files exist and create if they don't exist '''
        # Appending will create a file if there is none
        for file in self.log_files:
            with open(f'{self.config.log_dir}/{file}', 'w'):
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
                print(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('source')}\t{line}")
 
    def fileLog(self, log: dict): 
        ''' Writes the log to flat file '''
        if log.get('level') <= self.config.flatfile_level:
            with open(f'{self.config.log_dir}/groo.log', 'a') as file:
                log_lines = log.get('body','').split('\n')
                for line in log_lines: 
                    file.write(f"{log.get('timestamp')}\t{log.get('name')}\t{log.get('source')}\t{line}\n")