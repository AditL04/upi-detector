import numpy as np

def blockiness(img):

    vertical=np.sum(np.abs(img[:,1:]-img[:,:-1]))

    horizontal=np.sum(np.abs(img[1:,:]-img[:-1,:]))

    return vertical+horizontal