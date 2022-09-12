from datetime    import datetime as dt

from www         import config
from database    import __schema__ as schema
# , db, returnDictFromDboObject, nextUniqueId
from modules     import logging 

logger = logging.Log(py=__name__)

# Paginate functions

def paginatePageContent(dc_id, active, page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    query = schema.Page_content.query.filter(
            schema.Page_content.dc_id == dc_id,
            schema.Page_content.active == active
        ).order_by(
            schema.Page_content.page_content_id.desc()
        ).limit(config.max_table_length).offset(page * config.max_table_length).all()
    # Use the same qury without the sorting to get the count quickly
    count = schema.Page_content.query.filter(
            schema.Page_content.dc_id == dc_id,
            schema.Page_content.active == active
        ).count()

    employee_list = []
    for row in query:
        employee_list.append(returnDictFromDboObject(row))
    return { 'count': count,'results': employee_list }

# Return functions

def returnPageByContentId(page_content_id) -> dict:
    query = schema.Page_content.query.filter(schema.Page_content.page_content_id == page_content_id).first()
    return returnDictFromDboObject(query)

def returnHomepagePosts(dc_id) -> list:
    ''' Returns a list of post dicts to display on the users homepage'''
    sql_formated_date = dt.today().strftime(config.sql_date_format)
    content = schema.Page_content.query.filter(schema.Page_content.publish_until > sql_formated_date
                    ,schema.Page_content.publish_on <= sql_formated_date
                    ,schema.Page_content.active == True
                    ,((schema.Page_content.dc_id == dc_id) | (schema.Page_content.dc_id == 0))
                ).order_by(schema.Page_content.page_content_id.desc()
                ).limit(config.posts_on_homepage
                ).all()

    output = []
    for post in content:
        author = ''
        postDict = { 'title': post.title, 'content': post.content, 'user_id': author.get('first_last_name') }
        output.append(postDict)

    return output

# Update functions

def updatePageContentDb(form) -> bool:
    ''' Adds or updates page content record '''
    new_record   = False
    log_activity = 'update'
    if form.get('page_content_id') == '':
        new_record = True
        form['page_content_id'] = nextUniqueId(schema.Page_content.page_content_id) 
        log_activity = 'create' 

    form['active'] = True if form.get('active') == 'on' or form.get('active') == True else False
    
    try:
        if new_record:
            record_dbo = schema.Page_content(
                page_content_id = form.get('page_content_id')
                ,user_id    = form.get('user_id')
                ,dc_id          = form.get('dc_id')
                ,title          = form.get('title') 
                ,content        = form.get('content') 
                ,publish_on     = form.get('publish_on')
                ,publish_until  = form.get('publish_until')
                ,active         = True
            )
            db.session.add(record_dbo)
        else:
            record_dbo = schema.Page_content.query.filter(schema.Page_content.page_content_id == form.get('page_content_id')).first()
            record_dbo.user_id   = form.get('user_id')
            record_dbo.title         = form.get('title')
            record_dbo.content       = form.get('content')
            record_dbo.publish_on    = form.get('publish_on')
            record_dbo.publish_until = form.get('publish_until')
            record_dbo.active        = form.get('active')
                  
        db.session.commit()
        msg_txt = f"{log_activity.capitalize()}d page_content: { form['title'] }"
        logger.write(activity= log_activity, resource_id=form['page_content_id'], note=msg_txt)
        return True
    except Exception as e:
        db.session.rollback()
        logger.write(activity= log_activity, resource_id=form['page_content_id'], error=e)
        return False
