from datetime import datetime as dt
from www      import config
from www.modules.forms.form_config import formElemConfig


class Form:
    def __init__(self, *args, form_type, **kwargs) -> None:
        self.config     = formElemConfig.get(form_type)()
        self.key_value_attributes = {}
        self.flag_attributes      = []
        self.kwargs     = kwargs
        self.label      = kwargs.get('label', None)
        self.field_type = form_type

        # Add the config defaults into the class before processing 
        kwargs['_class'] = f'{self.config._class} {kwargs.get("_class","")}'
        self.overwrite_ALL_Attributes(*args, **kwargs)
        self.setHidden(self.kwargs.get('hidden', False))

    def prep_html(self):
        self.__set_hidden_style()
        self.__set_id_if_none_then_copy_to_name()
        self.__set_attribute_html()
        self.__set_label_html()
        self.__set_required_html()

    def __set_id_if_none_then_copy_to_name(self):
        if not self.key_value_attributes.get('id') and self.field_type != 'button':
            self.key_value_attributes['id'] = f'{ self.field_type }-{ next(id_seq) }'
        if self.field_type != 'button':
            self.key_value_attributes['name'] = self.key_value_attributes['id']

    def __set_attribute_html(self):
        attribute_list = [ f'{k}="{v}"' for k, v in self.key_value_attributes.items() ]
        attribute_list += self.flag_attributes
        self.attribute_html = " ".join(attribute_list).strip()

    def __set_hidden_style(self):
        hidden_already = self.key_value_attributes.get('style','').find('display:none;') != -1
        if self.hidden:
            if not hidden_already:
                self.key_value_attributes['style'] = self.key_value_attributes.get('style', '') + 'display:none;'
            self.hidden_html_attribute = 'style="display:none;"'
        else:
            if hidden_already:
                self.key_value_attributes['style'].replace('display:none;','') 
            self.hidden_html_attribute = ''

    def __set_label_html(self):
        if self.label:
            self.label_html = f'<label for="{ self.key_value_attributes.get("id") }" class="{ self.config.label_class }">{ self.label }</label>\n'
        else:
            self.label_html = ''

    def __set_required_html(self):
        if 'required' in self.flag_attributes:
            self.required_html = f'<div class="invalid-feedback">{ self.kwargs.get("required_txt", "Required") }</div>\n'
        else:
            self.required_html = ''

    def __parse_kwargs_attributes_to_dict(self, kwargs):
        return { k.replace("_", ""): str(v) for k, v in kwargs.items() if k[0] == '_' }

    def addAttributes(self, *args, **kwargs):
        ''' Add an html attribute like style, class, id etc. 
            An underscore must prepend every attribute. eg. ...(_value="example").
            Attributes are added to existing attributes, use overrideAttributes to replace all values in that attribute
        '''
        self.flag_attributes += [ x for x in args if x not in self.flag_attributes ] 
        new_atributes = self.__parse_kwargs_attributes_to_dict(kwargs)
        for k, v in new_atributes.items():
            self.key_value_attributes[k] = str(self.key_value_attributes.get(k,'') + " " + str(v)).strip()    

    def addJs(self, **kwargs):
        for k, v in kwargs.items():
            key = k.replace('_','')
            self.key_value_attributes[key] = self.key_value_attributes.get(key, '') + v

    def overrideAttributes(self, *args, **kwargs):
        filtered_for_duplicated = [ x for x in args if x not in self.flag_attributes ] 
        self.flag_attributes += filtered_for_duplicated
        new_attributes = self.__parse_kwargs_attributes_to_dict(kwargs)
        for k, v in new_attributes.items():
            self.key_value_attributes[k] = v       

    def overwrite_ALL_Attributes(self, *args, **kwargs):
        self.flag_attributes = list(args)
        new_attributes = self.__parse_kwargs_attributes_to_dict(kwargs)
        self.key_value_attributes = {}
        for k, v in new_attributes.items():
            self.key_value_attributes[k] = v       

    def hiddenHtmlAttribute(self) -> str:
        self.__set_hidden_style()
        return self.hidden_html_attribute

    def setHidden(self, hidden=bool):
        self.hidden = hidden



## Form elements ##
# The html form elements are represented here as classes which all inherit from the Form superclass
#
# HTML tags are barebones unless you pass in attributes.
# Due to language keyword conflicts (class for example) all attributes should be passed in with a single underscore
#   eg. NumberField(..., _value=1, _id="skids")
# Where necessary defaults are set. 
# - Because forms are submitted by name the id field is copied to name unless overridden by passing in _name 


# The following id sequence is a generator to prevent collisions when assigning generic id's 
# id_sequence only executes and yields one number at a time and is assigned to id_seq
# to get the next id...
#  eg.. next(id_seq)

def id_sequence():
    num = 1
    while True:
        yield num
        num += 1

id_seq = id_sequence()

def prep_form_submission_dictionary(form) -> dict:
    '''Converts form data from list to scalar if only one value in form element '''
    for k,v in form.items():
        if type(v) == list and len(v) == 1:
            form[k] = v[0]
    return form


class CheckField(Form):
    '''Labels are required for check fields. Dont forget to pass label in 
        - Pass in outer_div_class="eg-5" to positioning box along with the label
        
        Special HTML attributes: _checked
    '''
    def __init__(self, label, *args, **kwargs) -> None:  
        super().__init__(form_type='check', label=label, *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''<div class="form-check { self.kwargs.get('outer_div_class','') }">\n{self.label_html}<input type="checkbox" { self.attribute_html } />\n</div>\n'''


class DateField(Form):
    ''' 
        Defaults to today unless passed _value='YYYY-MM-DD'
        Special HTML attributes: _min, _max, _step 
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(form_type='date', *args, **kwargs)

    def __ifNoValueSetToToday(self):
        if not self.key_value_attributes.get('value'):
            self.key_value_attributes['value'] = dt.strftime(dt.now(), '%Y-%m-%d')

    def html(self):
        self.__ifNoValueSetToToday()
        self.prep_html()
        return f'''{ self.label_html }<input type="date" { self.attribute_html } />\n{ self.required_html }'''


class Email(Form):
    ''' 
        Special HTML attributes: _maxlength, _minlength, _pattern
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(form_type='text', *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''{ self.label_html }<input type="email" { self.attribute_html } />\n{ self.required_html }'''


class HiddenField:
    ''' 
        Simple form does not inherit from anything since it only needs to values. 
        Set these value directly rather than from function
        - Requires _id, _val
    '''
    def __init__(self,_id, _value) -> None:
        self.id = _id
        self.value = _value

    def html(self):
        return f'''<input type="hidden" id="{self.id}" name="{self.id}" value="{self.value}" />\n'''     


class NumberField(Form):
    ''' 
        Special HTML attributes _min, _max, _step 
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(form_type='number', *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''{ self.label_html }<input type="number" { self.attribute_html } />\n{ self.required_html }'''     


class Password(Form):
    ''' 
        Minimum password length is set in config
        Special HTML attributes: _maxlength, _pattern
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(form_type='text', *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''{ self.label_html }<input type="password" { self.attribute_html } minlength="{ config.min_password_length }" />\n{ self.required_html }'''

class Phone(Form):
    ''' 
        preset to pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}"
        Special HTML attributes: _maxlength, _minlength, _pattern
    '''
    def __init__(self, *args, **kwargs) -> None:
        kwargs['_pattern'] = "[0-9]{3}-[0-9]{3}-[0-9]{4}"
        kwargs['_placeholder'] = kwargs.get('_placeholder', 'XXX-XXX-XXXX')
        super().__init__(form_type='text', *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''{ self.label_html }<input type="tel" { self.attribute_html } />\n{ self.required_html }'''


class SelectField(Form):
    ''' Create a drop down menu OR a multiselect field
        - multiple attribute will create a fitted height box, to override this assign _size=n, 
        - set _size=True for a fitted single select field
        - option_list will take a list of strings or dicts of shape {'txt': ..., 'value': ..., 'selected': False (optional)}
        
        Special HTML attributes: _multiple, _size 
    '''
    def __init__(self, *args, **kwargs) -> None:
        self.option_list = kwargs.get('option_list',[]) 
        self.__conform_option_list_to_dict()
        super().__init__(form_type='select', *args, **kwargs)

    def __conform_option_list_to_dict(self):
        conformed_list = []
        if self.option_list:
            for opt in self.option_list:
                if type(opt) != dict:
                    conformed_list.append({'txt': opt,'value': opt, 'selected': False }) 
                else:
                    # If either txt or value is missing it will take it's counterpart
                    conformed_list.append({
                        'txt': opt.get('txt', opt.get('value')),
                        'value': opt.get('value', opt.get('txt')), 
                        'selected': opt.get('selected', False ) })
            self.option_list = conformed_list

    def __options_to_string(self):
        option_html_list = []
        if self.option_list:
            for i, opt in enumerate(self.option_list):
                selected = 'selected' if opt['selected'] else ''
                txt      = opt["txt"]
                value    = opt["value"]
                option_html_list.append(  f'<option value="{ value }" { selected }>{ txt }</option>')
            self.options_html = '\n'.join(option_html_list)
        else:
            self.options_html = ''

    def __set_size(self):
        if 'multiple' in self.flag_attributes:
            self.key_value_attributes['size'] = self.kwargs.get('_size', len(self.option_list))
        if self.kwargs.get('_size') == True:
            self.key_value_attributes['size'] = len(self.option_list)

    def optionsHtml(self):
        self.__options_to_string()
        return self.options_html

    def html(self):
        self.__conform_option_list_to_dict()
        self.__set_size()
        self.prep_html()
        self.__options_to_string()
        return f'''{self.label_html}<select { self.attribute_html }>\n{ self.options_html }</select>\n{ self.required_html }'''

    def addOption(self, txt, value=None, selected=False):
        value = value if value != None else txt
        self.option_list.insert(0, {'txt': txt, 'value': value, 'selected': selected})

    def removeOption(self, txt=None, value=None):
        if txt:
            self.option_list = [ x for x in self.option_list if x.get('txt') != txt ]
        else:
            self.option_list = [ x for x in self.option_list if x.get('value') != value ]            

    def returnSingleSelected(self):
        if self.option_list:
            selected = [option.get('value') for option in self.option_list if option.get('selected') ]
            if len(selected) > 0: 
                return next(option.get('value') for option in self.option_list if option.get('selected'))
            else:
                return self.option_list[0].get('value')

    def returnMultipleSelected(self):
        return [option.get('value') for option in self.option_list if option.get('selected') == 'selected']

    def setSelectedByValue(self, value):
        if self.option_list:
            for option in self.option_list:
                option['selected'] = True if str(option.get('value')) == str(value) else False

    def setSelectedMultipleByValues(self, values_list):
        if self.option_list:
            for option in self.option_list:
                option['selected'] = True if str(option.get('value')) in values_list else False

    def setSelectedByTxt(self, id):
        for option in self.option_list:
            option['selected'] = True if option.get('txt') == id else False


class SubmitBtn(Form):
    ''' A simple submit button to use in a form
    - bootstrap_color: appends to btn- in class to style the button
    - txt: text to display on button
        
    '''
    def __init__(self, bootstrap_color='success', txt='Submit', _class='', *args, **kwargs) -> None:
        self.bootstrap_color = bootstrap_color
        self.txt    = txt
        self._class = _class
        if bootstrap_color == 'success':
            self._class += " text-light"
        super().__init__(form_type='button', *args, **kwargs)

    def html(self):
        self.prep_html()
        # Button labels dont have a new line after them. Adding it to make button labels fit the format
        # Labeling a button is most often done just to space it properly using &nbsp;
        if self.label_html != '':
            self.label_html += "<br/>"
        return f'''{ self.label_html }<button type="submit" class="{ self.config._class } btn-{ self.bootstrap_color } { self._class } " { self.attribute_html }>{ self.txt }</button>\n'''   


class TextArea(Form):
    ''' 
        Default height is as listed in the view/config.py file
        Special HTML attributes: _rows
    '''
    def __init__(self, txt="", *args, **kwargs) -> None:
        self.txt = txt
        super().__init__(form_type='textarea', *args, **kwargs)
        self.__set_height()

    def __set_height(self):
        self.key_value_attributes['rows'] = self.key_value_attributes.get('rows', self.config.rows)

    def html(self):
        self.prep_html()
        if self.txt != '':
            return f'''{ self.label_html }<textarea { self.attribute_html } >{ self.txt }</textarea>\n{ self.required_html }'''
        else:
            return f'''{ self.label_html }<textarea { self.attribute_html }></textarea>{ self.required_html }'''


class Text(Form):
    ''' 
        Special HTML attributes: _maxlength, _minlength, _pattern
    '''
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(form_type='text', *args, **kwargs)

    def html(self):
        self.prep_html()
        return f'''{ self.label_html }<input type="text" { self.attribute_html } />\n{ self.required_html }'''
