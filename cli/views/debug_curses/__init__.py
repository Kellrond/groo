import curses
from cli.view_builder import ViewBuilder

class View(ViewBuilder):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.inputScreenCreate()
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
    
    self.addLine(self.screen, "TL", y=0, x=0)
    self.addLine(self.screen, "R", y=0, x=width - 2)

    self.addLine(self.screen, "BL", y=height - 1, x=0)
    self.addLine(self.screen, "R", y=height - 1, x=width - 2)

    self.addLine(self.screen, f"Screen size Lines: { height } Cols: { width }")
    self.addLine(self.screen, f'Last key: {self.ui.last_key}')
    self.addLine(self.screen, f'Menu num: {self.ui.menu_opt}')
    self.addLine(self.screen, f'Curs y x: {self.ui.cursor_y} {self.ui.cursor_x}')
    self.addLine(self.screen, f'Scroll y x: { self.ui.scroll_y } { self.ui.scroll_x }')
    self.addLine(self.screen, f"Resize count: { self.ui.resize_count }")
    self.addLine(self.screen, f"View width: { self.ui.view_w }")
    self.addLine(self.screen, f"Draw func width: { width }")
    self.addLine(self.screen, )
    self.addLine(self.screen, f'TOP_BAR', attr=self.ui.colors.TOP_BAR)
    self.addLine(self.screen, f'NAV_BAR', attr=self.ui.colors.NAV_BAR)
    self.addLine(self.screen, f'NAV_SELECT', attr=self.ui.colors.NAV_SELECT)
    self.addLine(self.screen, f'INPUT_BAR', attr=self.ui.colors.INPUT_BAR)

    