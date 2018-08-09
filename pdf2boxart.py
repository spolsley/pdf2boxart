#!/usr/bin/env python
import pdf2image
from PIL import Image
import numpy as np
import sys, os

def process_pdf(filename,path=""):
	if len(path) > 0 and path[len(path)-1] != "/":
		path = path + "/"
	filename = path + filename
	images = pdf2image.convert_from_path(filename)
	new_images = []

	# set window size and threshold for RGB value differences
	if len(sys.argv) < 3:
		w = 26
	else:
		w = int(sys.argv[2])
	if len(sys.argv) < 4:
		# thresh = [50]*3 # 3 to have one for each value of RGB space
		thresh = 6 # average all to one instead of keeping RGB separate
	else:
		thresh = int(sys.argv[3])

	# enumerate images for cropping
	index = 1
	for image in images:
		img = np.array(image)
		# upper left, upper right, lower left, lower right
		ul,ur,ll,lr = None,None,None,None
		i,j = 0,0
		# ref_avg = np.mean(img[i:i+w,j:j+w],axis=(0,1)) # reference average based on first square
		ref_avg = np.mean(img[j:j+w,i:i+w]) # average all to one, rather than keep individiual RGB changes
		i+=w
		(y,x,z) = np.shape(img)
		was_out = False # use this to trigger whether entering or exiting shape
		# First pass works from upper left, across, down one step, across again, and so on until upper corners found
		while j + w < y:
			while i + w < x:
				# avg = np.mean(img[i:i+w,j:j+w],axis=(0,1))
				avg = np.mean(img[j:j+w,i:i+w])
				out_thresh = abs(avg-ref_avg) > thresh # detect if this window average is outside thresh from reference
				# set coordinates accordingly
				# if out_thresh[0] and out_thresh[1] and out_thresh[2] and not was_out:
				if out_thresh and not was_out:
					if not ul:
						ul = (i,j)
					was_out = True
				# elif not out_thresh[0] and not out_thresh[1] and not out_thresh[2] and was_out:
				elif not out_thresh and was_out:
					if not ur:
						ur = (i,j)
					was_out = False
				i+=w # step x
			i = 0
			j+=w # step y
			if ul and ur: # if both upper corners found, done
				break
		# Second pass works from bottom left, across left, up one step, across left again, and so on until lower corners found
		i = x - w - 1
		j = y - w - 1
		was_out = False
		while j - w > 0:
			while i - w > 0:
				# avg = np.mean(img[i:i+w,j:j+w],axis=(0,1))
				avg = np.mean(img[j:j+w,i:i+w])
				out_thresh = abs(avg-ref_avg) > thresh # detect if this window average is outside thresh from reference
				# set coordinates accordingly
				# if out_thresh[0] and out_thresh[1] and out_thresh[2] and not was_out:
				if out_thresh and not was_out:
					if not lr:
						lr = (i,j)
					was_out = True
				# elif not out_thresh[0] and not out_thresh[1] and not out_thresh[2] and was_out:
				elif not out_thresh and was_out:
					if not ll:
						ll = (i,j)
					was_out = False
				i-=w # step x
			i = x - w - 1
			j-=w # step y
			if ll and lr: # if both lower corners found, done
				break
		# Crop and save updated image
		new_image = image.crop(box=(min(ul[0],ll[0]),min(ul[1],ur[1]),max(lr[0],ur[0]),max(lr[1],ll[1])))
		# Handle top and bottom if present, make sure they are wider than height for correct positioning
		if index == 5 or index == 6:
			width, height = new_image.size
			if width < height:
				new_image = new_image.transpose(Image.ROTATE_270)
		new_images.append(new_image)
		index+=1

	filename_parts = filename.split('.')
	new_filename = filename_parts[0] + '_cover.jpg'

	# combine images
	# one image, just use cover
	if len(new_images) == 1:
		new_images[0].save(new_filename)
		new_images[0].show()
	# any other number need concatenation
	else:
		# Always use the first 4 images as front, back, and sides
		if len(new_images) < 5:
			widths, heights = zip(*(im.size for im in new_images))
		else:
			widths, heights = zip(*(im.size for im in new_images[0:4]))
		total_width = sum(widths)
		x_offset = 0
		max_height = max(heights)
		y_offset = 0
		bottom_y_offset = 0
		# If top and/or bottom present, adjust height accordingly
		if len(new_images) >= 5:
			width, height = new_images[4].size
			max_height += height
			y_offset = height
		if len(new_images) >= 6:
			width, height = new_images[5].size
			bottom_y_offset = max_height
			max_height += height
		# New image placeholder
		new_im = Image.new('RGB',(total_width,max_height))
		for index in range(0,min(len(new_images),4)):
			im = new_images[index]
			new_im.paste(im, (x_offset,y_offset))
			if index == 2: # at back, check for top and/or bottom of cover
				if y_offset > 0: # was top
					new_im.paste(new_images[4], (x_offset,0)) # place at same spot as back but 0 y_offset
				if bottom_y_offset > 0: # was bottom
					new_im.paste(new_images[5], (x_offset,bottom_y_offset))
			x_offset += im.size[0]
		new_im.save(new_filename)
		new_im.show()


if len(sys.argv) < 2:
	print "Usage: pdf2boxart.py <file or directory> <optional: window size> <optional: threshold>"
	exit(0)

# Read pdf pages as images
infile = sys.argv[1]

if os.path.isdir(infile):
	for filename in os.listdir(infile):
		if ".pdf" in filename:
			process_pdf(filename,path=infile)
elif ".pdf" in infile:
	process_pdf(infile)
else:
	print "Input must be a PDF"

