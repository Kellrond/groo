import  datetime as dt
from    flask    import session, request

from    www.config      import logging_level
from    database.log_db import writeLogToDb
from    modules.logging import apache_etl


class Log():
    ''' Captains Log: Stardate 41153.7 
        The standard logger boiler plate looks like this 
- Head looks like this 
`from    www.modules               import logging`
`logger = logging.Log(py=__name__)`

- The action you are trying and logging.  If no try needed great. Just use the logger.write()
`try:
    db.session.commit()
    msg_txt = f'{log_activity.capitalize()}d and more information here'
    logger.write(activity=log_activity, resource_id=resource_id if any, note=msg_txt)
    return {'success': True, 'msg': msg_txt, 'additional_return_data': data }
except Exception as e:
    db.session.rollback()
    logger.write(activity= log_activity, resource_id=manifest_id, error=e)
    return {'success': False, 'msg': str(e), 'additional_return_data': data}`

    '''
    def __init__(self, py) -> None:
        self.logging_level  = logging_level 
        self.py = py

    def write(self, activity=None, error=None, level = 2, note = None, resource_id=None) -> None:
        ''' Write a log, activity is the action taking place, 
            Currently only two levels: 1 and 2. 1 being an error and 2 being a message 
                - Eventually this may mirror more standard log levels if more logging is helpful
        '''
        argDict     = request.args.to_dict()      
        endpoint    = request.endpoint
        ip          = request.remote_addr

        log_dict = {
            'activity'      : activity,
            'args'          : '\n'.join([f'{k}: {v}' for k,v in argDict.items()]),
            'user_id'       : session.get('user_id','visitor'),
            'endpoint'      : endpoint,
            'error'         : str(error) if error else None,
            'ip'            : ip,
            'level'         : level if error == None or level != 2 else 1,
            'note'          : note,
            'py'            : self.py,
            'resource_id'   : resource_id,
            'timestamp'     : dt.datetime.now(),
        }
        # This places errors in the apache log as well
        if error:
            print(error)

        writeLogToDb(log_dict)

