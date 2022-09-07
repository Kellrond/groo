from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String 
from sqlalchemy.orm import declarative_base

from config import db_config
from database import Db

Base = declarative_base()
## Bulletin board tables

class Bb_categories(Base, Db):
    __tablename__ = 'bb_categories'

    category_id         = Column(Integer(), primary_key=True)
    name                = Column(String())
    description         = Column(String())
    permissions         = Column(Integer())
    slug                = Column(String())
    parent_category_id  = Column(Integer())
    ext_table_name      = Column(String())
    active              = Column(Boolean())


class Bb_messages(Base, Db):
    __tablename__ = 'bb_messages'

    post_id             = Column(Integer(), primary_key=True)
    parent_post_id      = Column(Integer())
    title               = Column(String())
    author_id           = Column(String())
    post_date           = Column(DateTime())
    latest_reply_date   = Column(DateTime())
    latest_reply_by     = Column(String())
    edit_date           = Column(DateTime())
    edited_by           = Column(String())
    body                = Column(String())  
    ext_ref_id          = Column(Integer())
    sticky              = Column(Boolean())
    sticky_weight       = Column(Integer())
    category_id         = Column(Integer(), ForeignKey('bb_categories.category_id'))
    active              = Column(Boolean())


class Bb_subscribe(Base, Db):
    __tablename__ = 'bb_subscribe'

    user_id = Column(String(), primary_key=True)
    category_id = Column(Integer(), ForeignKey('bb_categories.category_id'), primary_key=True)


class Bb_unread_status(Base, Db):
    __tablename__ = 'bb_unread_status'

    user_id = Column(String(), primary_key=True)
    post_id     = Column(Integer(), ForeignKey('bb_messages.post_id'), primary_key=True)
    category_id = Column(Integer(), ForeignKey('bb_categories.category_id'), primary_key=True)


## Calendar table 
class Calendar(Base, Db):
    __tablename__ = 'calendar'

    date_id             = Column(DateTime(), primary_key=True)
    date                = Column(DateTime())
    yyyy_mm_dd_str      = Column(String())
    yyyy_int            = Column(Integer())
    yyyy_str            = Column(String())
    yy_str              = Column(String())
    month               = Column(String())
    month_abr           = Column(String())
    mm_str              = Column(String())
    m_int               = Column(Integer())
    dd_str              = Column(String())
    d_int               = Column(Integer())
    leap                = Column(String())
    DoW_int             = Column(Integer())
    DoW_abb             = Column(String())
    DoW_full            = Column(String())
    DoY_int             = Column(Integer())
    week_int            = Column(Integer())
    fiscal_period       = Column(Integer())
    fiscal_yyyy         = Column(Integer())
    school_year_period  = Column(Integer())
    school_yyyy         = Column(Integer())
    school_yyyy_yy      = Column(String())
    bc_holiday          = Column(String())
    ab_holiday          = Column(String())
    sk_holiday          = Column(String())
    mb_holiday          = Column(String())
    on_holiday          = Column(String())
    qc_holiday          = Column(String())
    nl_holiday          = Column(String())
    nb_holiday          = Column(String())
    ns_holiday          = Column(String())
    pe_holiday          = Column(String())
    us_holiday          = Column(String()) 

## Log tables
class Activity_logs(Base, Db):
    __tablename__ = 'activity_logs'

    activity    = Column(String()) 
    args        = Column(String())
    user_id     = Column(String(), primary_key=True)
    endpoint    = Column(String()) 
    error       = Column(String()) 
    ip          = Column(String())
    level       = Column(Integer())
    note        = Column(String()) 
    page        = Column(String())
    tab         = Column(String())
    resource_id = Column(String())
    py          = Column(String()) 
    timestamp   = Column(DateTime(), primary_key=True)


class Apache_error(Base, Db):
    __tablename__ = 'apache_error'

    error_time  = Column(DateTime, primary_key=True) 
    error_type  = Column(String())
    pid         = Column(String(), primary_key=True)
    ip          = Column(String()) 
    port        = Column(String()) 
    error       = Column(String())


class Apache_access(Base, Db):
    __tablename__ = 'apache_access'

    ip          = Column(String(), primary_key=True) 
    timestamp   = Column(DateTime(), primary_key=True) 
    method      = Column(String()) 
    url         = Column(String(), primary_key=True) 
    response    = Column(String()) 
    size        = Column(Integer()) 
    referrer    = Column(String()) 
    mozilla     = Column(String()) 
    system_info = Column(String()) 
    platform    = Column(String())
    extensions  = Column(String())

## Site content tables
class Page_content(Base, Db):
    __tablename__   = "page_content"

    page_content_id = Column(Integer(), primary_key=True)
    user_id         = Column(String())
    title           = Column(String())
    content         = Column(String())
    publish_on      = Column(DateTime())
    publish_until   = Column(DateTime())
    active          = Column(Boolean())
    dc_id           = Column(Integer())

## Dev tables used mainly for documentation
class Doc_classes(Base, Db):
    __tablename__ = 'doc_classes'

    class_id    = Column(Integer(), primary_key=True)
    file_id     = Column(Integer())
    name        = Column(String())
    superclass  = Column(String())
    docstring   = Column(String())
    parameters  = Column(String())

class Doc_dependencies(Base, Db):
    __tablename__ = 'doc_dependencies'

    dependency_id = Column(Integer(), primary_key=True)
    file_id       = Column(Integer())
    module        = Column(String())
    object        = Column(String())


class Doc_functions(Base, Db):
    __tablename__ = 'doc_functions'

    function_id = Column(Integer(), primary_key=True)
    class_id    = Column(Integer())
    file_id     = Column(Integer())
    name        = Column(String())
    returns     = Column(String())
    docstring   = Column(String())
    parameters  = Column(String())

class Doc_folders(Base, Db):
    __tablename__ = 'doc_folders'

    folder_id = Column(Integer(), primary_key=True)
    parent_id = Column(Integer())
    file_path = Column(String())
    name      = Column(String())

class Doc_files(Base, Db):
    __tablename__ = 'doc_files'

    file_id   = Column(Integer(), primary_key=True)
    folder_id = Column(Integer())
    name      = Column(String())
    file_path = Column(String())
    ext       = Column(String())
    lines     = Column(Integer())


class Doc_routes(Base, Db):
    __tablename__ = 'doc_routes'

    file_id     = Column(Integer())
    methods     = Column(String())
    permissions = Column(String())
    url         = Column(String(), primary_key=True)


def buildTables():
    db = Db(db_config.garden_db_connect)
    Base.metadata.create_all(db.engine)