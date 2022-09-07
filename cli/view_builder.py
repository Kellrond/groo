import curses

class ViewBuilder:
  def __init__(self, **kwargs) -> None:
    # System items
    from cli import UI
    self.ui = kwargs.get('ui', UI)
    # Flags
    self.viewing = True
    # Dimensions
    self.input_screen_height = 1
    # Screens 
    self.input_screen = None
    self.menu_screen = None
    self.menu_cur = ''
    self.menu_list = []
    self.screen_list = []
    self.line_list = []
    self.screen_lines = {}
    self.cur_line = 0

  # Screen handling
  def screenListAdd(self, screen):
    self.screen_list.append(screen)

  def screenListPurgeUnused(self):
    self.screen_list = [ x for x in self.screen_list if x != None ]

  def resize(self):
    for screen in self.screen_list:
      screen.resize(*screen.getmaxyx())
      screen.refresh()

  def erase(self):
    for screen in self.screen_list:
      screen.erase()

  def refresh(self):
    for screen in self.screen_list:
      screen.noutrefresh()

  # Draw screen functions
  def draw(self):
    self.erase()
    # Handle optional screens 
    if self.input_screen != None:
      self.inputScreenDraw()
    if self.menu_screen != None:
      self.menuScreenDraw()
    self.splitLineListByScreen()
    self.setViewTotalLines()

    for screen, lines in self.screen_lines.items():
      height, width = screen.getmaxyx()

      for line in lines:
      # Handle the input and menu screens differently so the scroll doesn't impact them
        if screen == self.input_screen or screen == self.menu_screen:
          txt = line.get('txt','')
          txt = txt + " " * (width - line.get('x') - len(txt) - 1)
          if len(txt) <= width - 1:
            start_pos = 0
            end_pos = len(txt)
          else:
            start_pos = 0
            end_pos = width - line.get('x') - 2
          screen.addstr(line.get('y'), line.get('x'), txt[start_pos:end_pos], line.get('attr'))
        else:
          if line.get('y') < height + self.ui.scroll_y and line.get('y') >= self.ui.scroll_y:
            txt = line.get('txt','')
            txt = txt # + " " * (width - line.get('x') - len(txt) - 1)
            if len(txt) <= width - 1:
              start_pos = 0
              end_pos = len(txt)
            else:
              start_pos = 0
              end_pos = width - line.get('x') - 2

            if line.get('attr') != None:
              screen.addstr(line.get('y') - self.ui.scroll_y, line.get('x'), txt[start_pos:end_pos], line.get('attr'))
            else:
              screen.addstr(line.get('y') - self.ui.scroll_y,line.get('x'), txt[start_pos:end_pos])
            

    self.fillEmptyLines()
    self.refresh()
    curses.doupdate()



  def addLine(self, screen, txt='', y=None, x=None, attr=None):
    if y == None:
      y = self.nextAvailableLineByScreen(screen)

    line = {
      'screen': screen,
      'txt': txt,
      'y': y,
      'x': x if x != None else 0,
      'attr': attr
    }
    self.line_list.append(line)

  def splitLineListByScreen(self):
    self.screen_lines = {}
    for line in self.line_list:
      if self.screen_lines.get(line.get('screen'), None) == None:
        self.screen_lines[line.get('screen')] = []
      
      self.screen_lines[line.get('screen')].append(line)

  def setViewTotalLines(self):
    view_lines = [ line for scr, line in self.screen_lines.items() if scr != self.input_screen and scr != self.menu_screen ][0]

    max_y = max([ x.get('y') for x in view_lines ])
    line_count = len(view_lines)
    self.ui.view_line_count = max(line_count, max_y)

  def fillEmptyLines(self):
    # Fill empty lines
    for scr, lines in self.screen_lines.items():
      lines_y = [ x.get('y') for x in lines ]

      height, width = scr.getmaxyx()
      for i in range(height):
        if scr == self.input_screen or scr == self.menu_screen:
          if i not in lines_y:
            spacing = ' ' * (width - 1)
            scr.addstr(i, 0, spacing)
        else:
          if i + self.ui.scroll_y not in lines_y:
            spacing = ' ' * (width - 1)
            scr.addstr(i, 0, spacing)

  def clearLineList(self):
    self.line_list = []

  def nextAvailableLineByScreen(self, screen):
    screen_lines = [ x.get('y') for x in self.line_list if x.get('screen') == screen ]
    if len(screen_lines) == 0:
      return 0

    for i in range(1000):
      if i not in screen_lines:
        return i

  # Input handling
  def inputScreenCreate(self):
    self.input_screen = curses.newwin(self.input_screen_height, self.ui.view_w, self.ui.top_bar_height, self.ui.pad_x - 1)
    self.ui.view_h -= self.input_screen_height
    self.ui.view_y += self.input_screen_height
    self.ui.cursor_x = self.ui.side_bar_width + len(self.ui.input_prompt) - 1
    self.ui.cursor_x_min = self.ui.cursor_x
    self.screenListAdd(self.input_screen)

  def inputScreenDraw(self):
    if self.input_screen != None:
      height, width = self.input_screen.getmaxyx()
      spacing       = ' ' * (width - len(self.ui.input_prompt) - len(self.ui.input_str) - 3)

      self.addLine(self.input_screen, f'{ self.ui.input_prompt }{ self.ui.input_str }', y=0, x=0, attr=self.ui.colors.INPUT_BAR)
      self.ui.stdscr.move(self.ui.top_bar_height, self.ui.cursor_x)


  def inputScreenDestroy(self):
    if self.input_screen != None:
      self.ui.view_h += self.input_screen_height
      self.ui.view_y -= self.input_screen_height
      self.ui.cursor_x = self.ui.width - 1
      self.ui.cursor_y = self.ui.height - 1
      self.ui.input_str = ''
      self.input_screen = None
      self.screenListPurgeUnused()

  # Menu screen
  def menuScreenCreate(self):
    self.menu_w = max([ len(x.get('title')) for x in self.menu_list ]) + 2
    self.menu_screen = curses.newwin(self.ui.view_h, self.menu_w, self.ui.view_y, self.ui.view_x)
    self.ui.view_w -= self.menu_w
    self.ui.view_x += self.menu_w

    self.screenListAdd(self.menu_screen)

  def menuScreenDraw(self):
    if self.menu_screen != None:
      height, width = self.menu_screen.getmaxyx()

      menu_len = len(self.menu_list)

      for i in range(height):
        if i < menu_len:
          title = self.menu_list[i].get('title')
          spacing = " " * (width - len(title) - 2)

          input_len = len(self.ui.input_str)
          if input_len > 0 and self.ui.input_str.lower().strip() == title[:input_len].lower():
            color = self.ui.colors.NAV_BAR
          else:
            color = self.ui.colors.NAV_SELECT 

          self.addLine(self.menu_screen, f'{ title }{ spacing }', attr=color)
        else:
          self.addLine(self.menu_screen, " " * (width - 1), attr=self.ui.colors.NAV_SELECT)

  def menuScreenDestroy(self):
    if self.menu_screen != None:
      self.ui.view_w += self.menu_w
      self.ui.view_x -= self.menu_w
      self.menu_screen = None
      self.screenListPurgeUnused()

  def stringMenuHandler(self):
      if self.ui.last_key == 10:
        input_len = len(self.ui.input_str)
        for menu in self.menu_list:
          title = menu.get('title')
          if input_len > 0 and self.ui.input_str.lower().strip() == title[:input_len].lower():
            self.menu_cur = title
            self.ui.resetInput()

  def tabMenuHandler(self):
    # TAB handles the menu navigation. It's used to escape programs
    if self.ui.last_key == 9 or self.ui.last_key == 353:
      self.ui.resetViewVariables()
      self.inputScreenDestroy()
      self.menuScreenDestroy()
      self.viewing = False
      self.ui.exit_code = 'menu'

  # Widget handling

  def getCurrentWidget(self):
    for menu in self.menu_list:
      if menu.get('title') == self.menu_cur:
        return menu.get('widget')