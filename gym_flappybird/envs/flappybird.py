import base64
import io
import datetime as dt

try:
    import numpy as np
except:
    import logging

    logging.warning('numpy not found, ndarray snapshots wonnt work')

import re
import uuid
from collections import namedtuple

from PIL import Image
from pyppeteer import launch
from syncer import sync

GameState = namedtuple('GameState',
                       ['game_id', 'id', 'score', 'status', 'hiscore', 'snapshot', 'timestamp', 'dimensions'])

DEFAULT_GAME_URL = 'https://fabito.github.io/flappybird/'

DEFAULT_CHROMIUM_LAUNCH_ARGS = ['--no-sandbox', '--window-size=80,315', '--disable-infobars']


START_SCREEN = 0
GAME_SCREEN = 1
GAME_OVER_SCREEN = 2


class FlappyBird(object):

    def __init__(self, headless=True, user_data_dir=None, game_url=DEFAULT_GAME_URL):
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.game_url = game_url
        self.browser = None
        self.page = None
        self.state = None
        self.game_id = str(uuid.uuid4())
        self.state_id = 0
        self._seed = 0

    async def initialize(self):
        if self.user_data_dir is not None:
            self.browser = await launch(headless=self.headless, userDataDir=self.user_data_dir, args=DEFAULT_CHROMIUM_LAUNCH_ARGS)
        else:
            self.browser = await launch(headless=self.headless, args=DEFAULT_CHROMIUM_LAUNCH_ARGS)

        pages = await self.browser.pages()
        if len(pages) > 0:
            self.page = pages[0]
        else:
            self.page = await self.browser.newPage()

        # self.page.setDefaultNavigationTimeout(self.navigation_timeout)
        await self.page.setViewport(dict(width=120, height=160))
        await self.load()

    @staticmethod
    async def create(headless=True, user_data_dir=None, game_url=DEFAULT_GAME_URL) -> 'FlappyBird':
        o = FlappyBird(headless, user_data_dir, game_url)
        await o.initialize()
        return o

    async def load(self):
        await self.page.goto(self.game_url, {'waitUntil': 'networkidle2'})
        await self.page.waitForFunction('''() => {
            return createjs.Ticker.getTicks() > 0;
        }''')
        return self

    async def stop(self):
        await self.browser.close()

    async def tap(self, delay=0):
        await self.page.click('#testCanvas', {'delay': delay})

    async def restart(self):
        await self.page.evaluate('''(seed) => {
                Math.seedrandom(seed);
                restart();
            }''', self._seed)
        await self.tap()

    async def is_over(self):
        is_over = await self.page.evaluate('''() => {
                return dead;
            }''')
        return is_over

    async def seed(self, v):
        print('setting seed to ' + v)
        self._seed = v

    async def is_paused(self):
        return await self.page.evaluate('''() => {
            return createjs.Ticker.getPaused();
        }''')

    async def pause(self):
        await self.page.evaluate('''() => {
            let paused = createjs.Ticker.getPaused();
            if (!paused)
                createjs.Ticker.setPaused(true);
        }''')
        return self

    async def resume(self):
        await self.page.evaluate('''() => {
            let paused = createjs.Ticker.getPaused();
            if (paused)
                createjs.Ticker.setPaused(false);
        }''')
        return self

    async def get_score(self):
        score = await self.page.evaluate('''() => {
            return counter.text;
        }''')
        return int(score) if score else 0

    async def get_state(self, include_snapshot='numpy', fmt='image/jpeg', quality=30):
        """

        :param include_snapshot: numpy, pil, ascii, bytes, None
        :param fmt:
        :param quality:
        :return:
        """
        self.state_id += 1
        state = await self.page.evaluate('''(includeSnapshot, format, quality) => {
            return new Promise((resolve, reject) => {
                const {x, y, width, height} = stage.getBounds();
                const dimensions = {x, y, width, height};
                const score = counter.text;
                const hiscore = counter.text;
                let status = 0;
                if (!started && !dead) {
                    status = 0;
                } else if (started && !dead) {
                    status = 1;
                } else {
                    status = 2;
                }
                let snapshot = null;
                if (includeSnapshot) {
                    snapshot = stage.toDataURL(format, quality);
                }
                resolve({score, hiscore, snapshot, status, dimensions});
            })
        }''', include_snapshot, fmt, quality)

        state['hiscore'] = int(state['hiscore'])
        state['score'] = int(state['score'])
        state['status'] = int(state['status'])
        state['id'] = self.state_id
        state['game_id'] = self.game_id
        state['timestamp'] = dt.datetime.today().timestamp()

        if include_snapshot is not None:
            base64_string = state['snapshot']
            base64_string = re.sub('^data:image/.+;base64,', '', base64_string)
            imgdata = base64.b64decode(base64_string)

            bytes_io = io.BytesIO(imgdata)

            if include_snapshot == 'numpy':
                image = Image.open(bytes_io)
                state['snapshot'] = np.array(image)
            elif include_snapshot == 'pil':
                image = Image.open(bytes_io)
                state['snapshot'] = image
            elif include_snapshot == 'bytes':
                state['snapshot'] = bytes_io
            else:
                raise ValueError('Supported snapshot formats are: numpy, pil, ascii, bytes')

        self.state = GameState(**state)

        return self.state


class SyncFlappyBird:

    def __init__(self, game: FlappyBird):
        self.game = game

    def __getattr__(self, attr):
        return sync(getattr(self.game, attr))

    @staticmethod
    def create(headless=True, user_data_dir=None, game_url=DEFAULT_GAME_URL) -> 'SyncFlappyBird':
        o = sync(FlappyBird.create)(headless, user_data_dir, game_url)
        return SyncFlappyBird(o)
