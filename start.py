import glob,os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path

# import pvporcupine
# from voice.porcupine import PorcupineDemo
# import pvcheetah

# from pvrecorder import PvRecorder

# import websockets
# import asyncio
# import base64
# import json
# import pyaudio

from IT8951.display import AutoEPDDisplay
from IT8951 import constants
from sys import path

from image_tools.tools import display_image, partial_update, default_display

from dalle.dalle import Dalle2
from dalle.dalle_automation import Selenium_Driver

from voice import VoiceManager

load_dotenv()

dalle_key = os.getenv('DALLE_KEY')
dalle_email = os.getenv('DALLE_EMAIL')
dalle_password = os.getenv('DALLE_PASSWORD')
pico_key = os.getenv('PICO_KEY')
image_path = os.getenv('IMAGE_PATH')
assembly_key = os.getenv('ASSEMBLY_KEY')

test_opencv = False
test_pico = False
test_dalle_selenium = False
test_dalle_api = False
test_display = True
test_rename = False

display = AutoEPDDisplay(vcom=-2.06, rotate='CW', mirror=False, spi_hz=24000000)

default_display(display)

if (test_display):
    dalle = Dalle2(dalle_key)

    # This can be removed
    fns = {
        'jarvis': lambda a: print("jarvis"),
    #    'computer': computer_callback
    }

    vm = VoiceManager(pico_access_key=pico_key, fns=fns, input_device_index=-1)
    transcript = vm.run()
    print(transcript)

    dalle.generate_and_download(transcript, "./imgs/tmp")
    
    temp_dir = "./imgs/tmp"
    targ_dir = "./imgs"
    i = 0
    for file in os.listdir(temp_dir):
        os.rename(os.path.join(temp_dir,file), os.path.join(targ_dir,transcript + "-" + str(i) + ".webp"))
        i += 1

    display_image(display, os.path.join(targ_dir, transcript + "-0" + ".webp"), transcript)

if (test_rename):
    faketranscript = "transcip"
    temp_dir = "./imgs/tmp"
    targ_dir = "./imgs"
    i = 0
    for file in os.listdir(temp_dir):
        os.rename(os.path.join(temp_dir,file), os.path.join(targ_dir,'transcript-' + str(i) + ".webp"))
        i += 1


if (test_pico):
    print("test_pico")
    PorcupineDemo.show_audio_devices()

    # jarvis, blueberry, alexa, grapefruit, ok google, picovoice, hey siri, grasshopper, hey barista, americano, porcupine, hey google, pico clock, bumblebee, computer, terminator
    fns = {
        'jarvis': lambda a: print("jarvis"),
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

# Does not work
if (test_dalle_selenium):
    print("test_dalle")
    selenium = Selenium_Driver()
    selenium.login(dalle_email, dalle_password)
    selenium.download_images("a frog walking his dog on a sunny day")

# Works
if (test_dalle_api):
    dalle = Dalle2(dalle_key)
    dalle.generate_and_download("a frog with really big front teath", image_path)
