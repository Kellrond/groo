from www         import config
from database    import __schema__ as schema
from database   import db

def paginateDocs(lvl1,lvl2,lvl3,lvl4,lvl5,lvl6,page=1) -> dict:
    page = int(page) - 1 # adjust for pagination offest to start from 1
    like_str = ''
    if lvl1:
        like_str = f'{lvl1}'
    if lvl2:
        like_str += f'/{lvl2}'
    if lvl3:
        like_str += f'/{lvl3}'
    if lvl4:
        like_str += f'/{lvl4}'
    if lvl5:
        like_str += f'/{lvl5}'
    if lvl6:
        like_str += f'/{lvl6}'
    
    like_str += '%'

    sql = f'''
        SELECT * FROM doc_files f
        WHERE f.file_path like '{ like_str }'
        ORDER BY f.file_path
    '''

    file_paths_query = db.session.execute(sql).all()
    file_paths = [x.file_path for x in file_paths_query ]
    file_ids = [ x.file_id for x in file_paths_query ] 

    # Filepaths 
    sql = f'''
        SELECT * FROM doc_files f
        ORDER BY f.file_path
    '''

    tempQuery = db.session.execute(sql)
    nav_list = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        nav_list.append(tempDict)

    # Classes
    sql = f'''
        SELECT c.*, f.file_path
        FROM doc_classes c
        JOIN doc_files f ON c.file_id = f.file_id
        WHERE c.file_id IN ('{ "','".join([ str(x) for x in file_ids]) }')
        ORDER BY c.name    
    '''

    tempQuery = db.session.execute(sql)
    classes = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        classes.append(tempDict)

    # Routes
    sql = f'''
        SELECT *
        FROM doc_routes r
        JOIN doc_files f ON r.file_id = f.file_id
        WHERE r.file_id IN ('{ "','".join([ str(x) for x in file_ids]) }')
        ORDER BY r.url    
    '''

    tempQuery = db.session.execute(sql)
    routes = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        routes.append(tempDict)


    # imports
    sql = f'''
        SELECT *
        FROM doc_dependencies d
        JOIN doc_files f ON d.file_id = f.file_id
        WHERE d.file_id IN ('{ "','".join([ str(x) for x in file_ids]) }')
        ORDER BY d.module, d.object    
    '''

    tempQuery = db.session.execute(sql)
    imports = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        imports.append(tempDict)

    # Class methods 
    sql = f'''
        SELECT f.*, fi.file_path
        FROM doc_functions f
        JOIN doc_files fi ON f.file_id = fi.file_id
        WHERE f.file_id IN ('{ "','".join([ str(x) for x in file_ids]) }')   
        AND f.class_id IS NOT NULL
        AND LEFT(f.name, 1) <> '_'
        ORDER BY f.name
    '''

    tempQuery = db.session.execute(sql)
    methods = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        methods.append(tempDict)

    # Functions 
    sql = f'''
        SELECT f.*, fi.file_path
        FROM doc_functions f
        JOIN doc_files fi ON f.file_id = fi.file_id
        WHERE f.file_id IN ('{ "','".join([ str(x) for x in file_ids]) }')  
        AND f.class_id IS NULL
        AND LEFT(f.name, 1) <> '_'
        ORDER BY f.name
    '''

    tempQuery = db.session.execute(sql)
    functions = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        functions.append(tempDict)

    return { 'file_path': file_paths, 'nav_list': nav_list, 'classes': classes, 'class_funcs': methods, 'functions': functions, 'routes': routes, 'imports': imports}

def paginateImportDependancies() -> dict:
    ''' Does not paginate. Displays all on one page '''

    sql = f'''
        SELECT 
            f.file_path
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 3) = 'app' THEN 1 ELSE 0 END ) as app
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 11) = 'app.modules' THEN 1 ELSE 0 END ) as app_modules
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 9) = 'app.views' THEN 1 ELSE 0 END ) as app_views
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 17) = 'environment' THEN 1 ELSE 0 END ) as environment 
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 8) = 'database' THEN 1 ELSE 0 END ) as database 
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 4) = 'docs' THEN 1 ELSE 0 END ) as docs 
            ,SUM(CASE WHEN SUBSTRING(d.module, 1, 7) = 'modules' THEN 1 ELSE 0 END ) as modules 
        FROM doc_dependencies d
        JOIN doc_files f ON d.file_id = f.file_id
        WHERE REPLACE(d.module, '.', '/') || '/' IN ( 
            SELECT f.file_path FROM doc_folders f
        )
        OR 
        REPLACE(SUBSTRING(d.module, 1, length(d.module) - position('.' in reverse_string(d.module))), '.', '/') || '/' IN (
            SELECT f.file_path FROM doc_folders f
            )
        GROUP BY f.file_path
        ORDER BY f.file_path
    '''
    tempQuery = db.session.execute(sql)
    internal_dependencies = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        internal_dependencies.append(tempDict)

    sql = f'''
        SELECT *
        FROM doc_dependencies d
        JOIN doc_files f ON d.file_id = f.file_id
        WHERE REPLACE(d.module, '.', '/') || '/' NOT IN ( 
            SELECT f.file_path FROM doc_folders f
        )
        AND 
        REPLACE(SUBSTRING(d.module, 1, length(d.module) - position('.' in reverse_string(d.module))), '.', '/') || '/' NOT IN (
            SELECT f.file_path FROM doc_folders f
            )

        ORDER BY f.file_path;
    '''
    tempQuery = db.session.execute(sql)
    external_dependencies = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        external_dependencies.append(tempDict)



    return { 'internal': internal_dependencies, 'external': external_dependencies }

def paginateRoutes() -> dict:
    ''' Does not paginate. Displays all on one page '''
    sql = f'''
        SELECT r.url, r.permissions, r.methods, f.file_path
        FROM doc_routes r
        JOIN doc_files f ON r.file_id = f.file_id
        ORDER BY r.url;
    '''
    tempQuery = db.session.execute(sql)
    query = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        query.append(tempDict)

    count = db.session.execute(sql)
    return {'results': query}

def paginateStats() -> dict:
    ''' Does not paginate. Displays all on one page '''
    sql = f'''
        SELECT count(*) as total_files
            ,SUM(CASE WHEN f.ext = 'css' THEN 1 ELSE 0 END) AS css_files
            ,SUM(CASE WHEN f.ext = 'js' THEN 1 ELSE 0 END) AS js_files
            ,SUM(CASE WHEN f.ext = 'py' THEN 1 ELSE 0 END) AS py_files
            ,SUM(CASE WHEN f.ext = 'sh' THEN 1 ELSE 0 END) AS sh_files
            ,SUM(CASE WHEN f.ext = 'sql' THEN 1 ELSE 0 END) AS sql_files
            ,sum(f.lines) as total_lines
            ,SUM(CASE WHEN f.ext = 'css' THEN f.lines ELSE 0 END) AS css_lines
            ,SUM(CASE WHEN f.ext = 'js' THEN f.lines ELSE 0 END) AS js_lines
            ,SUM(CASE WHEN f.ext = 'py' THEN f.lines ELSE 0 END) AS py_lines
            ,SUM(CASE WHEN f.ext = 'sh' THEN f.lines ELSE 0 END) AS sh_lines
            ,SUM(CASE WHEN f.ext = 'sql' THEN f.lines ELSE 0 END) AS sql_lines
        FROM doc_files f
    '''
    tempQuery = db.session.execute(sql)
    summary = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        # Summary here is = since the statement returns only one row
        summary = tempDict

    sql = f'''
        SELECT *
        FROM doc_files f
        ORDER BY f.file_path
    '''
    tempQuery = db.session.execute(sql)
    file_list = []
    keys = [x for x in tempQuery.keys()]
    for row in tempQuery:
        tempDict = {}
        for i in range(len(keys)):
            tempDict[keys[i]] = row[i]
        # file_list here is = since the statement returns only one row
        file_list.append(tempDict)

    return {'summary': summary, 'detail': file_list}

def dropAllDocs() -> bool:
    # try:
    tables = ['doc_routes', 'doc_functions', 'doc_classes', 'doc_dependencies', 'doc_folders', 'doc_files']
    for table in tables:
        sql = f'DELETE FROM { table } WHERE 1=1;'
        db.execute(sql)
    return True
    # except Exception as e: 
    #     db.session.rollback()
    #     logger.write(activity='drop all route docs from DC', resource_id='', error=e)
    #     return False     

def getDocFolderIdFromFilePath(file_path):
    file_path = file_path.split('/')
    file_path.pop()
    file_path = '/'.join(file_path) + '/'

    sql = f'''
        SELECT f.folder_id 
        FROM doc_folders f
        WHERE f.file_path = '{ file_path }'
    '''

    return db.session.execute(sql).scalar()

def getDocFileIdFromFilePath(file_path):
    folder_id = getDocFolderIdFromFilePath(file_path) 
    name = file_path
    name = name.split('/').pop()

    sql = f'''
        SELECT f.file_id 
        FROM doc_files f
        WHERE f.folder_id = '{ folder_id }'
        AND f.name = '{ name }'
    '''
    return db.session.execute(sql).scalar()

def updateDocRoutesDb(routes) -> bool:
    ''' Adds to the documentation for routes '''
    try:
        for link in routes:
            file_path = link.get('file_path')
            permissions = link.get('permissions')

            for url in link.get('route'):
                route_dbo = schema.Doc_routes(
                    file_id     = getDocFileIdFromFilePath(file_path)
                    ,methods     = ", ".join(url.get('methods',[]))
                    ,permissions = permissions
                    ,url         = url.get('url')
                )
                db.session.add(route_dbo)
                
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def updateDocClassesDb(classes) -> bool:
    ''' Adds to the documentation for classes '''
    try:
        for cls in classes:
            class_id    = nextUniqueId(schema.Doc_classes.class_id)
            class_dbo = schema.Doc_classes(
                class_id    = class_id
                ,file_id    = getDocFileIdFromFilePath(cls.get('file_path'))
                ,name       = cls.get('name')
                ,superclass = ", ".join(cls.get('superclass',[]))
                ,docstring  = cls.get('docstring')
                ,parameters = cls.get('parameters')
            )
            db.session.add(class_dbo)
            db.session.commit()
            for func in cls.get('methods'):
                func_id = nextUniqueId(schema.Doc_functions.function_id)
                func_dbo = schema.Doc_functions(
                    function_id = func_id
                    ,class_id   = class_id
                    ,file_id    = getDocFileIdFromFilePath(func.get('file_path'))
                    ,name       = func.get('name')
                    ,returns    = func.get('returns')
                    ,docstring  = func.get('docstring')
                    ,parameters = func.get('parameters')
                )
                db.session.add(func_dbo)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def updateDocFilesDb(file_paths) -> bool:
    for id, fp in enumerate(file_paths):
        folder_id = getDocFolderIdFromFilePath(fp)
        ext = fp

        # in case there is no extension
        if ext.find('.') == -1:
            ext = ''
        else:
            while ext.find('.') != -1:
                ext = ext[ext.find('.')+1:]

        lines = 0
        with open(fp, 'r') as file:
            lines = len(file.readlines())

        file_dbo = schema.Doc_files(
            file_id = id
            ,folder_id = folder_id
            ,name  = fp.split('/').pop()
            ,file_path = fp
            ,ext   = ext
            ,lines = lines
        )
        db.session.add(file_dbo)
        db.session.commit()

def updateDocFunctionsDb(functions) -> bool:
    ''' Adds to the documentation for functions '''
    try:
        for func in functions:
            func_id = nextUniqueId(schema.Doc_functions.function_id)
            func_dbo = schema.Doc_functions(
                function_id = func_id
                ,class_id   = None
                ,file_id    = getDocFileIdFromFilePath(func.get('file_path'))
                ,name       = func.get('name')
                ,returns    = func.get('returns')
                ,docstring  = func.get('docstring')
                ,parameters = func.get('parameters')
            )
            db.session.add(func_dbo)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.write(activity='write functions', resource_id='', error=e)
        return False

def updateDocFolderDb(folders) -> bool:
    ''' Adds to the documentation for functions '''
    try:
        root_id = 0
        for folder in folders:
            split_fp = folder.get('split_file_path')
            # This is / and it has no split file path
            if len(split_fp) == 0:
                parent_id = None
                root_id = folder.get('folder_id')
            # This catches all top level folders
            elif len(split_fp) == 1:
                parent_id = root_id
            # The parents should all be in place now we 
            else:
                parent_path = db.session.query(schema.Doc_folders).filter(schema.Doc_folders.file_path == '/'.join(split_fp[:-1]) + '/').first()
                
                if parent_path:
                    parent_id = parent_path.folder_id

            # Name the root folder
            if len(split_fp) >= 1:
                name = split_fp[-1]
            else:
                name = '/'


            func_dbo = schema.Doc_folders(
                folder_id   = folder.get('folder_id')
                ,parent_id  = parent_id
                ,file_path  = folder.get('file_path') if folder.get('file_path') != '' else '/'
                ,name       = name
            )
            db.session.add(func_dbo)
            db.session.commit()


        return True
    except Exception as e:
        db.session.rollback()
        logger.write(activity='write docs folder heirarchy', resource_id='', error=e)
        return False

def updateDocDependencyDb(depenancies) -> bool:
    ''' Adds to the documentation for dependencies '''
    try:
        for dep in depenancies:
            if len(dep.get('objects')) > 0:
                for obj in dep.get('objects'):
                    depencancy_dbo = schema.Doc_dependencies(   
                        file_id     = getDocFileIdFromFilePath(dep.get('file_path'))
                        ,module    = dep.get('module')
                        ,object    = obj
                    )
                    db.session.add(depencancy_dbo)
            else:
                depencancy_dbo = schema.Doc_dependencies(
                    file_id    = getDocFileIdFromFilePath(dep.get('file_path'))
                    ,module    = dep.get('module')
                )
                db.session.add(depencancy_dbo)                
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.write(activity='write functions', resource_id='', error=e)
        return False