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

    # jarvis, blueberry, alexa, grapefruit, ok google, picovoice, hey siri, grasshopper, hey barista, americano, porcupine, hey google, pico clock, bumblebee, computer, terminator,    
    keywords = ['jarvis', 'computer']
    paths = [pvporcupine.KEYWORD_PATHS[x] for x in keywords]

    demo = PorcupineDemo(
        access_key=pico_key,
        library_path=pvporcupine.LIBRARY_PATH,
        model_path=pvporcupine.MODEL_PATH,
        keyword_paths= paths,
        sensitivities=[0.8] * len(paths), # Higher is more sensitive
        input_device_index=-1)

    demo.run()

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