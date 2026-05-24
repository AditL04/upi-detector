import cv2
import numpy as np

def preprocess(path):
    img = cv2.imread(path)

    h, w = img.shape[:2]

    scale = 380 / max(h, w)

    resized = cv2.resize(img, (int(w*scale), int(h*scale)))

    canvas = np.zeros((380, 380, 3), dtype=np.uint8)

    canvas[:resized.shape[0], :resized.shape[1]] = resized

    return canvas / 255.0