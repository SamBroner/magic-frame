import glob,os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path

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

def run_display():

    # Create Dalle
    dalle = Dalle2(dalle_key)

    # Create Voice Manager
    vm = VoiceManager(pico_access_key=pico_key, keywords=["jarvis"], input_device_index=-1)
    time.sleep(5)
    default_display(display)

    transcript = vm.run(display)
    print(transcript)

    if (test_dalle):
        dalle.generate_and_download(transcript, "./imgs/tmp")
        temp_dir = "./imgs/tmp"
        targ_dir = "./imgs"
        i = 0
        for file_name in os.listdir(temp_dir):
            os.rename(os.path.join(temp_dir,file_name), os.path.join(targ_dir,transcript + "-" + str(i) + ".webp"))
            i += 1

        display_image(display, os.path.join(targ_dir, transcript + "-0" + ".webp"), transcript)
    else:
        print("No Dalle Test")
        
        targ_dir = "./imgs"
        file_name = "Show me a man walking a porcupine with a hat on.-1.webp"
        transcript = "Show me a man walking a porcupine with a hat on."

        display_image(display, os.path.join(targ_dir, file_name), transcript)

    
    run_display()

run_display()
