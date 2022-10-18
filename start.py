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
from pvrecorder import PvRecorder

import websockets
import asyncio
import base64
import json
import pyaudio

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
assembly_key = os.getenv('ASSEMBLY_KEY')

test_opencv = False
test_pico = False
test_assembly = True
test_dalle_selenium = False
test_dalle_api = False

display = AutoEPDDisplay(vcom=-2.06, rotate='CW', mirror=False, spi_hz=24000000)
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

default_display(display)

 
async def send_receive(recorder):
    print(f'Connecting websocket to url ${URL}')
    async with websockets.connect(
        URL,
        extra_headers=(("Authorization", assembly_key),),
        ping_interval=5,
        ping_timeout=20
    ) as _ws:

        await asyncio.sleep(0.1)
        print("Receiving SessionBegins ...")
        session_begins = await _ws.recv()
        print(session_begins)
        print("Sending messages ...")

        async def send():
            while True:
                try:
                   data = recorder.read(FRAMES_PER_BUFFER)
                   data = base64.b64encode(data).decode("utf-8")
                   json_data = json.dumps({"audio_data":str(data)})
                   await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
                except Exception as e:
                   assert False, "Not a websocket 4008 error"
                
                await asyncio.sleep(0.01)
            return True

        async def receive():
            stopper = False # Helps make sure you only record one sentence
            last_text = ""
            while True:
                try:
                    result_str = await _ws.recv()
                    print(result_str)
                    text = json.loads(result_str)['text']
                    if (stopper == True and text == "" ):
                        print ("STOPPPINGSTOPPING")
                        return last_text
                        # break
                    if (text != ""):
                        stopper=True
                        last_text = text
                    print(json.loads(result_str)['text'])
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
        
        send_task = asyncio.create_task(send())
        receive_task = asyncio.create_task(receive())
        result = await asyncio.wait([send_task, receive_task], return_when=asyncio.FIRST_COMPLETED)

        send_task.cancel()
        await _ws.close()
        return result[0]


if (test_assembly):
    print("test_assembly")
    FRAMES_PER_BUFFER = 3200
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    p = pyaudio.PyAudio()
    
    # starts recording
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input_device_index=-1,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    receive_results = asyncio.run(send_receive(stream))
    result = receive_results.pop().result()
    print(result)

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
