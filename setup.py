from setuptools import setup, find_packages
import sys

if sys.version_info.major != 3:
    print('This Python is only compatible with Python 3, but you are running '
          'Python {}. The installation will likely fail.'.format(sys.version_info.major))

# Loading the "long description" from the projects README file.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='gym-flappybird',
      packages=[package for package in find_packages()],
      install_requires=[
          'gym',
          'syncer',
          'pyppeteer',
          'asciimatics'
      ],
      long_description=long_description,
      long_description_content_type="text/markdown",
      description='Flappy Bird Gym',
      author='Fabito',
      url='https://github.com/fabito/gym-flappybird',
      author_email='fabio.uechi@gmail.com',
      version='0.1',
      # PyPI package information:
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Intended Audience :: Developers",
          "Intended Audience :: Education",
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Mathematics",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Topic :: Software Development",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      license="MIT License",
      python_requires=">=3.8",
      keywords=' '.join([
          "Flappy-Bird"
          "Game",
          "Gym",
          "OpenAI-Gym",
          "Reinforcement-Learning",
          "Reinforcement-Learning-Environment",
      ]),
      )
