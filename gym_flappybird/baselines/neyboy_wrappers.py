from pathlib import Path

import cv2
import gym
from baselines import logger


class ObservationSaver(gym.ObservationWrapper):
    def __init__(self, env, stage_name):
        gym.ObservationWrapper.__init__(self, env)
        self.stage_name = stage_name
        self.counter = 0

    @staticmethod
    def _save(obs, stage_name, counter):
        log_dir = logger.get_dir()
        data_dir = Path(log_dir, 'observations')
        data_dir.mkdir(exist_ok=True)
        obs = cv2.cvtColor(obs, cv2.COLOR_BGR2RGB)
        cv2.imwrite(str(Path(data_dir, '{}_{}.jpg'.format(stage_name, counter))), obs)

    def observation(self, frame):
        self.counter += 1
        self._save(frame, self.stage_name, self.counter)
        # threading.Thread(target=self._save, args=(frame, self.stage_name, self.counter)).start()
        return frame


class ObservationSaver2(ObservationSaver):
    pass

