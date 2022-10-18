import os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path
from threading import Thread

import pvporcupine

import pyaudio
import websockets
import asyncio
import base64
import json

import struct

load_dotenv()

dalle_key = os.getenv('DALLE_KEY')
dalle_email = os.getenv('DALLE_EMAIL')
dalle_password = os.getenv('DALLE_PASSWORD')
pico_key = os.getenv('PICO_KEY')
image_path = os.getenv('IMAGE_PATH')
assembly_key = os.getenv('ASSEMBLY_KEY')

print("Hello World")
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

class VoiceManager(Thread):

    def __init__(
        self,
        pico_access_key,
        fns,
        input_device_index,
        sensitivity = .8
        ):

        self._pico_access_key = pico_access_key
        self._input_device_index = input_device_index

        self.input = pyaudio.PyAudio()

        self.fns = fns
        self._keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in self.fns.keys()]

        self.ws = None

        self.porcupine = pvporcupine.create(
                access_key=self._pico_access_key,
                library_path=pvporcupine.LIBRARY_PATH,
                model_path=pvporcupine.MODEL_PATH,
                keyword_paths=self._keyword_paths,
                sensitivities= [sensitivity] * len(self._keyword_paths))

        self.keywords = list()
        for x in self._keyword_paths:
            keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
            if len(keyword_phrase_part) > 6:
                self.keywords.append(' '.join(keyword_phrase_part[0:-6]))
            else:
                self.keywords.append(keyword_phrase_part[0])
        
    
    def run(self):
        FRAMES_PER_BUFFER = 3200
        FRAME_LENGTH = 512 # (TODO)
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        stream = self.input.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=self.porcupine.sample_rate,
            input_device_index=-1,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        listening = False

        print("Audio Loop Starting... ")

        while(True):
            pcm = stream.read(self.porcupine.frame_length)

            # I haven't investigated this transformation, but fn sender & porcupine need diff formats
            # My guess is I actually don't need this
            # TODO: Investigage
            pcm_tuple = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            pcm_frames = []

            if not listening:
                result = self.porcupine.process(pcm_tuple)            
                keyword = self.keywords[result]
                if result >= 0:                    
                    print("result")
                    listening = True
                    asyncio.run(self.get_ws())
                    if self.fns.__contains__(keyword):
                        self.fns[keyword]()
            elif listening and self.ws == None:
                print("listening")
                print ("waiting for connection")
                pcm_frames.push(pcm)

            elif listening and self.ws != None:
                print("connected")
                print(len(pcm_frames))

                asyncio.run(self.sender(pcm))
                asyncio.run(self.receiver())

    async def assembly_runner(self):
        ws = await self.get_ws()

    async def sender(self, pcm):
        print(pcm)
        data = base64.b64encode(pcm).decode("utf-8")
        json_data = json.dumps({"audio_data":str(data)})
        await self.ws.send(json_data)

    async def receiver(self):
        result_str = await self.ws.recv()
        print(result_str)
        text = json.loads(result_str)['text']

    async def get_ws(self):
        if self.ws != None:
            print("Returning WS")
            return self.ws

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

            self.ws = _ws
            return self.ws

    def close_ws(self):
        self.ws.close()
        self.ws = None

    async def send_receive(self, recorder):
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

def jarvis_callback():
    print("jarvis_callback")

fns = {
    'jarvis': jarvis_callback
}

voice_manager = VoiceManager(pico_access_key=pico_key, fns=fns, input_device_index=-1)
voice_manager.run()