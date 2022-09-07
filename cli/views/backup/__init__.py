import curses
from cli.view_builder import ViewBuilder


class View(ViewBuilder):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.screen = curses.newwin(self.ui.view_h, self.ui.view_w, self.ui.view_y, self.ui.view_x)
    self.screenListAdd(self.screen)
    
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

    self.addLine(self.screen, "Backup homepage" )
    self.addLine(self.screen)
    self.addLine(self.screen, "  == TODO ==")
    self.addLine(self.screen, " - Backup database")
    self.addLine(self.screen, " - Backup config files")
    self.addLine(self.screen, " - Backup package list")
    self.addLine(self.screen, " - Backup email")
