from modules.logging import apache_etl

def processLogFiles():
    access_logs = apache_etl.ApacheAccess()
    access_logs.readErrorLogToDatabase()
    error_logs = apache_etl.ApacheErrors()
    error_logs.readErrorLogToDatabase()

if __name__ == '__main__':
    processLogFiles()