#-- EXAMPLE -- Please remove all comments like #-- ... and keep the ## ones
from flask     import session

from database   import _skeleton_db
from www.modules import forms

class ExampleForm:
    ''' Please fill out the doc string with helpfull information for any others
            
            - example_object: is a class object from a module
            - example_arg: can be a default value for the form, user_id is a common one
            - dbo_dict: dict from dbo to repopulate form
            - form_data: form field data from http response to rebuild form with
            - submit: if submit=True then form objects will not be built 
            
        Eg: ` this is a code example `
    '''
    def __init__(self, example_object=None, example_arg=None, dbo_dict=None, form_data=None, submit=False) -> None:
        self.example_obj = example_object
        self.example_arg = example_arg
        self.dbo_dict    = dbo_dict
        self.form_data   = form_data
        self.submit      = submit

        #-- If the form is called to submit we dont need to build all the objects
        if self.submit == False:
            self.__build_form_field_objects()
            #-- If also fed form data we want to populate the form
            if self.dbo_dict or self.form_data:
                self.__repopulate_form()

    #-- Here the form field objects are created we avoid the extra cycles if submit=True
    def __build_form_field_objects(self):

        ## Form Elements

        #-- If you have a lot of hidden tags you can use the boilerplate below
        #-- Or just use forms.HiddenField(_id="example_id", _value="example_value")
        hidden_tag_lists = [
            forms.HiddenField(_id="example_id_a", _value="example_value"),
            forms.HiddenField(_id="example_id_b", _value="example_value"),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        self.text_field   = forms.Text('required', label="Text field", _id="text_field")
        self.text_area    = forms.TextArea(txt='', label="Text area", _id="text_area", _rows=4)
        self.select_field = forms.SelectField('required', label="Select Field", _id="select_field")
        self.select_multiple = forms.SelectField('multiple', 'required', label="Select multiple", _id="select_multiple")
        self.number_field = forms.NumberField('required', label="Number field", _id="number_field", _min=0, _max=10000, _step=1)
        self.date_field   = forms.DateField('required', label="Date field", _id="date_field")
        self.check_field  = forms.CheckField(label="Show text area", _id="check_field")
        self.submit       = forms.SubmitBtn()

        #-- Build option list for select_field
        example_list = _skeleton_db.returnExampleListById(self.example_obj.example_id)
        self.select_field.option_list = [{'txt':e.get('ex_text'),'value':e.get('ex_value')} for e in example_list]

        ## Element cusomizations
        self.text_field.addAttributes(_placeholder="Placeholder text")
        self.text_area.txt = "This is some example text\nYou need to add\nNew lines"
        self.select_field.addOption(txt="New option", value='example_value')
        self.select_field.setSelectedByValue('example_value')
        
        self.select_multiple.option_list = [{'txt':'manual list 1', 'value': '1'},{'txt':'manual list 2', 'value': '2'},{'txt':'manual list 3', 'value': '3'},]

        self.date_field.addAttributes(_value='1984-12-16') 
        self.text_area.setHidden(True)
        #-- ['elem_1', 'elem_2'] passed to toggleVisible to toggle multiple else 'elem_1'
        self.check_field.addJs(_onchange="toggleVisible(['text_area', 'hide_also_for_label']);")

    def __repopulate_form(self):
        #-- The dict from dbo_dict expands each id out to its object 
        #-- ie. dc_id in form_data is the dc object in dbo_dict
        #-- The following resets this
        if self.dbo_dict:
            self.form_data = self.dbo_dict
            self.form_data['courier_id']  = self.dbo_dict['courier'].get('courier_id')
            self.form_data['dc_id']       = self.dbo_dict['dc'].get('dc_id')
            self.form_data['check_field'] = 'on' if self.form_data.get('check_field') else ''
        else:
            #-- The http request has to be flat=False or multiple select fields don't get picked up.
            #-- flat=False puts every item as a list. The following converts lists of one item to 
            self.form_data = forms.prep_form_submission_dictionary(self.form_data)

        ## Rebuild form elements
        #-- Here you can rebuild any form elements. Sometimes its necessary or cleaner than modifying elements
        hidden_tag_lists = [
            forms.HiddenField(_id="example_id_a", _value="example_value"),
            forms.HiddenField(_id="example_id_b", _value="example_value"),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        #-- Fill form values 
        self.text_field.addAttributes(_value=self.form_data.get('text_field'))    
        #-- Text area newlines have to be inserted    
        if self.dbo_dict:
            self.text_area.txt ="\n".join(self.dbo_dict.get('text_area','')) + '\n' 
        else:
            self.text_area.txt = "\n".join([x.strip().replace('\r','') for x in self.form_data.get('text_area','').split('\n') if x.strip() != '']) + '\n'

        self.select_field.setSelectedByValue(self.form_data.get('select_field')) 
        self.select_multiple.setSelectedMultipleByValues(self.form_data.get('select_multiple',[]))
        self.number_field.addAttributes(_value=self.form_data.get('number_field')) 
        #-- Date is set automatically so you must override the attribute instead
        self.date_field.overrideAttributes(_value=self.form_data.get('date_field'))   
        if self.form_data.get('check_field') == 'on':
            self.check_field.addAttributes('checked') 
            self.text_area.setHidden(False) 

    def submitForm(self, form_data):
        ''' Take an http request form as a dict'''
        self.form_data = forms.prep_form_submission_dictionary(form_data)
        results = _skeleton_db.updateExampleDb(self.form_data)
        return results


