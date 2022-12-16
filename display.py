import random, os, textwrap
from PIL import Image, ImageDraw, ImageFont
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
            display.width             # ymax (but make it a square with room for prompt underneath)
        )

        display.frame_buf.paste(color, box=box)

    # Update display
    display.draw_full(constants.DisplayModes.GC16)


async def loading_screen(display):
    for i in range(17):
        loading_frame(display, i)


def render(display, prompt, image):
    # Clear image to white
    clear_display(display)
    img = Image.open(image)

    dims = (display.width, display.height)
    # Resize image to fit on screen
    img.thumbnail(dims)

    display.frame_buf.paste(img, [0, 0])

    _write_text_box(display.frame_buf, prompt)

    display.draw_full(constants.DisplayModes.GC16)

def _write_text_box(display, prompt, fontsize=60):
    """
    Write the prompt on the display, wrapping text to fit the screen. Recursively reduces fontsize until the prompt fits into 4 lines
    """
    draw = ImageDraw.Draw(display)
    current_line = prompt
    remaining_text = prompt

    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf', fontsize)
    except OSError:
        font = ImageFont.truetype(
            '/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    # Text height actually varies suprisingly, but it's centered around the fontsize. So we try fontsize
    text_width = font.getlength(prompt)
    text_height = fontsize

    usable_width = display.width - 20
    usable_height = display.height - display.width - 20
    image_bottom = display.width
    lines = []

    characters = 100
    while (remaining_text != ""):
        if (text_width > usable_width):
            current_line = textwrap.shorten(current_line, width=characters, placeholder="")
            characters = characters - 1
        else:
            lines.append(current_line)
            remaining_text = remaining_text.split(current_line, 1)[1].strip()
            current_line = remaining_text
            characters = 100
    
        text_width = font.getlength(current_line)
    
    if (len(lines) > 4):
        print("Too many lines, recurse with smaller font")
        _write_text_box(display, prompt, fontsize = fontsize - 2)
    else:
        print("# of Lines:" + str(len(lines)))
        print("Font Size:" + str(fontsize))
        row_height = text_height + text_height/2
        line_start_y = image_bottom + 10 + (usable_height - row_height * len(lines))/2
        
        for line in lines:
            print(line)
            text_width = font.getlength(line)
            draw.text((10, line_start_y), line, font=font)
            line_start_y = line_start_y + text_height + text_height/2 

def display_integration_test():

    display = AutoEPDDisplay(vcom=-2.06, rotate='CW',
                            mirror=False, spi_hz=24000000)
    clear_display(display)

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
    two_line = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"
    three_line = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt"
    four_line = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et"
    five_line = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Aliquam eleifend"
    long_string = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Aliquam eleifend mi in nulla posuere sollicitudin aliquam ultrices sagittis. Tellus in metus vulputate eu scelerisque felis imperdiet proin. Vitae proin sagittis nisl rhoncus."

    prompt = long_string

    render(display, prompt, image)