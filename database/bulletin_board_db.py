from datetime   import datetime
from flask      import session

from www      import config
# from database import __schema__ as schema, db, nextUniqueId, returnDictFromDboObject
# from modules  import logging

# logger = logging.Log(py=__name__)

# # Pagination functions for display on pages

# def paginateBulletinBoardCategories(page=1) -> dict:
#     page = int(page) - 1 # adjust for pagination offest to start from 1

#     sql = f'''
#         SELECT
#             c.category_id
#             ,c.name
#             ,c.description
#             ,c.permissions
#             ,c.slug
#             ,parent.name as parent_category
#             ,p.count
#             ,c.active
#         FROM bb_categories c
#         LEFT JOIN bb_categories parent ON c.parent_category_id = parent.category_id
#         LEFT JOIN (
#             SELECT category_id
#               , count(*) as count
#             FROM bb_messages
#             GROUP BY category_id
#         ) p ON c.category_id = p.category_id
#         ORDER BY parent.name 
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
#     sql = f''' SELECT count(*) FROM bb_categories c '''
#     count = db.session.execute(sql)

#     return { 'count': count.scalar(), 'results': query}

# def paginateBulletinBoardMessages(board_id, active, page=1) -> dict:
#     page = int(page) - 1 # adjust for pagination offest to start from 1
#     active_string = 'TRUE' if active else 'FALSE'  

#     sql = f"""  SELECT m.*
#                     ,e1.first_last_name as author_name
#                     ,e2.first_last_name as reply_name
#                     ,CASE
#                         WHEN u.user_id IS NULL
#                         THEN FALSE
#                         ELSE TRUE
#                     END as unread
#                 FROM bb_messages m
#                 LEFT JOIN employees e1 on m.author_id = e1.user_id
#                 LEFT JOIN employees e2 on m.latest_reply_by = e2.user_id
#                 LEFT JOIN bb_unread_status u on m.post_id = u.post_id
#                     AND u.user_id = '{ session.get('user_id') }' 
#                 WHERE m.category_id = { board_id }
#                     AND m.parent_post_id IS NULL
#                     AND m.active = { active_string }
#                 ORDER BY m.sticky DESC
#                     ,m.latest_reply_date DESC
#                     ,m.post_date DESC 
#                 LIMIT { config.bulletin_board_posts_per_page }
#                 OFFSET { page * config.bulletin_board_posts_per_page };
#                     """

#     query = db.session.execute(sql).all()

#     output = []
#     for row in query:
#         rowDict = dict(row)
#         output.append(rowDict)


#     # Count the rows
#     sql = f''' 
#         SELECT count(*)
#         FROM bb_messages m
#         WHERE m.category_id = { board_id }
#             AND m.parent_post_id IS NULL
#             AND m.active = { active_string }
#      '''
#     count = db.session.execute(sql)

#     return { 'count': count.scalar(), 'results': output}

# def paginateMessage(post_id, page=1) -> dict:
#     ''' Sometimes might be fed no post_id if used embeded on pages '''
#     if post_id == None:
#         return None

#     page = int(page) - 1 # adjust for pagination offest to start from 1 

#     sql = f"""
#         WITH RECURSIVE posts AS (
#             SELECT q.*
#                 ,'a' AS sort
#                 ,0 AS level
#             FROM bb_messages q

#             WHERE post_id = { post_id } 
#             UNION
#                 SELECT
#                     b.*
#                     ,a.sort || (row_number() over ())::text || 'b'::text as sort
#                     ,a.level + 1 AS level
#                 FROM posts a
#                 INNER JOIN bb_messages b ON a.post_id = b.parent_post_id
#                 )
#         SELECT p.*
#             ,e.first_last_name
#             ,e.email
#         FROM posts p
#         JOIN employees e ON p.author_id = e.user_id
#         ORDER BY sort
#         LIMIT { config.bulletin_board_posts_per_page }
#         OFFSET { page * config.bulletin_board_posts_per_page };
#     """
#     query = db.session.execute(sql).all()

#     output = []
#     for row in query:
#         rowDict = dict(row)
#         rowDict['post_date'] = row['post_date'].strftime(config.date_format)
#         if type(rowDict.get('edit_date')) == datetime:
#             rowDict['edit_date'] = row['edit_date'].strftime(config.date_format)
#         output.append(rowDict)

#     # Count the rows
#     sql = f''' 
#         SELECT count(*)
#         FROM bb_messages m
#         WHERE m.parent_post_id = { post_id }
#      '''
#     count = db.session.execute(sql)

#     # +1 is for the original post. For efficiency the children of the parent post are searched, 
#     # so the original post is missing in the count
#     return { 'count': count.scalar() + 1, 'results': output}

# # Return functions

# def returnPostFromId(post_id) -> dict:
#     post = schema.Bb_messages.query.filter(schema.Bb_messages.post_id == post_id).first()
#     return returnDictFromDboObject(post)

# def returnCategoryFromId(category_id) -> dict:
#     category = schema.Bb_categories.query.filter(schema.Bb_categories.category_id == category_id).first()
#     return returnDictFromDboObject(category)

# def returnCategoryFromSlug(slug) -> dict:
#     category = schema.Bb_categories.query.filter(schema.Bb_categories.slug == slug).first()
#     if category:
#         return returnDictFromDboObject(category)

# def returnBoardParents(bb_id) -> list:
#     ''' Is sorted heirarchically
#         Returns: 
#         `[{'name', 'category_id', 'permissions', 'slug'}, {...}, ...]`
#     '''
#     topq = db.session.query(schema.Bb_categories
#                 ).filter(schema.Bb_categories.category_id == bb_id
#                 ).cte('cte', recursive=True)

#     bottomq = db.session.query(schema.Bb_categories
#                     ).join(topq, schema.Bb_categories.category_id == topq.c.parent_category_id)

#     recursive_q = topq.union(bottomq)
#     bb_heirarchy = db.session.query(recursive_q).all()

#     bb_heirarchy_list = []

#     for board in bb_heirarchy:
#         bb_heirarchy_list.insert(0, {'name':board.name, 'category_id':board.category_id, 'permissions': board.permissions, 'slug': board.slug })

#     return bb_heirarchy_list

# def returnBoardChildren(bb_id=None) -> list:
#     topq = schema.Bb_categories.query.filter(schema.Bb_categories.category_id == bb_id,
#                         schema.Bb_categories.permissions <= session.get('permissions', 0)
#                 ).cte('cte', recursive=True)

#     bottomq = schema.Bb_categories.query.join(topq, schema.Bb_categories.parent_category_id == topq.c.category_id)

#     recursive_q = topq.union(bottomq)
#     bb_heirarchy = db.session.query(recursive_q)

#     output = []
#     prev_parent_id = None
#     level = 0 
#     for row in bb_heirarchy:
#         if row.parent_category_id == None:
#             level = 0
#             prev_parent_id = None
#         elif row.parent_category_id != prev_parent_id:
#             level += 1
#             prev_parent_id = row.parent_category_id    
#         output += [{'level': level,
#                     'unread_count': countUnreadMessages(row.category_id),
#                     'category_id': row.category_id,
#                     'slug': row.slug,
#                     'name':row.name,
#                     'description':row.description,
#                     'permissions':row.permissions
#                     }]
#     output = output[1:]

#     return output

# def returnCategoriesList() -> list:
#     ''' Returns a list of [{'name': ..., 'category_id': ...}]'''
#     sql = f'''
#             SELECT c.category_id
#                 ,c.name
#             FROM bb_categories c
#     '''
#     query = db.session.execute(sql).all()
#     output = []
#     for k,v in dict(query).items():
#         output.append({'name': v, 'category_id': k})
#     return output 

# # Update functions

# def updateCategory(form) -> bool:
#     ## Fix the boolean string 'on' from html response
#     form['active'] = True if form.get('active') == 'on' or form.get('active') == True else False

#     new_record   = False
#     log_activity = 'update'
#     if form.get('category_id') == '':
#         new_record = True
#         form['category_id'] = nextUniqueId(schema.Bb_categories.category_id) 
#         log_activity = 'create' 

#     if form.get('parent_category_id') == '':
#         form['parent_category_id'] = None

#     try:
#         if new_record:
#             record_dbo = schema.Bb_categories(
#                 category_id         = form.get('category_id')
#                 ,name               = form.get('name')
#                 ,description        = form.get('description')
#                 ,permissions        = form.get('permissions')
#                 ,slug               = form.get('slug')
#                 ,parent_category_id = form.get('parent_category_id')
#                 ,ext_table_name     = form.get('ext_table_name')
#                 ,active             = form.get('active')
#             )
#             db.session.add(record_dbo)
#         else:
#             record_dbo = schema.Bb_categories.query.filter(schema.Bb_categories.category_id == form.get('category_id')).first()
#             record_dbo.name                = form.get('name')
#             record_dbo.description         = form.get('description')
#             record_dbo.permissions         = form.get('permissions')
#             record_dbo.slug                = form.get('slug')
#             record_dbo.parent_category_id  = form.get('parent_category_id')
#             record_dbo.ext_table_name      = form.get('ext_table_name')
#             record_dbo.active              = form.get('active')

#         db.session.commit()

#         msg_txt = f"{log_activity.capitalize()}d {form.get('name')}"
#         logger.write(activity= log_activity, resource_id=form.get('name'), note=msg_txt)
#         return True

#     except Exception as e:
#         db.session.rollback()
#         logger.write(activity= log_activity, resource_id=form.get('name'), error=e)
#         return False

# def postMessage(form):
#     new_record   = False
#     # New post
#     if form.get('parent_post_id') == None:
#         if form.get('post_id') != None:
#             log_activity = 'post update'
#         else:
#             log_activity = 'post create'
#             new_record = True
#     # Reply
#     else:
#         updateLatestPostDate(form.get('parent_post_id'))
#         if form.get('post_id') != None:
#             log_activity = 'reply update'
#         else:
#             log_activity = 'reply create'
#             new_record = True
    
#     try:
#         if new_record:
#             form['post_id'] = nextUniqueId(schema.Bb_messages.post_id)
#             record_dbo = schema.Bb_messages(
#                 post_id         = form.get('post_id')
#                 ,parent_post_id = form.get('parent_post_id')
#                 ,title          = form.get('title', form.get('ext_ref_id'))
#                 ,author_id      = form.get('author_id')
#                 ,post_date      = datetime.now()
#                 ,body           = form.get('body')
#                 ,ext_ref_id     = form.get('ext_ref_id')
#                 ,category_id    = form.get('category_id')
#                 ,active         = True
#             )
#             db.session.add(record_dbo)
#         else:
#             record_dbo = schema.Bb_messages.query.filter(schema.Bb_messages.post_id == form.get('post_id')).first()
#             record_dbo.title               = form.get('title')
#             record_dbo.body                = form.get('body')
#             record_dbo.edited_by           = form.get('edited_by')
#             record_dbo.edit_date           = datetime.now()

#         db.session.commit()

#         msg_txt = f"{log_activity.capitalize()}d {form.get('title')}"
#         logger.write(activity= log_activity, resource_id=form.get('title'), note=msg_txt)
#         return True

#     except Exception as e:
#         db.session.rollback()
#         logger.write(activity= log_activity, resource_id=form.get('title'), error=e)
#         return False 

# def updateLatestPostDate(post_id):
#     post = schema.Bb_messages.query.filter(schema.Bb_messages.post_id == post_id).first()
#     post.latest_reply_date = datetime.now()
#     post.latest_reply_by = session.get('user_id')
#     db.session.commit()

# # Helper functions

# def countUnreadMessages(bb_id) -> int:
#     user_id = session.get('user_id')
#     subscribed = schema.Bb_unread_status.query.filter(schema.Bb_unread_status.user_id == user_id, schema.Bb_unread_status.category_id == bb_id)
#     count = getCount(subscribed)
#     return count

# def getCount(q) -> int:
#     count_q = q.statement.with_only_columns([func.count()]).order_by(None)
#     count = q.session.execute(count_q).scalar()
#     return count

# def isSubscribedToBoard(bb_id) -> bool:
#     user_id = session.get('user_id')
#     subscribed = schema.Bb_subscribe.query.filter(schema.Bb_subscribe.user_id == user_id, schema.Bb_subscribe.category_id == bb_id).first()
#     if subscribed:
#         return True
#     else:
#         return False  
