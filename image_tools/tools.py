from PIL import Image, ImageDraw, ImageFont

from IT8951.display import AutoEPDDisplay
from IT8951 import constants

def default_display(display):
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))
    img = Image.open("/home/pi/code/dall-e-2-art/imgs/thinking.webp")

    dims = (display.width, display.height)

    img.thumbnail(dims)

    # TODO: Paste to top of screen
    paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    print(paste_coords)
    display.frame_buf.paste(img, [0,0])

    display.draw_full(constants.DisplayModes.GC16)

    _place_text(display.frame_buf, "Jarvis, show me a...", x_offset=20, y_offset=375, fontsize=80)
    display.draw_partial(constants.DisplayModes.DU)

def display_image(display, path, text):

    # clearing image to white
    display.frame_buf.paste(0xFF, box=(0, 0, display.width, display.height))

    img = Image.open(path)

    # TODO: this should be built-in
    dims = (display.width, display.height)

    img.thumbnail(dims)

    # TODO: Paste to top of screen
    # paste_coords = [dims[i] - img.size[i] for i in (0,1)]  # align image with bottom of display
    display.frame_buf.paste(img, [0,0])

    display.draw_full(constants.DisplayModes.GC16)
    print(text)
    _place_text(display.frame_buf, text, x_offset=20, y_offset=375, fontsize=40)
    
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

# this function is just a helper for the others
def _place_text(img, text, x_offset=0, y_offset=0, fontsize=80):
    '''
    Put some centered text at a location on the image.
    '''
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = fontsize

    draw_x = (img_width - text_width)//2 + x_offset
    draw_y = (img_height - text_height)//2 + y_offset

    draw.text((draw_x, draw_y), text, font=font)
