from    math    import ceil
from    flask   import session

from    www               import config as conf


class WidgetBuilder:
    ''' Superclass for widgets. Do not call this directly. Provides common functions to widgets
            Params:
                - outer_div: css class for the div containing the widget
                - **kwargs: holds the keyword args passed into the child class 

            Usage:
                `class DatabaseControlWidget(WidgetBuilder):`

            Notes:
                - some widgets, like home page posts, give a list of widgets in return
    '''
    def __init__(self, outer_div: str, **kwargs) -> None:
        self.kwargs = kwargs
        self.outer_div = outer_div
        self.toast_html = ''

    def html(self) -> str:
        ''' Returns the HTML for the widget as a string and adds toast if there is a toast in the session cookie '''
        self.__set_toast_html()
        return self.__wrap_outer_div()

    def __set_toast_html(self):
        if session.get('toast'):
            toast_dict = session.pop('toast')
            toast_success = 'bg-success text-light' if toast_dict.get('success') else 'bg-danger text-dark'
            self.toast_html = f'''
                <div class="position-fixed top-0 end-0 p-3 mt-5 me-5" style="z-index: 9">
                    <div id="liveToast" class="toast" role="alert" data-bs-delay="{ conf.toast_time_ms }">
                        <div id="msg-colour" class="toast-header { toast_success }">
                        <strong id="msg-header" class="me-auto">{ toast_dict.get('header','') }</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                        </div>
                        <div id="msg-body" class="toast-body fs-6 text-center">{ toast_dict.get('msg', '') }</div>
                    </div>
                </div>
            '''    
        else:
            self.toast_html = ''  

    def __wrap_outer_div(self):
        widget_inner_html = self.getWidgetHtml()
        # Some widgets give out a list of widgets, Home page for example. 
        widget_list = []
        if type(widget_inner_html) == str:
            widget_list.append(widget_inner_html)
        else:
            widget_list = widget_inner_html
        wrapped_widgets = ''
        for widget in widget_list:
            wrapped_widgets += f'<div id="{self.widget_id}" class="{ self.outer_div }">{ widget }</div>'
        wrapped_widgets += self.toast_html
        return wrapped_widgets

    def buildPaginationLinks(self, count: int, api_url: str, api_value:str, url_args=None) -> str:
        ''' Creates pagination links and result count when returned results exceed the page limit

                Params:
                    - count: the total number of results available
                    - api_url: the url of the 
                    - api_value: if the route has a variable ie. /manifest_edit/<manifest_id>
                    - url_args=None: adds arguments to the url string. & must separate multiple args

        '''
        max_rows = conf.max_table_length
        # Some pages have custom lengths set them here
        if api_url[:25] == '/widget/bb_category/list/':
            max_rows = conf.bulletin_board_posts_per_page

        page = int(self.kwargs.get('page', 1))
        if count > max_rows:
            link_list = []

            max_pages = ceil((count + 0.0) / max_rows )

            if max_pages <= conf.max_pagination_links:
                start_range = 1
                end_range   = max_pages
            else:
                half_way_in_buttons = ceil(conf.max_pagination_links / 2)
                if page <= half_way_in_buttons:
                    start_range = 1
                    end_range = conf.max_pagination_links
                else:
                    start_range = page - half_way_in_buttons
                    end_range   = page + half_way_in_buttons - 1

            end_range = end_range if end_range <= max_pages else max_pages

            for i in range(start_range, end_range + 1):
                arg_string = '?'
                if url_args:
                    arg_string += url_args + "&"
                arg_string += f'page={ i }'

                highight = ''
                if i == page:
                    highight = 'active'
                link_list.append(f'''
                    <li class="page-item { highight }">
                        <a class="page-link" onclick="replaceHtml(id_to_rplc='{ self.widget_id }', api_url='{ api_url }', api_value='{ api_value }{ arg_string }')" style="cursor: pointer;">{ i }</a>
                    </li>''')
            link_string = f'''
                <nav>
                    <ul class="pagination">
                        { "".join(link_list) }
                    </ul>
                </nav>
            '''
            # Fix the results on the final page to cap out at the count - ie. not show 31-45 of 33 results
            if page * max_rows > count:
                upper_result_cap = count 
            else:
                upper_result_cap =  page * max_rows 
            return f'''
                <div class="d-flex justify-content-between">
                { link_string }
                { (page - 1) * max_rows + 1 } - { upper_result_cap } of { count } results
                </div>
            '''
        else:
            return ''

            