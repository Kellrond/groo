from flask     import session

from database    import bulletin_board_db as bb_dbo
from www.modules import bulletin_board as bb, forms


class PostForm:
    ''' This form appears and behaves differerntly depending on the post type
            
            - post_type: how the form is shon 
            - dbo_dict: dict from dbo to repopulate form
            - form_data: form field data from http response to rebuild form with
            - submit: if submit=True then form objects will not be built 
            
        Eg: ` this is a code example `
    '''
    def __init__(self, 
            post_type=None, 
            post_id=None,
            parent_post_id=None, 
            ext_ref_id=None, 
            slug=None, 
            dbo_dict=None, 
            form_data=None, 
            submit=False) -> None:
        self.post_type      = post_type
        self.post_id        = post_id
        self.parent_post_id = parent_post_id
        self.ext_ref_id     = ext_ref_id
        self.slug           = slug
        self.dbo_dict       = dbo_dict
        self.form_data      = form_data
        self.submit         = submit

        if self.submit == False:
            self.__build_form_field_objects()
            if self.dbo_dict or self.form_data:
                self.__repopulate_form()


    def __build_form_field_objects(self):
        if self.post_type == 'new_reply':
            btn_txt = 'Reply'
        elif self.post_type == 'edit_reply':
            btn_txt = 'Edit'
        elif self.post_type == 'new_post':
            btn_txt = 'Post'
        elif self.post_type == 'edit_post':
            btn_txt = 'Edit'
        elif self.post_type == 'new_ext_ref':
            btn_txt = 'Post'
            existing_post = bb.getPostIdFromExtRefId(self.slug, self.ext_ref_id)
            if existing_post:
                self.parent_post_id = existing_post
        elif self.post_type == 'edit_ext_ref':
            btn_txt = 'Edit'
            existing_post = bb.getPostIdFromExtRefId(self.slug, self.ext_ref_id)
            if existing_post:
                self.parent_post_id = existing_post
                self.dbo_dict = bb.returnPostById(self.post_id)


        if self.slug:
            category = bb.returnCategoryBySlug(self.slug)
            category_id = category.get('category_id')
        else:
            category_id = ''
        
        hidden_tag_lists = [
            forms.HiddenField(_id="category_id", _value=category_id),
            forms.HiddenField(_id="author_id", _value=session.get('user_id')),
            ]
        if self.parent_post_id:
            hidden_tag_lists.append(forms.HiddenField(_id="parent_post_id", _value=self.parent_post_id))
        if self.post_id:
            hidden_tag_lists.append(forms.HiddenField(_id="post_id", _value=self.post_id))
        if self.ext_ref_id:
            hidden_tag_lists.append(forms.HiddenField(_id="ext_ref_id", _value=self.ext_ref_id))

        self.hidden_tag_html = "".join([form.html() for form in hidden_tag_lists])

        self.title   = forms.Text('required', label="Title", _id="title", _class="mb-2")
        self.body    = forms.TextArea(txt='', _id="body", _rows=10)
        self.body.addAttributes(_placeholder="Write post")
        self.submit  = forms.SubmitBtn(txt=btn_txt,_class="mb-2")


    def __repopulate_form(self):
        if self.dbo_dict:
            self.form_data = self.dbo_dict
        else:
            self.form_data = forms.prep_form_submission_dictionary(self.form_data)

        ## Rebuild form elements
        hidden_tag_lists = [
            forms.HiddenField(_id="edited_by", _value=session.get('user_id')),
            ]
        # The pattern is different here since we want to keep the original hidden tags as well as add these. 
        self.hidden_tag_html += "".join([form.html() for form in hidden_tag_lists])

        self.title.addAttributes(_value=self.form_data.get('title'))    

        self.body.txt = self.dbo_dict.get('body','')


    def submitForm(self, form_data):
        ''' Take an http request form as a dict'''
        self.form_data = forms.prep_form_submission_dictionary(form_data)
        results = bb_dbo.postMessage(self.form_data)
        return results


