import imagehash
from PIL import Image

def phash(path):

    img=Image.open(path)

    return imagehash.phash(img)