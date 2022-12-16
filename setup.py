import sys, os
from setuptools import setup

dependencies = ['Pillow', 'python-dotenv', 'pvporcupine', 'pvcheetah', 'webdriver-manager', 'selenium','pvrecorder', "openai", "websockets", "pyaudio"]

if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    dependencies += ['RPi.GPIO', 'spidev']

dependencies += ['requests', 'cairosvg']

setup(
    name='waveshare-epd',
    description='Waveshare e-Paper Display',
    author='Waveshare',
    # package_dir={'': 'lib'},
    # packages=['waveshare_epd'],
    install_requires=dependencies,
)