import curses
from cli.view_builder import ViewBuilder
from modules import sys_info


class View(ViewBuilder):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    self.screen = curses.newwin(self.ui.view_h, self.ui.view_w, self.ui.view_y, self.ui.view_x)
    self.screenListAdd(self.screen)
    self.system = kwargs.get('system', sys_info.System())

  def loop(self):
    self.ui.stdscr.nodelay(True)
    while self.viewing == True:
      self.fill_page()
      self.draw()
      self.ui.getInput()
      self.tabMenuHandler()

  def fill_page(self):
    height, width = self.screen.getmaxyx()
    self.clearLineList()
    # Prep everything
    self.system.refreshAll()
    self.setSystemStrings()

    lines = [
      f"Host: { self.system.host }",
      f"Time: { self.system.date_time}" ,
      " ",
      '  == CPU ==',
      f'CPU:  { self.cpuStr  }',
      f'Load: { self.loadStr  }',
      " ",
      '  == Memory ==',
      f'Mem:  { self.memStr  }',
      f'Swap: { self.swapStr  }',
      f'Buff: { self.bufStr  }',
      " ",
      '  == Disks ==',
      f'Total: { self.diskStr  }',
      " ",
      '  -- Partitions -- ',
    ]
    for disk in self.allDisks:
      lines.append(disk)

    for line in lines:
      self.addLine(self.screen, line)

  def setSystemStrings(self):
    # CPU
    self.cpuStr   = f'{ self.system.cpu.perc }% of { self.system.cpu.logic_cores } logic core(s) at { self.system.cpu.freq_current } MHz'
    self.loadStr  = f'{ self.system.cpu.load_1m} 1 min - { self.system.cpu.load_5m } 5 min - { self.system.cpu.load_15m } 15 min'
    # Memory
    self.memStr   = f'{ self.system.memory.perc }% of { self.system.memory.total } GB - { self.system.memory.available } GB available'
    self.bufStr   = f'{ self.system.memory.buffers } buffers - { self.system.memory.cached } GB cached'
    self.swapStr  = f'{ self.system.memory.swap_perc }% of { self.system.memory.swap_total } GB '
    # Disks
    self.diskStr  = f'{ self.system.disk.perc }% used of { self.system.disk.total } GB - { self.system.disk.free } GB free'
    self.allDisks = [f'{ d.get("part") }: { d.get("perc") }% used of { d.get("total") } GB' for d in self.system.disk.drives]
  
  

      