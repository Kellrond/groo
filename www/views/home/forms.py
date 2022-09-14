from datetime  import datetime as dt, timedelta
from flask     import session

from www         import config
from www.modules import forms


class HomepageContentForm:
    ''' Updates and adds new home page content which displays in a blog style on the homepage '''
    def __init__(self, dbo_dict=None, form_data=None, submit=False) -> None:
        self.dbo_dict    = dbo_dict
        self.form_data   = form_data
        self.submit      = submit

        if self.submit == False:
            self.__build_form_field_objects()
            if self.dbo_dict or self.form_data:
                self.__repopulate_form()

    def __build_form_field_objects(self):
        hidden_tag_lists = [
            forms.HiddenField(_id='page_content_id', _value=''),
            forms.HiddenField(_id='dc_id', _value=session.get('dc_id')),
            forms.HiddenField(_id='user_id', _value=session.get('user_id')),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        self.title           = forms.Text(label='Title', _id="title")
        self.content         = forms.TextArea(label='Content', _id='content', _rows=14)
        self.publish_on      = forms.DateField(label="Publish on", _id="publish_on")
        self.publish_until   = forms.DateField(label="Publish until", _id="publish_until")
        self.active          = forms.CheckField(label='Active', _id="active")
        self.submit_btn      = forms.SubmitBtn()

        publish_until_date = dt.today() + timedelta(days=config.homepage_content_publish_for_days)
        self.publish_until.overrideAttributes(_value=publish_until_date.strftime(config.sql_date_format))

    def __repopulate_form(self):
        if self.dbo_dict:
            self.form_data = self.dbo_dict
        else:
            self.form_data = forms.prep_form_submission_dictionary(self.form_data)

        hidden_tag_lists = [
            forms.HiddenField(_id='page_content_id', _value=self.form_data.get('page_content_id')),
            forms.HiddenField(_id='dc_id', _value=self.form_data.get('dc_id')),
            forms.HiddenField(_id='user_id', _value=self.form_data.get('user_id')),
            ]
        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        self.title.addAttributes(_value=self.form_data.get('title'))
        self.publish_on.overrideAttributes(_value=self.form_data.get('publish_on'))
        self.publish_until.overrideAttributes(_value=self.form_data.get('publish_until'))
        self.content.txt = self.form_data.get('content','')

        if self.form_data.get('active') == 'on' or self.form_data.get('active') == True:
            self.active.addAttributes('checked') 

    def submitForm(self, form_data):
        ''' Take an http request form as a dict'''
        self.form_data = forms.prep_form_submission_dictionary(form_data) 
        results = page_content_db.updatePageContentDb(self.form_data)
        return results
