import cv2
import numpy as np

import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd=os.environ.get('TESSERACT_PATH')

from .wordle_analysis import WordleAnalysis


TILE_PCT_AREA_CUTOFF = 0.02 # this was derived empirically

class ScreenShotAnalysis:
    def __init__(self):
        self.wa = WordleAnalysis()
        pass

    def load_image(self, img_path):
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    
    def test(self, img_path):
        img = self.load_image(img_path)
        print(img.shape)

    def correct_letter(self, letter):
        correction_dict = {
            '|': "I",
            '0': "O"
        }
        return correction_dict.get(letter, letter)

    def process(self, img_path):
        img = self.load_image(img_path)
        img_area = img.shape[0] * img.shape[1]
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img_gray_inv = cv2.bitwise_not(img_gray)
        ret, thresh = cv2.threshold(img_gray_inv, 70, 155, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        square_contours = []
        # Note: this is going to depend on size of image. Will need to resize image, 
        # and adjust/recompute this val as necessay. Or calc as % of image size
        square_area_thresh = img_area * TILE_PCT_AREA_CUTOFF #15000
        for c in contours:
            area = cv2.contourArea(c)
            if (area > square_area_thresh) & (len(c) == 4):
                square_contours.append(c)
        print(f"Num tiles detected: {len(square_contours)}")

        # Order the square contours by row, column
            # Note: coordinates of a given contour are:
            # - upper L: y,x
            # - upper R: y,x
            # - lower R: y,x
            # - lower L: y,x
        square_contours.sort(key=lambda coord: (coord[0][0][1], coord[0][0][0]))

        # get color masks
        ## define colors
        gray = np.array([121, 124, 126])
        yellow = np.array([199, 180, 102])
        green = np.array([121, 167, 107])

        bool_mask_green = cv2.inRange(img, green-10, green+10)
        img_green_mask = cv2.bitwise_and(img, img, mask=bool_mask_green)

        bool_mask_yellow = cv2.inRange(img, yellow-10, yellow+10)
        img_yellow_mask = cv2.bitwise_and(img, img, mask=bool_mask_yellow)

        bool_mask_gray = cv2.inRange(img, gray-10, gray+10)
        img_gray_mask = cv2.bitwise_and(img, img, mask=bool_mask_gray)

        color_mask_dict = {
            2: img_green_mask,
            1: img_yellow_mask,
            0: img_gray_mask 
        }

        letters = []
        letter_colors = []

        for c in square_contours:
            # create a blank (all-black) image
            cimg = np.zeros_like(img)
            # draw the contour over the blank image
            cv2.drawContours(cimg, [c], 0, color=252, thickness=-1)
            # generate a mask from this
            bool_mask = cv2.inRange(cimg, 250, 255)
            # apply to original image
            masked_img = cv2.bitwise_and(img, img, mask=bool_mask)
            # convert to grayscale
            mimg_grey = cv2.cvtColor(masked_img, cv2.COLOR_RGB2GRAY)
            # apply a threshold to get black&white
            _, mimg_bw = cv2.threshold(mimg_grey, 180, 255, 0)
            # invert B&W so letter is in black, background in white
            mimg_bw_inv = cv2.bitwise_not(mimg_bw)
            # now, tesseract should work
            ## though we only take the first character, JIC
            letter_detected = pytesseract.image_to_string(mimg_bw_inv, lang="eng", config="--psm 7").strip()[0]

            letters.append(
                self.correct_letter(letter_detected)
            )

            # check for overlap with the color masks
            for color_code, img_color_mask in color_mask_dict.items():
                if np.max(cv2.bitwise_and(img_color_mask, masked_img)) > 0:
                    letter_colors.append(color_code)

        # split into rows
        n = 5
        row_letters = []
        row_colors = []
        for i in range(0, len(letters), n):
            row_letters.append(letters[i: i+n])
            row_colors.append(letter_colors[i: i+n])

        print("Detected letters & color codes:")
        print(row_letters)
        print(row_colors)
        num_words, word_list = self.wa.new_cheat(row_letters, row_colors, True)
        return num_words, word_list