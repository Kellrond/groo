import config
from modules.documentation import Docs
from modules import logging, utilities


log = logging.Log(__name__)

class_id_gen    = utilities.generateIntegerSequence()
function_id_gen = utilities.generateIntegerSequence()
# Meta Id's
todo_id_gen   = utilities.generateIntegerSequence()
import_id_gen = utilities.generateIntegerSequence()
file_comment_id_gen = utilities.generateIntegerSequence()

class PyDocsParser(Docs):
    ''' File comments reside at the top of a file before the imports 
    '''    

    folders = []
    files   = [] 
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
    def parsePyDocs(self):
        ''' Runs the flagging in the correct order. Though in this case order does not matter as much. '''
        self.parseFilesToParts()

    @log.performance
    def parseFilesToParts(self):
        ''' Takes the flagged lines and converts them into objects'''

        for file in self.file_lines:
            py_class_lines = []
            py_meta_lines  = []
            py_func_lines  = []
            for line in file.get('lines'):
                flags = line.get('flags')

                # Can either be a class or a function not both
                if 'cls' in flags:
                    py_class_lines.append(line)
                elif 'func' in flags or 'decorated' in flags:
                    py_func_lines.append(line)
                # But imports and todos can exist in both classes and functions
                if 'import' in flags or 'file docs' in flags or 'todo' in flags:
                    py_meta_lines.append(line)

            self.parseClasses(file, py_class_lines)
            self.parseFunctions(file, py_func_lines)
            self.parseMeta(file, py_meta_lines)

    @log.performance
    def parseClasses(self, file:dict, lines:list):
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

        # Loop through each class individually
        for class_lines in class_list:
            cls = {
                'file_id': file_id,
                'class_id': next(class_id_gen),
                'name': '',
                'superclass': [],
                'docstring': [],
                'parameters': [],
                'line_start': class_lines[0].get('line_no'),
                'line_count': len(class_lines)
            }

            method_list = []

            for ln_dict in class_lines:
                flags = ln_dict.get('flags')
                txt   = ln_dict.get('line')
                # Parameters
                if 'init' in flags:
                    params_str = txt[txt.find('(')+1:]
                    if params_str.find(')') > -1:
                        params_str = params_str[:params_str.find(')')]
                        cls['parameters'] = [ x.strip() for x in params_str.split(',')]

                if 'meth' in flags:
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
        for method in method_lists:
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

            ## Fill in the rest here............

            self.functions.append(meth)


    @log.performance
    def parseFunctions(self, file:dict, lines:list):
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
                        func['parameters'] = parameters
                elif 'func param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
                    func['parameters'] = parameters
                elif 'func param' in flags:
                    param_str += txt
                if 'func return' in flags:
                    return_str = txt[txt.find('->')+2:txt.find(':')].strip()
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
                        func['parameters'] = parameters
                elif 'nest func param end' in flags:
                    param_str += txt[:txt.find(')')]    
                    parameters = [ x.strip() for x in param_str.split(',') ]
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

            self.functions.append(func)


    @log.performance
    def parseMeta(self, file:dict, lines:list):
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
                        line = line[pos_colon_todo+5:]
                    elif pos_todo > -1:
                        line = line[pos_todo+4:]

                    self.todo.append({'todo_id':next(todo_id_gen), 'file_id': file_id, 'line_start': ln_no, 'line_count': 1, 'line': line})

            elif 'file docs' in flags:
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
                        alias = ''
                        if obj.find('as') > -1:
                            obj, alias = obj.split('as')
                        self.imports.append(
                            {
                                'import_id': next(import_id_gen), 
                                'file_id': file_id, 
                                'line_no': ln_no,
                                'module': module,
                                'object': obj.strip(), 
                                'alias': alias.strip()
                                }
                            )   
                else:
                    if line.find('\\') > -1:
                        multi_line_import = True
                    
                    if line[:7] == 'import ':
                        trim_line = line[7:].lstrip()
                        module_list = trim_line.split(',')
                        for module in module_list:
                            alias = ''
                            if module.find('as') > -1:
                                module, alias = module.split('as')
                            self.imports.append(
                                {
                                    'import_id': next(import_id_gen), 
                                    'file_id': file_id, 
                                    'line_no': ln_no,
                                    'module': module.strip(),
                                    'object': '', 
                                    'alias': alias.strip()
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
                            alias = ''
                            if obj.find('as') > -1:
                                obj, alias = obj.split('as')
                            self.imports.append(
                                {
                                    'import_id': next(import_id_gen), 
                                    'file_id': file_id, 
                                    'line_no': ln_no,
                                    'module': module,
                                    'object': obj.strip(), 
                                    'alias': alias.strip()
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
        
        while doc_list[-1].strip() == '':
            doc_list.pop(-1)

        self.file_docs.append({
            'file_id': file_id,
            'docs': '\n'.join(doc_list)
        })

