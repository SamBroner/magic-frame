# dall-e-2-art

## To Do

## To Do

- [ ] Move helper functions into their own file
- [ ] Move more constants into the .env and .config files
- [ ] Fix the latency issues in start.py, specifically the 1second delay in the random image display
- [ ] Consider making the loading screen faster
- [ ] Refactor the text rendering in display.py/render so it's in it's own function
- [ ] Fix the text rendering to change text sizes if text is too long
- [ ] Consider making Jarvis slightly easier to trigger
- [ ] Allow Assembly AI to take a longer pause

## Getting Started

** May need to run as sudo**

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


# Display Info
https://www.waveshare.net/w/upload/c/c4/E-paper-mode-declaration.pdf
## Display Mode Summary

GC16 is to publish high quality images. It kind of works in draw partial, but not really?
It seems like only DU works in 