import os
import string
from dotenv import load_dotenv
import time
import requests
import urllib.request
import asyncio
import threading
import openai
import pvporcupine
from collections import deque
import pyaudio
import websockets
import asyncio
import base64
import json
import struct
from IT8951.display import AutoEPDDisplay

from image_tools.tools import display_image, partial_update, default_display

load_dotenv()

dalle_secret = os.getenv('DALLE_SECRET')
pico_key = os.getenv('PICO_KEY')
assembly_key = os.getenv('ASSEMBLY_KEY')

display = AutoEPDDisplay(vcom=-2.06, rotate='CW',
                         mirror=False, spi_hz=24000000)

default_display(display)

openai.api_key = dalle_secret

# Create Audio Stream
input = pyaudio.PyAudio()
FRAMES_PER_BUFFER = 3200
FRAME_LENGTH = 512  # (TODO)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Create porcupine voice manager
porcupine = pvporcupine.create(
    access_key=pico_key,
    keywords=["jarvis"],
    sensitivities=[0.8],)

stream = input.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=porcupine.sample_rate,
    input_device_index=-1,
    input=True,
    frames_per_buffer=porcupine.frame_length)

frames = deque(maxlen=1000)

# Create Audio Capture Thread. The frames object is used to transport audio across threads


def audio_capture():
    while True:
        pcm = stream.read(porcupine.frame_length)
        frames.append(pcm)
        time.sleep(0.01)


# Create event Loop
loop = asyncio.get_event_loop()

# Create WakeWord Event
wakeword_event = asyncio.Event()


async def voice_trigger_setter():
    print("set")

    # This frames object is used to re-add the audio of asking the question of Jarvis
    trigger_frames = deque(maxlen=60)
    try:
        while True:
            if len(frames) > 0:
                pcm = frames.popleft()
                pcm_tuple = struct.unpack_from(
                    "h" * porcupine.frame_length, pcm)
                result = porcupine.process(pcm_tuple)
                trigger_frames.append(pcm)
                if result >= 0:
                    wakeword_event.set()
                    frames.clear()
                    while (len(trigger_frames) > 0):
                        frames.appendleft(trigger_frames.pop())

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
                    if (len(frames) > 6):
                        one = bytes(frames.popleft())
                        two = bytes(frames.popleft())
                        three = bytes(frames.popleft())
                        four = bytes(frames.popleft())
                        five = bytes(frames.popleft())
                        six = bytes(frames.popleft())
                        data = b''.join([one, two, three, four, five, six])
                        data = base64.b64encode(data).decode("utf-8")
                        json_data = json.dumps({"audio_data": str(data)})
                        await _ws.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                except Exception as e:
                    print(e)
                    break
                    # TODO: We eat this error. The error is because we close the session in receive and continue sending data.
                await asyncio.sleep(0.01)

            return True

        async def receive():
            print("hello")
            while True:
                try:
                    print("receiving...")
                    result_str = await _ws.recv()
                    load = json.loads(result_str)
                    print(load['text'])
                    if (load["message_type"] == "FinalTranscript"):
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
        return receive_result


def make_directory(prompt):
    t = round(time.time())
    os.mkdir(os.path.join("./imgs", str(t)))
    with (open("./imgs/" + str(t) + "/prompt.txt", "w")) as f:
        f.write(prompt)
    return str(t)


def get_img_name(prompt):
    # create a translation table to remove punctuation and make the string lowercase
    table = str.maketrans('', '', string.punctuation)

    # apply the translation table to the string
    processed_string = prompt.translate(table).lower()

    # replace spaces with underscores
    processed_string = processed_string.replace(" ", "_")

    # print the processed string
    return processed_string


def download_image(url, t, prompt):
    response = requests.get(url)

    path = os.path.join("./imgs", t, get_img_name(prompt) + ".jpeg")
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

def clean_prompt(prompt):
    print("Removing content before Trigger Word")
    first_occurance = prompt.find("Jarvis")
    trimmed_string = prompt[first_occurance:]
    return trimmed_string

async def main():
    while True:
        print("Hello, World")
        await asyncio.gather(voice_trigger_setter(), voice_trigger_waiter())
        print("Awake")
        _, prompt = await asyncio.gather(display_thinking(), send_receive())
        print(prompt)
        prompt = clean_prompt(prompt)
        print(prompt)
        t = make_directory(prompt)
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response["data"][0]["url"]
        image_path = download_image(image_url, t, prompt)
        display_image(display, image_path, prompt)
        print("done")

thread = threading.Thread(target=audio_capture)
thread.start()

# Wait for the thread to start running, with a timeout of 5 seconds
try:
    thread.join(timeout=5)
except TimeoutError:
    print("The thread did not start running within 5 seconds.")
else:
    print("The thread started running.")

asyncio.run(main())
