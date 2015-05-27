__author__ = 'Andy'

from setuptools import setup
import sys

setup(
    name='whirlybird',
    version='0.1',
    packages=['whirlybird'],
    url='',
    license='MIT',
    author='Andy Levisay',
    author_email='levisaya@gmail.com',
    description='',
    install_requires=['python3-protobuf==2.5.0',
                      'smbus-cffi',
                      'aioprocessing',
                      'RPi.GPIO>=0.5.11']
)