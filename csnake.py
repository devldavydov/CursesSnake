import curses
import locale

from game import SnakeGame


def main(stdscr):
    """Entry point"""
    SnakeGame(stdscr).start()


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(main)
