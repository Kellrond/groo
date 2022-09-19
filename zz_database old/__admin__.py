# import  glob, os, subprocess, time
# from    time      import strftime

# from    www       import config
# from    database  import db
# from    modules   import logging

# logger = logging.Log(py=__name__)


# ###############################################################################
# # These is the DB backup and restore functions   
# # They primarily use CLI with pg_dump and pg_restore so they can be done manually
# # from the shell. Restore is called if you run this file from shell 
# #
# # Backup is called via a crontab nightly 
# ################################################################################ 
 
# def deleteOldBackups(days_to_keep = 2):
#     seconds_in_day = 60 * 60 * 24
#     x_days_ago = time.time() - (seconds_in_day * days_to_keep)
#     # Delete old backup files first. 
#     glob_list = glob.glob(config.path.backup_dir + '*' + '.pgdump')
#     for file in glob_list:
#         file_info = os.stat(file)
#         if file_info.st_ctime < x_days_ago:
#             msg_txt = f"Deleting old log file: {file}"
#     logger.write(activity='delete db backup', resource_id=file, note=msg_txt)
#     os.unlink(file)

# def backupDb():
#     the_time = str(strftime("%Y-%m-%d-%H-%M")) 
#     file_name = 'database_' + the_time + ".sql.pgdump"
#     command = config.pg_dump_string % (config.Config.SQLALCHEMY_DATABASE_URI,  config.path.backup_dir + file_name)
#     try:
#         subprocess.call(command,shell = True)
#         msg_txt = f"Backed up database success"
#         logger.write(activity='backup db', resource_id=file_name, note=msg_txt)
#         return True
#     except Exception as e:
#         logger.write(activity='backup db', resource_id=file_name, error=e)
#         return False

# def restoreDb():
#     newestFile = returnMostRecentDbBackupPath()
#     command = config.pg_restore_string % (config.Config.SQLALCHEMY_DATABASE_URI, newestFile)
#     try:
#         subprocess.call(command,shell = True)
#         msg_txt = f"Restored database from: {newestFile}"
#         logger.write(activity='restore db', resource_id=newestFile, note=msg_txt)
#         return True
#     except Exception as e:
#         logger.write(activity='restore db', resource_id=newestFile, error=e)
#         return False

# def updateDbFromScript() -> None:
#     try:
#       with open(config.path.update_sql, 'r') as sql:
#         db.session.commit()
#         db.session.execute(sql.read())
#         db.session.commit()

#         with open(config.path.update_sql_log, 'a') as sql_log:
#           sql_log.writelines(sql.readlines())

#       msg_txt = f"DB updated from SQL script"
#       logger.write(activity='update db', resource_id='update.sql', note=msg_txt)
#       return True
#     except Exception as e:
#       db.session.commit()
#       logger.write(activity='restore db', resource_id='update.sql', error=e)
#       return False       
   
# def returnMostRecentDbBackupPath():
#     newestFileTime = 0
#     newestFile = ""
#     glob_list = glob.glob(config.path.backup_dir + 'database*' + '.pgdump')
#     for file in glob_list:
#         file_info = os.stat(file)
#         if file_info.st_ctime > newestFileTime:
#             newestFileTime = file_info.st_ctime
#             newestFile = file 
#     return newestFile

# ###############################################################################
# # These is the DB backup and restore functions   
# # They primarily use CLI with pg_dump and pg_restore so they can be done manually
# # from the shell. Restore is called if you run this file from shell 
# #
# # Backup is called via a crontab nightly 
# ################################################################################ 
 
# def deleteOldBackups(days_to_keep = 2):
#     seconds_in_day = 60 * 60 * 24
#     x_days_ago = time.time() - (seconds_in_day * days_to_keep)
#     # Delete old backup files first. 
#     glob_list = glob.glob(config.path.backup_dir + 'database*' + '.pgdump')
#     for file in glob_list:
#         file_info = os.stat(file)
#         if file_info.st_ctime < x_days_ago:
#             msg_txt = f"Deleting old log file: {file}"
#     logger.write(activity='delete db backup', resource_id=file, note=msg_txt)
#     os.unlink(file)

# def backupDb():
#     thetime = str(strftime("%Y-%m-%d-%H-%M")) 
#     file_name = 'database_' + thetime + ".sql.pgdump"
#     command = config.pg_dump_string % (config.Config.SQLALCHEMY_DATABASE_URI,  config.path.backup_dir + file_name)
#     try:
#         subprocess.call(command,shell = True)
#         msg_txt = f"Backed up database success"
#         logger.write(activity='backup db', resource_id=file_name, note=msg_txt)
#         return True
#     except Exception as e:
#         logger.write(activity='backup db', resource_id=file_name, error=e)
#         return False

# def restoreDb():
#     newestFile = returnMostRecentDbBackupPath()
#     command = config.pg_restore_string % (config.Config.SQLALCHEMY_DATABASE_URI, newestFile)
#     try:
#         subprocess.call(command,shell = True)
#         msg_txt = f"Restored database from: {newestFile}"
#         logger.write(activity='restore db', resource_id=newestFile, note=msg_txt)
#         return True
#     except Exception as e:
#         logger.write(activity='restore db', resource_id=newestFile, error=e)
#         return False

# def updateDbFromScript() -> None:
#     try:
#       with open(config.path.update_sql, 'r') as sql:
#         db.session.commit()
#         db.session.execute(sql.read())
#         db.session.commit()

#         with open(config.path.update_sql_log, 'a') as sql_log:
#           sql_log.writelines(sql.readlines())

#       msg_txt = f"DB updated from SQL script"
#       logger.write(activity='update db', resource_id='update.sql', note=msg_txt)
#       return True
#     except Exception as e:
#       db.session.commit()
#       logger.write(activity='restore db', resource_id='update.sql', error=e)
#       return False       
   
# def returnMostRecentDbBackupPath():
#     newestFileTime = 0
#     newestFile = ""
#     glob_list = glob.glob(config.path.backup_dir + 'database*' + '.pgdump')
#     for file in glob_list:
#         file_info = os.stat(file)
#         if file_info.st_ctime > newestFileTime:
#             newestFileTime = file_info.st_ctime
#             newestFile = file 
#     return newestFile

# def returnDbStatsPagination(page=1) -> dict:
#     page = int(page) - 1 # adjust for pagination offest to start from 1

#     sql = f'''
#         SELECT
#             schema_name,
#             relname as table_name,
#             pg_size_pretty(table_size) AS size,
#             table_size as bytes
#         FROM (
#             SELECT
#                 pg_catalog.pg_namespace.nspname           AS schema_name,
#                 relname,
#                 pg_relation_size(pg_catalog.pg_class.oid) AS table_size

#             FROM pg_catalog.pg_class
#                 JOIN pg_catalog.pg_namespace ON relnamespace = pg_catalog.pg_namespace.oid
#             ) t
#         WHERE schema_name NOT LIKE 'pg_%'
#         ORDER BY schema_name DESC, table_size DESC
#         LIMIT { config.max_table_length }
#         OFFSET { page * config.max_table_length };
#     '''
#     tempQuery = db.session.execute(sql)
#     query = []
#     keys = [x for x in tempQuery.keys()]
#     for row in tempQuery:
#         tempDict = {}
#         for i in range(len(keys)):
#             tempDict[keys[i]] = row[i]
#         query.append(tempDict)

#     # Count the rows
#     sql = f'''
#             SELECT
#                 count(*)
#             FROM (
#                 SELECT
#                     pg_catalog.pg_namespace.nspname           AS schema_name,
#                     relname,
#                     pg_relation_size(pg_catalog.pg_class.oid) AS table_size
#                 FROM pg_catalog.pg_class
#                     JOIN pg_catalog.pg_namespace ON relnamespace = pg_catalog.pg_namespace.oid
#                 ) t
#             WHERE schema_name NOT LIKE 'pg_%';
#             '''
#     count = db.session.execute(sql)

#     return { 'count': count.scalar(), 'results': query}



# def returnQueryPagination(sql, page=1) -> dict:
#     page = int(page) - 1 # adjust for pagination offest to start from 1

#     # Prevent bad sql queries
#     if sql[0:6] != 'SELECT':
#         return { 'count': 0, 'results': 'Query must start with SELECT'}
#     if sql.find(';') > -1:
#         sql = sql[0:sql.find(';')]

#     sql_page = sql + f'''
#         LIMIT { config.max_table_length }
#         OFFSET { page * config.max_table_length };
#     '''
#     try:
#         tempQuery = db.session.execute(sql_page)
#     except Exception as e:
#         error = e
#         tempQuery = None

#     query = []
#     if tempQuery:
#         keys = [x for x in tempQuery.keys()]
#         for row in tempQuery:
#             tempDict = {}
#             for i in range(len(keys)):
#                 tempDict[keys[i]] = row[i]
#             query.append(tempDict)

#         # Count the rows
#         count = len([ x for x in db.session.execute(sql) ])
#     else: 
#         count = 0
#         query = error

#     return { 'count': count, 'results': query}