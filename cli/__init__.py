import curses, os, psutil, socket, sys
from select import EPOLLEXCLUSIVE 
from datetime import datetime as dt

from modules import sys_info
from cli.views import backup, database, debug_curses, email, home, server 

bytes_per_gb = 1024 ** 3

class Cli():
  def __init__(self) -> None:
    # Instantiate the system class for access to system info
    self.system = sys_info.System()
    # Init the screen
    self.stdscr = curses.initscr()
    self.colors = Colors() 

    # Configure curses to respond to keystrokes
    curses.noecho()
    curses.cbreak()
    self.stdscr.keypad(True)  

    # Cursor and input
    self.ui = UI(stdscr=self.stdscr, system = self.system)   
    
    self.mainLoop()

  def mainLoop(self):
    self.ui.initWindows()
    exit = False
    while exit == False:
      self.height, self.width = self.stdscr.getmaxyx()
      self.ui.draw()

      view = self.ui.nav_list[self.ui.menu_opt].get('view')
      self.ui.view = view(**self.__dict__)
      self.ui.view.loop()

      curses.napms(50)
      if self.ui.last_key == 9 or self.ui.last_key == 353:
        pass
      
    self.quit()

  def quit(self):
    curses.nocbreak()
    self.stdscr.keypad(False)
    curses.echo()
    curses.endwin()


class Colors():
  def __init__(self) -> None:
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    self.TOP_BAR = curses.color_pair(1)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    self.NAV_BAR = curses.color_pair(2)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    self.NAV_SELECT = curses.color_pair(3)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    self.INPUT_BAR = curses.color_pair(4)


class UI():
  ''' Represents the cursor position and scroll position to be passed in and out of along with
    user input'''

  def __init__(self, stdscr, system) -> None:
    # System and curses
    self.stdscr = stdscr
    self.system = system 
    self.colors = Colors()
    # Input stuff
    self.inputBar = None
    self.input_prompt = "Input:"  
    self.input_str = ''
    self.last_key = 0
    self.menu_opt = 0
    self.exit_code = ''
    # Dimensions
    self.height = 0
    self.width  = 0
    self.cursor_y = 0 
    self.cursor_x = 0
    self.scroll_y = 0
    self.scroll_x = 0
    self.view_h = 0
    self.view_w = 0
    self.view_x = 0
    self.view_y = 0
    self.top_bar_height = 1
    self.side_bar_width = 14
    self.pad_x = self.side_bar_width
    self.cursor_x_min = self.pad_x + len(self.input_prompt)
    # View info
    self.view = None
    self.view_line_count = 0
    # DEBUG
    self.resize_count = 0

    self.nav_list = [
      {'title': 'Home', 'view': home.View},
      {'title': 'Server', 'view': server.View},
      {'title': 'Email', 'view': email.View},
      {'title': 'Database', 'view': database.View},
      {'title': 'Backup', 'view': backup.View},
      {'title': 'Curses debug', 'view': debug_curses.View}
    ]

  def initWindows(self):
    self.height, self.width = self.stdscr.getmaxyx()    

    self.topBar   = curses.newwin(self.top_bar_height, self.width, 0,0)
    self.navBar   = curses.newwin(self.height - self.top_bar_height, self.side_bar_width, self.top_bar_height,0)
    
    self.view_h = self.height - self.top_bar_height
    self.view_w = self.width - self.side_bar_width + 1
    self.view_y = self.top_bar_height
    self.view_x = self.side_bar_width - 1

    # Place cursor at the bottom
    self.stdscr.move(self.height - 1, self.width - 1)

  def resizeWindows(self):
    self.height, self.width = self.stdscr.getmaxyx()

    self.topBar.resize(self.top_bar_height, self.width)
    self.topBar.refresh()    
    self.navBar.resize(self.height - self.top_bar_height, self.side_bar_width)
    self.navBar.refresh()

    if self.inputBar != None: 
      self.inputBar.resize(1, self.width - self.side_bar_width)

    self.view_h = self.height - self.top_bar_height
    self.view_w = self.width - self.side_bar_width
    self.view_y = self.top_bar_height
    self.view_x = self.side_bar_width - 1
    self.resize_count += 1
    self.input_str = f'RESIZE - { self.resize_count }'

    self.view.resize()

    self.stdscr.refresh()

  def draw(self):
    self.drawTopBar()
    self.drawSideBar()

  def drawTopBar(self):
    height, width = self.topBar.getmaxyx()
    self.topBar.erase()
    left_txt  = 'System administration'
    right_txt = self.system.host
    spacing = " " * ( width - len(left_txt + right_txt) - 1 )
    self.topBar.addstr(f"{ left_txt }{ spacing }{ right_txt }", self.colors.TOP_BAR)
    self.topBar.noutrefresh()

  def drawSideBar(self):
    height, width = self.navBar.getmaxyx()
    self.navBar.erase()

    for i in range(0,height):
      menu_name = ''
      color = self.colors.NAV_BAR
      if i < len(self.nav_list):
        menu_name = self.nav_list[i].get('title')
        if i == self.menu_opt:
          color = self.colors.NAV_SELECT
      self.navBar.addstr(i,0,f"{menu_name}{' ' * (width - len(menu_name) - 1)}", color)
      self.navBar.noutrefresh()

  def setCursorYorX(self, y=None, x=None):
    if y:
      self.cursor_y = y 
    if x: 
      self.cursor_x = x

  def resetInput(self):
    self.input_str = ''
    self.cursor_x = self.cursor_x_min

  def incCursorX(self, n):
    if self.cursor_x < self.width - 1:
      self.cursor_x += n

  def incCursorY(self, n):
    self.cursor_y += n

  def incScrollX(self, n):
    self.scroll_x += n
    
  def incScrollY(self, n):
    if n < 0 and self.scroll_y > 0:
      self.scroll_y += n
    elif self.view_line_count > self.view_h and self.view_h + self.scroll_y <= self.view_line_count: 
      self.scroll_y += n

  def setInputPrompt(self, text):
    self.input_prompt = text
  
  def resetViewVariables(self):
    self.input_str = ''
    self.scroll_x = 0
    self.scroll_y = 0

  def getInput(self):
    self.last_key = self.stdscr.getch()

    # TAB navigation handler 
    if self.last_key == 9: # Tab
      self.resetViewVariables()
      if self.menu_opt < len(self.nav_list) - 1:
        self.menu_opt += 1
      else: 
        self.menu_opt = 0
    elif self.last_key == 353: # Shift tab
      self.resetViewVariables()
      if self.menu_opt > 0:
        self.menu_opt -= 1
      else:
        self.menu_opt = len(self.nav_list) - 1
    # LEFT and RIGHT 
    elif self.last_key == 260 and self.cursor_x > self.pad_x + len(self.input_prompt) - 1: # Left
      self.incCursorX(-1)
    elif self.last_key == 261 and self.cursor_x < self.pad_x + len(self.input_prompt) + len(self.input_str) - 1: # Right
      self.incCursorX(1) 
    # UP and DOWN
    elif self.last_key == 259 and self.scroll_y >= 1: # Up
      self.incScrollY(-1)
    elif self.last_key == 258: # Down
      self.incScrollY(1)
    
    # BACKSPACE
    elif self.last_key == 127 or self.last_key == 263:
      if self.cursor_x > self.cursor_x_min:
        self.input_str = self.input_str[:-1]
        self.incCursorX(-1)
    # DELETE
    elif self.last_key == 330:
      if self.cursor_x < self.cursor_x_min + len(self.input_str):
        self.input_str = self.input_str[:self.cursor_x - self.cursor_x_min] + self.input_str[self.cursor_x - self.cursor_x_min + 1:]
    # Window resize 
    elif self.last_key == curses.KEY_RESIZE:
      self.last_key = 0
      self.resizeWindows()
    
    # Must be a character, write to screen
    elif self.last_key >= 32 and self.last_key <= 126:
      pos = self.cursor_x - self.pad_x - len(self.input_prompt) + 1
      self.input_str = self.input_str[:pos] + chr(self.last_key) + self.input_str[pos:]
      self.incCursorX(1)
