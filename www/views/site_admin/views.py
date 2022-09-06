from www.modules.page_builder import PageBuilder
from www.views.site_admin.widgets import AnalyticsSearchWidget, AnalyticsResultSummaryWidget, BulletinBoardAdminWidget, BulletinBoardListWidget


class SiteAdminView(PageBuilder):
    ''' Site admin page. Provides access to site administration related features'''
    def __init__(self, tab=None, **kwargs) -> None:
        self.title = 'Site administration'
        self.tab = tab
        self.tab_dict = {'Dashboard': [ AnalyticsResultSummaryWidget, BulletinBoardListWidget], 
            'Analytics': [AnalyticsSearchWidget, AnalyticsResultSummaryWidget], 
            'Bulletin board': [BulletinBoardAdminWidget, BulletinBoardListWidget], 
            }
        super().__init__(**kwargs)

    def primaryHtml(self) -> str:
        innerHtml = self.returnWidgetHtmlFromTabs(self.tab_dict)
        return innerHtml
