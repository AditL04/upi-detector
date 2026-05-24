from PIL import Image, ImageChops, ImageEnhance
import numpy as np


def run_ela(path, quality=90):

    original = Image.open(path).convert("RGB")

    temp_filename = "temp_ela.jpg"

    original.save(temp_filename, "JPEG", quality=quality)

    compressed = Image.open(temp_filename)

    ela_image = ImageChops.difference(original, compressed)

    extrema = ela_image.getextrema()

    max_diff = max([ex[1] for ex in extrema])

    if max_diff == 0:
        max_diff = 1

    scale = 255.0 / max_diff

    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    ela_array = np.array(ela_image)

    score = np.mean(ela_array)

    return score