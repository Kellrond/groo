''' The camera module should contain all of the functionality related to getting and storing
    images in the system.

    A few things for the todo list

    General camera function:
        - detect, identify and get meta data about cameras connected
        - List any cameras currently in use
        - Register a camera with the system

    Camera functionality:
        - Take image
        - Schedule image
        - timer image
        - interval image
        - record video
        - detect motion
        - generate stream

    Camera parameters:
        - resolution
        - quality 
        - dimensions
        - color
        - contrast
        - brightness
'''


from time import sleep
import cv2


def runCameraTest():
    img_counter = 0
    while True:
        cam = cv2.VideoCapture(0)

        ret, frame = cam.read()
        
        img_name = f'data/images/image_{img_counter}.png' 
        cv2.imwrite(img_name, frame)
        img_counter += 1

        cam.release()
