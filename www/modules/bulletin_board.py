from    flask                           import session

from    database                        import db, bulletin_board_db
from    database.__schema__             import Bb_categories, Bb_messages, Bb_subscribe, Bb_unread_status

def isMsgRead(post_id: int) -> bool:
    ''' Checks if the message has been read by the user and returns the read status
    Returns:
        - True if read 
        - False if unread'''
    unread_row = Bb_unread_status.query.filter(Bb_unread_status.user_id == session.get('user_id')
                                                    ,Bb_unread_status.post_id == post_id).first()
    if unread_row:
        return False
    else:
        return True

def isSubscribedToBoard(category_id: int) -> bool:
    ''' Checks if the currently user is subscribed to the category '''
    subscription_status = bulletin_board_db.isSubscribedToBoard(category_id)
    return subscription_status

def returnPostById(post_id: int) -> dict:
    ''' Return only one post by it's post id
        Returns:
            `{  'active', 'author_id', 'body', 'category_id', 'edit_date', 'edited_by', 'ext_ref_id', 'latest_reply_by', 'latest_reply_date', 'parent_post_id', 'post_date', 'post_id','sticky', 'title'}`
    '''
    post = bulletin_board_db.returnPostFromId(post_id)   
    return post

def returnCategoryBySlug(slug: str) -> dict:
    ''' Returns a bullertin board category dictionary by the slug
        Returns:
            `{'active', 'category_id',  'description', 'ext_table_name', 'name', 'parent_category_id', 'permissions', 'slug'}` 
    '''
    category = bulletin_board_db.returnCategoryFromSlug(slug)
    return category

def returnBoardParents(category_id: int) -> list:
    ''' Returns a list of board parents sorted heirachicly with the top level parent first
        Returns: 
        `[{'name', 'category_id', 'permissions', 'slug'}, {...}, ... ]`
    '''
    parents = bulletin_board_db.returnBoardParents(category_id)
    return parents

def returnBoardChildren(category_id: int) -> list:
    ''' Returns a list of board children sorted heirachicly with the current category at the top
        Notes:
            - 'level' represents the indent level or how distant the category is from the parent
        Returns: 
        `[{'level', 'unread_count', 'category_id', 'slug', 'name', 'description', 'permissions'}, {...}, ... ]`
    '''
    children = bulletin_board_db.returnBoardChildren(category_id)
    return children

def toggleBoardSubscriptionSatus(slug: str) -> None:
    ''' Toggles the category subscription status of the current user. 
    A user is subscribed to a category if there is a record of the user_id and category_id in the bb_subscribe table'''
    category = returnCategoryBySlug(slug)
    user_id = session.get('user_id')
    subscribed = Bb_subscribe.query.filter(Bb_subscribe.user_id == user_id, Bb_subscribe.category_id == category.get('category_id')).first()
    if subscribed:
        db.session.delete(subscribed)
        db.session.commit()
    else:
        new_subscription = Bb_subscribe(user_id=user_id,category_id=category.get('category_id'))
        db.session.add(new_subscription)
        db.session.commit()

def toggleMessageReadStatus(post_id: int, slug: str) -> None:
    ''' Toggles the message read status for the current user. A user must be subscribed to a board before a message will be marked unread.
    Notes:
        When a post is submitted, a record is added to the bb_unread_status table for every subscribed user.
        When the message is read, the record is deleted from the table. 
     '''
    category = returnCategoryBySlug(slug)
    unread_row = Bb_unread_status.query.filter(Bb_unread_status.user_id == session.get('user_id')
                                                    ,Bb_unread_status.post_id == post_id).first()    
    if unread_row:
        db.session.delete(unread_row)
        db.session.commit()      
    else:
        user_id = session.get('user_id')
        unread_msg = Bb_unread_status(user_id=user_id, post_id=post_id, category_id=category.get('category_id'))
        db.session.add(unread_msg)
        db.session.commit()   
    
def togglePostSticky(post_id: int) -> None:
    ''' Toggles the sticky status of a post. 
    Stickied post will remain at the top of the message list on the first page only.'''
    msg = Bb_messages.query.filter(Bb_messages.post_id == post_id).first()
    new_status = False if msg.sticky != False else True
    msg.sticky = new_status
    db.session.commit()

def togglePostArchive(post_id: int) -> None:
    '''Toggles archive status of a post.
    Currently there is no facility to un-archive a post other than direct database access'''
    msg = Bb_messages.query.filter(Bb_messages.post_id == post_id).first()
    msg.active = False if msg.active != False else True
    db.session.commit()

def getPostIdFromExtRefId(slug: str, ext_ref_id) -> int:
    '''Bulletin boards are used to add threaded discussion to manifests and the like. 
    This function uses the table and its key to find posts to display. 
    
        Params:
            - slug: represents the database table; e.g. manifests
            - ext_ref_id: is the primary key for the above table; e.g. manifest_id '''
    category = returnCategoryBySlug(slug)
    post = Bb_messages.query.filter(
        Bb_messages.category_id == category.get('category_id'), 
        Bb_messages.ext_ref_id == ext_ref_id).first()
    if post:
        return int(post.post_id)
    else:
        return None

def unreadMessageCount() -> int:
    '''Returns the total unread messages in subscribed bulletin board categories. Used for login in toast'''
    messageCount = 0
    user_id = session.get('user_id')
    subscribed_boards = Bb_subscribe.query.filter(Bb_subscribe.user_id == user_id).all()
    for board in subscribed_boards:
        messageCount += bulletin_board_db.countUnreadMessages(board.category_id)      
    return messageCount
