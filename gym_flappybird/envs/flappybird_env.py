import math
import os

import numpy as np

import gym
from gym import spaces, utils, logger
from gym.utils import seeding

from gym_flappybird.envs.flappybird import SyncFlappyBird, GAME_OVER_SCREEN, DEFAULT_GAME_URL

ACTION_NAMES = ["NOOP", "FLAP"]
ACTION_NONE = 0
ACTION_FLAP = 1


class FlappyBirdEnv(gym.Env, utils.EzPickle):

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, headless=None, death_reward=-1, stay_alive_reward=0.01, user_data_dir=None):
        utils.EzPickle.__init__(self, headless, death_reward)

        if headless is None:
            headless = os.environ.get('GYM_FB_ENV_NON_HEADLESS', None) is None

        self.headless = headless
        self.obs_for_terminal = os.environ.get('GYM_FB_OBS_AS_BYTES', None) is not None

        self.stay_alive_reward = float(os.environ.get('GYM_FB_STAY_ALIVE_REWARD', stay_alive_reward))
        self.death_reward = float(os.environ.get('GYM_FB_DEATH_REWARD', death_reward))

        self._state = None
        self._old_state = None
        self.viewer = None

        game_url = os.environ.get('GYM_FB_GAME_URL', DEFAULT_GAME_URL)

        self.game = SyncFlappyBird.create(headless=headless, user_data_dir=user_data_dir, game_url=game_url)
        self._update_state()

        self.observation_space = spaces.Box(low=0, high=255, shape=self.state.snapshot.shape, dtype=np.uint8)
        self.action_space = spaces.Discrete(len(ACTION_NAMES))
        self.reward_range = -1., 1.

    @property
    def state(self):
        return self._state

    def _update_state(self):
        self._old_state = self._state
        if self.obs_for_terminal:
            self._state = self.game.get_state(include_snapshot='bytes')
        else:
            self._state = self.game.get_state()
        return self._old_state, self._state

    def step(self, a):
        self.game.resume()
        if a == ACTION_FLAP:
            self.game.tap()
        self._update_state()
        self.game.pause()

        is_over = self.state.status == GAME_OVER_SCREEN
        reward = self.compute_reward(is_over)
        logger.debug('HiScore: {}, Score: {}, Action: {}, Reward: {}, GameOver: {}'.format(
            self.state.hiscore,
            self.state.score,
            ACTION_NAMES[a],
            reward,
            is_over))
        return self._get_obs(), reward, is_over, dict(score=self.state.score)

    def _score_diff(self):
        return self._state.score - self._old_state.score if self._old_state is not None else 0

    def compute_reward(self, is_over):
        if is_over:
            reward = self.death_reward
        else:
            diff = self._score_diff()
            if diff == 0.0:
                reward = self.stay_alive_reward
            else:
                reward = 1.0
        return reward

    def _get_obs(self):
        return self.state.snapshot

    def reset(self):
        self.game.restart()
        self._update_state()
        self.game.pause()
        return self._get_obs()

    def render(self, mode='human', close=False):
        img = self.state.snapshot
        if mode == 'rgb_array':
            return img
        elif mode == 'human':
            from gym.envs.classic_control import rendering
            if self.viewer is None:
                self.viewer = rendering.SimpleImageViewer()
            self.viewer.imshow(img)
            return self.viewer.isopen

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None
        self.game.stop()
        super(FlappyBirdEnv, self).close()

    def get_action_meanings(self):
        return ACTION_NAMES

    def seed(self, seed=None):
        self.np_random, seed1 = seeding.np_random(seed)
        self.game.seed(str(seed))

    def __del__(self):
        self.game.stop()

