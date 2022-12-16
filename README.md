# dall-e-2-art

## To Do

- [ ] clean up globals in start.py
- [ ] Better error handling, especially on file reads (e.g. what if no image gets downloaded from openai, then the dir doesn't have an image)
- [ ] Consider saving text/image layout rather than recomputing
- [ ] Consider allowing for more than 4 lines of text for very long strings
- [x] Move more constants into the .env and .config files
- [x] Fix the latency issues in start.py, specifically the 1second delay in the random image display
- [x] Refactor the text rendering in display.py/render so it's in it's own function
- [x] Fix the text rendering to change text sizes if text is too long
- [x] Consider making Jarvis slightly easier to trigger

## Getting Started

**May need to run as sudo**

```
pip install .
python start
```

## Issues
```
Importing the numpy C-extensions failed. This error can happen for
many reasons, often due to issues with your setup or how NumPy was
installed.
```
Ended up uninstalling numpy and installying python3-numpy

```
pip uninstall numpy  # remove previously installed version
apt install python3-numpy
```


# Libraries & Dependencies
- [Greg D Mayer's Python wrapper around the IT8951 e-paper controller](https://github.com/GregDMeyer/IT8951)
    - Seems to have limitations around partial update for GC16 (full image) renders
- [Documentation for Display](https://www.waveshare.net/w/upload/c/c4/E-paper-mode-declaration.pdf)
- [AssemblyAI](https://www.assemblyai.com/)
- [Picovoice Porcupine](https://github.com/Picovoice/porcupine)
- [PIL](https://pillow.readthedocs.io/en/stable/)