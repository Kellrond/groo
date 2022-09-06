from www.modules.page_builder    import PageBuilder
from www.views.home.widgets      import PostWidget


class HomePageView(PageBuilder):
  ''' The home page consists of two columns 
      - Left: Posts are displayed here. To a max limit defined in app/config.py
      - Right: Upcoming rail, Suggestion box and Month shipments graph widgets
  '''
  def __init__(self, **kwargs) -> None:
    self.title = 'Home page'
    super().__init__(**kwargs)
      
  def primaryHtml(self):
    # posts_widget = PostWidget().html()

    col_1 = 'The most basic home page'
    col_2 = ''

    return f'''
      <div class="row p-0 mx-2">
        <div class="col-12">
          {col_1}
        </div>
      </div>
      '''
