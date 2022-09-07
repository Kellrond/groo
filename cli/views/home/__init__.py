import curses
from cli.view_builder import ViewBuilder

todo = [
  'create email view',
  'create backup view',
  ]

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

    self.addLine(self.screen, "Server administration app" )
    self.addLine(self.screen)
    self.addLine(self.screen, "  == TODO ==")

    for item in todo:
      self.addLine(self.screen, f' - { item }')

  