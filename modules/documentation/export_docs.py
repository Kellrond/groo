''' Documentation is exported here. It's important that `documentation.generateDocumentation()
    is run before any of these functions are run. They require the data that is gathered by the
    parser classes.  

    The file path for the export is set in configuration 
'''
from    datetime    import datetime as dt
# Local
from    database    import Db
from    modules.documentation import py_parser
from    modules.logging       import Log

log = Log(__name__)

pyParser = py_parser.PyParser()

@log.performance
def toTxt(write_path):
    ''' Writes the documentation to a plaintext file. Might get in the way of grep so move the
        file if required. 
        
        Does not print all the details gathered, decorators for instance would get noisy since
        everything has a log.performance. That could be taken care of with an if statement, but
        that sort of detail is better left for the web where it would be more readable.

        Params:
            - write_path: the filepath for the documentation to end up. 
    '''

    indent = '   '
    
    header = [f"█▀▀ █▀█ █▀█ █ █ █                                                    { dt.strftime(dt.now(),'%b %d %Y')}"]
    header += ["█▄█ █▀▄ █▄█ ▀▄▀▄▀                                      Source code documentation"]
    header += ["--------------------------------------------------------------------------------"]
    header += [""]
    header += ["This is a basic version of the documentation if you want to use search over it"]
    header += ["It's a double edged sword since a text version will interfere with grep however,"]
    header += ["using notepad ++, vs code, word or other text tools will be easier for others. "]
    header += [""]
    header += ["The overall structure will be to show the list of folders and files and then show"]
    header += ["the relevant documentation within that file."]
    header += ["\n"]


    files   = ["File and folder structure"] 
    files  += ["================================================================================"]
    files  += [""] 

    # Sort folder list 
    sorted_folders = sorted(pyParser.folder_list, key=lambda d: d['file_path'])

    for folder in sorted_folders:
        files += [f"{indent}{folder.get('file_path')}"]
        for fp in [ x for x in pyParser.file_lines if x.get('folder_id') == folder.get('folder_id')]:
            files += [f"{ indent * 2 }- {fp.get('file_path')}"]

    files += ["\n"]

    code = ["Source code documentation"]
    code += ["================================================================================"]
    code += [""]

    for folder in sorted_folders:
        code += ["################################################################################"]
        code += [f"#  Folder  #   {folder.get('file_path')}  "]
        code += ["################################################################################"]
        code += [""]
        for fp in [ x for x in pyParser.file_lines if x.get('folder_id') == folder.get('folder_id')]:

            file_docs = [ x for x in pyParser.file_docs if x.get('file_id') == fp.get('file_id')]
            file_classes = [ x for x in pyParser.classes if x.get('file_id') == fp.get('file_id')]
            file_functions = [ x for x in pyParser.functions if x.get('file_id') == fp.get('file_id')]
            file_imports = [ x for x in pyParser.imports if x.get('file_id') == fp.get('file_id')]

            code += ["--------------------------------------------------------------------------------"]
            code += [f"{ indent * 2 }{fp.get('file_path')}"]
            code += ["--------------------------------------------------------------------------------"]

            # Just grab the first file doc for the file. There should only be one. 
            if len(file_docs) > 0:
                code += [file_docs[0].get('docs')]
                code += ["\n"]

            for imp in file_imports:
                if imp.get('object') == None:
                    if imp.get('alias') == None:
                        code += [f"import {imp.get('module')}"]
                    else:
                        code += [f"import {imp.get('module')} as {imp.get('alias')}"]
                else:
                    if imp.get('alias') == None:
                        code += [f"from {imp.get('module')} import {imp.get('object')}"]
                    else:
                        code += [f"from {imp.get('module')} import {imp.get('object')} as {imp.get('alias')}"]
            
            if len(file_classes) > 0:
                code += [""]
                code += ["################################################################################"]
                code += ["#  Classes"]
                code += ["################################################################################"]
                code += ['']
            for cls in file_classes:
                if not cls.get('name'):
                    continue
                code += [f"{cls.get('name')}({', '.join(cls.get('parameters'))})"]
                if cls.get('superclass') != []:
                    code += [f"{ indent }Superclass: {', '.join(cls.get('superclass'))}"]     

                if len(cls.get('docstring')) > 0:
                    code += ['']
                    for line in cls.get('docstring'):
                        code += [f"{indent}{line}"]
                    code += ['\n']
                
                cls_meth = [x for x in file_functions if x.get('class_id') == cls.get('class_id') and x.get('parent_id') == None]
                if len(cls_meth) > 0:
                    code += [""]
                    for meth in cls_meth:
                        if meth.get('returns') != None:
                            rtn_str = f" -> {meth.get('returns')}:"
                        else:
                            rtn_str = ":"
                        code += [f"{indent}{meth.get('name')}({', '.join(meth.get('parameters'))}){rtn_str}"]

                        if len(meth.get('docstring')) > 0:
                            for line in meth.get('docstring'):
                                code += [f"{indent*2}{line}"]
                        code += [""]

                        for nest in [x for x in file_functions if x.get('parent_id') == meth.get('function_id')]:
                            if nest.get('returns') != None:
                                rtn_str = f" -> {nest.get('returns')}:"
                            else:
                                rtn_str = ":"
                            code += [f"{indent * 2}{nest.get('name')}({', '.join(nest.get('parameters'))}){rtn_str}"]

                            if len(nest.get('docstring')) > 0:
                                for line in nest.get('docstring'):
                                    code += [f"{indent*3}{line}"]
                            code += [""]                            
                        code += [""]
                code += ['']
            code += ['\n']
            # Finally the functions
            functions = [ x for x in file_functions if x.get('class_id') == None]
            for func in [x for x in functions if x.get('parent_id') == None]:
                if func.get('returns') != None:
                    rtn_str = f" -> {func.get('returns')}:"
                else:
                    rtn_str = ":"
                code += [f"{indent}{func.get('name')}({', '.join(func.get('parameters'))}){rtn_str}"]

                if len(func.get('docstring')) > 0:
                    for line in func.get('docstring'):
                        code += [f"{indent*2}{line}"]
                code += [""]

                for nest in [x for x in file_functions if x.get('parent_id') == func.get('function_id')]:
                    if nest.get('returns') != None:
                        rtn_str = f" -> {nest.get('returns')}:"
                    else:
                        rtn_str = ":"
                    code += [f"{indent * 2}{nest.get('name')}({', '.join(nest.get('parameters'))}){rtn_str}"]

                    if len(nest.get('docstring')) > 0:
                        for line in nest.get('docstring'):
                            code += [f"{indent*3}{line}"]
                    code += [""]                            
                code += [""]

    with open(write_path, 'w') as file:
        for line in header:
            file.write(f'{line}\n')
        for line in files:
            file.write(f'{line}\n')
        for line in code:
            file.write(f'{line}\n')


@log.performance
def toDb(db):
    ''' Inserts the parsed documentation into the database. Drops all rows before inserting 
        since this is a one shot deal.

        Params:
            - db: an instance of the Db class, passed as a parameter to enable testing 
    '''

    tables = ['doc_classes','doc_file_docs','doc_files','doc_folders','doc_functions','doc_imports','doc_todos']
    
    # Clear the tables of existing data. 
    for table in tables:
        sql = f'DELETE FROM {table} WHERE 1=1;'
        db.execute(sql)

    for folder in pyParser.folder_list:
        parent_id = folder.get('parent_id') if folder.get('parent_id') != None else 'NULL'
        name =  "'" +  folder.get('name') + "'" if folder.get('name') != None else 'NULL'
        sql = f'''
            INSERT INTO doc_folders ( folder_id,  parent_id, file_path, name )
            VALUES ({folder.get('folder_id')}, {parent_id}, '{folder.get('file_path')}', {name})
        '''   
        db.execute(sql)

    for file in pyParser.file_lines:
        sql = f'''
            INSERT INTO doc_files ( file_id, folder_id, file_path, name, ext, lines )
            VALUES ({file.get('file_id')}, {file.get('folder_id')}, '{file.get('file_path')}', '{file.get('name')}', '{file.get('ext')}', {file.get('length')})
        '''   
        db.execute(sql)
        
    for f_docs in pyParser.file_docs:
        sql = f'''
            INSERT INTO doc_file_docs ( file_id, docs )
            VALUES ({f_docs.get('file_id')}, '{f_docs.get('docs').replace("'","''")}')
        '''   
        db.execute(sql)

    for imp in pyParser.imports:
        module = "'" + imp.get('module') + "'" if imp.get('module') != None else 'NULL'
        
        obj = "'" + imp.get('object') + "'" if imp.get('object') != None else  'NULL'

        alias = "'" + imp.get('alias') + "'" if imp.get('alias') != None else  'NULL'

        sql = f'''
            INSERT INTO doc_imports ( import_id, file_id, module, object, alias, line_start )
            VALUES ({imp.get('import_id')}, {imp.get('file_id')}, {module}, {obj}, {alias}, {imp.get('line_no')})
        '''   
        db.execute(sql)

    for cls in pyParser.classes:
        dstring = 'NULL'
        if len(cls.get('docstring')) > 0:
            dstring =  "'" + '\n'.join(cls.get('docstring')).replace("'","''") + "'"

        params = 'NULL'
        if len(cls.get('parameters')) > 0:
            params =  "'" + ', '.join(cls.get('parameters')).replace("'","''") + "'"


        superclass = 'NULL'
        if len(cls.get('superclass')) > 0:
            superclass =  "'" + ', '.join(cls.get('superclass')) + "'"

        sql = f'''
            INSERT INTO doc_classes ( class_id, file_id, name, superclass, docstring, parameters, line_start, line_count )
            VALUES ({cls.get('class_id')}, {cls.get('file_id')}, '{cls.get('name')}', {superclass}, {dstring}, {params}, {cls.get('line_start')}, {cls.get('line_count')})
        '''   
        db.execute(sql)

    for fnc in pyParser.functions:
        dstring = 'NULL'
        if len(fnc.get('docstring')) > 0:
            dstring = "'" + '\n'.join(fnc.get('docstring')).replace("'","''") + "'"

        params = 'NULL'
        if len(fnc.get('parameters')) > 0:
            params = "'" + ', '.join(fnc.get('parameters')).replace("'","''") + "'"

        decorator = 'NULL'
        if len(fnc.get('decorators')) > 0:
            decorator = "'" + ', '.join(fnc.get('decorators')) + "'"

        parent_id = fnc.get('parent_id') if fnc.get('parent_id') != None else 'NULL'
        class_id  = fnc.get('class_id') if fnc.get('class_id') != None else 'NULL'
        rtns  = "'" + fnc.get('returns') + "'" if fnc.get('returns') != None else 'NULL'

        sql = f'''
            INSERT INTO doc_functions ( function_id, parent_id, file_id, class_id, name, docstring, parameters, returns, decorators, line_start, line_count )
            VALUES ({fnc.get('function_id')}, {parent_id}, {fnc.get('file_id')}, {class_id}, '{fnc.get('name')}', {dstring}, {params}, {rtns}, {decorator}, {fnc.get('line_start')}, {fnc.get('line_count')})
        '''   
        db.execute(sql)        


    for todo in pyParser.todo:
        sql = f'''
            INSERT INTO doc_todos ( todo_id,  file_id, line_start, line_count, todo )
            VALUES ({todo.get('todo_id')}, {todo.get('file_id')}, {todo.get('line_start')}, {todo.get('line_count')}, '{todo.get('line').replace("'", "''")}')
        '''   
        db.execute(sql)
