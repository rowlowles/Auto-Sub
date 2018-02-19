import cv2
import numpy as np

# import picamera

def get_image():
    # Implement some code here to get the image address from the pi
    return "Golf_Balls_crop.jpg"


#RGB Values of "Red" = R: 198 G: 69 B: 73
# Make range for red RGB: 180,60,80 --> 220,80,100
def find_colours(image_address):
    # A one unit list containing a tuple of two BGR colour lists
    red_bound = [([80,60,180],[100,80,220])]
    img = cv2.imread(image_address)

    for lower,upper in red_bound:
        lower = np.array(lower,dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(img, lower,upper)
        output = cv2.bitwise_and(img,img, mask=mask)
        cv2.imshow("images",output )#np.hstack([img,output]))
        cv2.waitKey(0)
    print("Process image")


def blob_finding(image_address):
    img = cv2.imread(image_address)

    params = cv2.SimpleBlobDetector_Params()

    detector = cv2.SimpleBlobDetector_create(params)

    keypoints = detector.detect(img)
    im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("image",im_with_keypoints)
    cv2.waitKey(0)

def camera_capture():
    print("Insert pi camera logic here")

if __name__ == "__main__":
    image = get_image()
    #blob_finding(image)
    find_colours(image)
    print ("Hello")