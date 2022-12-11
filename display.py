import time
import random
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

from IT8951.display import AutoEPDDisplay
from IT8951 import constants


def clear_display(display):
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))
    display.draw_full(constants.DisplayModes.INIT)


def loading_frame(display, j):
    # set frame buffer to gradient
    for i in range(16):
        color = ((i+j)*0x10) % 0xFF
        box = (
            i*display.width//16,      # xmin
            0,                        # ymin
            (i+1)*display.width//16,  # xmax
            display.width             # ymax (but make it a box)
        )

        display.frame_buf.paste(color, box=box)

    box = (
        0,                        # xmin
        display.width,            # ymin
        display.width,            # xmax
        display.height            # ymax
    )
    display.frame_buf.paste(0xFF, box=box)

    # update display
    display.draw_full(constants.DisplayModes.GC16)


async def loading_screen(display):
    for i in range(17):
        loading_frame(display, i)


def render(display, prompt, image):
    print("RENDERING")
    # clearing image to white
    clear_display(display)
    img = Image.open(image)

    # TODO: this should be built-in
    dims = (display.width, display.height)
    print("Display Dimensions:" + str(dims))

    img.thumbnail(dims)

    # TODO: Paste to top of screen
    paste_coords = [dims[i] - img.size[i]
                    for i in (0, 1)]  # align image with bottom of display
    print("Paste Cords")
    print(paste_coords)
    display.frame_buf.paste(img, [0, 0])

    draw = ImageDraw.Draw(display.frame_buf)
    fontsize = 60

    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype(
            '/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    # Text height actually varies suprisingly, but it's centered around the fontsize. So we hardcode 60
    # text_width, text_height = font.getsize(prompt)
    text_width = font.getlength(prompt)
    text_height = 60

    usable_width = display.width - 20
    usable_height = display.height - display.width - 20
    image_bottom = display.width
    lines = []

    current_line = prompt
    characters = 100
    while (prompt != ""):
        if (text_width > usable_width):
            current_line = textwrap.shorten(current_line, width=characters, placeholder="")
            characters = characters - 1
        else:
            print(characters)
            lines.append(current_line)
            prompt = prompt.split(current_line, 1)[1].strip()
            current_line = prompt
            characters = 100
    
        text_width = font.getlength(current_line)

    print("# of Lines:" + str(len(lines)))
    row_height = text_height + text_height/2
    line_start_y = image_bottom + 10 + (usable_height - row_height * len(lines))/2
    
    for line in lines:
        print(line)
        text_width = font.getlength(line)
        a = f"""
line_start_y: {line_start_y}
usable_height: {usable_height}
text_height: {text_height}
        """
        print(a)
        draw.text((10, line_start_y), line, font=font)
        line_start_y = line_start_y + text_height + text_height/2

    display.draw_full(constants.DisplayModes.GC16)

# So what's our goal here?
# I think we want a maximum of 3 lines of text
# Let's try that out...

# Default Font Size is 60
# Max Lines is 4

def _write_text_box(frame_buf, text, xmin, xmax, ymin, ymax, fontsize=60):
    draw = ImageDraw.Draw(frame_buf)
    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype(
            '/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    lines = []
    line = []

    words = text.split(' ')


def _text_handler(img, text, image_height, display_width, fontsize=80, width=20):
    # Image Height tells us how low down on the screen we should start rendering text
    # This is because we want to render the text below the image
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype(
            '/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    lines = textwrap.wrap(text, width)

    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = fontsize

    if (text_width * .9 > display_width):
        fontsize = fontsize * (display_width / text_width) * .9
        _text_handler(img, text, image_height, display_width, fontsize)


# this function is just a helper for the others
def _place_text(img, text, x_offset=0, y_offset=0, fontsize=80):
    '''
    Put some centered text at a location on the image.
    '''
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype(
            '/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = fontsize

    draw_x = (img_width - text_width)//2 + x_offset
    draw_y = (img_height - text_height)//2 + y_offset

    draw.text((draw_x, draw_y), text, font=font)


def display_gradient(display):
    print('Displaying gradient...')

    # set frame buffer to gradient
    for i in range(16):
        color = i*0x10
        box = (
            i*display.width//16,      # xmin
            0,                        # ymin
            (i+1)*display.width//16,  # xmax
            display.height            # ymax
        )

        display.frame_buf.paste(color, box=box)

    # update display
    display.draw_full(constants.DisplayModes.GC16)

    # then add some black and white bars on top of it, to test updating with DU on top of GC16
    box = (0, display.height//5, display.width, 2*display.height//5)
    display.frame_buf.paste(0x00, box=box)

    box = (0, 3*display.height//5, display.width, 4*display.height//5)
    display.frame_buf.paste(0xF0, box=box)

    display.draw_partial(constants.DisplayModes.DU)


def partial_update(display):
    print('Starting partial update...')

    # clear image to white
    # display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))

    print('  writing full...')
    _place_text(display.frame_buf, 'partial', x_offset=-display.width//4)
    display.draw_full(constants.DisplayModes.GC16)

    # TODO: should use 1bpp for partial text update
    print('  writing partial...')
    _place_text(display.frame_buf, 'update', x_offset=+display.width//4)
    display.draw_partial(constants.DisplayModes.DU)


def test():
    display = AutoEPDDisplay(vcom=-2.06, rotate='CW',
                            mirror=False, spi_hz=24000000)
    clear_display(display)

    # loading_screen(display)
    dir = os.path.join("./imgs", random.choice(os.listdir("./imgs")))

    image = dir
    for file in os.listdir(dir):
        print(file)
        if file.endswith(".jpeg"):
            image = os.path.join(dir, file)

    print(image)

    prompt_file = os.path.join(dir, "prompt.txt")
    prompt = open(prompt_file, 'r').read()
    print(prompt)


    one_line = "Jarvis, show me a turkey"
    two_line = "Jarvis, show me a turkey driving a truck with a line two"
    three_line = "Jarvis, show me a turkey driving a truck with a line one and a line two and a line three"
    four_line = "Jarvis, show me a turkey driving a truck with al ine one and a line two and a line three and a line four"

    prompt = one_line

    render(display, prompt, image)
