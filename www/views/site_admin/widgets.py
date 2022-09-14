from datetime    import datetime as dt, timedelta

from www         import config
from database    import bulletin_board_db, log_db
from www.modules import forms
from www.modules.widget_builder import WidgetBuilder
from www.views.site_admin.forms import BbAdminForm


class AnalyticsSearchWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'Analytics search'
        self.widget_id = 'analytics_search'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        hidden_tag = forms.HiddenField(_id='tab', _value="Analytics")
        start_date_dt = dt.today() - timedelta(days=config.logging_date_range)
        start_date_dt = start_date_dt.strftime(config.sql_date_format)
        start_date = forms.DateField(label="Start date", _id="start_date", _value=self.kwargs.get('start_date', start_date_dt))
        end_date   = forms.DateField(label="End date", _id="end_date", _value=self.kwargs.get('end_date', dt.today().strftime(config.sql_date_format)))
        ip         = forms.Text(label="Ip", _id="ip",_placeholder="172.x.xx.xxx", _pattern="[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
        submit     = forms.SubmitBtn() 

        if self.kwargs.get('ip'):
            ip.addAttributes(_value=self.kwargs.get('ip'))

        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <form action="/site_admin?tab=Analytics">
                { hidden_tag.html() }
                <div class="form-group row mt-2">
                    <div class="col">
                        { start_date.html() }   
                    </div>
                    <div class="col">
                        { end_date.html() }
                    </div>
                    <div class="col">
                        { ip.html() }
                    </div>
                    <div class="d-flex justify-content-end mt-2">
                        { submit.html() }
                    </div>
                </div>
            </form>
        '''
        return inner_html


class AnalyticsResultSummaryWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Analytics summary'
        self.widget_id = 'analytics_summary'

        self.default_start_date = dt.today() - timedelta(days=config.logging_date_range)
        self.start_date = kwargs.get('start_date', self.default_start_date.strftime(config.sql_date_format))
        self.end_date   = kwargs.get('end_date', dt.today().strftime(config.sql_date_format))
        self.ip         = kwargs.get('ip', '')
        
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        analytics_summary = log_db.returnAnalyticsSummary(start_date=self.start_date, end_date=self.end_date, ip=self.ip)
        inner_html = f'''
            <div class="d-flex row justify-content-between">
                <div class="col">
                    <h5>{ self.title }</h5>
                </div>
                <div class="col d-flex justify-content-end">
                 { self.start_date } to { self.end_date }
                </div>
            </div>
            <hr class="p-0 m-0" />
            <div class="row">
                <div class="col-3 d-flex justify-content-between">
                    <strong>Page views</strong>
                    { analytics_summary.get('page_views') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Bytes sent</strong>
                    { analytics_summary.get('bytes_sent') } kb
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Searches</strong>
                    { analytics_summary.get('searches') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Logins</strong>
                    { analytics_summary.get('logins') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Cron backups</strong>
                    { analytics_summary.get('backups') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Email manifest</strong>
                    { analytics_summary.get('email_manifest') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Edit manifest</strong>
                    { analytics_summary.get('edit_manifest') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Error apache</strong>
                    { analytics_summary.get('apache_error') }
                </div>
                <div class="col-3 d-flex justify-content-between">
                    <strong>Error activity</strong>
                    { analytics_summary.get('activity_error') }
                </div>
            </div>
        '''
        return inner_html


class BulletinBoardAdminWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.bb_category = kwargs.get('bb_category')
        self.title = 'Bulletin board administration'
        self.widget_id = 'bb_admin'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        form = BbAdminForm(bb_category=self.bb_category)
        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <div class="form-group col mb-2">
                <form action="/widget/bb_admin/category" method="POST"> 
                    { form.hidden_tag_html }
                    <div class="form-group row mt-2">
                        <div class="col-lg-6">
                            { form.parent_category_id.html() }
                            { form.name.html() }
                            { form.description.html() }
                        </div>  
                        <!-- Right side of form -->
                        <div class="col-lg-6">          
                            <div class="row">
                                <div class="col">
                                    { form.slug.html() }
                                </div>
                                <div class="col">
                                    { form.ext_table_name.html() }
                                </div>
                            </div>
                            { form.permissions.html() }
                            <strong>&nbsp;</strong>
                            { form.active.html() }
                        </div>
                    </div>
                    <div class="d-flex justify-content-end mt-3">
                        { form.submit.html() }
                    </div>
                </form>
            </div>
        '''
        return inner_html


class BulletinBoardListWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Bulletin boards'
        self.widget_id = 'bb_list'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict = self.__get_pagination_dict()
        category_table = self.__return_discrepancy_table_html(
            category_list=page_dict.get('results'))
        pagination_links = self.buildPaginationLinks(count=page_dict.get(
            'count'), api_url='/widget/database/stats', api_value="")

        inner_html = f'''
            <div class="d-flex justify-contents-between">
                <div>
                    <h5>{ self.title }</h5>
                </div>
            </div>
            <hr class="p-0 m-0" />
            { category_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = bulletin_board_db.paginateBulletinBoardCategories(
            page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, category_list) -> list:
        html = f'''
            <table id="bb_table" class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:14%;" onclick="sortTable(0, 'bb_table')">Name</th>
                    <th style="width:12%;" onclick="sortTable(1, 'bb_table')">Slug</th>
                    <th style="width:14%;" onclick="sortTable(2, 'bb_table')">Parent</th>
                    <th style="width:26%;" onclick="sortTable(3, 'bb_table')">Description</th>
                    <th style="width:12%;" onclick="sortTable(4, 'bb_table')">Permissions</th>
                    <th style="width:8%;" onclick="sortTable(5, 'bb_table')">Posts</th>
                    <th style="width:8%;" onclick="sortTable(6, 'bb_table')">Active</th>
                    <th style="width:8%;">Edit</th>
                </tr>
        '''
        for i, table in enumerate(category_list):
            edit_btn = forms.SubmitBtn(bootstrap_color='outline-danger',
                                       txt='Edit', _class='btn-sm py-0 px-1 my-0', _id=f'edit-{i}')
            edit_btn.addJs(
                _onclick=f"replaceHtml(id_to_rplc='bb_admin', api_url='/widget/bb_admin/category/',api_value='{table.get('category_id')}')")
            row_id = f'db_{ i }'
            permission_name = [k for k, v in config.Permissions.__dict__.items(
            ) if v == table.get('permissions')][0]
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('name') }</td>
                    <td>{ table.get('slug') }</td>
                    <td>{ table.get('parent_category') }</td>
                    <td>{ table.get('description') }</td>
                    <td>{ permission_name }</td>
                    <td>{ table.get('count') }</td>
                    <td>{ table.get('active') }</td>
                    <td>{ edit_btn.html() }</td>
                </tr>
            '''
        html += '</table>'
        return html

