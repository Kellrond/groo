from modules.documentation import Docs
# from database import docs_db

class FunctionsDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.functions  = []

    def rebuildFunctionsDocs(self):
        self.functions = self.generateDocumentation(self.__parse_functions)
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

