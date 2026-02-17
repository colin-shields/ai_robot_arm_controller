from PIL import ImageDraw, Image


def draw_box(image, coord1, coord2, color, width=1):
    """
    Draws a rectangular box on an image using pixel coordinates.

    Parameters:
        image  : PIL.Image.Image
            The image to draw on.
        coord1 : tuple (x1, y1)
            First corner in pixel coordinates.
        coord2 : tuple (x2, y2)
            Opposite corner in pixel coordinates.
        color  : tuple or str
            Box color (e.g. (255, 0, 0) or "red").
        width  : int
            Line thickness (default = 1).
    """
    draw = ImageDraw.Draw(image)

    x1, y1 = coord1
    x2, y2 = coord2

    # Ensure correct ordering
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)

    draw.rectangle(
        [left, top, right, bottom],
        outline=color,
        width=width
    )

    return image


def draw_quad(image, coord1, coord2, coord3, coord4, color, width=1):
    """
    Draws a quadrilateral on an image using pixel coordinates.

    Parameters:
        image  : PIL.Image.Image
            The image to draw on.
        coord1–coord4 : tuple (x, y)
            Four vertices of the quadrilateral in pixel coordinates.
            Points must be provided in order (clockwise or counter-clockwise).
        color  : tuple or str
            Line color (e.g. (255, 0, 0) or "red").
        width  : int
            Line thickness (default = 1).
    """
    draw = ImageDraw.Draw(image)

    p1 = coord1
    p2 = coord2
    p3 = coord3
    p4 = coord4

    draw.line([p1, p2], fill=color, width=width)
    draw.line([p2, p3], fill=color, width=width)
    draw.line([p3, p4], fill=color, width=width)
    draw.line([p4, p1], fill=color, width=width)

    return image


RESPONSE_1 = {
    "paper": [
        [85, 49],
        [958, 102],
        [931, 893],
        [113, 882]
    ],
    "blocks": [
        {
            "color": "yellow",
            "top-left": [142, 411],
            "bottom-right": [278, 578]
        },
        {
            "color": "red",
            "top-left": [805, 196],
            "bottom-right": [941, 351]
        }
    ]
}   # ...889
RESPONSE_2 = {"paper": [[87, 56], [954, 86], [933, 893], [109, 893]],
              "blocks": [{"color": "yellow", "top-left": [142, 408], "bottom-right": [277, 574]},
                         {"color": "red", "top-left": [805, 198], "bottom-right": [940, 342]}]}
RESPONSE_3 = {
  "paper": [
    [53, 47],
    [624, 76],
    [606, 880],
    [71, 893]
  ],
  "blocks": [
    {
      "color": "yellow",
      "top-left": [91, 410],
      "bottom-right": [178, 574]
    },
    {
      "color": "red",
      "top-left": [516, 194],
      "bottom-right": [602, 345]
    }
  ]
}
RESPONSE_4 = {
  "paper": [
    [53, 47],
    [624, 76],
    [606, 453],
    [71, 460]
  ],
  "blocks": [
    {
      "color": "yellow",
      "top-left": [91, 194],
      "bottom-right": [178, 274]
    },
    {
      "color": "red",
      "top-left": [516, 91],
      "bottom-right": [602, 168]
    }
  ]
}
RESPONSE_5 = {
  "paper": [
    [26, 107],
    [606, 85],
    [825, 436],
    [54, 401]
  ],
  "blocks": [
    {
      "color": "red",
      "top-left": [154, 289],
      "bottom-right": [285, 370]
    },
    {
      "color": "blue",
      "top-left": [631, 191],
      "bottom-right": [763, 263]
    }
  ]
}   # move red next to blue
RESPONSE_6 = {
  "paper": [
    [26, 84],
    [606, 71],
    [589, 431],
    [31, 418]
  ],
  "blocks": [
    {
      "color": "red",
      "top-left": [154, 250],
      "bottom-right": [286, 343]
    },
    {
      "color": "blue",
      "top-left": [629, 147],
      "bottom-right": [640, 235]
    }
  ]
}   # using gemini's "perfected" prompt
RESPONSE_7 = {
  "paper": [
    [25, 105],
    [585, 83],
    [530, 418],
    [46, 434]
  ],
  "blocks": [
    {
      "color": "red",
      "top-left": [98, 234],
      "bottom-right": [183, 322]
    },
    {
      "color": "blue",
      "top-left": [405, 139],
      "bottom-right": [489, 221]
    }
  ]
}   # old prompt, 'thinking' model
RESPONSE_8 = {
  "paper": [[28, 83], [612, 98], [584, 453], [48, 442]],
  "blocks": [
    {
      "color": "yellow",
      "top-left": [76, 83],
      "bottom-right": [158, 170]
    },
    {
      "color": "red",
      "top-left": [416, 318],
      "bottom-right": [500, 403]
    }
  ]
}   # perfect prompt, thinking, ...055
RESPONSE_9 = {
  "paper": [
    [32, 72],
    [906, 73],
    [891, 938],
    [30, 887]
  ],
  "blocks": [
    {
      "color": "yellow",
      "top-left": [118, 169],
      "bottom-right": [245, 331]
    },
    {
      "color": "red",
      "top-left": [650, 632],
      "bottom-right": [780, 804]
    }
  ]
}   # 0-100 scale, 055, old prompt
RESPONSE_10 = {
    'paper': [(20, 10), (620, 10), (630, 470), (15, 475)], 'blocks': [{'color': 'yellow', 'top-left': (120, 90), 'bottom-right': (200, 170)}, {'color': 'red', 'top-left': (390, 250), 'bottom-right': (480, 340)}]}  # chatGPT, 640x480, old prompt


# IMAGE_PATH = "responses/picture_1769804055.png"
IMAGE_PATH = "responses/picture_1769802889.png"
NEW_PATH = "image_with_boxes.png"

response_used = RESPONSE_4

coords = [tuple(x) for x in response_used['paper']]
blocks = response_used['blocks']

img = Image.open(IMAGE_PATH)

# draw outline of paper
img_2 = draw_quad(img, *coords, color='white', width=5)

# draw bounding boxes of blocks
for block in blocks:
    img_2 = draw_box(img_2, block['top-left'], block['bottom-right'], block['color'])

img_2.save(NEW_PATH)

