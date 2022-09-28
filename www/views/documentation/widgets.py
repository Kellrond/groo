from    flask import request

from    www.modules import forms
from    www.modules.widget_builder   import WidgetBuilder
from    database import docs_db
from    modules.documentation.py_functions import Docs, parseDocstringToHtml


class DocsAdminWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', sql=None, **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.sql = sql if sql != None else 'SELECT * FROM locations'
        self.title = 'Documentation admin and file stats'
        self.widget_id = 'docs_admin'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):     
        rebuild_docs  = forms.SubmitBtn(txt="Rebuild documentation")
        rebuild_docs.addJs(onclick=f'''replaceHtml(id_to_rplc='docs_admin', api_url='/widget/documentation/', api_value='rebuild')''')

        stats_data = docs_db.paginateStats()
        summary_stats = stats_data.get('summary')
        file_details = stats_data.get('detail')
        detail_table_html = self.__get_file_stats_table_html(file_details)

        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <div class="text-center my-2">
                <p>The documentation is all generated from the code. Rebuild the documentation to the current code</p>
                { rebuild_docs.html() }
            </div>
            <hr class="p-0 m-2" />
            <div class="row">
                <h5>Stats</h5>
                <table class="table table-hover text-center me-auto ms-auto" style="width:50%">
                    <tr>
                        <th>Total files</th>
                        <td>{ summary_stats.get('total_files') }</td>
                        <th>Total lines</th>
                        <td>{ summary_stats.get('total_lines') }</td>
                    </tr>
                    <tr>
                        <th>css</th>
                        <td>{ summary_stats.get('css_files') }</td>
                        <th>css</th>
                        <td>{ summary_stats.get('css_lines') }</td>
                    </tr>
                    <tr>
                        <th>js</th>
                        <td>{  summary_stats.get('js_files')  }</td>
                        <th>js</th>
                        <td>{  summary_stats.get('js_lines')  }</td>
                    </tr>
                    <tr>
                        <th>py</th>
                        <td>{  summary_stats.get('py_files')  }</td>
                        <th>py</th>
                        <td>{  summary_stats.get('py_lines')  }</td>
                    </tr>
                    <tr>
                        <th>sh</th>
                        <td>{  summary_stats.get('sh_files')  }</td>
                        <th>sh</th>
                        <td>{  summary_stats.get('sh_lines')  }</td>
                    </tr>
                    <tr>
                        <th>sql</th>
                        <td>{ summary_stats.get('sql_files') }</td>
                        <th>sql</th>
                        <td>{ summary_stats.get('sql_lines') }</td>
                    </tr>
                </table>
            </div>
            <hr class="p-0 m-2" />
            { detail_table_html }
        '''

        return inner_html

    def __get_file_stats_table_html(self, file_details):
        html = '''
            <table id="stats_tbl" class="table table-hover">
                <tr>
                    <th style="width:60%;" onclick="sortTable(0, 'stats_tbl')">File</th>
                    <th style="width:20%;" onclick="sortTable(1, 'stats_tbl')">Extension</th>
                    <th style="width:20%;" onclick="sortTable(2, 'stats_tbl')">Lines</th>
                </tr>'''

        for file in file_details:
            html += f'''
                <tr>
                    <td>{ file.get('file_path') }</td>
                    <td>{ file.get('ext') }</td>
                    <td>{ file.get('lines') }</td>
                </tr>
            '''
        html += '</table>'
        return html


class DocsRoutesWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Routes'
        self.widget_id = 'docs_routes'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        docs = Docs()

        page_dict   = self.__get_pagination_dict()
        routes_tbl_html = self.__return_table_html(routes_result=page_dict.get('results'))

        inner_html = f'''
            <div class="d-flex justify-contents-between">
                <div>
                    <h5>{ self.title }</h5>
                </div>
            </div>
            <hr class="p-0 m-0" />
            { routes_tbl_html }
        '''
        return inner_html


    def __get_pagination_dict(self) -> dict:
        pagination_dict = docs_db.paginateRoutes()
        return pagination_dict

    def __return_table_html(self, routes_result) -> list:
        html = f'''
            <table id="routes_table" class="table table-hover table-striped table-borderless">
                <tr class="overflow-hidden">
                    <th style="width:35%;" onclick="sortTable(0, 'routes_table')">URL</th>
                    <th style="width:15%;" onclick="sortTable(1, 'routes_table')">Permissions</th>
                    <th style="width:15%;" onclick="sortTable(2, 'routes_table')">Methods</th>
                    <th style="width:35%;" onclick="sortTable(3, 'routes_table')">file_path</th>
                </tr>
        '''
        for i, row in enumerate(routes_result):
            row_id   = f'route_{ i }'
            row['url'] = row.get('url','').replace('<','[').replace('>',']')
            if row.get('url').find('[') == -1:
                url_str = f'''<a href="{ row.get('url') }">{ row.get('url') }</a>'''
            else:
                url_str = row.get('url')
            html += f'''
                <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
                    <td>{ url_str }</td>
                    <td>{ row.get('permissions') }</td>
                    <td>{ row.get('methods') }</td>
                    <td>{ row.get('file_path') }</td>
                </tr>    
            '''
        html += '</table>'
        return html


class DocsWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.title = 'Documentation'
        self.widget_id = 'docs_classes'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        docs = Docs()

        page_dict   = self.__get_pagination_dict()

        nav_html = self.__return_docs_nav(page_dict.get('nav_list'))
        documentation_html = self.__return_table_html(
            file_paths=page_dict.get('file_path'), 
            classes=page_dict.get('classes'), 
            class_funcs=page_dict.get('class_funcs'), 
            functions=page_dict.get('functions'),
            routes=page_dict.get('routes'),
            imports=page_dict.get('imports')
            )

        inner_html = f'''
            <div class="row">
                <div class="col-3 mt-3">
                    <h3>API docs</h3>
                    { nav_html }
                </div>
                <div class="col-9">
                    { documentation_html }
                </div>
            </div>
        '''
        return inner_html

    def __get_pagination_dict(self) -> dict:
        lvl1 = self.kwargs.get('lvl1')
        lvl2 = self.kwargs.get('lvl2')
        lvl3 = self.kwargs.get('lvl3')
        lvl4 = self.kwargs.get('lvl4')
        lvl5 = self.kwargs.get('lvl5')
        lvl6 = self.kwargs.get('lvl6')

        pagination_dict = docs_db.paginateDocs(lvl1,lvl2,lvl3,lvl4,lvl5,lvl6,page=self.page)
        return pagination_dict

    def __return_docs_nav(self, file_paths):
        html = ''
        file_paths = [ x.get('file_path') for x in file_paths ]

        # TODO: Theres a better way to do this but I haven't spent the time to think of it. This was to keep moving. Please fix 
        split_paths = []
        for path in file_paths:
            path_parts = path.split('/')
            split_paths.append(path_parts)

        cur_lvl1 = ''
        cur_lvl2 = ''
        cur_lvl3 = ''
        cur_lvl4 = ''
        cur_lvl5 = ''
        cur_lvl6 = ''

        arg_lvl1 = self.kwargs.get('lvl1')
        arg_lvl2 = self.kwargs.get('lvl2')
        arg_lvl3 = self.kwargs.get('lvl3')
        arg_lvl4 = self.kwargs.get('lvl4')
        arg_lvl5 = self.kwargs.get('lvl5')
        arg_lvl6 = self.kwargs.get('lvl6')       

        for parts in split_paths:
            if len(parts) >= 1 and parts[0] != cur_lvl1:
                if parts[0].find('.') > -1:
                    html += f'<small><a href="/developer?tab=Documentation&subtab=Documentation&lvl1={ parts[0]}">{ parts[0] }</a></small><br />'
                else:
                    html += f'<strong><a href="/developer?tab=Documentation&subtab=Documentation&lvl1={ parts[0]}">{ parts[0] }/</a></strong><br />'
                cur_lvl1 = parts[0]
            if len(parts) >= 2 and parts[1] != cur_lvl2:
                if arg_lvl1 == parts[0]:
                    fw = ''
                    slash = ''    
                    if parts[1].find('.py') == -1:
                        fw = 'fw-bold'
                        slash = '/'
                    html += f'<small class="{fw}">&nbsp;&nbsp;<a href="/developer?tab=Documentation&subtab=Documentation&lvl1={parts[0]}&lvl2={parts[1]}">{ parts[1] }{ slash }</a></small><br />'
                cur_lvl2 = parts[1]
            if len(parts) >= 3 and parts[2] != cur_lvl3:
                if arg_lvl1 == parts[0] and arg_lvl2 == parts[1]:
                    fw = ''
                    slash = ''    
                    if parts[2].find('.py') == -1:
                        fw = 'fw-bold'
                        slash = '/'
                    html += f'<small class="{fw}">&nbsp;&nbsp;&nbsp;&nbsp;<a href="/developer?tab=Documentation&subtab=Documentation&lvl1={parts[0]}&lvl2={parts[1]}&lvl3={parts[2]}">{ parts[2] }{ slash }</a></small><br />'
                cur_lvl3 = parts[2]
            if len(parts) >= 4 and parts[3] != cur_lvl4:
                if arg_lvl1 == parts[0] and arg_lvl2 == parts[1] and arg_lvl3 == parts[2]:
                    fw = ''
                    slash = ''    
                    if parts[3].find('.py') == -1:
                        fw = 'fw-bold'
                        slash = '/'
                    html += f'<small class="ms-3 {fw}">&nbsp;&nbsp;&nbsp;<a href="/developer?tab=Documentation&subtab=Documentation&lvl1={parts[0]}&lvl2={parts[1]}&lvl3={parts[2]}&lvl4={parts[3]}">{ parts[3] }{ slash }</a></small><br />'
                cur_lvl4 = parts[3]
            if len(parts) >= 5 and parts[4] != cur_lvl5:
                if arg_lvl1 == parts[0] and arg_lvl2 == parts[1] and arg_lvl3 == parts[2] and arg_lvl4 == parts[3]:
                    slash = ''    
                    fw = ''
                    if parts[4].find('.py') == -1:
                        slash = '/'
                        fw = 'fw-bold'
                    html += f'<small class="ms-5 {fw}"><a href="/developer?tab=Documentation&subtab=Documentation&lvl1={parts[0]}&lvl2={parts[1]}&lvl3={parts[2]}&lvl4={parts[3]}&lvl5={parts[4]}">/{ parts[4] }</a></small><br />'
                cur_lvl5 = parts[4]
            if len(parts) >= 6 and parts[5] != cur_lvl6:
                if arg_lvl1 == parts[0] and arg_lvl2 == parts[1] and arg_lvl3 == parts[2] and arg_lvl4 == parts[3] and arg_lvl5 == parts[4]:
                    fw = ''
                    slash = ''    
                    if parts[5].find('.py') == -1:
                        fw = 'fw-bold'
                        slash = '/'
                    html += f'<small class="ms-5 {fw}">&nbsp;&nbsp;<a href="/developer?tab=Documentation&subtab=Documentation&lvl1={parts[0]}&lvl2={parts[1]}&lvl3={parts[2]}&lvl4={parts[3]}&lvl5={parts[4]}&lvl6={parts[5]}">/{ parts[5] }</a></small><br />'
                cur_lvl5 = parts[5]

        return html

    def __return_table_html(self, file_paths, classes, class_funcs, functions, routes, imports) -> list:
        html = ''
        for fp in file_paths:
            html += f'<h3 class="mt-4 text-secondary">{fp}</h3><hr class="p-0 m-0" />'
            # Routing
            filtered_routes = [ x for x in routes if x.get('file_path') == fp ]
            if len(filtered_routes) > 0:
                html += '<h5 class="mt-3 text-secondary">Routes</h5>'
                html += '<table class="table table-hover table-striped"><tr><th>Url</th><th>Method</th><th>Permissions</th></tr>'
                for route in filtered_routes:
                    html += f'''<tr><td>{ route.get('url').replace('<','&lt;') }</td><td>{ route.get('methods') }</td><td>{ route.get('permissions') }</td></tr>'''
                html += '</table>'
            # Imports
            if len(imports) > 0:
                prev_module = None
                prev_obj = None
                for imp in [ x for x in imports if x.get('file_path') == fp ]:
                    if imp.get('object') == None:
                        if prev_module != None:
                            html += f'<span class="text-info">from <strong class="text-success">&nbsp;{ prev_module }&nbsp;</strong> import <strong class="text-secondary">&nbsp;{ prev_obj }&nbsp;</strong></span><br />'
                            prev_module = None
                            prev_obj = None                   
                        html += f'<span class="text-info">import <strong class="text-success">&nbsp;{ imp.get("module") }&nbsp;</strong></span><br />'
                    else:
                        if prev_module != imp.get("module"):
                            if prev_module != None:
                                html += f'<span class="text-info">from <strong class="text-success">&nbsp;{ prev_module }&nbsp;</strong> import <strong class="text-secondary">&nbsp;{ prev_obj }&nbsp;</strong></span><br />'
                            prev_module = imp.get("module")
                            prev_obj = imp.get("object")
                        else:
                            prev_obj += f', { imp.get("object") }'
                # Catch the last one
                if prev_module != None:
                    html += f'<span class="text-info">from <strong class="text-success">&nbsp;{ prev_module }&nbsp;</strong> import <strong class="text-secondary">&nbsp;{ prev_obj }&nbsp;</strong></span><br />'
            # Classes
            for cls in [ x for x in classes if x.get('file_path') == fp ]:
                title = f"<h4 class='mt-3 text-success'>{ cls.get('name') }<span class='text-secondary fs-5 fw-b'>({ cls.get('parameters') })</span></h4>"
                superclass = f'''<span class="ms-3 mt-2 pt-3"> Inherits from <strong class="text-success">&nbsp;{ cls.get('superclass') }</strong></span>''' if cls.get('superclass') else ''
                docstring = f'''<blockquote>{ parseDocstringToHtml(cls.get('docstring')) }</blockquote><br />'''  if cls.get('docstring') else ''
                methods = [ x for x in class_funcs if x.get('class_id') == cls.get('class_id') ]
                method_html = ''
                for meth in methods:
                    returns = f'<strong class="text-warning ms-2">-> { meth.get("returns") }</strong>' if meth.get('returns') else ''
                    docstr = f'<blockquote class="ms-5 ps-5">{ parseDocstringToHtml(meth.get("docstring")) }</blockquote>' if meth.get('docstring') else ''
                    method_html += f'''<span class="mt-5"><strong class="text-primary ms-5">{ meth.get("name") }</strong>( {meth.get('parameters')} ) { returns }</span><br />{ docstr }'''
                html += f'''
                <div class="docs_div">
                    <div class="d-flex justify-content-between">
                        { title }
                        { superclass }
                    </div>
                    { docstring } 
                    { method_html }
                </div>
                '''
            # Functions
            for func in [ x for x in functions if x.get('file_path') == fp ]:
                returns_html = f'<strong class="text-warning fs-6"> -> { func.get("returns") }</strong>' if func.get('returns') else ''
                doc_str = f'<blockquote class="ms-5">{ parseDocstringToHtml(func.get("docstring")) }</blockquote>' if func.get("docstring") else ''
                html += f'''
                    <h5 class='mt-5 text-primary'>{ func.get('name') }<span class='text-secondary fs-6 fw-b'>({ func.get('parameters') })</span> { returns_html }</h5>
                    { doc_str }
                '''
            html += '<br />'
        return html


class DocsImportdependencyWidget(WidgetBuilder):
    def __init__(self, outer_div='box_div', sql=None, **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.sql = sql if sql != None else 'SELECT * FROM locations'
        self.title = 'Python dependencies'
        self.widget_id = 'docs_dependencies'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        referrer = request.url
        referrer = referrer.split('?')
        dependency_list = docs_db.paginateImportDependancies()

        html = ''

        # TODO: The following 2 if statements can be simplified. 
        if len(dependency_list.get('internal')) > 0:
            html += '''
                <h4>Internal dependencies</h4>
                    <table id="dependency_table" class="table table-hover table-striped">
                        <tr class="overflow-hidden">
                            <th onclick="sortTable(0, 'dependency_table')" style="width:30%;">File path</th>
                            <th onclick="sortTable(1, 'dependency_table')" style="width:10%;">app</th>
                            <th onclick="sortTable(2, 'dependency_table')" style="width:10%;">app.modules</th>
                            <th onclick="sortTable(3, 'dependency_table')" style="width:10%;">app.views</th>
                            <th onclick="sortTable(4, 'dependency_table')" style="width:10%;">environment</th>
                            <th onclick="sortTable(5, 'dependency_table')" style="width:10%;">database</th>
                            <th onclick="sortTable(6, 'dependency_table')" style="width:10%;">docs</th>
                            <th onclick="sortTable(7, 'dependency_table')" style="width:10%;">modules</th>
                        </tr>'''
            for row_id, imp in enumerate(dependency_list.get('internal')):
                html += f'''
                    <tr id="d-{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id=`d-{ row_id }`)">
                        <td>{ imp.get('file_path') }</td>
                        <td>{ imp.get('app') }</td>
                        <td>{ imp.get('app_modules') }</td>
                        <td>{ imp.get('app_views') }</td>
                        <td>{ imp.get('environment') }</td>
                        <td>{ imp.get('database') }</td>
                        <td>{ imp.get('docs') }</td>
                        <td>{ imp.get('modules') }</td>
                    </tr>
                    '''
            html += '</table>'


        if len(dependency_list.get('external')) > 0:
            prev_module = None
            prev_fp  = None
            prev_obj = None
            html += '''
            <h4>External dependencies</h4>
                <table id="ext_dependency_table" class="table table-hover table-striped">
                    <tr>
                        <th onclick="sortTable(0, 'ext_dependency_table')" style="width:30%">File path</th>
                        <th onclick="sortTable(1, 'ext_dependency_table')" style="width:20%">Module</th>
                        <th onclick="sortTable(2, 'ext_dependency_table')" style="width:50%">Objects</th>
                    </tr>'''
            for row_id, imp in enumerate(dependency_list.get('external')):
                
                if imp.get('object') == None:
                    if prev_module != None:
                        html += f'<tr id="r-{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id=`r-{ row_id }`)"><td>{ prev_fp }</td><td>{ prev_module }</td><td>{ prev_obj }</td></tr>'
                        prev_module = None
                        prev_obj = None    
                        prev_fp  = None               
                    html += f'<tr id="r-{ row_id }" class="overflow-hidden"><td>{ imp.get("file_path") }</td><td>{ imp.get("module") }</td><td></td></tr>'
                else:
                    if prev_module != imp.get("module"):
                        if prev_module != None:
                            html += f'<tr id="r-{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id=`r-{ row_id }`)"><td>{ prev_fp }</td><td>{ prev_module }</td><td>{ prev_obj }</td></tr>'
                        prev_module = imp.get("module")
                        prev_obj = imp.get("object")
                        prev_fp  = imp.get("file_path")
                    else:
                        prev_obj += f', { imp.get("object") }'
            # Catch the last one
            if prev_module != None:
                html += f'<tr id="r-{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id=`r-{ row_id }`)"><td>{ prev_fp }</td><td>{ prev_module }</td><td>{ prev_obj }</td></tr>'
            html += '</table>'

        inner_html = f'''
            <h5>{ self.title }</h5>
            <hr class="p-0 m-0" />
            <div class="my-2">
                { html }
            </div>
        '''
        return inner_html
