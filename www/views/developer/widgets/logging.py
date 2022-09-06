from    datetime import datetime as dt, timedelta

from    www import config
from    www.modules import forms
from    www.modules.widget_builder   import WidgetBuilder
from    database import log_db


class ActivityLogWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Activity'
        self.widget_id = 'activity_log'
        
        default_start_date = dt.today() - timedelta(days=config.logging_date_range)
        self.start_date = kwargs.get('start_date', default_start_date.strftime(config.sql_date_format))
        self.end_date   = kwargs.get('end_date', dt.today().strftime(config.sql_date_format))
        self.ip         = kwargs.get('ip', '')

        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict = self.__get_pagination_dict()
        activity_table = self.__return_discrepancy_table_html(
            activity_list=page_dict.get('results'))

        pagination_links = self.buildPaginationLinks(count=page_dict.get(
            'count'), api_url='/widget/logging/activity', api_value="", url_args=f"start_date={ self.start_date }&end_date={ self.end_date }&ip={ self.ip }")

        inner_html = f'''
            <div class="d-flex justify-contents-between">
                <div>
                    <h5>{ self.title }</h5>
                </div>
            </div>
            <hr class="p-0 m-0" />
            { activity_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = log_db.paginateActivityLog(start_date=self.start_date, end_date=self.end_date, ip=self.ip, page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, activity_list) -> list:
        html = f'''
            <table  class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:13%;">Time</th>
                    <th style="width:12%;">Ip</th>
                    <th style="width:10%;">Employee</th>
                    <th style="width:18%;">Endpoint</th>
                    <th style="width:12%;">Activity</th>
                    <th style="width:8%;">Id</th>
                    <th style="width:15%;">Arguments</th>
                    <th style="width:15%;">Notes</th>
                </tr>
        '''
        for i, table in enumerate(activity_list):
            row_id = f'act_{ i }'
            warn = 'bg-warning' if table.get('error') else ''
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden { warn }" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('timestamp').strftime('%b %d %H:%M.%S') }</td>
                    <td>{ table.get('ip') }</td>
                    <td>{ table.get('user_id') }</td>
                    <td>{ table.get('endpoint') }</td>
                    <td>{ table.get('activity') }</td>
                    <td>{ table.get('resource_id') }</td>
                    <td>{ table.get('args') }</td>
                    <td>{ str(table.get('note','')) + str(table.get('error','')) }</td>
                </tr>
            '''
        html += '</table>'
        return html


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


class ApacheAccessWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Apache access'
        self.widget_id = 'apache_access'
        
        default_start_date = dt.today() - timedelta(days=config.logging_date_range)
        self.start_date = kwargs.get('start_date', default_start_date.strftime(config.sql_date_format))
        self.end_date   = kwargs.get('end_date', dt.today().strftime(config.sql_date_format))
        self.ip         = kwargs.get('ip', '')

        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict = self.__get_pagination_dict()
        access_table = self.__return_discrepancy_table_html(
            apache_access_list=page_dict.get('results'))
        pagination_links = self.buildPaginationLinks(count=page_dict.get(
            'count'), api_url='/widget/logging/access', api_value="", url_args=f"start_date={ self.start_date }&end_date={ self.end_date }&ip={ self.ip }")

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
            { access_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = log_db.paginateApacheAccess(start_date=self.start_date, end_date=self.end_date, ip=self.ip, page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, apache_access_list) -> list:
        html = f'''
            <table class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:15%;">Timestamp</th>
                    <th style="width:15%;">Ip</th>
                    <th style="width:10%;">Method</th>
                    <th style="width:10%;">Status</th>
                    <th style="width:10%;">Size</th>
                    <th style="width:40%;">Url</th>
                </tr>
        '''
        for i, table in enumerate(apache_access_list):
            warn = 'bg-warning' if int(table.get('response')) >= 400 else ''
            row_id = f'access_{ i }'
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden { warn }" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('timestamp').strftime('%b %d %H:%M.%S') }</td>
                    <td>{ table.get('ip') }</td>
                    <td>{ table.get('method') }</td>
                    <td>{ table.get('response') }</td>
                    <td>{ table.get('size') }</td>
                    <td>{ table.get('url') }</td>
                </tr>
            '''
        html += '</table>'
        return html


class ApacheErrorWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Apache error'
        self.widget_id = 'apache_error'
        
        default_start_date = dt.today() - timedelta(days=config.logging_date_range)
        self.start_date = kwargs.get('start_date', default_start_date.strftime(config.sql_date_format))
        self.end_date   = kwargs.get('end_date', dt.today().strftime(config.sql_date_format))
        self.ip         = kwargs.get('ip', '')

        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict = self.__get_pagination_dict()
        error_table = self.__return_discrepancy_table_html(
            apache_error_list=page_dict.get('results'))

        pagination_links = self.buildPaginationLinks(count=page_dict.get(
            'count'), api_url='/widget/logging/error', api_value="", url_args=f"start_date={ self.start_date }&end_date={ self.end_date }&ip={ self.ip }")

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
            { error_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = log_db.paginateApacheError(start_date=self.start_date, end_date=self.end_date, ip=self.ip, page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, apache_error_list) -> list:
        html = f'''
            <table class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:15%;">Timestamp</th>
                    <th style="width:15%;">Ip</th>
                    <th style="width:70%;">Error</th>
                </tr>
        '''
        for i, table in enumerate(apache_error_list):
            row_id = f'error_{ i }'
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('error_time').strftime('%b %d %H:%M.%S') }</td>
                    <td>{ table.get('ip') }</td>
                    <td>{ table.get('error') }</td>
                </tr>
            '''
        html += '</table>'
        return html


class ErrorAlertWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Error alerts'
        self.widget_id = 'error_alerts'
        
        default_start_date = dt.today() - timedelta(days=config.logging_date_range)
        self.start_date = kwargs.get('start_date', default_start_date.strftime(config.sql_date_format))
        self.end_date   = kwargs.get('end_date', dt.today().strftime(config.sql_date_format))
        self.ip         = kwargs.get('ip', '')

        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict = self.__get_pagination_dict()
        access_table = self.__return_discrepancy_table_html(
            apache_access_list=page_dict.get('results'))
        pagination_links = self.buildPaginationLinks(count=page_dict.get(
            'count'), api_url='/widget/logging/alerts', api_value="", url_args=f"start_date={ self.start_date }&end_date={ self.end_date }&ip={ self.ip }")

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
            { access_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = log_db.paginateErrorAlert(start_date=self.start_date, end_date=self.end_date, ip=self.ip, page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, apache_access_list) -> list:
        html = f'''
            <table class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:12%;">Timestamp</th>
                    <th style="width:12%;">Ip</th>
                    <th style="width:10%;">Log type</th>
                    <th style="width:66%;">Error reference</th>

                </tr>
        '''
        for i, table in enumerate(apache_access_list):
            row_id = f'access_{ i }'
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('timestamp').strftime('%b %d %H:%M.%S') }</td>
                    <td>{ table.get('ip') }</td>
                    <td>{ table.get('log_type') }</td>
                    <td>{ table.get('reference') }</td>
                </tr>
            '''
        html += '</table>'
        return html


class LoggingSearchWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'Logging search'
        self.widget_id = 'logging_search'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        hidden_tag = forms.HiddenField(_id='tab', _value="Logging")
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
            <form action="/site_admin?tab=Logging">
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

