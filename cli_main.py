from curses import wrapper
import cli

def main(stdscr):
    app = cli.Cli()

wrapper(main)


