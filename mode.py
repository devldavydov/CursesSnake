"""Game mode classes"""
import collections
import curses
import random
import time

import stats


class GameMode(object):
    """Game mode base class"""

    def __init__(self, game_obj):
        """Constructor"""
        self.game_obj = game_obj
        self.border = {
            'h': u'\u2550'.encode('utf-8'),         # Horizontal
            'v': u'\u2551'.encode('utf-8'),         # Vertical
            'jtl': u'\u2554'.encode('utf-8'),       # Junction TopLeft
            'jtr': u'\u2557'.encode('utf-8'),       # Junction TopRight
            'jbl': u'\u255a'.encode('utf-8'),       # Junction BottomLeft
            'jbr': u'\u255d'.encode('utf-8'),       # Junction BottomRight
            'jhl': u'\u2560'.encode('utf-8'),       # Junction HorizontalLeft
            'jhr': u'\u2563'.encode('utf-8')        # Junction HorizontalRight
        }
        self.howto = (
            u'USE \u2190 \u2191 \u2192 \u2193 TO CONTROL SNAKE',
            u"PRESS 's' TO START GAME",
            u"PRESS 'i' TO INTRO SCREEN",
            u"PRESS 'p' TO PAUSE",
            u"PRESS 't' TO CHANGE TIMESTAMP FORMAT",
            u"PRESS 'q' TO EXIT"
        )

    def render(self):
        """Mode next step"""
        raise NotImplemented()


class GameModeIntro(GameMode):
    """Game mode: INTRO"""

    def __init__(self, game_obj):
        """Constructor"""
        super(GameModeIntro, self).__init__(game_obj)
        self.howto = tuple(val for i, val in enumerate(self.howto) if not i in (2, 3))
        self.about_form = {
            'w': 65,
            'h': 30
        }
        self.about_form['x'] = (self.game_obj.scr_x[1] - self.game_obj.scr_x[0] - self.about_form['w']) / 2
        self.about_form['y'] = (self.game_obj.scr_y[1] - self.game_obj.scr_y[0] - self.about_form['h']) / 2

        # Background matrix
        self.bg_matrix = [
            GameModeIntro.MatrixItem(
                (i, self.game_obj.scr_y[0] + 1),
                self.game_obj.scr_y[1] - self.game_obj.scr_y[0] - 1
            )
            for i in range(self.game_obj.scr_x[0] + 1, self.game_obj.scr_x[1] - 1, 5)
        ]

    def _render_bg(self):
        """Render background"""
        with self.game_obj.attrmng(curses.color_pair(1)):
            [m.render(self.game_obj) for m in self.bg_matrix]

    def _render_about_form(self):
        """Render about form"""
        # Render about form background
        with self.game_obj.attrmng(curses.color_pair(1)):
            x, y = self.about_form['x'], self.about_form['y']
            for i in range(self.about_form['h'] + 3):
                self.game_obj.addstr(y - 1 + i, x - 1, ' ' * (self.about_form['w'] + 2))

            # Render about form border
            self.game_obj.addstr(
                y, x,
                self.border['jtl'] +
                self.border['h'] * (self.about_form['w'] - 2) +
                self.border['jtr']
            )
            self.game_obj.addstr(
                y + 4, x,
                self.border['jhl'] +
                self.border['h'] * (self.about_form['w'] - 2) +
                self.border['jhr']
            )
            self.game_obj.addstr(
                y + self.about_form['h'], x,
                self.border['jbl'] +
                self.border['h'] * (self.about_form['w'] - 2) +
                self.border['jbr']
            )
            for i in [j for j in range(self.about_form['h']) if j not in (0, 4)]:
                self.game_obj.addstr(y + i, x, self.border['v'])
                self.game_obj.addstr(y + i, x + self.about_form['w'] - 1, self.border['v'])

        # Render about form text
        with self.game_obj.attrmng(curses.color_pair(2)):
            s = '!!! WELCOME TO SNAKE GAME !!!'
            self.game_obj.addstr(y + 2, x + (self.about_form['w'] - len(s)) / 2, s)
            y += 8
            x += 2

            # Enter username or print howto
            if not self.game_obj.username:
                prompt = 'ENTER YOUR NAME: '
                self.game_obj.scr_obj.nodelay(0)
                curses.echo()
                self.game_obj.addstr(y + 2, x, prompt)
                while not self.game_obj.username:
                    self.game_obj.username = self.game_obj.scr_obj.getstr(y + 2, x + len(prompt))[:10].upper()
                self.game_obj.scr_obj.nodelay(1)
                curses.noecho()
            else:
                for s in self.howto:
                    y += 2
                    self.game_obj.addstr(y, x, s.encode('utf-8'))

    def render(self):
        """Render about form and background"""
        if self.game_obj.username:
            self._render_bg()
        self._render_about_form()

    class MatrixItem(object):
        """Background matrix item"""

        def __init__(self, start_point, data_len):
            """Constructor"""
            self.letters = 'SNAKE GAME '
            self.start_point = start_point      # x, y
            self.data_list = [''] * data_len
            self.pos = 0
            self.t = 0
            self._new_cur_iter()

        def _new_cur_iter(self):
            """Create new symbol iterator"""
            self.cur_iter = iter(' ' * random.randrange(1, 5)) if random.random() > 0.5 else iter(self.letters)
            self.timeout = random.choice(range(5, 10, 1)) * 0.01

        def render(self, game_obj):
            """Render matrix item"""
            if time.time() - self.t > self.timeout:
                try:
                    s = next(self.cur_iter)
                except StopIteration:
                    self._new_cur_iter()
                    s = next(self.cur_iter)

                self.data_list[self.pos] = s
                self.pos = self.pos + 1 if self.pos < len(self.data_list) - 1 else 0
                self.t = time.time()

            for pos, val in enumerate(self.data_list):
                game_obj.addstr(self.start_point[1] + pos, self.start_point[0], val)


class GameModePlay(GameMode):
    """Game mode: PLAY"""

    def __init__(self, game_obj):
        """Constructor"""
        super(GameModePlay, self).__init__(game_obj)
        # Common
        self.howto = tuple(val for i, val in enumerate(self.howto) if i != 1)
        self.stats_form = {
            'w': 60
        }
        self.field = {
            'x': (1, self.game_obj.scr_x[1] - self.stats_form['w']),
            'y': (1, self.game_obj.scr_y[1])
        }
        # Pause
        self.pause = {
            'flag': False,
            'text': '*** PAUSE ***'
        }
        # Game over
        self.gameover = {
            'flag': False,
            'text': '*** GAME OVER ***'
        }
        # Snake
        self.points = 0
        self.speed = 1.0
        self.direction_map = {
            curses.KEY_UP: (0, -1, 0),          # x, y, direction_group_id
            curses.KEY_DOWN: (0, 1, 0),
            curses.KEY_LEFT: (-1, 0, 1),
            curses.KEY_RIGHT: (1, 0, 1)
        }
        self.snake = {
            'items': collections.deque([[self.field['x'][1] / 2, self.field['y'][1] / 2]]),        # List of x, y
            'direction': self.direction_map[curses.KEY_UP],                     # Incr. of x, y
            'symbol': '#',
            'time': 0
        }
        for i in range(1, 5):
            self.snake['items'].append(
                [self.snake['items'][0][0], self.snake['items'][0][1] + i]
            )
        # Prey
        self.prey = {
            'point': self._get_new_prey(),
            'symbol': u'\u25c9'.encode('utf-8'),
            'time': 0,
            'timeout': 0.3,
            'show_flag': True
        }
        # Users stats
        self.users_stats = stats.load_stats()

    def _render_field_border(self):
        """Render game field border"""
        with self.game_obj.attrmng(curses.color_pair(1)):
            self.game_obj.addstr(self.field['y'][0], self.field['x'][0], self.border['jtl'])
            self.game_obj.addstr(self.field['y'][1], self.field['x'][0], self.border['jbl'])
            self.game_obj.addstr(self.field['y'][0], self.field['x'][1], self.border['jtr'])
            self.game_obj.addstr(self.field['y'][1], self.field['x'][1], self.border['jbr'])
            for i in range(self.field['x'][0] + 1, self.field['x'][1]):
                self.game_obj.addstr(self.field['y'][0], i, self.border['h'])
                self.game_obj.addstr(self.field['y'][1], i, self.border['h'])
            for i in range(self.field['y'][0] + 1, self.field['y'][1]):
                self.game_obj.addstr(i, self.field['x'][0], self.border['v'])
                self.game_obj.addstr(i, self.field['x'][1], self.border['v'])

    def _render_stats_form(self):
        """Render stats form"""
        with self.game_obj.attrmng(curses.color_pair(2)):
            x, y = self.field['x'][1] + 3, self.field['y'][0]
            self.game_obj.addstr(y + 1, x, 'YOUR POINTS = {0}'.format(self.points))
            self.game_obj.addstr(y + 3, x, 'YOUR SPEED = {0}'.format(self.speed))
            self.game_obj.addstr(y + 5, x, 'SNAKE LENGTH = {0}'.format(len(self.snake['items'])))

            # Users stats
            if self.users_stats:
                y += 10
                self.game_obj.addstr(y, x, 'TOP 5 USERS:')
                self.game_obj.addstr(y + 1, x, '************')

                y += 1
                for i, u in enumerate(self.users_stats):
                    self.game_obj.addstr(y + i + 1, x, '{0} - {1}'.format(u[0], u[1]))

            # How to
            y = self.field['y'][1] - len(self.howto)
            for s in self.howto:
                self.game_obj.addstr(y, x, s.encode('utf-8'))
                y += 1

    def _check_field_border(self, x, y):
        """Check if point on field border"""
        return x <= self.field['x'][0] or x >= self.field['x'][1] or y <= self.field['y'][0] or y >= self.field['y'][1]

    def _render_snake(self):
        """Render snake"""
        with self.game_obj.attrmng(curses.color_pair(1)):
            for i, item in enumerate(self.snake['items']):
                self.game_obj.addstr(item[1], item[0], self.snake['symbol'])

        if (
            not (self.pause['flag'] or self.gameover['flag']) and
            (time.time() - self.snake['time'] > 1 / (self.speed * 10))
        ):
            # Check key
            key = self.game_obj.check_key(lambda k: k in self.direction_map)
            if key:
                # Check not one group directions
                if not self.snake['direction'][2] == self.direction_map[key][2]:
                    self.snake['direction'] = self.direction_map[key]

            # Change items coordinates
            # Tail items
            for i in range(len(self.snake['items']) - 1, 0, -1):
                for j in (0, 1):
                    self.snake['items'][i][j] = self.snake['items'][i - 1][j]
            # Head
            self.snake['items'][0][0] += self.snake['direction'][0]
            self.snake['items'][0][1] += self.snake['direction'][1]

            # Check game over
            if (
                self._check_field_border(*self.snake['items'][0]) or
                self.snake['items'].count(self.snake['items'][0]) > 1
            ):
                self.gameover['flag'] = True
                # Save user stats
                if self.points:
                    stats.save_stats(self.game_obj.username, self.points)

            self.snake['time'] = time.time()

    def _render_prey(self):
        """Render prey"""
        if time.time() - self.prey['time'] > self.prey['timeout']:
            self.prey['show_flag'] = not self.prey['show_flag']
            self.prey['time'] = time.time()

        with self.game_obj.attrmng(curses.color_pair(4)):
            self.game_obj.addstr(
                self.prey['point'][1],
                self.prey['point'][0],
                self.prey['symbol'] if self.prey['show_flag'] else ''
            )

    def _check_prey(self):
        """Check prey eaten"""
        if self.prey['point'] == self.snake['items'][0]:
            self.prey['point'] = self._get_new_prey()
            self.points += 1
            if self.points % 5 == 0:
                self.speed += 0.1

            # Append to snake
            self.snake['items'].appendleft([
                self.snake['items'][0][0] + self.snake['direction'][0],
                self.snake['items'][0][1] + self.snake['direction'][1]
            ])

    def _render_pause_gameover(self):
        """Render pause or gameover"""

        def _render_center_str(s):
            """Helper function to render string at game field center"""
            self.game_obj.addstr(
                (self.field['y'][1] + self.field['y'][0]) / 2,
                self.field['x'][0] + (self.field['x'][1] - self.field['x'][0] + 1 - len(s)) / 2,
                s
            )

        if self.gameover['flag']:
            _render_center_str(self.gameover['text'])
        elif self.pause['flag']:
            _render_center_str(self.pause['text'])

    def _check_pause(self):
        """Check pause"""
        if self.game_obj.check_key(lambda k: k == ord('p')):
            self.pause['flag'] = not self.pause['flag']

    def _get_new_prey(self):
        return [
            random.randrange(self.field['x'][0] + 1, self.field['x'][1] - 1),
            random.randrange(self.field['y'][0] + 1, self.field['y'][1] - 1)
        ]

    def render(self):
        """Render play mode"""
        self._render_field_border()
        self._render_stats_form()
        self._render_snake()
        self._render_prey()
        self._render_pause_gameover()
        self._check_prey()
        self._check_pause()
