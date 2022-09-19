from www.modules.page_builder import PageBuilder
from www.views.developer.widgets import ApacheAccessWidget, ApacheErrorWidget, ActivityLogWidget, ErrorAlertWidget, LoggingSearchWidget
from www.views.developer.widgets import DatabaseControlWidget, DatabaseStatsWidget, GlogbalConfigWidget, SqlConsoleWidget, SqlResultsWidget


class DeveloperPageView(PageBuilder):
    ''' Developer admin page. Provides access to development related features and DB controls'''
    def __init__(self, tab=None, **kwargs) -> None:
        self.title = 'Developer'
        self.tab = tab
        self.tab_dict = {'Dashboard': [ErrorAlertWidget, DatabaseControlWidget,  SqlConsoleWidget], 
            'Database': {
                'Database': [DatabaseControlWidget, DatabaseStatsWidget], 
                'SQL window': [SqlConsoleWidget, SqlResultsWidget]
            }, 
            'Global config': [GlogbalConfigWidget], 
            'Logging': [LoggingSearchWidget, ActivityLogWidget, ApacheErrorWidget, ApacheAccessWidget],
            }
        super().__init__(**kwargs)

    def primaryHtml(self) -> str: 
        innerHtml = self.returnWidgetHtmlFromTabs(self.tab_dict)
        return innerHtml

