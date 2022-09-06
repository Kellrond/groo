from flask   import session, url_for
from www     import config as conf
from www.modules     import formatting
from www.modules.nav_builder import NavBuilder


class PageBuilder:
    ''' Is a Superclass which is inherited from when creating Views. 
    Do not instantiate this class on it's own. 

        Useage:
            `class ExampleView(PageBuilder):`

    Wraps the HTML and makes it pretty. Also handles toast on page load
    '''

    def __init__(self, **kwargs) -> None:
        self.toast  = ''
        self.kwargs = kwargs

    def html(self) -> str:
        ''' Renders the final HTML to be sent to the client. 
        Nav bar and widgets are rendered then added into the page template
        
            Notes:
                - currently pretty prints the HTML this may change
        '''
        self.sendToast()
        nav       = NavBuilder()
        tab_html  = self.__return_tab_html()
        page_body = self.primaryHtml()

        footer    = f'''

        '''

        html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8' />
                <meta http-equiv='X-UA-Compatible' content='IE=edge' />
                <title>Garden Pi</title>
                <meta name='viewport' content='width=device-width, initial-scale=1' /> 
                <script src="https://d3js.org/d3.v7.min.js" defer></script>
                <script src="https://cdn.jsdelivr.net/npm/d3-scale@4" defer></script>
                <link rel='stylesheet' type='text/css' media='screen' href="{ url_for('static', filename='css/bootstrap.css') }" />
                <link rel='stylesheet' type='text/css' media='screen' href="{ url_for('static', filename='css/main.css') }" />
                <link rel="shortcut icon" href="{ url_for('static', filename='favicon.ico') }" />
            </head>
            <body>
                <div class="container">
                    { nav.html() } 
                    <div id="body_div" class="body-container ">
                        <div class="mt-5">
                            <h2>{ self.title }</h2>
                            { tab_html }
                        </div>
                        <div class="col-sm-12 col mt-1 mb-5" id="page_body">
                            { page_body }
                        </div>
                    </div>
                    <footer class="d-flex justify-content-between bg-dark fixed-bottom text-white" style="opacity: 90%;">
                        <div class="footer-block d-none d-md-block"></div>
                        <div class="footer-block d-none d-md-block"> Garden Pi</div>
                        <div class="footer-block my-2 mx-4"></div>
                    </footer> 
                    { self.toast }
                </div>
                <script src="{ url_for('static', filename='js/bootstrap.bundle.min.js') }"></script>
                <script src="{ url_for('static', filename='js/app.js') }"></script> 
            </body>
            </html>
        '''
        return formatting.prettyHtml(html)
    
    def sendToast(self, toast_dict=None):
        ''' Toasts are the popup js windows the site uses to inform the user of the results of an action
        A toast can either be sent to the page object before it is called with this function

        Params:
            - toast_dict=None: {'header': '', 'msg': '', 'success': True} is accepted

        Useage:
            - Method A
            `view = ExampleView()
            view.sendToast({'header': '', 'msg': 'Example toast', 'success': True})
            return view.html(), 200
            `
            - Method B: More useful to send a message to the next page
            `view = ExampleView()
            session['toast'] = {'header': '', 'msg': 'Example toast', 'success': True})
            return view.html(), 200
            `
        
        Notes:
            - this method is also called right before rendering, so toasts stored in session data will be displayed
            
        '''
        if toast_dict == None and session.get('toast'):
            toast_dict = session.get('toast')
            session.pop('toast')

        # Only allow one toast. Show the first one received
        if toast_dict and self.toast == '':
            toast_success = 'bg-success text-light' if toast_dict.get('success') else 'bg-danger text-dark'
            self.toast = f'''
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
            self.toast = ''  

    def returnWidgetHtmlFromTabs(self, tab_dict):
        '''Renders a set of widgets based on a tab dictionary. 

                Usage:
                    `self.tab_dict = {
                    'Dashboard': [ExampleWidget1], 
                    'DropDownTab1': {'Tab1': [ExampleWidget2], 'Tab2': [ExampleWidget3]},
                    'DropDownTab2': {'Tab1': [ExampleWidget4, ExampleWidget5]}
                    }
                    ...
                    innerHtml = self.returnWidgetHtmlFromTabs(self.tab_dict)
                    `

                Notes:
                    - first item in the dict should be a list not a dict. Otherwise the landing page will be blank.

        '''
        innerHtml = ''
        widget_list = tab_dict.get(self.tab)
        if type(widget_list) == list:
            for widget in widget_list:
                new_widget = widget(**self.kwargs)
                innerHtml += f'''{ new_widget.html() } '''
        elif type(widget_list) == dict:
            widget_list = widget_list.get(self.kwargs.get('subtab'),[])
            for widget in widget_list:
                new_widget = widget(**self.kwargs)
                innerHtml += f'''{ new_widget.html() } '''
        return innerHtml        

    def __return_tab_html(self):
        if hasattr(self, 'tab_dict'):
            if not self.tab:
                self.tab = list(self.tab_dict)[0]
            html = '<ul class="nav nav-pills justify-content-end mb-0">'
            for tab, val in self.tab_dict.items():
                active = 'active' if self.tab == tab else ''
                if type(val) == list:
                    html += f'<li class="nav-item"><a class="nav-link { active } px-3 py-1 my-0" aria-current="page" href="?tab={ tab }">{ tab }</a></li>'
                if type(val) == dict:
                    html += f'<li class="nav-item dropdown"><a class="nav-link { active } dropdown-toggle px-3 py-1 my-0" data-bs-toggle="dropdown" href="?tab={ tab }" role="button">{ tab }</a>'
                    html += '<ul class="dropdown-menu">'
                    for sub_key in val.keys():
                        html += f'<li><a class="dropdown-item" href="?tab={ tab }&subtab={ sub_key }">{ sub_key }</a></li>'
                    html += '</ul></li>'
            html += '</ul>'
            return html
        else:
            return ''

