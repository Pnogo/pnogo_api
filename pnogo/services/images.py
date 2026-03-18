import random
from io import BytesIO

from PIL import Image, ImageOps

JPEG_QUALITY = 85


def resize_image(image_data, width=None, height=None, maxsize=1280):
    """Resize image preserving aspect ratio. Returns a BytesIO with JPEG data."""
    img = Image.open(image_data).convert("RGB")
    img = ImageOps.exif_transpose(img)
    overscale = True

    if width is None and height is None:
        overscale = False
        if img.size[0] > img.size[1]:
            width = int(maxsize)
        else:
            height = int(maxsize)

    if height is None:
        width = int(width)
        ratio = width / float(img.size[0])
        height = int(float(img.size[1]) * ratio)
    elif width is None:
        height = int(height)
        ratio = height / float(img.size[1])
        width = int(float(img.size[0]) * ratio)
    else:
        width = int(width)
        height = int(height)

    if overscale or img.size[0] > width or img.size[1] > height:
        img = img.resize((width, height), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, "JPEG", optimize=True, quality=JPEG_QUALITY)
    buf.seek(0)
    return buf


def stretch_image(image_data, maxsize=1920):
    """Stretch image to random distorted dimensions. Returns a BytesIO with JPEG data."""
    img = Image.open(image_data).convert("RGB")

    otherside = int(random.uniform(1 / 20, 1) * maxsize)
    horizontal = random.random() < 0.5
    width = otherside if horizontal else maxsize
    height = maxsize if horizontal else otherside

    img = img.resize((width, height), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, "JPEG", optimize=True, quality=JPEG_QUALITY)
    buf.seek(0)
    return buf


def to_bitmap(image_data, width=128, height=64):
    """Convert image to 1-bit bitmap and return hex-encoded string."""
    img = Image.open(image_data).convert("RGB")
    img = img.resize((int(width), int(height)), Image.LANCZOS)
    img = img.convert("1")
    return "".join("0x%02x," % b for b in img.tobytes())
