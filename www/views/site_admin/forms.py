from database   import bulletin_board_db
from www.modules import forms
from www.modules.forms.templates import PermissionsSelect


class BbAdminForm:
    def __init__(self, bb_category=None, form_data=None, submit=False) -> None:
        self.dbo_dict    = bb_category
        self.form_data   = form_data
        self.submit      = submit

        if self.submit == False:
            self.__build_form_field_objects()
            if self.dbo_dict or self.form_data:
                self.__repopulate_form()

    def __build_form_field_objects(self):
        ## Form Elements
        hidden_tag_lists = [
            forms.HiddenField(_id="category_id", _value=""),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        category_options = [ {'txt': x.get('name'), 'value': x.get('category_id')} for x in bulletin_board_db.returnCategoriesList() ]
        self.parent_category_id = forms.SelectField(label="Parent category", option_list=category_options, _id="parent_category_id")

        self.description  = forms.Text('required', label="Category description", _id="description")
        self.name  = forms.Text('required', label="Category name", _id="name")
        self.slug           = forms.Text('required', label="Slug", _id="slug")
        self.ext_table_name = forms.Text(label="Db reference", _id="ext_table_name")
        self.permissions    = PermissionsSelect(all=True, label="Permissions required")
        self.active         = forms.CheckField(label="Active category", _id="active")
        self.submit         = forms.SubmitBtn()

    def __repopulate_form(self):
        if self.dbo_dict:
            self.form_data = self.dbo_dict
        else:
            self.form_data = forms.prep_form_submission_dictionary(self.form_data)

        ## Rebuild form elements
        hidden_tag_lists = [
            forms.HiddenField(_id="category_id", _value=self.form_data.get('category_id')),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        self.parent_category_id.setSelectedByValue(self.form_data.get('parent_category_id')) 
        self.name.addAttributes(_value=self.form_data.get('name'))  
        self.description.addAttributes(_value=self.form_data.get('description'))      
        self.slug.addAttributes(_value=self.form_data.get('slug'))       
        self.ext_table_name.addAttributes(_value=self.form_data.get('ext_table_name'))     
        self.permissions.setSelectedByValue(self.form_data.get('permissions'))                         
         
        if self.form_data.get('active') == 'on' or self.dbo_dict.get('active') == True:
            self.active.addAttributes('checked') 

    def submitForm(self, form_data):
        ''' Take an http request form as a dict'''
        self.form_data = forms.prep_form_submission_dictionary(form_data)
        results = bulletin_board_db.updateCategory(self.form_data)
        return results


