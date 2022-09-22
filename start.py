import os
from dotenv import load_dotenv
import logging
import time
import requests
import urllib
import urllib.request
from pathlib import Path

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