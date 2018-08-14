from setuptools import setup, find_packages
import sys

if sys.version_info.major != 3:
    print('This Python is only compatible with Python 3, but you are running '
          'Python {}. The installation will likely fail.'.format(sys.version_info.major))

setup(name='gym-flappybird',
      packages=[package for package in find_packages()],
      install_requires=[
          'gym',
          'syncer',
          'pyppeteer',
          'asciimatics'
      ],
      description='Flappy Bird Gym',
      author='Fabito',
      url='https://github.com/fabito/gym-flappybird',
      author_email='fabio.uechi@gmail.com',
      version='0.1')