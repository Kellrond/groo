from glob import glob
# from database import docs_db

class Docs:
    def __init__(self) -> None:
        self.file_paths = []
        self.folder_list = []
        self.ext_list    = ['py', 'html', 'txt', 'sh','sql', 'js', 'css', 'md', 'wsgi', 'yml']
        self.__generate_folder_list()
        self.__generate_file_paths()
    
    def __generate_folder_list(self):
        folder_list = glob(f"./**/", recursive=True)

        # Remove the ./ in front
        folder_list = [ x[2:] for x in folder_list ]

        # Remove ignored first tier folders
        ignore_folders_list = ['venv', 'styling']
        for ignored_folder in ignore_folders_list:
            folder_list  = [ x for x in folder_list if x[:len(ignored_folder)] != ignored_folder ]


        folder_list = [ x for x in folder_list if x.find('__pycache__') == -1 ]
        folder_list = [ {'file_path': x, 'split_file_path': [ sq for sq in x.split('/') if sq != '' ], 'folder_id': i } for i, x in enumerate(folder_list) ]

        self.folder_list = folder_list

    def __generate_file_paths(self):
        for folder in self.folder_list:
            for ext in self.ext_list:
                self.file_paths += glob(f"{ folder.get('file_path') }*.{ ext }")

    def update_folders_and_files_db(self):
        docs_db.updateDocFolderDb(self.folder_list)
        docs_db.updateDocFilesDb(self.file_paths)

    def generate_documentation(self, param_func) -> list:
        document_list = []
        for file_path in self.file_paths:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                routes_in_file = param_func(lines, file_path)
                if len(routes_in_file) > 0:
                    document_list += routes_in_file 
        return document_list 


class ClassesDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.classes  = []
        
    def rebuildClassesDocs(self):
        self.classes = self.generate_documentation(self.__parse_classes)
        self.__update_classes_db()

    def __parse_classes(self, file_lines, file_path):
        parsed_list = []
        def new_class_dict() -> dict:
            return {
                'file_path': file_path,
                'name': '',
                'superclass': [],
                'parameters': '',
                'docstring': '',
                'methods': []
                }

        def new_funct_dict() -> dict:
            return {
                'file_path': file_path,
                'name': '',
                'parameters': [],
                'returns': '',
                'docstring': ''
            }

        class_dict  = new_class_dict()
        func_dict   = new_funct_dict()
        in_class    = False
        in_function = False
        in_func_def = False
        check_for_docstring = False
        check_for_func_docstring = False
        in_doc_string = False
        for line in file_lines:
        
            # END OF CLASS   
            #   This must come first since a second class definition typically follows the first. 
            #   Therefore we need to end a class first then check for a new class
            #   Docstrings may also end up in the first column of a file so we want to check that flag      
            if in_class and not in_doc_string and not check_for_docstring and not check_for_func_docstring and (ord(line[:1]) in range(65, 123)):
                if len(class_dict['methods']) > 0 and class_dict['methods'][0].get('name') == '__init__':
                    init_func = class_dict['methods'].pop(0)
                    class_dict['parameters'] = init_func.get('parameters')[4:]
                    if len(class_dict['parameters']) >0 and class_dict['parameters'][0] == ',':
                        class_dict['parameters'] = class_dict['parameters'][1:].strip()

                parsed_list.append(class_dict)
                class_dict = new_class_dict()
                in_class = False

            # START OF CLASS
            # Lets start a new class if we spot the definition, gather up the doc string and append the class dict when out of the class
            if line[:5] == 'class':
                in_class   = True
                in_doc_string = False
                check_for_docstring = True

                if line.find('(') > -1:
                    class_dict['name']      = line[6:line.find('(')]
                    class_dict['superclass'] = line[line.find('(')+1:line.find(')')].split(',')
                    class_dict['superclass'] = [ x.strip() for x in class_dict['superclass'] if x != '' ]
                else:
                    class_dict['name'] = line[6:line.find(':')]

            # work with the docstring
            elif not in_function and (check_for_docstring or in_doc_string):
                # First we check for docstring. If we dont find it turn off checking for docstring
                if check_for_docstring and line.find("'''") == -1:
                    check_for_docstring = False
                # While still checking we found a ''' so we turn off checking and turn on in doc string and write it
                elif not in_doc_string and line.find("'''") > -1:
                    check_for_docstring = False
                    in_doc_string = True
                    class_dict['docstring'] = line[line.find("'''")+3:]
                elif in_doc_string:
                    class_dict['docstring'] += line

                # Now look for the ending ''' to the doc string
                if class_dict.get('docstring','').find("'''") > -1:
                    in_doc_string = False
                    class_dict['docstring'] = class_dict.get('docstring','').replace("'''","").strip()

            # DURING CLASS
            # start a new if block so that the doc string check doesn't wipe out the def __init__(self, .. ):
            if in_class:

                # Function parsing
                stripped_ln = line.strip()
                if not in_function and stripped_ln[:4] == 'def ':            
                    func_dict = new_funct_dict()
                    func_dict['name'] = stripped_ln[4:stripped_ln.find('(')]
                    func_dict['parameters'] = stripped_ln[stripped_ln.find('(')+1:]
                    in_function = True
                    in_func_def = True

                if in_func_def and func_dict['parameters'].find(')') > -1:
                    params = func_dict['parameters']
                    if params.find('->') > -1:
                        rtn_arrow_pos = params.find('->')
                        func_end_pos = params[rtn_arrow_pos:].find(':') + rtn_arrow_pos
                        func_dict['returns'] = params[rtn_arrow_pos+2:func_end_pos].strip()

                    func_dict['parameters'] = params[:params.find(')')]

                    in_func_def = False 
                    check_for_func_docstring = True

                # FUNCTION DOCSTRING
                if in_function and ( check_for_func_docstring or in_doc_string ) and stripped_ln[:3] != 'def':

                    # First we check for docstring. If we dont find it turn off checking for docstring
                    if check_for_func_docstring and line.find("'''") == -1:
                        check_for_func_docstring = False
                    # While still checking we found a ''' so we turn off checking and turn on in doc string and write it
                    elif not in_doc_string and line.find("'''") > -1:
                        check_for_func_docstring = False
                        in_doc_string = True
                        func_dict['docstring'] = line[line.find("'''")+3:]
                    elif in_doc_string:
                        func_dict['docstring'] += line

                    # Now look for the ending ''' to the doc string
                    if func_dict.get('docstring','').find("'''") > -1:
                        in_doc_string = False
                        func_dict['docstring'] = func_dict.get('docstring','').replace("'''","").strip()

                # Once we enter the function we are either in the def or the docstring. 
                # If those are both False we must be out of the function definition
                if in_function and (not in_func_def and not in_doc_string and not check_for_func_docstring):
                    in_function = False
                    class_dict['methods'].append(func_dict)

        # catch the last class if the loop ends with a class
        if len(class_dict.get('name')) > 0:
            parsed_list.append(class_dict)
            if len(class_dict['methods']) > 0 and class_dict['methods'][0].get('name') == '__init__':
                init_func = class_dict['methods'].pop(0)
                class_dict['parameters'] = init_func.get('parameters')[4:]
                if len(class_dict['parameters']) >0 and class_dict['parameters'][0] == ',':
                    class_dict['parameters'] = class_dict['parameters'][1:].strip()
        return parsed_list

    def __update_classes_db(self):
        docs_db.updateDocClassesDb(self.classes)


class FunctionsDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.functions  = []

    def rebuildFunctionsDocs(self):
        self.functions = self.generate_documentation(self.__parse_functions)
        self.__update_functions_db()

    def __parse_functions(self, file_lines, file_path) -> list:
        parsed_list = []
        def new_funct_dict() -> dict:
            return {
                'file_path': file_path,
                'name': '',
                'parameters': [],
                'returns': '',
                'docstring': ''
            }
        func_dict   = new_funct_dict()
        in_function = False
        in_func_def = False
        check_for_func_docstring = False
        in_doc_string = False
        for line in file_lines:

            if not in_function and line[:4] == 'def ':            
                func_dict = new_funct_dict()
                func_dict['name'] = line[4:line.find('(')]
                func_dict['parameters'] = line[line.find('(')+1:]
                in_function = True
                in_func_def = True

            if in_func_def and func_dict['parameters'].find(')') > -1:
                params = func_dict['parameters']
                if params.find('->') > -1:
                    rtn_arrow_pos = params.find('->')
                    func_end_pos = params[rtn_arrow_pos:].find(':') + rtn_arrow_pos
                    func_dict['returns'] = params[rtn_arrow_pos+2:func_end_pos].strip()

                func_dict['parameters'] = params[:params.find(')')]

                in_func_def = False 
                check_for_func_docstring = True

            # FUNCTION DOCSTRING
            if in_function and ( check_for_func_docstring or in_doc_string ) and line[:3] != 'def':

                # First we check for docstring. If we dont find it turn off checking for docstring
                if check_for_func_docstring and line.find("'''") == -1:
                    check_for_func_docstring = False
                # While still checking we found a ''' so we turn off checking and turn on in doc string and write it
                elif not in_doc_string and line.find("'''") > -1:
                    check_for_func_docstring = False
                    in_doc_string = True
                    func_dict['docstring'] = line[line.find("'''")+3:]
                elif in_doc_string:
                    func_dict['docstring'] += line

                # Now look for the ending ''' to the doc string
                if func_dict.get('docstring','').find("'''") > -1:
                    in_doc_string = False
                    func_dict['docstring'] = func_dict.get('docstring','').replace("'''","").strip()

            # Once we enter the function we are either in the def or the docstring. 
            # If those are both False we must be out of the function definition
            if in_function and (not in_func_def and not in_doc_string and not check_for_func_docstring):
                in_function = False
                parsed_list.append(func_dict)
        
        return parsed_list

    def __update_functions_db(self):
        docs_db.updateDocFunctionsDb(self.functions)


class DependencyDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.dependencies  = []

    def rebuilddependencyDocs(self):
        self.dependencies = self.generate_documentation(self.__parse_dependencies)
        self.__update_dependencies_db()

    def __parse_dependencies(self, file_lines, file_path) -> list:
        parsed_list = []
        def new_depend_dict() -> dict:
            return {
                'file_path': file_path,
                'module': '',
                'objects': []
            }

        filtered_lines = []
        importing = False
        new_line = ''
        for line in file_lines:
            # Check if line starts with an import statement
            if line.split(' ')[0] in ['from', 'import'] and file_path[-3:] == '.py':
                # The line above may be importing and we need to write the old line before starting again 
                if importing:
                    filtered_lines.append(new_line)
                    importing = False
                # Write the new line
                new_line = line
                # Check if the import statement is continued over lines
                if new_line.find('\\') != -1:
                    new_line = new_line[:new_line.find('\\')]
                    importing = True
                else:
                    filtered_lines.append(new_line)
                    importing = False
                    new_line = ''
            elif importing:
                new_line += line
                if new_line.find('\\') != -1:
                    new_line = new_line[:new_line.find('\\')]
                else:
                    filtered_lines.append(new_line)
                    importing = False
                    new_line = ''

        for line in filtered_lines:
            depend_dict   = new_depend_dict()
            if line[:4] == 'from':
                split_list = line[4:].split('import')
                depend_dict['module'] = split_list[0].strip()
                obj_list = [ x.strip() for x in split_list[1].split(',') ]
                depend_dict['objects'] = [ x.split(' as ')[0] for x in obj_list ]
            else:
                line = line[6:].strip()
                depend_dict['module'] = line.split(' as ')[0].strip()
            parsed_list.append(depend_dict)

        return parsed_list

    def __update_dependencies_db(self):
        docs_db.updateDocDependencyDb(self.dependencies)
 

class RoutesDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.routes  = []

    def rebuildRoutesDocs(self):
        self.routes = self.generate_documentation(self.__parse_flask_routing_lines)
        self.__update_routes_db()

    def __parse_flask_routing_lines(self, file_lines, file_path) -> list:
        ''' Returns the usefull information from the flask routing definitions '''
        parsed_list = []
        def new_route() -> dict:
            return {
                'file_path': file_path,
                'route': [],
                'permissions': '',
                }

        route_dict = new_route()
        for line in file_lines:
            if line.find('@bp.route(') > -1 and file_path != 'docs/__init__.py':
                s_pos = 11
                single_quote = line[s_pos:].find("'")
                double_quote = line[s_pos:].find('"')
                comma = line[s_pos:].find(',')
                comma = comma if comma > -1 else 999
                # the comma is to catch any cases where the route and method string quotes are mismatched
                if single_quote > -1 and single_quote < comma:
                    e_pos = s_pos + single_quote
                elif double_quote > -1 and double_quote < comma:
                    e_pos = s_pos + double_quote

                url = line[s_pos:e_pos]
                #Check if method is defined or default to GET
                s_pos = line.find('methods=[')
                if s_pos > -1:
                    s_pos = s_pos + 8
                    e_pos = line.find(']') + 1
                    list_str = line[s_pos:e_pos]
                    methods = eval(list_str)
                else:
                    methods = ['GET']
                
                route_dict['route'].append({'url': url, 'methods': methods})
                prev_line = line
            else:
                if len(route_dict['route']) > 0:
                    if line.find('#@permissions_required(config.Permissions.') > -1:
                        route_dict['permissions'] = line[41:line.find(')')]
                    parsed_list.append(route_dict)
                    route_dict = new_route()
                prev_line = line
        return parsed_list

    def __update_routes_db(self) -> bool:
        return docs_db.updateDocRoutesDb(self.routes)


def parseDocstringToHtml(docstr):
    docstr = [ x.strip() for x in docstr.split('\n') if x.strip() != '' ]
    
    in_p    = False
    in_list = False
    in_code = False

    html = ''
    useage_str = ''

    for line in docstr:
        # Look for list items
        if line[:1] == '-' and not in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if not in_list:
                in_list = True
                html += '<ul>'
            line = '• ' + line[1:]
            html += f'<li>{ line }</li>'
        # Code blocks
        elif line[:1] == '`' or in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if in_list:
                in_list = False
                html += '</ul>'
            
            if not in_code:
                in_code = True
                useage_str = f'<code>&nbsp;&nbsp;&nbsp;&nbsp;{ line.strip()[1:] }'
            else:
                useage_str += f'<br />&nbsp;&nbsp;&nbsp;&nbsp;{ line }'

            if line.strip()[-1:] == '`':
                in_code = False
                html += f'{ useage_str.strip()[:-1] }</code><br />'

        # Look for header
        elif line.find(':') > -1 and not in_code:
            if in_p:
                in_p = False
                html += '</p>'
            if in_list:
                in_list = False
                html += '</ul>'
            html += f'<strong>{ line }</strong><br />'
        else:
            if not in_p:
                in_p = True
                html += f'<p>'

            # safety_count = 0
            while line.find('`') > -1:
                # if safety_count > 10:
                #     break
                pos = line.find('`')
                pos2 = pos + line[pos+1:].find('`') + 1

                code_str = line[pos+1: pos2].replace('<', '&lt;')

                line = line[:pos] + '<span style="font-family:courier;">&nbsp;' + code_str + '</span>' + line[pos2+1:]
                # safety_count += 1
            html += f' { line}'
    return html

