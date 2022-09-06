class FormConfig:
    ''' Superclass for form field items. Global configuration of 
    
        Values:
            - forms_required_by_default
            - label_class
    '''
    forms_required_by_default = True
    label_class = 'fw-bold text-secondary'

class CheckFieldConfig(FormConfig):
    ''' Defines the defaults for check box form elements 

        Values:
            - _class = 'form-check-input'
            - label_class = ''
    '''
    _class = 'form-check-input'
    label_class = ''

class DateFieldConfig(FormConfig):
    ''' Defines the defaults for date form elements 
    
        Values:
            - _class = 'form-control'
    '''
    _class = 'form-control'

class NumberFieldConfig(FormConfig):
    ''' Defines the defaults for number form elements 
    
        Values:
            - _class = 'form-control'
    '''
    _class = 'form-control'

class SelectFieldConfig(FormConfig):
    ''' Defines the defaults for select field form elements 
    
        Values:
            - _class = 'form-control'
    '''
    _class = 'form-control'

class ButtonConfig(FormConfig):
    ''' Defines the defaults for button form elements 
    
        Values:
            - _class = 'btn'
    '''
    _class = 'btn'

class TextAreaConfig(FormConfig):
    ''' Defines the defaults for text area form elements  
    
        Values:
            - _class = 'form-control'
            - rows = 6
    '''
    _class  = 'form-control'
    rows    = 6

class TextConfig(FormConfig):
    ''' Defines the defaults for text form elements 
    
        Values:
            - _class = 'form-control'
    '''
    _class  = 'form-control'

# This dictionary is used by the Form Superclass to set the defaults on form elements. 
formElemConfig = {
    'button'   : ButtonConfig,
    'check'    : CheckFieldConfig,
    'date'     : DateFieldConfig,
    'number'   : NumberFieldConfig,
    'select'   : SelectFieldConfig,
    'textarea' : TextAreaConfig,
    'text'     : TextConfig,
}
