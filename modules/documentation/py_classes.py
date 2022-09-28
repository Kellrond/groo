from modules.documentation import Docs
# from database import docs_db


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

