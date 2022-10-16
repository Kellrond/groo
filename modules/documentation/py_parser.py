''' This file holds the PyParser class which goes through each line and parses code 
    documentation from file_lines
'''
# Internal
import  config
from    modules.documentation import Docs
from    modules import logging, utilities


log = logging.Log(__name__)

class_id_gen    = utilities.generateIntegerSequence()
function_id_gen = utilities.generateIntegerSequence()
# Meta Id's
todo_id_gen   = utilities.generateIntegerSequence()
import_id_gen = utilities.generateIntegerSequence()
file_comment_id_gen = utilities.generateIntegerSequence()
 
# TODO: ! This is not showing up in documentation

class PyParser(Docs):
    ''' This class parses the flags which were set by the other documentation classes.

        The class variables are the final output of the parser
            - classes
            - functions
            - file_docs
            - imports
            - todo

        Others are listed under the Docs class, which is available here as well due to the superclass.
            - folder_list
            - file_lines
    '''    

    classes = []
    functions = []
    file_docs = []
    imports = []
    todo = []

    def __init__(self) -> None:
        self.config = config.modules.Documentation
        super().__init__()

    @classmethod
    @log.performance
    def from_test_conf(cls, config):
        ''' Loads a test configuration file and returns an instance of the class '''
        test_class = cls()
        test_class.config = config
        log.verbose('Test class instantiated')
        return test_class

    @log.performance
    def parsePython(self):
        ''' Takes the flagged lines and converts them into objects'''
        log.verbose('Start parsing Python documentation')
        for file in self.file_lines:
            py_class_lines = []
            py_meta_lines  = []
            py_func_lines  = []
            for line in file.get('lines'):
                flags = line.get('flags')

                if file.get('file_path') == './modules/documentation/py_parser.py':
                    print(line)
                # Can either be a class or a function not both
                if 'cls' in flags:
                    py_class_lines.append(line)
                elif 'func' in flags or 'decorated' in flags:
                    py_func_lines.append(line)
                # But imports and todos can exist in both classes and functions
                if 'import' in flags or 'file docs' in flags or 'todo' in flags:
                    py_meta_lines.append(line)

            self.__parse_classes(file, py_class_lines)
            self.__parse_functions(file, py_func_lines)
            self.__parse_meta(file, py_meta_lines)
        log.verbose('Stop parsing Python documentation')

    @log.performance
    def __parse_classes(self, file:dict, lines:list):
        ''' Extract the class docs data like parameters, returns, docstring, methods, and nested methods.
            This is fed individual files at a time. 
        
            Params: 
                - file: i in Doc.file_lines[i] has meta data we want to add to records
                - lines: a filtered list of lines containing relevant flags
        '''
        file_id  = file.get('file_id')

        # Split classes into their own lists
        class_list = []
        class_lines = []
        for ln_dict in lines:
            class_lines.append(ln_dict)
            flags = ln_dict.get('flags')
            
            if 'cls end' in flags:
                class_list.append(class_lines)
                class_lines = []

        # Catch the classes that run up to the end of the file and the class end flag gets removed
        if len(class_lines) > 0:
            class_list.append(class_lines) 

        # Loop through each class individually
        for class_ln in class_list:
            cls = {
                'file_id': file_id,
                'class_id': next(class_id_gen),
                'name': '',
                'superclass': [],
                'docstring': [],
                'parameters': [],
                'line_start': class_ln[0].get('line_no'),
                'line_count': len(class_ln)
            }

            method_list = []

            for ln_dict in class_ln:
                flags = ln_dict.get('flags')
                txt   = ln_dict.get('line')
                # Parameters
                if 'init' in flags:
                    params_str = txt[txt.find('(')+1:]
                    if params_str.find(')') > -1:
                        params_str = params_str[:params_str.find(')')]
                        cls['parameters'] = [ x.strip() for x in params_str.split(',') if x.strip() != 'self']
                # Methods
                if 'meth' in flags or 'decorated' in flags:
                    method_list.append(ln_dict)
                    continue # to next line, no more processing needed

                if 'cls start' in flags:
                    if txt.find('(') > -1:
                        cls['name'] = txt[6:txt.find('(')].strip()
                    else:
                        cls['name'] = txt[6:txt.find(':')].strip()
                # Superclass
                if 'super cls' in flags:
                    super_cls_str = txt[txt.find('(')+1:txt.find(')')]
                    cls['superclass'] = [x.strip() for x in super_cls_str.split(',')]
                # Docstring
                if 'cls docs start' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    cls['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif  'cls docs end' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    cls['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'cls docs' in flags:
                    cls['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                    
            # Format the docstring by cutting to the minimum whitespace
            if len(cls.get('docstring')) > 0:
                min_wht_spc = min([x.get('whitespace') for x in cls.get('docstring') if x.get('line').strip() != ''])
                for ds in cls['docstring']:
                    ds['line'] = ds.get('line')[min_wht_spc:]

                while len(cls['docstring'][-1].get('line').strip()) == 0:
                    cls['docstring'].pop(-1)
            cls['docstring'] = [ x.get('line') for x in cls.get('docstring')]

            self.classes.append(cls)

            self.__parse_methods(file, cls.get('class_id'), method_list)
            # End of loop through classes

    @log.performance
    def __parse_methods(self, file:dict, class_id:int, method_lists:list):
        ''' Splits out the logic for methods from classes.  
        
            Params: 
                - file: the file parameter from the function that called this
                - class_id: the parent function_id to be placed in the nested function object
                - method_lists: a filtered list of lines containing relevant flags
        '''  
        # Split methods into their own lists
        meth_list = []
        meth_lines = []
        for ln_dict in method_lists:
            meth_lines.append(ln_dict)
            flags = ln_dict.get('flags')
            if 'meth end' in flags:
                meth_list.append(meth_lines)
                meth_lines = []

        for method in meth_list:     
            meth = {
                'file_id': file.get('file_id'),
                'class_id': class_id,
                'parent_id': None,
                'function_id': next(function_id_gen),
                'name': '',
                'parameters': [],
                'returns': None,
                'docstring': [],
                'decorators': [], 
                'line_start': method[0].get('line_no'),
                'line_count': len(method)                
            }
            nested_function_lines = []
            nested_functions = []
            for line in method:
                flags = line.get('flags') 
                txt = line.get('line')
                if 'decorated' in flags:
                    meth['decorators'].append(txt[line.get('whitespace')+1:])
                if 'meth start' in flags:
                    open_parameter_pos = txt.find('(')
                    meth['name'] = txt[line.get('whitespace')+4:open_parameter_pos].strip()

                # Parameters and returns
                if 'meth param start' in flags:
                    param_str = txt[txt.find('(')+1:]
                    if 'meth param end' in flags:
                        param_str = param_str[:param_str.find(')')]
                        parameters = [ x.strip() for x in param_str.split(',') ]
                        meth['parameters'] = parameters
                elif 'meth param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
                    meth['parameters'] = parameters
                elif 'meth param' in flags:
                    param_str += txt
                if 'meth return' in flags:
                    txt = txt[txt.find('->')+2:]
                    return_str = txt[:txt.find(':')].strip()
                    meth['returns'] = return_str

                # Docstring
                if 'meth docs start' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif  'meth docs end' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'meth docs' in flags:
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                # Nested functions
                if 'nest meth' in flags:
                    nested_function_lines.append(line)
                if 'nest meth end' in flags:
                    nested_functions.append(nested_function_lines)
                    nested_function_lines = []

            # format the docstring by cutting to the minimum whitespace
            if len(meth.get('docstring')) > 0:
                min_wht_spc = min([x.get('whitespace') for x in meth.get('docstring') if x.get('line').strip() != ''])
                for ds in meth['docstring']:
                    ds['line'] = ds.get('line')[min_wht_spc:]
                while len(meth['docstring'][-1].get('line').strip()) == 0:
                    meth['docstring'].pop(-1)

            meth['docstring'] = [x.get('line') for x in meth.get('docstring')]

            self.functions.append(meth)
            self.__nested_methods(file, func_id=meth.get('function_id'), class_id=meth.get('class_id'),nested_functions=nested_functions)
            

    @log.performance
    def __nested_methods(self, file:dict, func_id:int, class_id:int, nested_functions:list):
        ''' Splits out the logic for nested functions.  
        
            Params: 
                - file: the file parameter from the function that called this
                - func_id: the parent function_id to be placed in the nested function object
                - class_id: the class this nested function is related to
                - nested_functions: a filtered list of lines containing relevant flags
        '''        
        file_id = file.get('file_id')
        for nest_meth in nested_functions:
            meth = {
                'file_id': file_id,
                'class_id': class_id,
                'parent_id': func_id,
                'function_id': next(function_id_gen),
                'name': '',
                'parameters': [],
                'returns': None,
                'docstring': [],
                'decorators': [], 
                'line_start': nest_meth[0].get('line_no'),
                'line_count': len(nest_meth)
            }

            for line in nest_meth:
                flags = line.get('flags') 
                txt = line.get('line')

                if 'decorated' in flags:
                    meth['decorators'].append(txt[1:])
                if 'nest meth start' in flags:
                    open_parameter_pos = txt.find('(')
                    meth['name'] = txt[line.get('whitespace')+4:open_parameter_pos].strip()

                # Parameters and returns
                if 'nest meth param start' in flags:
                    param_str = txt[txt.find('(')+1:].replace('\\','')
                    if 'nest meth param end' in flags:
                        param_str = param_str[:param_str.find(')')]
                        parameters = [ x.strip() for x in param_str.split(',') ]
                        if parameters != ['']:
                            meth['parameters'] = parameters
                elif 'nest meth param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
                    if parameters != ['']:
                        meth['parameters'] = parameters
                elif 'nest meth param' in flags:
                    param_str += txt.replace('\\','')

                if 'nest meth return' in flags:
                    txt = txt[txt.find('->')+2:]
                    return_str = txt[:txt.find(':')].strip()
                    meth['returns'] = return_str

                # Docstring
                if 'nest meth docs start' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'nest meth docs end' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'nest meth docs' in flags:
                    meth['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})

            # format the docstring by cutting to the minimum whitespace
            if len(meth.get('docstring')) > 0:
                min_wht_spc = min([x.get('whitespace') for x in meth.get('docstring') if x.get('line').strip() != ''])
                for ds in meth['docstring']:
                    ds['line'] = ds.get('line')[min_wht_spc:]
            meth['docstring'] = [x.get('line') for x in meth.get('docstring')]

            self.functions.append(meth)


    @log.performance
    def __parse_functions(self, file:dict, lines:list):
        ''' Extract the function docs data like parameters, returns, docstring, nested functions.
            This is fed individual files. 
        
            Params: 
                - file: i in Doc.file_lines[i] has meta data we want to add to records
                - lines: a filtered list of lines containing relevant flags
        '''
        file_id  = file.get('file_id')

        # Split functions into their own lists
        functions_list = []
        func_lines = []
        for ln_dict in lines:
            func_lines.append(ln_dict)
            flags = ln_dict.get('flags')
            
            if 'func end' in flags:
                functions_list.append(func_lines)
                func_lines = []
        
        # Iterate through each functions list of lines
        param_str = ''
        for function_lines in functions_list:
            # Start of a new function
            func = {
                'file_id': file_id,
                'class_id': None,
                'parent_id': None,
                'function_id': next(function_id_gen),
                'name': '',
                'parameters': [],
                'returns': None,
                'docstring': [],
                'decorators': [], 
                'line_start': function_lines[0].get('line_no'),
                'line_count': len(function_lines)
            }

            nested_functions = []
            nested_function_lines = []
            for line in function_lines:
                flags = line.get('flags') 
                txt = line.get('line')
                if 'decorated' in flags:
                    func['decorators'].append(txt[1:])
                if 'func start' in flags:
                    open_parameter_pos = txt.find('(')
                    func['name'] = txt[4:open_parameter_pos].strip()

                # Parameters and returns
                if 'func param start' in flags:
                    param_str = txt[txt.find('(')+1:]
                    if 'func param end' in flags:
                        param_str = param_str[:param_str.find(')')]
                        parameters = [ x.strip() for x in param_str.split(',') ]
                        if parameters != ['']:
                            func['parameters'] = parameters
                elif 'func param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
                    if parameters != ['']:
                        func['parameters'] = parameters
                elif 'func param' in flags:
                    param_str += txt
                if 'func return' in flags:
                    txt = txt[txt.find('->')+2:]
                    return_str = txt[:txt.find(':')].strip()
                    func['returns'] = return_str

                # Docstring
                if 'func docs start' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif  'func docs end' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'func docs' in flags:
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                # Nested functions
                if 'nest func' in flags:
                    nested_function_lines.append(line)
                if 'nest func end' in flags:
                    nested_functions.append(nested_function_lines)
                    nested_function_lines = []
            
            # format the docstring by cutting to the minimum whitespace
            if len(func.get('docstring')) > 0:
                min_wht_spc = min([x.get('whitespace') for x in func.get('docstring') if x.get('line').strip() != ''])
                for ds in func['docstring']:
                    ds['line'] = ds.get('line')[min_wht_spc:]
                while len(func['docstring'][-1].get('line').strip()) == 0:
                    func['docstring'].pop(-1)

            func['docstring'] = [x.get('line') for x in func.get('docstring')]
            self.functions.append(func)

            self.__nested_functions(file, func.get('function_id'), nested_functions)
            # End of function section 

    @log.performance
    def __nested_functions(self, file:dict, func_id:int, nested_functions:list):
        ''' Splits out the logic for nested functions.  
        
            Params: 
                - file: the file parameter from the function that called this
                - func_id: the parent function_id to be placed in the nested function object
                - nested_functions: a filtered list of lines containing relevant flags
        '''        
        file_id = file.get('file_id')
        for nest_func in nested_functions:
            func = {
                'file_id': file_id,
                'class_id': None,
                'parent_id': func_id,
                'function_id': next(function_id_gen),
                'name': '',
                'parameters': [],
                'returns': None,
                'docstring': [],
                'decorators': [], 
                'line_start': nest_func[0].get('line_no'),
                'line_count': len(nest_func)
            }

            for line in nest_func:
                flags = line.get('flags') 
                txt = line.get('line')

                if 'decorated' in flags:
                    func['decorators'].append(txt[1:])
                if 'nest func start' in flags:
                    open_parameter_pos = txt.find('(')
                    func['name'] = txt[line.get('whitespace')+4:open_parameter_pos].strip()

                # Parameters and returns
                if 'nest func param start' in flags:
                    param_str = txt[txt.find('(')+1:].replace('\\','')
                    if 'nest func param end' in flags:
                        param_str = param_str[:param_str.find(')')]
                        parameters = [ x.strip() for x in param_str.split(',') ]
                        if parameters != ['']:
                            func['parameters'] = parameters
                elif 'nest func param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
                    if parameters != ['']:
                        func['parameters'] = parameters
                elif 'nest func param' in flags:
                    param_str += txt.replace('\\','')

                if 'nest func return' in flags:
                    txt = txt[txt.find('->')+2:]
                    return_str = txt[:txt.find(':')].strip()
                    func['returns'] = return_str

                # Docstring
                if 'nest func docs start' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'nest func docs end' in flags:
                    txt = txt.replace("'''",'   ').replace('"""', '   ')
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})
                elif 'nest func docs' in flags:
                    func['docstring'].append({'whitespace': len(txt) - len(txt.lstrip()), 'line': txt})

            # format the docstring by cutting to the minimum whitespace
            if len(func.get('docstring')) > 0:

                min_wht_spc = min([x.get('whitespace') for x in func.get('docstring') if x.get('line').strip() != ''])
                for ds in func['docstring']:
                    ds['line'] = ds.get('line')[min_wht_spc:]
            func['docstring'] = [x.get('line') for x in func.get('docstring')]
            self.functions.append(func)


    @log.performance
    def __parse_meta(self, file:dict, lines:list):
        ''' Extract the meta data like file comments, imports and todo comment  s 
        
            Params: 
                - file: i in Doc.file_lines[i] has meta data we want to add to records
                - lines: a filtered list of lines containing relevant flags
        '''
        file_id  = file.get('file_id')
        todo_line_numbers = []
        file_doc_list = []
        # Import variables
        multi_line_import = False
        module = ''
        for ln_dict in lines:
            flags = ln_dict.get('flags')
            line  = ln_dict.get('line')
            ln_no = ln_dict.get('line_no')
            wht_space = ln_dict.get('whitespace')

            # Todo section
            if 'todo' in flags:
                if len(self.todo) > 0:
                    prev_todo = self.todo[-1]

                # If the todo's are sequentially numbered, group them together
                if ln_no - 1 in todo_line_numbers:
                    prev_todo['line'] += f"\n{line[wht_space+1:]}"
                    prev_todo['line_count'] += len(todo_line_numbers)
                else: # Start of a new todo
                    todo_line_numbers = [ln_no]
                    # Clean up the # and the Todo
                    line = line[wht_space+1:]
                    pos_colon_todo = line.lower().find('todo:')
                    pos_todo = line.lower().find('todo ')
                    if pos_colon_todo > -1:
                        line = line[pos_colon_todo+6:]
                    elif pos_todo > -1:
                        line = line[pos_todo+5:]

                    self.todo.append({'todo_id':next(todo_id_gen), 'file_id': file_id, 'line_start': ln_no, 'line_count': 1, 'line': line})

            elif 'file docs' in flags:
                ln_dict['line'] =  line.replace("'''",'   ').replace('"""', '   ')
                ln_dict['whitespace'] = len(ln_dict['line']) - len(ln_dict['line'].lstrip())
                if ln_dict['whitespace'] >= 3:
                    ln_dict['line'][3:]
                file_doc_list.append(ln_dict)

            if 'import' in flags:
                if multi_line_import:
                    # Check if there is another line after this
                    if line.find('\\') == -1:
                        multi_line_import = False

                    trim_line = line.lstrip()
                    object_list = trim_line.split(',')

                    if multi_line_import: # The last item will be the line continuation \. remove it
                        object_list.pop(-1)
                    for obj in object_list:
                        alias = None
                        if obj.find(' as ') > -1:
                            obj, alias = [ x.strip() for x in obj.split(' as ') ]
                        self.imports.append(
                            {
                                'import_id': next(import_id_gen), 
                                'file_id': file_id, 
                                'line_no': ln_no,
                                'module': module.strip(),
                                'object': obj.strip(), 
                                'alias': alias
                                }
                            )   
                else:
                    if line.find('\\') > -1:
                        multi_line_import = True
                    
                    if line[:7] == 'import ':
                        trim_line = line[7:].lstrip()
                        module_list = trim_line.split(',')
                        for module in module_list:
                            alias = None
                            if module.find(' as ') > -1:
                                module, alias = [ x.strip() for x in module.split(' as ') ]
                            self.imports.append(
                                {
                                    'import_id': next(import_id_gen), 
                                    'file_id': file_id, 
                                    'line_no': ln_no,
                                    'module': module.strip(),
                                    'object': None, 
                                    'alias': alias
                                    }
                                )                            
                    if line[:5] == 'from ':
                        trim_line = line[5:].lstrip()
                        module, objects = trim_line.split('import')
                        module = module.strip()

                        object_list = objects.split(',')
                        if multi_line_import: # The last item will be the line continuation \. remove it
                            object_list.pop(-1)
                        for obj in object_list:
                            alias = None
                            if obj.find(' as ') > -1:
                                obj, alias = [ x.strip() for x in obj.split(' as ') ]
                            self.imports.append(
                                {
                                    'import_id': next(import_id_gen), 
                                    'file_id': file_id, 
                                    'line_no': ln_no,
                                    'module': module,
                                    'object': obj.strip(), 
                                    'alias': alias
                                    }
                                )   
        # End of for loop through file lines

        # Handle the comments after the file has all be read through
        if len(file_doc_list) > 0:
            hashtag_docs = file_doc_list[0].get('line')[0] == '#'
            
        doc_list = []
        for line in file_doc_list:
            if hashtag_docs:
                doc_list.append(line.get('line')[1:])
            else:
                if 'file docs start' in line.get('flags') or 'file docs end' in line.get('flags'):
                    line['line'].replace('"""', '   ')
                    line['line'].replace("'''", '   ')
                doc_list.append(line.get('line'))
        
        if len(doc_list) > 0:
            while doc_list[-1].strip() == '':
                doc_list.pop(-1)

        if len(doc_list) > 0:
            self.file_docs.append({
                'file_id': file_id,
                'docs': '\n'.join(doc_list)
            })

