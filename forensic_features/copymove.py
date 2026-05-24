import cv2

def orb_features(img):

    orb=cv2.ORB_create()

    kp,des=orb.detectAndCompute(img,None)

    return len(kp)