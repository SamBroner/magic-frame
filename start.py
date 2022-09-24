import os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path
import pvporcupine
from voice.porcupine import PorcupineDemo

from IT8951.display import AutoEPDDisplay
from IT8951 import constants
from sys import path

from image_tools.tools import display_image, partial_update, default_display

from dalle.dalle import Dalle2
from dalle.dalle_automation import Selenium_Driver

load_dotenv()

dalle_key = os.getenv('DALLE_KEY')
dalle_email = os.getenv('DALLE_EMAIL')
dalle_password = os.getenv('DALLE_PASSWORD')

pico_key = os.getenv('PICO_KEY')
image_path = os.getenv('IMAGE_PATH')

test_opencv = False
test_pico = True
test_assembly = False
test_dalle_selenium = False
test_dalle_api = False

display = AutoEPDDisplay(vcom=-2.06, rotate='CW', mirror=False, spi_hz=24000000)

default_display(display)

def get_text()

def jarvis_callback():
    print("jarvis_callback")

    img_path = '/home/pi/Pictures/Dall-E/generation-JqiIKN0LzZeoMXhwXV5QRbhd.webp'
    print('Displaying "{}"...'.format(img_path))
    display_image(display, img_path, "hello world")


if (test_pico):
    print("test_pico")
    PorcupineDemo.show_audio_devices()

    # jarvis, blueberry, alexa, grapefruit, ok google, picovoice, hey siri, grasshopper, hey barista, americano, porcupine, hey google, pico clock, bumblebee, computer, terminator
    fns = {
        'jarvis': jarvis_callback,
    #    'computer': computer_callback
    }

    paths = [pvporcupine.KEYWORD_PATHS[x] for x in fns.keys()]

    demo = PorcupineDemo(
        access_key=pico_key,
        library_path=pvporcupine.LIBRARY_PATH,
        model_path=pvporcupine.MODEL_PATH,
        keyword_paths= paths,
        sensitivities=[0.8] * len(paths), # Higher is more sensitive
        input_device_index=-1)

    recorder, porcupine = demo.run(fns)

if (test_assembly):
    print("test_assembly")

# Does not work
if (test_dalle_selenium):
    print("test_dalle")
    selenium = Selenium_Driver()
    selenium.login(dalle_email, dalle_password)
    selenium.download_images("a frog walking his dog on a sunny day")

# Works
if (test_dalle_api):
    dalle = Dalle2(dalle_key)
    dalle.generate_and_download("an abstract image of an astronaut on a sailboat", image_path)
