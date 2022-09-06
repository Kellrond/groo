from www import config
from database import __schema__ as schema, db, nextUniqueId, returnDictFromDboObject

# Paginate functions

def paginateActivityLog(start_date, end_date, ip, page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    if ip == '':
        ip = schema.Activity_logs.ip    
    query = schema.Activity_logs.query.filter(
            schema.Activity_logs.timestamp >= start_date,
            schema.Activity_logs.timestamp <= end_date,
            schema.Activity_logs.ip        == ip
        ).order_by(
            schema.Activity_logs.timestamp.desc()
        ).limit(config.max_table_length).offset(page * config.max_table_length).all()
    # Use the same qury without the sorting to get the count quickly
    count = schema.Activity_logs.query.filter(
            schema.Activity_logs.timestamp >= start_date,
            schema.Activity_logs.timestamp <= end_date,
            schema.Activity_logs.ip        == ip
        ).count()

    discrepancy_list = []
    for row in query:
        discrepancy_list.append(returnDictFromDboObject(row))
    return { 'count': count,'results': discrepancy_list }

def paginateApacheAccess(start_date, end_date, ip, page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    if ip == '':
        ip = schema.Apache_access.ip
    query = schema.Apache_access.query.filter(
            schema.Apache_access.timestamp >= start_date,
            schema.Apache_access.timestamp <= end_date,
            schema.Apache_access.response  != '304',
            schema.Apache_access.ip        == ip
        ).order_by(
            schema.Apache_access.timestamp.desc()
        ).limit(config.max_table_length).offset(page * config.max_table_length).all()
    # Use the same qury without the sorting to get the count quickly
    count = schema.Apache_access.query.filter(
            schema.Apache_access.timestamp >= start_date,
            schema.Apache_access.timestamp <= end_date,
            schema.Apache_access.response  != '304',
            schema.Apache_access.ip        == ip
        ).count()

    discrepancy_list = []
    for row in query:
        discrepancy_list.append(returnDictFromDboObject(row))
    return { 'count': count,'results': discrepancy_list }

def paginateApacheError(start_date, end_date, ip, page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    if ip == '':
        ip = schema.Apache_error.ip
    query = schema.Apache_error.query.filter(
            schema.Apache_error.error_time >= start_date,
            schema.Apache_error.error_time <= end_date,
            schema.Apache_error.ip         == ip
        ).order_by(
            schema.Apache_error.error_time.desc()
        ).limit(config.max_table_length).offset(page * config.max_table_length).all()
    # Use the same qury without the sorting to get the count quickly
    count = schema.Apache_error.query.filter(
            schema.Apache_error.error_time >= start_date,
            schema.Apache_error.error_time <= end_date,
            schema.Apache_error.ip         == ip
        ).count()

    discrepancy_list = []
    for row in query:
        discrepancy_list.append(returnDictFromDboObject(row))
    return { 'count': count,'results': discrepancy_list }

def paginateErrorAlert(start_date, end_date, ip, page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    if ip == '':
        acs_ip = 'acs.ip' 
        err_ip = 'err.ip'
        act_ip = 'act.ip'
    else:
        acs_ip = f"'{ip}'"
        err_ip = f"'{ip}'"
        act_ip = f"'{ip}'"

    sql = f'''
        SELECT acs.timestamp
            ,acs.ip
            ,acs.response || ' ' || acs.url as reference
            ,'Apache access' as log_type
        FROM apache_access acs
        WHERE acs.timestamp >= '{ start_date }'
            AND acs.timestamp <= '{ end_date }'
            AND acs.response::int >= 400
            AND acs.ip = { acs_ip}
        UNION
        SELECT err.error_time as timestamp
            ,err.ip
            ,err.error as reference
            ,'Apache error' as log_type
        FROM apache_error err
        WHERE err.error_time >= '{ start_date }'
            AND err.error_time <= '{ end_date }'
            AND err.ip = { err_ip }
        UNION
        SELECT act.timestamp
            ,act.ip
            ,act.error as reference
            ,'Activity log' as reference
        FROM activity_logs act
        WHERE act.timestamp >= '{ start_date }'
            AND act.timestamp <= '{ end_date }'
            AND act.level = 1
            AND act.ip = { act_ip }
        ORDER BY timestamp desc
        LIMIT { config.max_table_length }
        OFFSET { page * config.max_table_length };
    '''
    tempQuery = db.session.execute(sql)
    query = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        query.append(tempDict)

    # Count the rows
    sql = f'''
        SELECT COUNT(*) FROM
            (SELECT acs.timestamp
            FROM apache_access acs
            WHERE acs.timestamp >= '{ start_date }'
                AND acs.timestamp <= '{ end_date }'
                AND acs.response::int >= 400
                AND acs.ip = { acs_ip}
            UNION
            SELECT err.error_time as timestamp
            FROM apache_error err
            WHERE err.error_time >= '{ start_date }'
                AND err.error_time <= '{ end_date }'
                AND err.ip = { err_ip }
            UNION
            SELECT act.timestamp
            FROM activity_logs act
            WHERE act.timestamp >= '{ start_date }'
                AND act.timestamp <= '{ end_date }'
                AND act.level = 1
                AND act.ip = { act_ip }) sq
            '''
    count = db.session.execute(sql)

    return { 'count': count.scalar(), 'results': query}

# Return functions

def returnAnalyticsSummary(start_date, end_date, ip):
    if ip != '':
        access_ip = ip
        error_ip = ip    
        activity_ip = ip 
        acs_ip = ip
        err_ip = ip
        act_ip = ip
    else:
        access_ip = schema.Apache_access.ip
        error_ip = schema.Apache_error.ip
        activity_ip = schema.Activity_logs.ip
        acs_ip = 'acs.ip'
        err_ip = 'err.ip'
        act_ip = 'act.ip'
    
    page_views = schema.Apache_access.query.filter(
            schema.Apache_access.timestamp >= start_date,
            schema.Apache_access.timestamp <= end_date,
            schema.Apache_access.response  != '304',
            schema.Apache_access.ip == access_ip
        ).count()
    
    sql = f'''
            SELECT SUM(acs.size)
            FROM apache_access acs
            WHERE acs.timestamp >= '{ start_date }'
                AND acs.timestamp <= '{ end_date }'
                AND acs.response::int <> 304
                AND acs.ip = { acs_ip }
            '''
    bytes_sent = int(db.session.execute(sql).scalar() / 1024)

    sql = f'''
            SELECT count(*)
            FROM apache_access acs
            WHERE acs.timestamp >= '{ start_date }'
                AND acs.timestamp <= '{ end_date }'
                AND acs.response::int <> 304
                AND acs.ip = { acs_ip }
                AND acs.url = '/manifest_search'
            '''
    searches = db.session.execute(sql).scalar()

    sql = f'''
        SELECT count(*)
        FROM activity_logs act
        WHERE act.timestamp >= '{ start_date }'
            AND act.timestamp <= '{ end_date }'
            AND act.ip = { act_ip }
            AND act.activity = 'login'
        '''
    logins = db.session.execute(sql).scalar()

    sql = f'''
            SELECT count(*)
            FROM apache_access acs
            WHERE acs.timestamp >= '{ start_date }'
                AND acs.timestamp <= '{ end_date }'
                AND acs.response::int <> 304
                AND acs.ip = { acs_ip }
                AND acs.url = '/cron/backup_db?pword=distPsa1'
            '''
    backups = db.session.execute(sql).scalar()


    sql = f'''
        SELECT count(*)
        FROM activity_logs act
        WHERE act.timestamp >= '{ start_date }'
            AND act.timestamp <= '{ end_date }'
            AND act.ip = { act_ip }
            AND act.activity = 'email manifest'
            '''
    email_manifest = db.session.execute(sql).scalar()

    sql = f'''
        SELECT count(*)
        FROM activity_logs act
        WHERE act.timestamp >= '{ start_date }'
            AND act.timestamp <= '{ end_date }'
            AND act.ip = { act_ip }
            AND act.activity = 'manifest edit'
            '''
    edit_manifest = db.session.execute(sql).scalar()

    apache_error = schema.Apache_error.query.filter(
            schema.Apache_error.error_time >= start_date,
            schema.Apache_error.error_time <= end_date,
            schema.Apache_error.ip         == error_ip
        ).count()

    activity_error = schema.Activity_logs.query.filter(
            schema.Activity_logs.timestamp >= start_date,
            schema.Activity_logs.timestamp <= end_date,
            schema.Activity_logs.ip        == activity_ip
        ).count()

    results = {
        'page_views' : page_views,
        'bytes_sent' : bytes_sent,
        'searches' : searches,
        'logins' : logins,
        'backups' : backups,
        'email_manifest' : email_manifest,
        'edit_manifest' : edit_manifest,
        'apache_error': apache_error,
        'activity_error': activity_error
    }
    return results
    
# Update functions

def writeLogToDb(log_dict):
    log_entry   = schema.Activity_logs()

    log_entry.activity      = log_dict.get('activity')
    log_entry.args          = log_dict.get('args')
    log_entry.dc_id         = log_dict.get('dc_id')
    log_entry.user_id   = log_dict.get('user_id')
    log_entry.endpoint      = log_dict.get('endpoint')
    log_entry.error         = log_dict.get('error')
    log_entry.ip            = log_dict.get('ip')
    log_entry.level         = log_dict.get('level')
    log_entry.note          = log_dict.get('note')
    log_entry.py            = log_dict.get('py')
    log_entry.resource_id   = log_dict.get('resource_id')
    log_entry.timestamp     = log_dict.get('timestamp')
    
    try:
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print('Logger failed to write to DB:', e)
