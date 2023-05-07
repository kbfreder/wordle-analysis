import cv2
import matplotlib.pyplot as plt

import pytesseract

TESSERACT_PATH = "/usr/local/Cellar/tesseract/5.3.1/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd=TESSERACT_PATH


def load_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
img_gray_inv = cv2.bitwise_not(img_gray)
ret, thresh = cv2.threshold(img_gray_inv, 70, 155, 0)
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

square_contours = []
square_area_thresh = 15000
for c in contours:
    area = cv2.contourArea(c)
    if (area > square_area_thresh) & (len(c) == 4):
        square_contours.append(c)

# Note: coordinates of a given contour are:
# - upper L: y,x
# - upper R: y,x
# - lower R: y,x
# - lower L: y,x

# Need to order the square contours by row, column
square_contours.sort(key=lambda coord: (coord[0][0][1], coord[0][0][0]))

letters = []

for c in square_contours:
    # TODO: detect colors along with letters
    cimg = np.zeros_like(img)
    plt.imshow(cv2.drawContours(cimg, [c], 0, color=252, thickness=-1))
    mask = cv2.inRange(cimg, 250, 255)
    res_green = cv2.bitwise_and(img, img, mask=mask)
    res_gray = cv2.cvtColor(res_green, cv2.COLOR_RGB2GRAY)
    _, res_thresh = cv2.threshold(res_gray, 180, 255, 0)
    res_gray_inv = cv2.bitwise_not(res_thresh)
    letters.append(pytesseract.image_to_string(res_gray_inv, lang="eng", config="--psm 7"))

# split into rows
n = 5
row_letters = []
for i in range(0, len(letters), n):
    row_letters.append(letters[i: i+n])
