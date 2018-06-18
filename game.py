"""Game main module"""

import contextlib
import curses
import datetime

import mode


class GameMetaObject(object):
    """Game meta object"""

    def __init__(self, scr_obj):
        """Constructor"""
        self.scr_obj = scr_obj      # Curses screen object
        self.scr_x = [1, None]      # Screen X [min, max]
        self.scr_y = [1, None]      # Screen Y [min, max]
        self.key = 0                # Key pressed

    def addstr(self, *args):
        """Wrapper function addstr"""
        self.scr_obj.addstr(*args)

    @contextlib.contextmanager
    def attrmng(self, *args):
        """Contextmanager for curses output attr"""
        [self.scr_obj.attron(opt) for opt in args]
        yield
        [self.scr_obj.attroff(opt) for opt in args]

    def check_key(self, f_check):
        """Check pressed key"""
        if f_check(self.key):
            k, self.key = self.key, 0
            return k
        else:
            return 0


class SnakeGame(object):
    """Main game class"""

    def __init__(self, stdscr):
        """Constructor"""
        # Base init
        curses.curs_set(0)
        self.game_obj = GameMetaObject(stdscr)
        stdscr.nodelay(1)
        stdscr.clear()
        stdscr.refresh()

        # Window size and coordinates
        screen_h, screen_w = stdscr.getmaxyx()
        if screen_h < 40 or screen_w < 140:
            raise SystemExit(
                'Current terminal size: [{0} x {1}]. Minimum required size: 140 x 40'.format(screen_w, screen_h)
            )
        self.game_obj.scr_y[1] = screen_h - 3    # Additional -1 for statusbar
        self.game_obj.scr_x[1] = screen_w - 2

        # Mode
        self.mode = mode.GameModeIntro(self.game_obj)

        # Color scheme
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

        # Other
        self.logo = 'SNAKE GAME [{0} x {1}]'.format(screen_w, screen_h)
        self.timeformats = [0, (
            '%d.%m.%Y %H:%M:%S',
            '%d.%m.%Y %H:%M:%S.%f',
            '%d.%m.%Y',
            '%H:%M:%S'
        )]

    def _get_cur_timeformat(self):
        return self.timeformats[1][self.timeformats[0]]

    def _next_timeformat(self):
        ind = self.timeformats[0] + 1
        self.timeformats[0] = 0 if (ind == len(self.timeformats[1])) else ind

    def _common_render(self):
        """Common render"""
        self.game_obj.scr_obj.erase()
        with self.game_obj.attrmng(curses.color_pair(1)):
            self.game_obj.scr_obj.border()

        # Render statusbar
        self._render_statusbar()

    def _render_statusbar(self):
        """Render status bar"""
        str_time = datetime.datetime.now().strftime(self._get_cur_timeformat())

        with self.game_obj.attrmng(curses.color_pair(1)):
            self.game_obj.addstr(
                self.game_obj.scr_y[1] + 1,
                self.game_obj.scr_x[0],
                '{0}{1}'.format(self.logo.ljust(self.game_obj.scr_x[1] - len(str_time) - 1, ' '), str_time)
            )

    def start(self):
        """Main game loop"""
        while True:
            # Check key
            if self.game_obj.check_key(lambda k: k == ord('q')):
                raise SystemExit()
            elif self.game_obj.check_key(lambda k: k == ord('t')):
                self._next_timeformat()
            elif self.game_obj.check_key(lambda k: k == ord('s')):
                if not isinstance(self.mode, mode.GameModePlay):
                    self.mode = mode.GameModePlay(self.game_obj)
            elif self.game_obj.check_key(lambda k: k == ord('i')):
                if not isinstance(self.mode, mode.GameModeIntro):
                    self.mode = mode.GameModeIntro(self.game_obj)
            elif self.game_obj.check_key(lambda k: k == curses.KEY_RESIZE):
                raise SystemExit('Terminal resize not supported')
            else:
                pass

            # Common rendering
            self._common_render()

            # Mode rendering
            self.mode.render()

            # Refresh and read input
            self.game_obj.scr_obj.refresh()
            ch = self.game_obj.scr_obj.getch()
            if ch != -1:
                self.game_obj.key = ch
