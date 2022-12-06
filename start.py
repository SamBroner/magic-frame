import glob,os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path
import asyncio

import pvporcupine
import pvcheetah

import pyaudio
import websockets
import asyncio
import base64
import json
import struct

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

display = AutoEPDDisplay(vcom=-2.06, rotate='CW', mirror=False, spi_hz=24000000)

default_display(display)

test_dalle = False

# def run_display():

#     # Create Dalle
#     dalle = Dalle2(dalle_key)

#     # Create Voice Manager
#     vm = VoiceManager(pico_access_key=pico_key, keywords=["jarvis"], input_device_index=-1)
#     time.sleep(10)
#     default_display(display)

#     transcript = vm.run(display)
#     print(transcript)

#     if (test_dalle):
#         dalle.generate_and_download(transcript, "./imgs/tmp")
#         temp_dir = "./imgs/tmp"
#         targ_dir = "./imgs"
#         i = 0
#         for file_name in os.listdir(temp_dir):
#             os.rename(os.path.join(temp_dir,file_name), os.path.join(targ_dir,transcript + "-" + str(i) + ".webp"))
#             i += 1

#         display_image(display, os.path.join(targ_dir, transcript + "-0" + ".webp"), transcript)
#     else:
#         print("No Dalle Test")
        
#         targ_dir = "./imgs"
#         file_name = "Show me a man walking a porcupine with a hat on.-1.webp"
#         transcript = "Show me a man walking a porcupine with a hat on."

#         display_image(display, os.path.join(targ_dir, file_name), transcript)

    
#     run_display()

# run_display()


# Create porcupine voice manager
porcupine = pvporcupine.create(
                access_key=pico_key,
                keywords=["jarvis"])

# Create Audio Stream
input = pyaudio.PyAudio()
FRAMES_PER_BUFFER = 3200
FRAME_LENGTH = 512 # (TODO)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
stream = input.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=porcupine.sample_rate,
            input_device_index=-1,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

# Create event Loop
loop = asyncio.get_event_loop()

# Create WakeWord Event
wakeword_event = asyncio.Event()

async def voice_trigger_setter():
    print("set")
    try:
        while True:
            pcm = stream.read(porcupine.frame_length)
            pcm_tuple = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm_tuple)

            if result >= 0:                    
                wakeword_event.set()
                break
    except Exception as e:
        print("voice_trigger_setter Exception")
        print(e)

async def voice_trigger_waiter():
    try:
        await wakeword_event.wait()
    except Exception as e:
        print("voice_trigger_waiter Exception")
        print(e)


async def connect_assembly_ai():
    print("connected")

async def display_thinking():
    display_image(display, "./imgs/thinking.webp", "Let me get ready...")

URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

async def send_receive():
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
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data":str(data)})
                    await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    print(e)
                    break
                    # TODO: eat this error. It's because we close the session in receive and continue sending data.
                await asyncio.sleep(0.01)
            
            return True
      
        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    load = json.loads(result_str)
                    print(load['text'])
                    if(load["message_type"] == "FinalTranscript"):
                        json_data = json.dumps({"terminate_session": "true"})
                        await _ws.send(json_data)
                        await _ws.close()
                        return load['text']
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    assert False, "Not a websocket 4008 error"
      
        send_result, receive_result = await asyncio.gather(send(), receive())
        # return await asyncio.gather(send(), receive())
        return receive_result
        

async def main():
    print("Hello, World")
    await asyncio.gather(voice_trigger_setter(), voice_trigger_waiter())
    print("Awake")
    _, text = await asyncio.gather(display_thinking(), send_receive())
    print("done")
    print(text)

asyncio.run(main())
