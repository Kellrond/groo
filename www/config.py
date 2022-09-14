from types import SimpleNamespace
from datetime import timedelta

## Developer settings
logging_level = 5

## Global display 
max_table_length = 15
posts_on_homepage = 3
toast_time_ms = 2000
max_pagination_links = 20

## Date time
date_format = '%b %d %Y'
datetime_format = '%b %d %Y %H:%M'
sql_date_format = '%Y-%m-%d'
form_date_format = '%Y-%m-%d'

## Bulletin board options
bulletin_board_posts_per_page = 7
message_preview_length = 500

## Site admin
logging_date_range = 7
homepage_content_publish_for_days = 365

## User settings
min_password_length = 6
default_password = 'password123'

##
## Permissions
##

class Permissions():
    ''' 
    The permissions are a session variable and can be used throughout the web app. 
    
    Useage:
        `session.get('permissions', 0) >= config.Permissions.dc_manager`

    Notes:
        - NOT available outside of the web app. 
        - When using session.get('permissions',0) don't forget the default 0 or there may be errors in comparisons  
    '''
    inactive = 0
    user     = 1


## 
## Development options. If you need to change the development routing please comment out the existing paths
##

pg_dump_string =""" pg_dump --dbname=%s -Z 9 -f"%s" -F c""" 
pg_restore_string =""" pg_restore --dbname=%s -c -w"%s""" 
pathDict = {
    'error_path'   : 'logs/error.log'
    ,'access_path' : 'logs/access.log'
    ,'backup_dir'  : 'backups/'
}

path = SimpleNamespace(**pathDict)

class Config(object):
    ''' This class is a Flask object which is loaded as config at app creation

    Constants:
        - PERMANENT_SESSION_LIFETIME - sets the expiry time of the session cookie
        - SECRET_KEY - alter this to force a refresh of all sessions. It's a byte string!
        - SQLALCHEMY_DATABASE_URI - connection string. Can replace localhost with dev environment ip when used with db management software
        - SQLALCHEMY_TRACK_MODIFICATIONS - leave False or it add's extra tables to track schema changes
    '''
    PERMANENT_SESSION_LIFETIME     = timedelta(minutes=480)
    SECRET_KEY = b"\xec\xc5\x06)'\x951\xab\xbef:\xb97.\x12\xd7"
    SQLALCHEMY_DATABASE_URI        = 'postgresql://localhost:5432/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
 