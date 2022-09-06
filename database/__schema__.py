from database import db

## Bulletin board tables

class Bb_categories(db.Model):
    __tablename__ = 'bb_categories'

    category_id         = db.Column(db.Integer(), primary_key=True)
    name                = db.Column(db.String())
    description         = db.Column(db.String())
    permissions         = db.Column(db.Integer())
    slug                = db.Column(db.String())
    parent_category_id  = db.Column(db.Integer())
    ext_table_name      = db.Column(db.String())
    active              = db.Column(db.Boolean())


class Bb_messages(db.Model):
    __tablename__ = 'bb_messages'

    post_id             = db.Column(db.Integer(), primary_key=True)
    parent_post_id      = db.Column(db.Integer())
    title               = db.Column(db.String())
    author_id           = db.Column(db.String())
    post_date           = db.Column(db.DateTime())
    latest_reply_date   = db.Column(db.DateTime())
    latest_reply_by     = db.Column(db.String())
    edit_date           = db.Column(db.DateTime())
    edited_by           = db.Column(db.String())
    body                = db.Column(db.String())  
    ext_ref_id          = db.Column(db.Integer())
    sticky              = db.Column(db.Boolean())
    sticky_weight       = db.Column(db.Integer())
    category_id         = db.Column(db.Integer(), db.ForeignKey('bb_categories.category_id'))
    active              = db.Column(db.Boolean())


class Bb_subscribe(db.Model):
    __tablename__ = 'bb_subscribe'

    user_id = db.Column(db.String(), primary_key=True)
    category_id = db.Column(db.Integer(), db.ForeignKey('bb_categories.category_id'), primary_key=True)


class Bb_unread_status(db.Model):
    __tablename__ = 'bb_unread_status'

    user_id = db.Column(db.String(), primary_key=True)
    post_id     = db.Column(db.Integer(), db.ForeignKey('bb_messages.post_id'), primary_key=True)
    category_id = db.Column(db.Integer(), db.ForeignKey('bb_categories.category_id'), primary_key=True)


## Calendar table 
class Calendar(db.Model):
    __tablename__ = 'calendar'

    date_id             = db.Column(db.DateTime(), primary_key=True)
    date                = db.Column(db.DateTime())
    yyyy_mm_dd_str      = db.Column(db.String())
    yyyy_int            = db.Column(db.Integer())
    yyyy_str            = db.Column(db.String())
    yy_str              = db.Column(db.String())
    month               = db.Column(db.String())
    month_abr           = db.Column(db.String())
    mm_str              = db.Column(db.String())
    m_int               = db.Column(db.Integer())
    dd_str              = db.Column(db.String())
    d_int               = db.Column(db.Integer())
    leap                = db.Column(db.String())
    DoW_int             = db.Column(db.Integer())
    DoW_abb             = db.Column(db.String())
    DoW_full            = db.Column(db.String())
    DoY_int             = db.Column(db.Integer())
    week_int            = db.Column(db.Integer())
    fiscal_period       = db.Column(db.Integer())
    fiscal_yyyy         = db.Column(db.Integer())
    school_year_period  = db.Column(db.Integer())
    school_yyyy         = db.Column(db.Integer())
    school_yyyy_yy      = db.Column(db.String())
    bc_holiday          = db.Column(db.String())
    ab_holiday          = db.Column(db.String())
    sk_holiday          = db.Column(db.String())
    mb_holiday          = db.Column(db.String())
    on_holiday          = db.Column(db.String())
    qc_holiday          = db.Column(db.String())
    nl_holiday          = db.Column(db.String())
    nb_holiday          = db.Column(db.String())
    ns_holiday          = db.Column(db.String())
    pe_holiday          = db.Column(db.String())
    us_holiday          = db.Column(db.String()) 

## Log tables
class Activity_logs(db.Model):
    __tablename__ = 'activity_logs'

    activity    = db.Column(db.String()) 
    args        = db.Column(db.String())
    user_id     = db.Column(db.String(), primary_key=True)
    endpoint    = db.Column(db.String()) 
    error       = db.Column(db.String()) 
    ip          = db.Column(db.String())
    level       = db.Column(db.Integer())
    note        = db.Column(db.String()) 
    page        = db.Column(db.String())
    tab         = db.Column(db.String())
    resource_id = db.Column(db.String())
    py          = db.Column(db.String()) 
    timestamp   = db.Column(db.DateTime(), primary_key=True)


class Apache_error(db.Model):
    __tablename__ = 'apache_error'

    error_time  = db.Column(db.DateTime, primary_key=True) 
    error_type  = db.Column(db.String())
    pid         = db.Column(db.String(), primary_key=True)
    ip          = db.Column(db.String()) 
    port        = db.Column(db.String()) 
    error       = db.Column(db.String())


class Apache_access(db.Model):
    __tablename__ = 'apache_access'

    ip          = db.Column(db.String(), primary_key=True) 
    timestamp   = db.Column(db.DateTime(), primary_key=True) 
    method      = db.Column(db.String()) 
    url         = db.Column(db.String(), primary_key=True) 
    response    = db.Column(db.String()) 
    size        = db.Column(db.Integer()) 
    referrer    = db.Column(db.String()) 
    mozilla     = db.Column(db.String()) 
    system_info = db.Column(db.String()) 
    platform    = db.Column(db.String())
    extensions  = db.Column(db.String())

## Site content tables
class Page_content(db.Model):
    __tablename__   = "page_content"

    page_content_id = db.Column(db.Integer(), primary_key=True)
    user_id         = db.Column(db.String())
    title           = db.Column(db.String())
    content         = db.Column(db.String())
    publish_on      = db.Column(db.DateTime())
    publish_until   = db.Column(db.DateTime())
    active          = db.Column(db.Boolean())
    dc_id           = db.Column(db.Integer())

## Dev tables used mainly for documentation
class Doc_classes(db.Model):
    __tablename__ = 'doc_classes'

    class_id    = db.Column(db.Integer(), primary_key=True)
    file_id     = db.Column(db.Integer())
    name        = db.Column(db.String())
    superclass  = db.Column(db.String())
    docstring   = db.Column(db.String())
    parameters  = db.Column(db.String())

class Doc_dependencies(db.Model):
    __tablename__ = 'doc_dependencies'

    dependency_id = db.Column(db.Integer(), primary_key=True)
    file_id       = db.Column(db.Integer())
    module        = db.Column(db.String())
    object        = db.Column(db.String())


class Doc_functions(db.Model):
    __tablename__ = 'doc_functions'

    function_id = db.Column(db.Integer(), primary_key=True)
    class_id    = db.Column(db.Integer())
    file_id     = db.Column(db.Integer())
    name        = db.Column(db.String())
    returns     = db.Column(db.String())
    docstring   = db.Column(db.String())
    parameters  = db.Column(db.String())

class Doc_folders(db.Model):
    __tablename__ = 'doc_folders'

    folder_id = db.Column(db.Integer(), primary_key=True)
    parent_id = db.Column(db.Integer())
    file_path = db.Column(db.String())
    name      = db.Column(db.String())

class Doc_files(db.Model):
    __tablename__ = 'doc_files'

    file_id   = db.Column(db.Integer(), primary_key=True)
    folder_id = db.Column(db.Integer())
    name      = db.Column(db.String())
    file_path = db.Column(db.String())
    ext       = db.Column(db.String())
    lines     = db.Column(db.Integer())


class Doc_routes(db.Model):
    __tablename__ = 'doc_routes'

    file_id     = db.Column(db.Integer())
    methods     = db.Column(db.String())
    permissions = db.Column(db.String())
    url         = db.Column(db.String(), primary_key=True)
