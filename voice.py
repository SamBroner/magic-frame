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

import struct

load_dotenv()

dalle_key = os.getenv('DALLE_KEY')
dalle_email = os.getenv('DALLE_EMAIL')
dalle_password = os.getenv('DALLE_PASSWORD')
pico_key = os.getenv('PICO_KEY')
image_path = os.getenv('IMAGE_PATH')
assembly_key = os.getenv('ASSEMBLY_KEY')

print("Hello World")

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

            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            result = self.porcupine.process(pcm)            
            keyword = self.keywords[result]
            if result >= 0:                    
                print("result")
                listening = True
                if self.fns.__contains__(keyword):
                    self.fns[keyword]()

            if listening:
                print("listening")


def jarvis_callback():
    print("jarvis_callback")

fns = {
    'jarvis': jarvis_callback
}

voice_manager = VoiceManager(pico_access_key=pico_key, fns=fns, input_device_index=-1)
voice_manager.run()