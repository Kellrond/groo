from    datetime        import datetime as dt
from    glob            import glob
from    sqlalchemy.dialects.postgresql import insert

from    database        import db
from    database.__schema__ import Apache_access, Apache_error
from    www.config      import path

class ApacheErrors:
    def __init__(self) -> None:
        self.error_path = path.error_path
    
    def processOldLogs(self):
        globList = glob(path.error_history + '*')
        for file_path in globList:
            with open(file_path, 'r') as file:
                errorList = file.readlines()
                cleanList = []
                for row in errorList:
                    row = self.parseFieldFromBrackets(row)
                    row = self.transformRows(row)
                    cleanList.append(row)
            joinedList = self.joinErrorRows(cleanList)
            self.loadToDatabase(joinedList)

    def readErrorLogToDatabase(self):
        with open(self.error_path, 'r') as file:
            errorList = file.readlines()
            cleanList = []
            for row in errorList:
                row = self.parseFieldFromBrackets(row)
                row = self.transformRows(row)
                cleanList.append(row)
        joinedList = self.joinErrorRows(cleanList)
        self.loadToDatabase(joinedList)
        with open(self.error_path, 'w') as file:
            pass
            
                
    def parseFieldFromBrackets(self, row) -> list:
        row = row.replace('] [', ';|;', 3)[1:]
        row = row.replace('] ', ';|;', 1)
        return row.split(';|;')
        
    def transformRows(self, row = []):
        timestamp = row[0][:19] + row[0][26:]
        row[0] =    dt.strptime(timestamp, '%a %b %d %H:%M:%S %Y')
        row[2] =    row[2][4:]
        if row[3][:6] == 'remote':
            row[3] =    row[3][7:]
            portPos =   row[3].find(':')
            row.insert(4, row[3][portPos+1:])
            row[3] =    row[3][:portPos]
        return row

    def joinErrorRows(self, errList):
        prev_time = ''
        prev_pid = ''
        objTemp = {
            'error_time': dt.now(),
            'error_type': '',
            'pid': '',
            'ip': '',
            'port': '',
            'error': ''
        }

        errorDict = objTemp
        returnList = []
        for row in errList:
            if row[0] == prev_time and row[2] == prev_pid:
                errorDict['error'] += row[5]
            else:
                if errorDict['error'] != '':
                    returnList.append(errorDict)
                errorDict = {
            'error_time': dt.now(),
            'error_type': '',
            'pid': '',
            'ip': '',
            'port': '',
            'error': ''
        } 
                prev_time = row[0]
                prev_pid =  row[2]
                errorDict['error_time'] = row[0]
                errorDict['error_type'] = row[1]
                errorDict['pid'] = row[2]
                if len(row) != 6:
                    errorDict['ip'] = '127.0.0.1'
                    errorDict['port'] = ''
                    errorDict['error'] = row[3]
                else :
                    errorDict['ip'] = row[3]
                    errorDict['port'] = row[4]
                    errorDict['error'] = row[5]
        return returnList

    def loadToDatabase(self, errorDict):
        for row in errorDict:
            try:
                insert_sql = insert(Apache_error).values(
                    error_time = row.get('error_time'),
                    error_type = row.get('error_type'),
                    pid = row.get('pid'),
                    ip = row.get('ip'),
                    port = row.get('port'),
                    error = row.get('error') 
                )
                do_insert = insert_sql.on_conflict_do_nothing(constraint="apache_error_pkey")
                db.session.execute(do_insert)
                db.session.commit()

            except Exception as e:
                print(e)


class ApacheAccess:
    def __init__(self) -> None:
        self.error_path = path.error_path
    
    def processOldLogs(self) -> None:
        globList = glob(path.access_history + '*')
        for file_path in globList:
            with open(file_path, 'r') as file:
                accessList = file.readlines()
                cleanList = []
                for row in accessList:
                    row = self.parseFieldsFromString(row)
                    cleanList.append(row)
            self.loadToDatabase(cleanList)

    def readErrorLogToDatabase(self):
        with open(path.access_path, 'r') as file:
            accessList = file.readlines()
            cleanList = []
            for row in accessList:
                row = self.parseFieldsFromString(row)
                cleanList.append(row)
        self.loadToDatabase(cleanList)
        with open(path.access_path, 'w') as file:
            pass
                
    def parseFieldsFromString(self, row) -> list:
        pos = row.find('-')
        ip =  row[:pos-1]

        pos = row.find('[')
        row = row[pos+1:]
        
        pos =       row.find(']')
        timestamp = dt.strptime(row[:pos], '%d/%b/%Y:%H:%M:%S %z')

        pos = row.find('"')
        row = row[pos+1:]

        pos =    row.find(' ')
        method = row[:pos]
        row = row[pos+1:]

        pos = row.find(' ')
        url = row[:pos]
        row = row[pos+1:]

        pos = row.find(' ')
        row = row[pos+1:]

        pos = row.find(' ')
        response = row[:pos]
        row = row[pos+1:]     

        pos = row.find(' ')
        size = row[:pos]

        pos = row.find('"')
        row = row[pos+1:]     

        pos = row.find('"')
        referrer = row[:pos]
        row = row[pos+3:]    

        pos = row.find('"')
        row = row[:pos]

        if len(row) > 30:
            pos = row.find(' ')
            product = row[:pos]
            row = row[pos+2:] 

            pos = row.find(')')
            system_info = row[:pos]
            row = row[pos+2:]         

            pos = row.find(')')
            platform = row[:pos+1]
            row = row[pos+2:]  
            
            extensions = row.strip()
        else:
            pos = row.find('"')
            product = row
            system_info = ''
            platform = ''
            extensions = ''

        return [ip, timestamp, method, url, response, size, referrer, product, system_info, platform, extensions]

    def loadToDatabase(self, accessList):
        for row in accessList:
            try:
                insert_sql = insert(Apache_access).values(
                    ip = row[0], 
                    timestamp = row[1],
                    method = row[2], 
                    url = row[3], 
                    response = row[4], 
                    size = row[5],
                    referrer = row[6], 
                    mozilla = row[7], 
                    system_info = row[8], 
                    platform = row[9],
                    extensions = row[10],
                )
                do_insert = insert_sql.on_conflict_do_nothing(constraint="apache_access_pkey")
                db.session.execute(do_insert)
                db.session.commit()

            except Exception as e:
                print(e)

