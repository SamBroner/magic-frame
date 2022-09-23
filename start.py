import os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path
import pvporcupine
from porcupine import PorcupineDemo


from dalle import Dalle2
from dalle_automation import Selenium_Driver

load_dotenv()

dalle_key = os.getenv('DALLE_KEY')
dalle_email = os.getenv('DALLE_EMAIL')
dalle_password = os.getenv('DALLE_PASSWORD')

pico_key = os.getenv('PICO_KEY')

test_dalle = False
test_pico = True
test_assembly = False

if (test_pico):
    print("test_pico")
    PorcupineDemo.show_audio_devices()

    demo = PorcupineDemo(
        access_key=pico_key,
        library_path=pvporcupine.LIBRARY_PATH,
        model_path=pvporcupine.MODEL_PATH,
        keyword_paths=[pvporcupine.KEYWORD_PATHS[x] for x in pvporcupine.KEYWORDS],
        sensitivities=[0.5] * len([pvporcupine.KEYWORD_PATHS[x] for x in pvporcupine.KEYWORDS]),
        input_device_index=-1)

    demo.run()

    porcupine = pvporcupine.create(
        access_key=pico_key,
        keywords=['picovoice', 'bumblebee']
    )



    # def get_next_audio_frame():
    #     recorder = PvRecoder(device_index=-3)
    #     recorder.start()
    #     pcm = recorder.read()
    #     ppn.process(pcm)
    #     pass

    # while True:
    #     audio_frame = get_next_audio_frame()
    #     keyword_index = porcupine.process(audio_frame)
    #     if keyword_index == 0:
    #         # detected `porcupine`
    #         print("porcupine")
    #     elif keyword_index == 1:
    #         print("bumblebee")
    #         # detected `bumblebee`

if (test_assembly):
    print("test_assembly")

if (test_dalle):
    print("test_dalle")
    selenium = Selenium_Driver()
    selenium.login(dalle_email, dalle_password)
    selenium.download_images("a frog walking his dog on a sunny day")


# dalle = Dalle2(dalle_key)
# generations = dalle.generate("portal to another dimension, digital art")
# print(generations)