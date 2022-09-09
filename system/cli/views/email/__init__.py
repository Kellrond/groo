import curses
from cli.view_builder import ViewBuilder

from db.mailserver import Mailserver
from cli.views.email.widgets import Home, Domains, Aliases, Users

class View(ViewBuilder):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.inputScreenCreate()
    # Menu 
    self.menu_list = [
      {'title': 'Home', 'widget': Home},
      {'title': 'Users', 'widget': Users},
      {'title': 'Aliases', 'widget': Aliases},
      {'title': 'Domains', 'widget': Domains}
    ]
    self.menu_cur = 'Home'    
    self.menuScreenCreate()
    # Screen
    self.screen = curses.newwin(self.ui.view_h, self.ui.view_w, self.ui.view_y, self.ui.view_x)
    self.screenListAdd(self.screen)
    self.mailserver = Mailserver()

  def loop(self):
    self.ui.stdscr.nodelay(False)
    while self.viewing == True:
      self.fill_page()
      self.draw()
      self.ui.getInput()
      self.tabMenuHandler()

  def fill_page(self):
    height, width = self.screen.getmaxyx()
    self.clearLineList()

    widget_class = self.getCurrentWidget()
    widget = widget_class(self.ui, *self.screen.getmaxyx())  

    for line in widget.draw():
      self.addLine(self.screen, line)



  # def draw(self):
  #   height, width = self.screen.getmaxyx()

  #   # Draw lines
  #   widget_class = self.getCurrentWidget()
  #   widget = widget_class(self.ui, *self.screen.getmaxyx())
  #   self.line_list = widget.draw()

  #   self.ui.view_line_count = len(self.line_list)
  #   self.screen.erase()
  #   i = 0
  #   while i < height - 1 and i < self.ui.view_line_count:
  #     self.screen.addstr(i, 0, self.line_list[self.ui.scroll_y + i][:width-2])
  #     i += 1

  #   self.screen.noutrefresh()



  def drawMenu(self):
    height, width = self.menu.getmaxyx()


    self.menu.noutrefresh()
