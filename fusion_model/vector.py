import numpy as np

def combine(cnn,ela,noise,block,meta,ocr):

    return np.concatenate([cnn,ela,noise,block,meta,ocr])