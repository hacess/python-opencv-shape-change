# -*- coding: utf-8 -*-
# @Author: user
# @Date:   2018-06-21 17:09:51
# @Last Modified by:   user
# @Last Modified time: 2018-06-21 18:18:39

from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2

class SizeChange():
	"""docstring for ClassName"""
	def midpoint(self,ptA, ptB):
		return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

	def imagedimenstion(self,images):
		assume_width=2
		dims_width=[]
		dims_length=[]
		print(images)
		imageA = cv2.imread(images[0])
		imageA = cv2.resize(imageA, (0, 0), None, .5, .5) # just resized the image to a half of its original size
		imageB = cv2.imread(images[1])
		imageB = cv2.resize(imageB, (0, 0), None, .5, .5)

		#concat both images to form one image with original at the left
		numpy_horizontal_concat = np.concatenate((imageA, imageB), axis=1)

		#output file created
		#now finding the dimenstion

		image = numpy_horizontal_concat
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)


		# perform edge detection, then perform a dilation + erosion to
		# close gaps in between object edges
		edged = cv2.Canny(gray, 50, 100)
		edged = cv2.dilate(edged, None, iterations=1)
		edged = cv2.erode(edged, None, iterations=1)

		# find contours in the edge map
		cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]

		# sort the contours from left-to-right and initialize the
		# 'pixels per metric' calibration variable
		(cnts, _) = contours.sort_contours(cnts)
		pixelsPerMetric = None

		# loop over the contours individually
		for c in cnts:
			# if the contour is not sufficiently large, ignore it
			if cv2.contourArea(c) < 100:
				continue

			# compute the rotated bounding box of the contour
			orig = image.copy()
			box = cv2.minAreaRect(c)
			box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
			box = np.array(box, dtype="int")

			# order the points in the contour such that they appear
			# in top-left, top-right, bottom-right, and bottom-left
			# order, then draw the outline of the rotated bounding
			# box
			box = perspective.order_points(box)
			cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

			# loop over the original points and draw them
			for (x, y) in box:
				cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

			# unpack the ordered bounding box, then compute the midpoint
			# between the top-left and top-right coordinates, followed by
			# the midpoint between bottom-left and bottom-right coordinates
			(tl, tr, br, bl) = box
			(tltrX, tltrY) = self.midpoint(tl, tr)
			(blbrX, blbrY) = self.midpoint(bl, br)

			# compute the midpoint between the top-left and top-right points,
			# followed by the midpoint between the top-righ and bottom-right
			(tlblX, tlblY) = self.midpoint(tl, bl)
			(trbrX, trbrY) = self.midpoint(tr, br)

			# draw the midpoints on the image
			cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
			cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

			# draw lines between the midpoints
			cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),(255, 0, 255), 2)
			cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),(255, 0, 255), 2)

			# compute the Euclidean distance between the midpoints
			dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
			dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

			# if the pixels per metric has not been initialized, then
			# compute it as the ratio of pixels to supplied metric
			# (in this case, inches)
			if pixelsPerMetric is None:
				# pixelsPerMetric = dB / args["width"]
				pixelsPerMetric = dB / assume_width

			# compute the size of the object
			dimA = dA / pixelsPerMetric
			dimB = dB / pixelsPerMetric

			# draw the object sizes on the image
			cv2.putText(orig, "{:.1f}in".format(dimA),
				(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 0), 2)
			cv2.putText(orig, "{:.1f}in".format(dimB),
				(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 0), 2)
			dims_width.append(dimB)
			dims_length.append(dimA)
			# show the output image
			# cv2.imshow("Image", orig)
			# cv2.waitKey(0)
		print("Widths",dims_width)
		inc_width=((dims_width[1]-dims_width[0])/dims_width[0])*100
		print("width inc percent",round(inc_width , 2) ,"%") 

		print("Height",dims_length)
		dec_length=((dims_length[0]-dims_length[1])/dims_length[0])*100
		print("Height dec percent",round(dec_length , 2) ,"%") 
		return inc_width
				