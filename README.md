# dall-e-2-art

## To Do

## To Do

- Connect to Dall-E 2 and fetch an image
    - Fix login issue with the selenium browser
- Connect to Assembly AI
- render text
- change save name so it can be replayed

## Getting Started

** May need to run as sudo**

```
pip install .
python start
```


## Getting a dalle token

https://github.com/ezzcodeezzlife/dalle2-in-python

1. Go to https://openai.com/dall-e-2/
2. Create a OpenAI Account
3. Go to https://labs.openai.com/
4. Open the Network Tab in Developer Tools
5. Type a prompt and press "Generate"
6. Look for fetch to https://labs.openai.com/api/labs/tasks
7. In the request header look for authorization then get the Bearer Token ("sess-xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
8. Put the bearer token ("sess-xxxxxxxxxxxxxxxxxxxxxxxxxxxx") into the .env file


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