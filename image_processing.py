import cv2
import numpy as np
#from picamera import PiCamera
import time
import datetime

camera = 3#PiCamera()

#RGB Values of "Red" = R: 198 G: 69 B: 73
# Make range for red RGB: 180,60,80 --> 220,80,100

def find_colours_rgb(image_address):
    # A one unit list containing a tuple of two BGR colour lists
    bounds = [([80, 60, 180], [100, 80, 220])]
    img = cv2.imread(image_address)  # , cv2.IMREAD_GRAYSCALE)

    for lower, upper in bounds:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(img, lower, upper)
        output = cv2.bitwise_and(img, img, mask=mask)

        cv2.namedWindow("image",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("image", 100,100)
        cv2.imshow("images", output)  # np.hstack([img,output]))
        cv2.waitKey(0)
    print("Process image")


def find_colours_hsv(image_address):
    im = cv2.imread(image_address)
    blur_im = cv2.GaussianBlur(im, (5, 5), 0)
    blur_hsv = cv2.cvtColor(blur_im, cv2.COLOR_BGR2HSV)

    # lowerRed = np.array([0, 117, 0])
    # upperRed = np.array([14, 255, 255])
    # lowerYellow = np.array([16, 117, 0])
    # upperYellow = np.array([33, 255, 255])
    lowerGreen = np.array([37, 157, 0])
    upperGreen = np.array([51, 255, 255])

    mask = cv2.inRange(blur_hsv, lowerGreen, upperGreen)
    res = cv2.bitwise_and(blur_hsv, blur_hsv, mask=mask)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 750, 1000)
    cv2.imshow("image", res)
    cv2.waitKey(0)

    params = cv2.SimpleBlobDetector_Params()
    # params.filterByCircularity = True
    # params.filterByCircularity = .9
    # params.filterByArea = True
    # params.minArea = 100
    # params.filterByInertia = True
    # params.minInertiaRatio = .5
    # params.maxInertiaRatio = 1


    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(mask)
    im_with_keypoints = cv2.drawKeypoints(mask, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow("image", im_with_keypoints)
    cv2.waitKey(0)


def blob_finding(image_address):
    img = cv2.imread(image_address)
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # edges = cv2.Canny(img, 50, 200)
    # cv2.namedWindow("edges", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("edges", 1000, 750)
    # cv2.imshow("edges", edges)
    # cv2.waitKey(0)

    params = cv2.SimpleBlobDetector_Params()
    params.filterByCircularity = True
    params.filterByCircularity = .9
    params.filterByArea = True
    params.minArea = 100
    params.filterByInertia = True
    params.minInertiaRatio = .5
    params.maxInertiaRatio = 1

    detector = cv2.SimpleBlobDetector_create(params)

    keypoints = detector.detect(img)

    im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 750, 1000)
    # cv2.imshow("images", output)
    cv2.imshow("image",im_with_keypoints)
    cv2.waitKey(0)


def camera_capture():
    # May prove useful but I don't have the PI so I can't say how useful it is:
    # https://picamera.readthedocs.io/en/release-1.10/recipes1.html#capturing-to-an-opencv-object
    currTime = datetime.datetime.now()
    camera.start_preview()
    # By default we need to let the camera adjust to the environment, which is why there is a 2 sec sleep
    # However, based off this: https://picamera.readthedocs.io/en/release-1.10/recipes1.html#capturing-consistent-images
    # We may be able to hardcode values for iso, shutter speed, etc to get consistent images without the sleep time
    # That will be what we need to do going forward and i can't test that remotely without the picamera, we need to do
    # it in water with some colour samples. 
    time.sleep(2)
    timeStampString = str(currTime.day)+"_"+str(currTime.hour)+"_"+str(currTime.minute)+"_"+str(currTime.second)
    fileName = "cap_"+timeStampString+".jpg"
    camera.annotate_text=timeStampString
    camera.capture(fileName)
    camera.stop_preview()
    return fileName


if __name__ == "__main__":
    # Comment in and out as needed
    image = "test_img_7.jpg"  # camera_capture()
    #blob_finding(image)
    #find_colours(image)
    find_colours_hsv(image)
    print ("Hello")