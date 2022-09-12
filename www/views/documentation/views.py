from www.modules.page_builder import PageBuilder
from www.views.documentation.widgets import DocsAdminWidget, DocsWidget, DocsRoutesWidget, DocsImportdependencyWidget


class DocumentationPageView(PageBuilder):
    ''' Developer admin page. Provides access to development related features and DB controls'''
    def __init__(self, tab=None, **kwargs) -> None:
        self.title = 'Developer'
        self.tab = tab
        self.tab_dict = {
                'Admin and Statistics': [ DocsAdminWidget],
                'Documentation': [ DocsWidget],
                'Import dependencies': [DocsImportdependencyWidget],
                'Routes': [DocsRoutesWidget]
            }
        super().__init__(**kwargs)

    def primaryHtml(self) -> str: 
        innerHtml = self.returnWidgetHtmlFromTabs(self.tab_dict)
        return innerHtml

