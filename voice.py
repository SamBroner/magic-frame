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
import pvcheetah

import pyaudio
import websockets
import asyncio
import base64
import json

import struct

from image_tools.tools import display_image, partial_update, default_display, _place_text
from IT8951 import constants

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
        keywords,
        input_device_index,
        sensitivity = .8
        ):

        self._pico_access_key = pico_access_key
        self._input_device_index = input_device_index

        self.input = pyaudio.PyAudio()

        self._keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in keywords]

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

        self.cheetah = pvcheetah.create(
                access_key=self._pico_access_key,
                endpoint_duration_sec=1,
                enable_automatic_punctuation=True
        )
    
    
    def run(self, display):
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

        listening_for_wakeword = True
        is_endpoint = False

        print("Audio Loop Starting... ")
        # Used to print stage of audio loop
        first_porc = True
        first_cheet = True
    
        # Keep appending content to the transcript
        transcript = ""

        # Audio Loop - keeps pulling off new audio frames from the stream
        while(True):
            pcm = stream.read(self.porcupine.frame_length)
            pcm_tuple = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

            if listening_for_wakeword:
                if first_porc: # Print the current stage of the loop
                    print("porcupine")
                    first_porc = False
                    first_cheet = True
    
                result = self.porcupine.process(pcm_tuple)            
                keyword = self.keywords[result]
                if result >= 0:                    
                    print("-----result-----")
                    listening_for_wakeword = False
                    time_end = time.time() + 10
                    
                    # Clear display 
                    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))
                    display.draw_full(constants.DisplayModes.DU) # is this necessary?


            # wait for an endpoint or cut it off at 10 seconds
            elif time.time() < time_end and not is_endpoint:
                if first_cheet: # Print the current stage of the loop
                    first_cheet = False
                    first_porc = True
                    print("cheetah")
                partial_transcript, is_endpoint = self.cheetah.process(pcm_tuple)

                transcript += partial_transcript
                _place_text(display.frame_buf, transcript, x_offset=20, y_offset=375, fontsize=40)
     
                display.draw_partial(constants.DisplayModes.DU)
                
                print(partial_transcript, end='', flush=True) # Flush makes sure the print happens in this loop of while
                if is_endpoint:
                    print("endpoint")
            else:
                listening_for_wakeword = True
                partial_transcript = self.cheetah.flush()
                transcript += partial_transcript
                print("---------------- End ----------------")
                break
        return transcript
