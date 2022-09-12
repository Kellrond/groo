import shutil
from flask import session, url_for 

from    www.modules import forms
from    www.modules.widget_builder   import WidgetBuilder
import  database
from    database import __admin__ as db_admin


class DatabaseControlWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'Database control'
        self.widget_id = 'database_control'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        arm_backup   = forms.CheckField(label="Arm backup")
        arm_restore  = forms.CheckField(label="Arm restore")
        arm_update   = forms.CheckField(label="Arm update")
        backup_btn   = forms.SubmitBtn(bootstrap_color='danger', txt='Backup DB', _class="my-1", _id='backup_btn')
        restore_btn  = forms.SubmitBtn(bootstrap_color='danger', txt='Restore DB', _class="my-1", _id='restore_btn')
        update_btn   = forms.SubmitBtn(bootstrap_color='danger', txt='Update DB', _class="my-1", _id='update_btn')
        download_btn = forms.SubmitBtn(txt='Download current backup', _class="my-1")

        backup_btn.setHidden(True)
        restore_btn.setHidden(True)
        update_btn.setHidden(True)

        backup_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='database_control', api_url='/widget/database/', api_value='backup'); this.disabled = true;")
        restore_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='database_control', api_url='/widget/database/', api_value='restore'); this.disabled = true;")
        update_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='database_control', api_url='/widget/database/', api_value='update'); this.disabled = true;")

        arm_backup.addJs(_onchange="toggleVisible('backup_btn');")
        arm_restore.addJs(_onchange="toggleVisible('restore_btn');")
        arm_update.addJs(_onchange="toggleVisible('update_btn');")

        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <div class="form-group row mb-2">
                <div class="col-lg-6">
                    <div class="row mt-1">
                        <div class="col">
                            { arm_backup.html() }
                        </div>
                        <div class="col">
                            { backup_btn.html() }
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col">
                            { arm_restore.html() }
                        </div>
                        <div class="col">
                            { restore_btn.html() }                                
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col">
                            { arm_update.html() }
                        </div>
                        <div class="col">                            
                            { update_btn.html() }
                        </div>
                    </div>
                </div>  
                    <div class="col-lg-6">
                    <div class="row mt-2">
                        <div class="col">
                            <form action="{ url_for('developer.database_control', command='download') }">
                            { download_btn.html() }
                            </form>
                        </div>
                    </div>
                </div>  
            </div>
        '''
        return inner_html


class DatabaseStatsWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Database statistics'
        self.widget_id = 'database_stats'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict   = self.__get_pagination_dict()
        stats_table = self.__return_discrepancy_table_html(table_stats_list=page_dict.get('results'))
        pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url='/widget/database/stats',api_value="")

        inner_html = f'''
            <div class="d-flex justify-contents-between">
                <div>
                    <h5>{ self.title }</h5>
                </div>
            </div>
            <hr class="p-0 m-0" />
            { stats_table }
            { pagination_links }
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        pagination_dict = db_admin.returnDbStatsPagination(page=self.page)
        return pagination_dict

    def __return_discrepancy_table_html(self, table_stats_list) -> list:
        html = f'''
            <table class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:18%;">Schema name</th>
                    <th style="width:46%;">Table name</th>
                    <th style="width:18%;">Size</th>
                    <th style="width:18%;">Bytes</th>
                </tr>
        '''
        for i, table in enumerate(table_stats_list):
            row_id   = f'db_{ i }'
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ table.get('schema_name') }</td>
                    <td>{ table.get('table_name') }</td>
                    <td>{ table.get('size') }</td>
                    <td>{ table.get('bytes') }</td>
                </tr>
            '''
        html += '</table>'
        return html


class SqlConsoleWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.title = 'SQL window'
        self.widget_id = 'sql_window'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        sql_console = forms.TextArea(_placeholder="SELECT * FROM locations", _id="sql_input")
        submit = forms.SubmitBtn(txt="Query DB")
        submit.addJs(_onclick=f"replaceHtml(id_to_rplc='sql_results', api_url='/widget/database/query', api_value=`?sql=${{document.getElementById('sql_input').value}}`);")
        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <div class="col mt-3">
                { sql_console.html() }
            </div>   
            <div class="d-flex justify-content-end mt-3">
                { submit.html() }
            </div>
        '''
        return inner_html


class SqlResultsWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', sql=None, **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.sql = sql if sql != None else 'SELECT * FROM locations'
        self.title = 'SQL results'
        self.widget_id = 'sql_results'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        if self.sql != None:
            page_dict   = self.__get_pagination_dict()

            if page_dict.get('count') > 0:
                stats_table = self.__return_table_html(sql_results=page_dict.get('results'))
                pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url='/widget/database/query',api_value='', url_args=f"sql={self.sql}")

                inner_html = f'''
                    <div class="d-flex justify-contents-between">
                        <div>
                            <h5>{ self.title }</h5>
                        </div>
                    </div>
                    <hr class="p-0 m-0" />
                    <div class="col overflow-scroll">
                        { stats_table }
                    </div>
                    { pagination_links }
                '''
                return inner_html
            else:
                return f'<div>{ page_dict.get("results") }</div>'

    def __get_pagination_dict(self) -> dict:
        pagination_dict = database.returnQueryPagination(sql=self.sql,page=self.page)
        return pagination_dict

    def __return_table_html(self, sql_results) -> list:
        html = '<table class="table table-hover table-striped table-borderless"><tr>'
        for key in sql_results[0].keys():
            html += f'<th>{ key }</th>'
        html += '</tr>'

        for i, row in enumerate(sql_results):
            row_id   = f'sql_{ i }'
            html += f'''<tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">'''
            for column in row.values():
                html += f'''<td>{ column }</td>'''
            html += '</tr>'
        html += '</table>'
        return html

