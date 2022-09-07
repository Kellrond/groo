import curses
from cli.view_builder import ViewBuilder

from db.mailserver import Mailserver

class View(ViewBuilder):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.screen = curses.newwin(self.ui.view_h, self.ui.view_w, self.ui.view_y, self.ui.view_x)
    self.screenListAdd(self.screen)
    self.databases = [Mailserver]

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

    self.addLine(self.screen, "Database administration" )
    self.addLine(self.screen)

    for db_class in self.databases:
      db = db_class()
      connect_str = 'Connect okay' if db.test_connection() else 'Connect failed'
      self.addLine(self.screen, f"{ db.__name__ } - { connect_str }")