from gym.envs.registration import register

register(
    id='flappybird-v0',
    entry_point='gym_flappybird.envs:FlappyBirdEnv',
)
