from flask import session, url_for

from www         import config
from database    import _skeleton_db
from www.modules import forms
from www.modules.widget_builder import WidgetBuilder
from www.views._skeletons.forms import ExampleForm
from www.modules import _skeletons


class ExampleListWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Example list widget'
        self.widget_id = 'example_list_id'
        self.show_active_results = True
        if kwargs.get('active') == False or kwargs.get('active') == 'False':
            self.show_active_results =  False
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict     = self.__get_pagination_dict()
        example_table = self.__return_discrepancy_table_html(example_table_list=page_dict.get('results'))
        pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url='/widget/example/list/',api_value=self.show_active_results)

        btn_txt = 'Show inactive' if self.show_active_results else 'Show active'
        toggle_inactive_btn = forms.SubmitBtn(bootstrap_color='outline-dark', txt=btn_txt, _class="btn-sm ms-auto mb-2")
        toggle_inactive_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='example_list_id', api_url='/widget/example/list/', api_value='{ not self.show_active_results }')")

        inner_html = f'''
            <div class="d-flex justify-contents-between">
                <div>
                    <h5>{ self.title }</h5>
                </div>
                { toggle_inactive_btn.html() }
            </div>
            <hr class="p-0 m-0" />
            { example_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = _skeleton_db.returnExamplePagination(active=self.show_active_results, page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, example_table_list) -> list:
        html = f'''
            <table class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:12%;">Text</th>
                    <th style="width:12%;">Select</th>
                    <th style="width:14%;">Date</th>
                    <th style="width:10%;">Number</th>
                    <th style="width:14%;">Text area</th>
                    <th style="width:14%;">Select multiple</th>
                    <th style="width:12%;">Active</th>
                    <th style="width:6%;"></th>
                </tr>
        '''
        for i, example in enumerate(example_table_list):
            toast_btn  = forms.SubmitBtn(bootstrap_color='outline-success', txt='Toast', _class='btn-sm py-0 px-1 my-0')
            toast_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='example_list_id', api_url='/widget/example/list/',api_value='{ self.show_active_results }?toast=Sent%20toast');launchToast()")
            row_id   = f'inv_disc_{ i }'
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ example.get('text_field') }</td>
                    <td>{ example.get('select_field') }</td>
                    <td>{ example.get('date_field') }</td>
                    <td>{ example.get('number_field') }</td>
                    <td>{ example.get('text_area') }</td>
                    <td>{ example.get('select_multiple') }</td>
                    <td>{ example.get('active') }</td>
                    <td>{ toast_btn.html() }</td>
                </tr>
            '''
        html += '</table>'
        return html


class ExampleFormWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'Example form widget'
        self.widget_id = 'example_form_widget_id'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        example_obj = _skeletons.ExampleObj()
        example_arg = session.get('user_id') 
        form = ExampleForm(example_object=example_obj, example_arg=example_arg, **self.kwargs)
        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <form id="example_form_id" action="{ url_for('example.__example') }" method="POST">  
                { form.hidden_tag_html }
                <div class="form-group row mb-2">
                    <div class="col-lg-6">
                        <div class="row mt-2">
                            <div class="col">
                                { form.text_field.html() }
                            </div>
                            <div class="col">
                                { form.select_field.html() }
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col">
                                { form.date_field.html() }
                            </div>
                            <div class="col">
                                { form.number_field.html() }
                            </div>
                        </div>
                    </div>  
                     <div class="col-lg-6">
                        <div class="row mt-2">
                            <div class="col">
                                <div id="hide_also_for_label" { form.text_area.hiddenHtmlAttribute() }>
                                    { form.text_area.html() }
                                </div>
                            </div>
                            <div class="col">
                                { form.select_multiple.html() }
                            </div>
                        </div>
                    </div>  
                </div>
                <div class="d-flex justify-content-between mt-3">
                    { form.check_field.html() }
                    { form.submit.html() }
                </div>
            </form>
        '''
        return inner_html
