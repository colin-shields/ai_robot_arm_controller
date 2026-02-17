from PIL import ImageDraw, Image


def draw_box(image, coord1, coord2, color, width=1):
    """
    Draws a rectangular box on an image using normalized coordinates (0–1000).

    Parameters:
        image  : PIL.Image.Image
            The image to draw on.
        coord1 : tuple (x1, y1)
            First corner in 0–1000 coordinate space.
        coord2 : tuple (x2, y2)
            Opposite corner in 0–1000 coordinate space.
        color  : tuple or str
            Box color (e.g. (255, 0, 0) or "red").
        width  : int
            Line thickness (default = 1).
    """
    draw = ImageDraw.Draw(image)
    img_width, img_height = image.size

    def scale(coord):
        x, y = coord
        px = int((x / 1000) * img_width)
        py = int((y / 1000) * img_height)
        return px, py

    x1, y1 = scale(coord1)
    x2, y2 = scale(coord2)

    # Ensure correct ordering
    left   = min(x1, x2)
    right  = max(x1, x2)
    top    = min(y1, y2)
    bottom = max(y1, y2)

    draw.rectangle(
        [left, top, right, bottom],
        outline=color,
        width=width
    )

    return image



img = Image.open("test_images/diagonal.webp")
img_2 = draw_box(img, (514, 258), (634, 465), "black", 1)
img_2 = draw_box(img_2, (343, 538), (463, 755), "black", 1)
img_2.save("test_images/diag_box.png")

