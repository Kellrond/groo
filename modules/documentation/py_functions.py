import config
from modules.documentation import Docs
from modules import logging

log = logging.Log(__name__)

class PyFunctionDocs(Docs):
    @log.performance
    def __init__(self) -> None:
        self.config = config.modules.Documentation
        super().__init__()
        self.readLines()

    @classmethod
    @log.performance
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    @log.performance
    def processPyFunctionDocs(self):
        ''' Runs all of the flagging in order. When in doubt this is the correct order '''
        self.flagFunctions()
        self.flagFunctionParams()
        self.flagFunctionDocstring()
        self.flagNestedFunctions()
        log.verbose('Python documentation generator: Functions')

    @log.performance
    def flagFunctions(self):
        ''' Find and flag functions '''
        for file in self.file_lines:
            in_function = False
            prev_line_w_text  = 0
            # Ignore non python files and continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                # First make sure that we are in a class and not flagging a nested function
                if 'cls' in line.get('flags'):
                    continue # If in a class it's a method and will get picked up in the classes file
                if in_function == True:
                    # Check if the function is finished
                    if line.get('whitespace') == 0:
                        
                        first_char = line.get('line')[0] if len(line.get('line')) > 0 else ''
                        
                        if first_char == '@':
                            # Technically we are starting a method here but since its not being
                            # declared we set it False
                            in_function = False
                            line['flags'].append('decorated')
                            file['lines'][prev_line_w_text]['flags'].append('func end')
                            # Clear the extra flags from the blank lines
                            clear_flags = 'func'
                            for i in range(prev_line_w_text + 1, line.get('line_no')):
                                file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     

                        # If def continues over 1 line its possible to have the closing parenthesis inline with the def
                        elif first_char != ')':
                            in_function = False
                            file['lines'][prev_line_w_text]['flags'].append('func end')
                            # clear flags between the end of the method and the line we are on  
                            clear_flags = 'func'
                            for i in range(prev_line_w_text + 1, line.get('line_no')):
                                file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     
                    
                    # If still in a method and tag as such
                    if in_function:
                        line['flags'].append('func')

                if in_function == False:
                    # Look for the start of methods
                    if line.get('line')[0:4] == 'def ':                             
                        in_function = True
                        line['flags'].append('func start')
                        line['flags'].append('func')

                if line.get('line').strip() != '':
                    prev_line_w_text = line.get('line_no')

            if in_function: # we are past the for loop now close off any open tags
                file['lines'][-1]['flags'].append('func end')

    @log.performance
    def flagFunctionParams(self):
        for file in self.file_lines:
            if not self.isFileOfExtension(file, 'py'): # Ignore non python files
                continue     

            in_function_params = False      
            for line in file.get('lines'):
                # These 3 if's should remain as three ifs to ensure the right flags stay on
                if 'func start' in line.get('flags'):
                    in_function_params = True
                    line['flags'].append('func param start')

                if in_function_params:
                    line['flags'].append('func param')

                if line.get('line').find(')') > -1 and in_function_params:
                    in_function_params = False
                    line['flags'].append('func param end')
                    # Look for a return hint
                    if line.get('line').find('->') > -1:
                        line['flags'].append('func return')

    @log.performance
    def flagFunctionDocstring(self):
        for file in self.file_lines:
            if not self.isFileOfExtension(file, 'py'): # Ignore non python files
                continue       

            line_after_function_def = False
            in_docstring = False   
            docs_start_pos = 0
            for line in file.get('lines'):
                if 'func param end' in line.get('flags'):
                    # If its the start of the function, start looking for the docstring. 
                    line_after_function_def = True
                    continue # to the next line. This line wont have the docstring

                if 'func' in line.get('flags'):
                    if line_after_function_def:
                        # docstrings can start with either ''' or """. Find returns -1 if not in string 
                        # So check both and if max > -1 then we found one  
                        docs_start_pos = max([ line.get('line').find("'''"), line.get('line').find('"""') ])
                        if docs_start_pos > -1:
                            in_docstring = True
                            line['whitespace'] += 3
                            line['flags'].append('func docs start')      
                        else: 
                            # There is no docstring stop looking 
                            line_after_function_def = False
                            continue

                if in_docstring:
                    line['flags'].append('func docs') 
                    # Check for single liner
                    if line_after_function_def:
                        closing_quotes = max([ line.get('line')[docs_start_pos+3:].find("'''"), line.get('line')[docs_start_pos+3:].find('"""') ])
                    else:
                        closing_quotes = max([ line.get('line').find("'''"), line.get('line').find('"""') ])

                    if closing_quotes > -1:
                        in_docstring = False
                        line['flags'] = [ x for x in line['flags'] if x != 'docs']
                        line['flags'].append('func docs end')

                # We need to use the line_after_function_def flag to check for 2 sets of triple quotes only
                if 'func param end' not in line.get('flags'):
                    line_after_function_def = False
         
    @log.performance
    def flagNestedFunctions(self):
        ''' This is a pretty long function. It could be broken up, but it works.'''
        for file in self.file_lines:
            in_nested_function = False
            in_params = False
            in_docs = False
            nested_whitespace = 0
            prev_line_w_text  = 0
            # Ignore non python files and continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                # First make sure that we are in a function
                if 'func' in line.get('flags'):
                    if in_nested_function == False:
                        if 'func' not in line.get('flags'):
                            continue # to next line
                        if 'func start' in line.get('flags'):
                            continue # wont start a nested function here 

                        # Look for the start of methods
                        start = line.get('whitespace')
                        end = start + 4
                        if line.get('line')[start:end] == 'def ':                             
                            in_nested_function = True
                            in_params = True
                            nested_whitespace = line.get('whitespace')
                            line['flags'].append('nest func start')
                            line['flags'].append('nest func param start')
                    
                        if line.get('line').find(')') > -1 and in_params:
                            in_params = False
                            line['flags'].append('nest func param')
                            line['flags'].append('nest func param end')
                            if line.get('line').find('->') > -1:
                                line['flags'].append('nest func return')   

                    if in_nested_function == True:
                        if in_params:
                            line['flags'].append('nest func param')
                            if line.get('line').find(')') > -1:
                                in_params = False
                                line['flags'].append('nest func param end')
                                if line.get('line').find('->') > -1:
                                    line['flags'].append('nest func return')   

                        # Check that another method has not ended 
                        if line.get('whitespace') == nested_whitespace and 'nest func start' not in line.get('flags'):
                            in_nested_function = False
                            file['lines'][prev_line_w_text]['flags'].append('nest func end')
                            # Clear flags between the end of the method and the line we are on  
                            clear_flags = 'nest func'
                            for i in range(prev_line_w_text + 1, line.get('line_no')):
                                file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     
                        
                            if line.get('line')[line.get('whitespace'):line.get('whitespace')+4] == 'def ':
                                line['flags'].append('nest func start')
                                line['flags'].append('nest func param start')
                                in_nested_function = True
                                in_params = True
                            # Check that the params didn't just close. 
                            if line.get('line').find(')') > -1 and in_params:
                                in_params = False
                                line['flags'].append('nest func param')
                                line['flags'].append('nest func param end')
                                if line.get('line').find('->') > -1:
                                    line['flags'].append('nest func return')   

                        # Docstring 
                        if in_docs or line.get('line').find("'''") > -1 or line.get('line').find('"""') > -1:
                            line['flags'].append('nest func docs')
                            first_three = line.get('line')[line.get('whitespace'):line.get('whitespace')+3]
                            if first_three == '"""' or first_three == "'''":
                                if in_docs:
                                    in_docs = False
                                    line['flags'].append('nest func docs end')
                                    continue # To next line
                                in_docs = True
                                line['flags'].append('nest func docs start')
                                remaining_line = line.get('line')[line.get('whitespace')+3:]
                                if remaining_line.find('"""') > -1 or remaining_line.find("'''") > -1:
                                    in_docs = False
                                    line['flags'].append('nest func docs end')
                            else: # This line must be an additional line
                                # Check if it closes
                                if line.get('line').find('"""') > -1 or line.get('line').find("'''") > -1:
                                    in_docs = False
                                    line['flags'].append('nest func docs end')
                           
                        # If still in a method and tag as such
                        if in_nested_function:
                            line['flags'].append('nest func')

                    if line.get('line').strip() != '':
                        prev_line_w_text = line.get('line_no')