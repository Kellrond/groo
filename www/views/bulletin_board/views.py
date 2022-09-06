from flask import session

from www       import config
from www.modules.page_builder import PageBuilder
from www.views.bulletin_board.widgets import BBNavWidget, BBCategoryListWidget, BBMessageListWidget, BBMessageWidget, BBPostWidget

class BulletinBoardView(PageBuilder):
    ''' Displays the full bulletin board. Individual widgets can be placed on pages as needed '''
    def __init__(self, **kwargs) -> None:
        self.title = ''
        super().__init__(**kwargs)

    def primaryHtml(self) -> str:
        widget_list = [BBNavWidget(**self.kwargs)]
        if self.kwargs.get('slug') == None or self.kwargs.get('slug') == 'bb':
            self.kwargs['slug'] = 'bb'
            widget_list.append(BBCategoryListWidget(**self.kwargs))
        if self.kwargs.get('post_id') == None:
            widget_list.append(BBMessageListWidget(**self.kwargs))
        if self.kwargs.get('post_id') != None:
            widget_list.append(BBMessageWidget(**self.kwargs))
            widget_list.append(BBPostWidget(**self.kwargs))

        innerHtml = ''
        for widget in widget_list:
            innerHtml += widget.html()
        return innerHtml