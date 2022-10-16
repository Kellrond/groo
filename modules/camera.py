import cv2


def runCameraTest():
    cam = cv2.VideoCapture(0)
    # title of the app
    # cv2.namedWindow('python webcam screenshot app')

    # # let's assume the number of images gotten is 0
    img_counter = 0


    ret, frame = cam.read()


    # the format for storing the images scrreenshotted
    img_name = f'opencv_frame_{img_counter}.jpg'
    # saves the image as a png file
    cv2.imwrite(img_name, frame)
    print('screenshot taken')
    # the number of images automaticallly increases by 1
    img_counter += 1

    # release the camera
    cam.release()

    # # stops the camera window
    # cam.destoryAllWindows()