"""Game mode classes"""
import json
import random
import time


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
        [m.render(self.game_obj.scr_obj) for m in self.bg_matrix]

    def _render_about_form(self):
        """Render about form"""
        # Render about form background
        x, y = self.about_form['x'], self.about_form['y']
        for i in range(self.about_form['h'] + 3):
            self.game_obj.scr_obj.addstr(y - 1 + i, x - 1, ' ' * (self.about_form['w'] + 2))

        # Render about form border
        self.game_obj.scr_obj.addstr(
            y, x,
            self.border['jtl'] +
            self.border['h'] * (self.about_form['w'] - 2) +
            self.border['jtr']
        )
        self.game_obj.scr_obj.addstr(
            y + 4, x,
            self.border['jhl'] +
            self.border['h'] * (self.about_form['w'] - 2) +
            self.border['jhr']
        )
        self.game_obj.scr_obj.addstr(
            y + self.about_form['h'], x,
            self.border['jbl'] +
            self.border['h'] * (self.about_form['w'] - 2) +
            self.border['jbr']
        )
        for i in [j for j in range(self.about_form['h']) if j not in (0, 4)]:
            self.game_obj.scr_obj.addstr(y + i, x, self.border['v'])
            self.game_obj.scr_obj.addstr(y + i, x + self.about_form['w'] - 1, self.border['v'])

        # Render about form text
        s = '!!! WELCOME TO SNAKE GAME !!!'
        self.game_obj.scr_obj.addstr(y + 2, x + (self.about_form['w'] - len(s)) / 2, s)
        y += 8
        x += 2
        for s in self.howto:
            y += 2
            self.game_obj.scr_obj.addstr(y, x, s.encode('utf-8'))

    def render(self):
        """Render about form and background"""
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

        def render(self, scr):
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
                scr.addstr(self.start_point[1] + pos, self.start_point[0], val)


class GameModePlay(GameMode):
    """Game mode: PLAY"""

    def __init__(self, game_obj):
        """Constructor"""
        super(GameModePlay, self).__init__(game_obj)
        self.stats_form = {
            'w': 60
        }
        self.field = {
            'x': (1, self.game_obj.scr_x[1] - self.stats_form['w']),
            'y': (1, self.game_obj.scr_y[1])
        }
        self.points = 0
        self.speed = 1
        self.howto = tuple(val for i, val in enumerate(self.howto) if i != 1)

    def _render_field_border(self):
        """Render game field border"""
        self.game_obj.scr_obj.addstr(self.field['y'][0], self.field['x'][0], self.border['jtl'])
        self.game_obj.scr_obj.addstr(self.field['y'][1], self.field['x'][0], self.border['jbl'])
        self.game_obj.scr_obj.addstr(self.field['y'][0], self.field['x'][1], self.border['jtr'])
        self.game_obj.scr_obj.addstr(self.field['y'][1], self.field['x'][1], self.border['jbr'])
        self.game_obj.scr_obj.addstr(self.field['y'][0], self.field['x'][0] + 1, 'F')
        for i in range(self.field['x'][0] + 1, self.field['x'][1]):
            self.game_obj.scr_obj.addstr(self.field['y'][0], i, self.border['h'])
            self.game_obj.scr_obj.addstr(self.field['y'][1], i, self.border['h'])
        for i in range(self.field['y'][0] + 1, self.field['y'][1]):
            self.game_obj.scr_obj.addstr(i, self.field['x'][0], self.border['v'])
            self.game_obj.scr_obj.addstr(i, self.field['x'][1], self.border['v'])

    def _render_stats_form(self):
        """Render stats form"""
        x, y = self.field['x'][1] + 3, self.field['y'][0]
        self.game_obj.scr_obj.addstr(y + 1, x, 'YOUR POINTS = {0}'.format(self.points))
        self.game_obj.scr_obj.addstr(y + 3, x, 'YOUR SPEED = {0}'.format(self.speed))

        y = self.field['y'][1] - len(self.howto)
        for s in self.howto:
            self.game_obj.scr_obj.addstr(y, x, s.encode('utf-8'))
            y += 1

    def render(self):
        """Render play mode"""
        self._render_field_border()
        self._render_stats_form()
