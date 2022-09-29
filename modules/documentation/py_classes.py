from modules.documentation import Docs
from modules import logging
# from database import docs_db

log = logging.Log(__name__)

class ClassesDocs(Docs):
    def __init__(self) -> None:
        super().__init__()
        self.classes  = []

    @classmethod
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    def processPyClassDocs(self):
        pass

    def flagClasses(self):
        ''' Find class start and endpoints in file and add appropriate flags '''
        for file in self.file_lines:
            prev_line_w_text = 0
            in_class = False
            # Start reading the lines of the file
            for line in file.get('lines'):
                if in_class == True:
                    # While in class we want to be sure we know where we are 
                    if line.get('whitespace') != 0:
                        line['flags'].append('class')
                        if line.get('line').strip() != '':
                            prev_line_w_text = line.get('line_no')
                    # If we have 0 whitespace the class must be over. 
                    else:
                        in_class = False
                        file['lines'][prev_line_w_text]['flags'].append('class end')
                        # Clear the extra flags from the blank lines
                        clear_flags = ['class']
                        for i in range(prev_line_w_text + 1, line.get('line_no')):
                            file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x not in clear_flags ]     
                # A class may end and start in the same line so separate out the if statements.
                if in_class == False: 
                    if line.get('whitespace') == 0 and line.get('line')[0:5] == 'class':
                        line['flags'].append('class')
                        line['flags'].append('class start')
                        in_class = True
            # Fix the flags at the end of the file
            if in_class:
                file['lines'][prev_line_w_text]['flags'].append('class end')
                clear_flags = ['class']
                for i in range(prev_line_w_text, line.get('line_no')):
                    file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x not in clear_flags ]   


    def flagClassDocstring(self):
        ''' Find the start and end of doc strings and flag appropriately '''
        for file in self.file_lines:
            looking_for_docstring = False
            in_docstring = False
            for line in file.get('lines'):
                if looking_for_docstring == True:
                    if line.get('line').find("'''") > -1 or line.get('line').find('"""') > -1:
                        in_docstring = True
                        # Replace the first ''' or """ of the docstring so we can search for it again
                        line['line'] = line['line'].replace("'''","   ",1)
                        line['line'] = line['line'].replace('"""',"   ",1)
                        line['whitespace'] += 3
                        line['flags'].append('docstr start')
                    looking_for_docstring = False

                if in_docstring == True:
                    if 'docstr start' not in line.get('flags'):
                        line['flags'].append('docstr')
                    # If ''' or """ this is the end of the docstring so lets wrap it up
                    if line.get('line').find("'''") > -1 or line.get('line').find('"""') > -1:
                        in_docstring = False
                        line['line'] = line['line'].replace("'''","   ",1)
                        line['line'] = line['line'].replace('"""',"   ",1)
                        line['flags'] = [ x for x in line['flags'] if x != 'docstr']
                        line['flags'].append('docstr end')
                        
                if in_docstring == False:
                    if 'class start' in line.get('flags'):
                        looking_for_docstring = True

    def flagClassMethods(self):
        ''' Find and flag class methods '''
        for file in self.file_lines:
            in_method = False
            method_whitespace = 0
            prev_line_w_text  = 0
            for line in file.get('lines'):
                if 'class' in line.get('flags'):
                    if in_method == True:
                        line['flags'].append('method')
                        # Check that another method has not started
                        if line.get('whitespace') == method_whitespace:
                            in_method = False
                            file['lines'][prev_line_w_text]['flags'].append('method end')
                            # Clear the extra flags from the blank lines
                            clear_flags = ['method']
                            for i in range(prev_line_w_text + 1, line.get('line_no')):
                                file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x not in clear_flags ]     

                            start = line.get('whitespace')
                            end = start + 4
                            if line.get('line')[start:end] == 'def ':
                                line['flags'].append('method start')
                                in_method = True

                    if in_method == False:
                        # Look for the start of methods
                        start = line.get('whitespace')
                        end = start + 4
                        if line.get('line')[start:end] == 'def ':                             
                            in_method = True
                            method_whitespace = line.get('whitespace')
                            line['flags'].append('method')
                            line['flags'].append('method start')


                if line.get('line').strip() != '':
                    prev_line_w_text = line.get('line_no')


    def debug_file_lines(self):
        # This bit is for printing the result of this function   
        for file in self.file_lines:
            prev_line_w_text = 0
            in_class = False
            for line in file.get('lines'):
                print(line.get('line_no'), line.get('flags'), line.get('line'))
                
    def rebuildClassesDocs(self):
        self.classes = self.generateDocumentation(self.__parse_classes)
        # self.__update_classes_db()

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

    # def __update_classes_db(self):
    #     docs_db.updateDocClassesDb(self.classes)

