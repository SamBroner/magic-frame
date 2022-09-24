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
image_path = os.getenv('IMAGE_PATH')


test_opencv = False
test_pico = False
test_assembly = False
test_dalle_selenium = False
test_dalle_api = True

def computer_callback():
    print("computer_callback")

    endpoint = "https://api.assemblyai.com/v2/transcript"

    json = {
    "audio_url": "https://storage.googleapis.com/bucket/b2c31290d9d8.wav"
    }

    headers = {
    "Authorization": "c2a41970d9d811ec9d640242ac12",
    "Content-Type": "application/json"
    }

    response = requests.post(endpoint, json=json, headers=headers)
    parse(response)

def jarvis_callback():
    print("jarvis_callback")

if (test_opencv):
    print(os.getcwd())

# Works
if (test_pico):
    print("test_pico")
    PorcupineDemo.show_audio_devices()

    # jarvis, blueberry, alexa, grapefruit, ok google, picovoice, hey siri, grasshopper, hey barista, americano, porcupine, hey google, pico clock, bumblebee, computer, terminator
    fns = {
        'jarvis': jarvis_callback,
       'computer': computer_callback
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
