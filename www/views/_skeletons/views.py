
from flask import session

from www       import config
from database  import _skeleton_db
from www.modules.page_builder import PageBuilder
from www.views._skeletons.widgets import ExampleFormWidget, ExampleListWidget


class ExampleView(PageBuilder):
    ''' An example view with 2 widgets Views are usually groupings of widgets with a little extra sometimes'''
    def __init__(self, **kwargs) -> None:
        self.title = 'Example view'
        super().__init__(**kwargs)

    def primaryHtml(self) -> str:
        example_form_widget = ExampleFormWidget(**self.kwargs)
        example_list = _skeleton_db.returnExampleListById('example_id')
        example_list_widget = ExampleListWidget(example_list=example_list, **self.kwargs) 
        innerHtml = f'''
            <div class="row">
                Something above the first widget. Often buttons
            </div>
            { example_form_widget.html() }
            { example_list_widget.html() }
            <div class="row">
                The results are generated randomly so the result count will vary
            </div>
        '''
        return innerHtml


class ExampleTabView(PageBuilder):
    ''' To create tabs you create a tab_dict at __init__ '''
    def __init__(self, tab=None, **kwargs) -> None:
        self.title = 'Example tabs'
        #-- The tab is passed in as an arg string to select which widgets to draw
        #-- and which tab to highlight. The tab_dict keys are the labels for the tabs 
        self.tab = tab
        self.tab_dict = {'Dashboard': [ExampleFormWidget], 
            'Tab 1': [ExampleFormWidget, ExampleListWidget], 
            'Tab 2': [ExampleListWidget, ExampleFormWidget, ExampleListWidget], 
            }
        super().__init__(**kwargs)

    def primaryHtml(self) -> str:
        innerHtml = ''
        widget_list = self.tab_dict.get(self.tab)
        for widget in widget_list:
            new_widget = widget(**self.kwargs)
            innerHtml += f'''{ new_widget.html() } '''
        return innerHtml