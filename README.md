# Magic Frame
A "magic frame" that displays generated art from audio prompts to an e-ink display.

[See it in action on Twitter!](https://twitter.com/SamBroner/status/1602137871523143680)

- Images Generated from [Dall-E 2](https://openai.com/dall-e-2/)
- Realtime Transcription from [AssemblyAI](https://www.assemblyai.com/)
- Wakeword Detection from [Picovoice Porcupine](https://github.com/Picovoice/porcupine)

## Getting Started
1. Clone Repo
2. Create accounts for AssemblyAI, OpenAI, and Picovoice. 
3. Create .env from .env.template with keys
4. Install
5. Start

```
pip install .
python start
```

## To Do

- [ ] clean up globals in start.py
- [ ] Better error handling, especially on file reads (e.g. what if no image gets downloaded from openai, then the dir doesn't have an image)
- [ ] Consider saving text/image layout rather than recomputing
- [ ] Consider allowing for more than 4 lines of text for very long strings
- [ ] Consider putting prompt on display before submitting to OpenAI (immediately after getting prompt back from AssemblyAI)
- [x] Move more constants into the .env and .config files
- [x] Fix the latency issues in start.py, specifically the 1second delay in the random image display
- [x] Refactor the text rendering in display.py/render so it's in it's own function
- [x] Fix the text rendering to change text sizes if text is too long
- [x] Consider making Jarvis slightly easier to trigger

# Dependencies

## Hardware
- [1200x825, 9.7inch E-Ink display HAT for Raspberry Pi](https://www.waveshare.com/9.7inch-e-paper-hat.htm) - $193.79
- [Raspberry Pi Model 4B - 4GB Ram](https://www.adafruit.com/product/4296) - $55.00
- [USB Lavalier Microphone](https://www.amazon.com/dp/B074BLM973) - $24.43
- Frame - $12
- Random - ~$15

Total: $300.22

## Libraries
- [Greg D Meyer's Python wrapper around the IT8951 e-paper controller](https://github.com/GregDMeyer/IT8951)
    - Seems to have limitations around partial update for GC16 (full image) renders
    - This is somewhat blocking my ability to do a partial update with text before rendering the image
- [Documentation for Display](https://www.waveshare.net/w/upload/c/c4/E-paper-mode-declaration.pdf)
- [AssemblyAI](https://www.assemblyai.com/)
- [Picovoice Porcupine](https://github.com/Picovoice/porcupine)
- [PIL](https://pillow.readthedocs.io/en/stable/)
- [Dall-E 2](https://openai.com/dall-e-2/)

# Issues

### NUMPY (OpenAI dependency)
```
Importing the numpy C-extensions failed. This error can happen for many reasons, often due to issues with your setup or how NumPy was installed.
```
Ended up uninstalling numpy and installying python3-numpy

```
pip uninstall numpy  # remove previously installed version
apt install python3-numpy
```
