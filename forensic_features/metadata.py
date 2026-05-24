from PIL import Image

def metadata(path):

    img=Image.open(path)

    return img.info