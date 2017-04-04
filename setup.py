import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pulsecon",
    version = "0.0.1",
    author = "Leon Bentrup",
    author_email = "andrewjcarter@gmail.com",
    description = ("Control pulseaudio from redis pubsub"),
    license = "BSD-2-Clause",
    keywords = "pulse redis daemon",
    url = "http://github.com/xanecs/pulsecon",
    packages=['pulsecon'],
    long_description=read('README.md'),
    install_requires=['pulsectl', 'redis', 'toml'],
     entry_points = {
        'console_scripts': ['pulsecon=pulsecon.pulsecon:init'],
    }
)
