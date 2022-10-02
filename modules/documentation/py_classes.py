from crypt import methods
from modules.documentation import Docs
from modules import logging
# from database import docs_db

log = logging.Log(__name__)

class PyClassesDocs(Docs):
    @log.performance
    def __init__(self) -> None:
        
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
    def processPyClassDocs(self):
        self.flagClasses()
        self.flagClassDocstring()
        self.flagClassMethods()
        self.flagMethodParams()
        self.flagMethodDocstring()
        self.flagMethodReturnHint()
        self.flagNestedFunctions()

    @log.performance
    def flagClasses(self):
        ''' Find class start and endpoints in file and add appropriate flags '''
        for file in self.file_lines:
            prev_line_w_text = 0
            in_class = False

            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                if in_class == True:
                    # While in class we want to be sure we know where we are 
                    if line.get('whitespace') != 0:
                        line['flags'].append('cls')
                        if line.get('line').strip() != '':
                            prev_line_w_text = line.get('line_no')
                    # If we have 0 whitespace the class must be over. 
                    else:
                        in_class = False
                        file['lines'][prev_line_w_text]['flags'].append('cls end')
                        # Clear the extra flags from the blank lines
                        clear_flags = ['cls']
                        for i in range(prev_line_w_text + 1, line.get('line_no')):
                            file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x not in clear_flags ]     
                # A class may end and start in the same line so separate out the if statements.
                if in_class == False: 
                    if line.get('whitespace') == 0 and line.get('line')[0:5] == 'class':
                        in_class = True
                        line['flags'].append('cls')
                        line['flags'].append('cls start')

                        # Find and flag superclasses. Classes are sometimes written with the open/close parenthesis
                        # therefore the open and close parentheses must be more than a col apart 
                        open_pos = line.get('line').find('(')
                        close_pos = line.get('line').find(')')
                        if close_pos - open_pos > 1:
                            line['flags'].append('super cls')
            # Fix the flags at the end of the file
            if in_class:
                file['lines'][prev_line_w_text]['flags'].append('cls end')
                clear_flags = ['cls']
                for i in range(prev_line_w_text, line.get('line_no')):
                    file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x not in clear_flags ]   


    @log.performance
    def flagClassDocstring(self):
        ''' Find the start and end of doc strings and flag appropriately '''
        for file in self.file_lines:
            line_after_class_def = False
            in_docstring = False
            docs_start_pos = 0
            # Ignore non python files and continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                if line_after_class_def == True:
                    # docsings can start with either ''' or """. Find returns -1 if not in string 
                    # So check both and if max > -1 then we found one  
                    docs_start_pos = max([ line.get('line').find("'''"), line.get('line').find('"""') ])
                    if docs_start_pos > -1:
                        in_docstring = True
                        line['whitespace'] += 3
                        line['flags'].append('cls docs start')

                if in_docstring == True:
                    line['flags'].append('cls docs')
                    # If it's in the first line after the class definition and in_docstring == True
                    # the second set of quotes must be found to end the docstring 
                    if line_after_class_def:
                        closing_quotes = max([ line.get('line')[docs_start_pos+3:].find("'''"), line.get('line')[docs_start_pos+3:].find('"""') ])
                    else:
                        closing_quotes = max([ line.get('line').find("'''"), line.get('line').find('"""') ])

                    if closing_quotes > -1:
                        in_docstring = False
                        line['flags'] = [ x for x in line['flags'] if x != 'docs']
                        line['flags'].append('cls docs end')

                if in_docstring == False:
                    if 'cls start' in line.get('flags'):
                        line_after_class_def = True

                # We need to use the line_after_class_def flag to check for 2 sets of triple quotes
                # You only need the flag for the first line after the class declaration so turn it off 
                # except for when the 'class start' flag exists because the next line is the one we want
                # to search 
                if 'cls start' not in line.get('flags'):
                    line_after_class_def = False

    @log.performance
    def flagClassMethods(self):
        ''' Find and flag class methods '''
        for file in self.file_lines:
            in_method = False
            method_whitespace = 0
            prev_line_w_text  = 0
            # Ignore non python files and continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                # First make sure that we are in a class and not flagging a nested function
                if 'cls' in line.get('flags'):
                    if in_method == True:
                        # Check that another method has not started
                        if line.get('whitespace') == method_whitespace:
                            stripped_line = line.get('line').strip()
                            first_char = stripped_line[0] if len(stripped_line) > 0 else ''
                            
                            if first_char == '@':
                                # Technically we are starting a method here but since its not being
                                # declared we set it False
                                in_method = False
                                line['flags'].append('decorated')
                                file['lines'][prev_line_w_text]['flags'].append('meth end')
                                # Clear the extra flags from the blank lines
                                clear_flags = 'meth'
                                for i in range(prev_line_w_text + 1, line.get('line_no')):
                                    file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     

                            # If def continues over 1 line its possible to have the closing parenthesis inline with the def
                            elif first_char != ')':
                                in_method = False
                                file['lines'][prev_line_w_text]['flags'].append('meth end')
                                # clear flags between the end of the method and the line we are on  
                                clear_flags = 'meth'
                                for i in range(prev_line_w_text + 1, line.get('line_no')):
                                    file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     
                        
                        # If still in a method and tag as such
                        if in_method:
                            line['flags'].append('meth')
    
                    if in_method == False:
                        # Look for the start of methods
                        start = line.get('whitespace')
                        end = start + 4
                        if line.get('line')[start:end] == 'def ':                             
                            in_method = True
                            method_whitespace = line.get('whitespace')
                            line['flags'].append('meth start')
                            line['flags'].append('meth')
                            if line.get('line')[start:end+8] == 'def __init__':
                                line['flags'].append('init')
                # Catch the end of class and close off methods
                elif in_method and 'cls' not in line.get('flags'):
                    in_method = False
                    file['lines'][prev_line_w_text]['flags'].append('meth end')
                    clear_flags = 'meth'
                    for i in range(prev_line_w_text + 1, line.get('line_no')):
                        file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]   
            
                if line.get('line').strip() != '':
                    prev_line_w_text = line.get('line_no')

    @log.performance
    def flagMethodParams(self):
        for file in self.file_lines:
            if not self.isFileOfExtension(file, 'py'): # Ignore non python files
                continue     

            in_method_params = False      
            for line in file.get('lines'):
                # These 3 if's should remain as three ifs to ensure the right flags stay on
                if 'meth start' in line.get('flags'):
                    in_method_params = True
                    line['flags'].append('meth param start')

                if in_method_params:
                    line['flags'].append('meth param')

                if line.get('line').find(')') > -1 and in_method_params:
                    in_method_params = False
                    line['flags'].append('meth param end')

    @log.performance
    def flagMethodDocstring(self):
        for file in self.file_lines:
            if not self.isFileOfExtension(file, 'py'): # Ignore non python files
                continue       

            line_after_method_def = False
            in_docstring = False   
            docs_start_pos = 0
            for line in file.get('lines'):
                if 'meth param end' in line.get('flags'):
                    # If its the start of the method start looking for the docstring. It wont be on this line so continue
                    line_after_method_def = True
                    continue

                if 'meth' in line.get('flags'):
                    if line_after_method_def:
                        # docstrings can start with either ''' or """. Find returns -1 if not in string 
                        # So check both and if max > -1 then we found one  
                        docs_start_pos = max([ line.get('line').find("'''"), line.get('line').find('"""') ])
                        if docs_start_pos > -1:
                            in_docstring = True
                            line['whitespace'] += 3
                            line['flags'].append('meth docs start')      
                        else: 
                            # There is no docstring stop looking 
                            line_after_method_def = False
                            continue

                if in_docstring:
                    line['flags'].append('meth docs') 
                    # Check for single liner
                    if line_after_method_def:
                        closing_quotes = max([ line.get('line')[docs_start_pos+3:].find("'''"), line.get('line')[docs_start_pos+3:].find('"""') ])
                    else:
                        closing_quotes = max([ line.get('line').find("'''"), line.get('line').find('"""') ])

                    if closing_quotes > -1:
                        in_docstring = False
                        line['flags'] = [ x for x in line['flags'] if x != 'docs']
                        line['flags'].append('meth docs end')

                # We need to use the line_after_method_def flag to check for 2 sets of triple quotes
                # You only need the flag for the first line after the class declaration so turn it off 
                # except for when the 'meth start' flag exists because the next line is the one we want
                # to search
                if 'meth param end' not in line.get('flags'):
                    line_after_method_def = False
         
    @log.performance
    def flagMethodReturnHint(self):

        for file in self.file_lines:
            if not self.isFileOfExtension(file, 'py'): # Ignore non python files
                continue       
            for line in file.get('lines'): 
                if 'meth param end' in line.get('flags'):
                    if line.get('line').find('->') > -1:
                        line['flags'].append('meth return')

    @log.performance
    def flagNestedFunctions(self):
        ''' This is a pretty long function. It could be broken up, but it works.'''
        for file in self.file_lines:
            in_nested_method = False
            in_params = False
            in_docs = False
            nested_whitespace = 0
            prev_line_w_text  = 0
            # Ignore non python files and continue to next file
            if not self.isFileOfExtension(file, 'py'):
                continue

            for line in file.get('lines'):
                # First make sure that we are in a method
                if 'meth' in line.get('flags'):

                    if in_nested_method == False:
                        if 'meth' not in line.get('flags'):
                            continue # to next line
                        if 'meth start' in line.get('flags'):
                            continue # wont start a nested function here 

                        # Look for the start of methods
                        start = line.get('whitespace')
                        end = start + 4
                        if line.get('line')[start:end] == 'def ':                             
                            in_nested_method = True
                            in_params = True
                            nested_whitespace = line.get('whitespace')
                            line['flags'].append('nest meth start')
                            line['flags'].append('nest meth param start')
                    
                        if line.get('line').find(')') > -1 and in_params:
                            in_params = False
                            line['flags'].append('nest meth param')
                            line['flags'].append('nest meth param end')
                            if line.get('line').find('->') > -1:
                                line['flags'].append('nest meth return')   

                    if in_nested_method == True:
                        if in_params:
                            line['flags'].append('nest meth param')
                            if line.get('line').find(')') > -1:
                                in_params = False
                                line['flags'].append('nest meth param end')
                                if line.get('line').find('->') > -1:
                                    line['flags'].append('nest meth return')   

                        # Check that another method has not ended 
                        if line.get('whitespace') == nested_whitespace and 'nest meth start' not in line.get('flags'):
                            in_nested_method = False
                            file['lines'][prev_line_w_text]['flags'].append('nest meth end')
                            # Clear flags between the end of the method and the line we are on  
                            clear_flags = 'nest meth'
                            for i in range(prev_line_w_text + 1, line.get('line_no')):
                                file['lines'][i]['flags'] = [ x for x in file['lines'][i]['flags'] if x != clear_flags ]     
                        
                            if line.get('line')[line.get('whitespace'):line.get('whitespace')+4] == 'def ':
                                line['flags'].append('nest meth start')
                                line['flags'].append('nest meth param start')
                                in_nested_method = True
                                in_params = True

                        # Docstring 
                        if in_docs or line.get('line').find("'''") > -1 or line.get('line').find('"""') > -1:
                            line['flags'].append('nest meth docs')
                            first_three = line.get('line')[line.get('whitespace'):line.get('whitespace')+3]
                            if first_three == '"""' or first_three == "'''":
                                if in_docs:
                                    in_docs = False
                                    line['flags'].append('nest meth docs end')
                                    continue # To next line
                                in_docs = True
                                line['flags'].append('nest meth docs start')
                                remaining_line = line.get('line')[line.get('whitespace')+3:]
                                if remaining_line.find('"""') > -1 or remaining_line.find("'''") > -1:
                                    in_docs = False
                                    line['flags'].append('nest meth docs end')
                            else: # This line must be an additional line
                                # Check if it closes
                                if line.get('line').find('"""') > -1 or line.get('line').find("'''") > -1:
                                    in_docs = False
                                    line['flags'].append('nest meth docs end')
                           
                        # If still in a method and tag as such
                        if in_nested_method:
                            line['flags'].append('nest meth')

                    if line.get('line').strip() != '':
                        prev_line_w_text = line.get('line_no')