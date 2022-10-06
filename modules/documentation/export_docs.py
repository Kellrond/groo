import modules.documentation as documentation
from modules.documentation import py_parser
from datetime import datetime as dt

def toTxt(write_path):
    ''' Writes the documentation to a plaintext file. Might get in the way of grep so perhaps 
        the file gets moved after creation? 

        Params:
            - write_path: the filepath for the documentation to end up. 
    '''
    parser = py_parser.PyDocsParser()
    documentation.generateDocumentation()

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

    for folder in parser.folder_list:
        files += [f"{indent}{folder.get('file_path')}"]
        for fp in [ x for x in parser.file_lines if x.get('folder_id') == folder.get('folder_id')]:
            files += [f"{ indent * 2 }- {fp.get('file_path')}"]

    files += ["\n"]

    code = ["Source code documentation"]
    code += ["================================================================================"]
    code += [""]

    for folder in parser.folder_list:
        code += ["################################################################################"]
        code += [f"#  Folder  #   {folder.get('file_path')}  "]
        code += ["################################################################################"]
        code += [""]
        for fp in [ x for x in parser.file_lines if x.get('folder_id') == folder.get('folder_id')]:
            # Just grab the first file doc for the file. There should only be one. 
            file_docs = [ x for x in parser.file_docs if x.get('file_id') == fp.get('file_id')][0]
            file_classes = [ x for x in parser.classes if x.get('file_id') == fp.get('file_id')]
            file_functions = [ x for x in parser.functions if x.get('file_id') == fp.get('file_id')]
            file_imports = [ x for x in parser.imports if x.get('file_id') == fp.get('file_id')]


            code += ["--------------------------------------------------------------------------------"]
            code += [f"{ indent * 2 }{fp.get('file_path')}"]
            code += ["--------------------------------------------------------------------------------"]
            
            code += [file_docs.get('docs')]
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



