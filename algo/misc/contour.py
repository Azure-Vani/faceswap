
import cv2
import sys
import numpy as np

from facepp import API, File, APIError

contour_name_list = [
	#'left_eyebrow_right_corner',
	'left_eyebrow_upper_right_quarter',
	'left_eyebrow_upper_middle', 
	'left_eyebrow_upper_left_quarter',
	'left_eyebrow_left_corner', 
	#'contour_left1',
	#'contour_left2','contour_left3',
	#'contour_left4',
	#'contour_left5',
	#'contour_left6',
	'contour_left7','contour_left8','contour_left9',
	'contour_chin',
	'contour_right9','contour_right8','contour_right7',
	#'contour_right6',
	#'contour_right5',
	#'contour_right4',
	#'contour_right3','contour_right2',
	#'contour_right1',
	'right_eyebrow_right_corner',
	'right_eyebrow_upper_right_quarter',
	'right_eyebrow_upper_middle', 
	'right_eyebrow_upper_left_quarter',
	#'right_eyebrow_left_corner', 
]

contour_name_list2 = [
	#'left_eyebrow_right_corner',
	'left_eyebrow_upper_right_quarter',
	'left_eyebrow_upper_middle', 
	'left_eyebrow_upper_left_quarter',
	'left_eyebrow_left_corner', 
	'mouth_left_corner',
	'mouth_lower_lip_left_contour2',
	'mouth_lower_lip_left_contour3',
	'mouth_lower_lip_right_contour3',
	'mouth_lower_lip_right_contour2',
	'mouth_right_corner',	
	'right_eyebrow_right_corner',
	'right_eyebrow_upper_right_quarter',
	'right_eyebrow_upper_middle', 
	'right_eyebrow_upper_left_quarter',
	#'right_eyebrow_left_corner', 
]

# please don't copy this
API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)


def extract_face(face_id, img_width, img_height, face_name):
	landmark = api.detection.landmark(face_id=face_id, type='83p')
	
	#center point to expend the contour
	nose_x = landmark['result'][0]['landmark']['nose_tip']['x']
	nose_y = landmark['result'][0]['landmark']['nose_tip']['y']
	nose_x = nose_x / 100 * img_width
	nose_y = nose_y / 100 * img_height

	contour = []
	contour_point_name = []
	for v in contour_name_list2:
    		x = landmark['result'][0]['landmark'][v]['x']
    		y = landmark['result'][0]['landmark'][v]['y']
    		x = x / 100 * img_width
    		y = y / 100 * img_height
    		if 'mouth' in v:
	    		dx = (x-nose_x) * 1.2
	    		dy = (y-nose_y) * 1.2
	    		#print '%s: %5.2f %5.2f' % (v, x-nose_x, y-nose_y)
	    		x = dx + nose_x 
	    		y = dy + nose_y
    		contour.append([x, y])
	contour = np.array(contour, dtype=np.int32)
	extract_face = cv2.imread(face_name, 0)
	#print extract_face.shape
	for x in xrange(img_width):
		for y in xrange(img_height):
			if cv2.pointPolygonTest(contour,(x,y),False) < 0:
				#print x, y
				extract_face[y][x][0] = 0
				extract_face[y][x][1] = 0
				extract_face[y][x][2] = 0
	return extract_face

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "usage: %s <image>" % sys.argv[0]
        exit(1)

    img_name = sys.argv[1]
    im = cv2.imread(sys.argv[1])

    rst = api.detection.detect(img = File(img_name), attribute='pose')
    img_width = rst['img_width']
    img_height = rst['img_height']
    for face in rst['face']:
    	face_id = face['face_id']
    	print "fetching landmark info.."
    	landmark = api.detection.landmark(face_id=face_id, type='83p')
    	print "done"
    	
    	#test contour
    	nose_x = landmark['result'][0]['landmark']['nose_tip']['x']
    	nose_y = landmark['result'][0]['landmark']['nose_tip']['y']
    	nose_x = nose_x / 100 * img_width
    	nose_y = nose_y / 100 * img_height

    	contour = []
    	contour_point_name = []
    	for v in contour_name_list2:
    		x = landmark['result'][0]['landmark'][v]['x']
    		y = landmark['result'][0]['landmark'][v]['y']
    		x = x / 100 * img_width
    		y = y / 100 * img_height
    		if 'mouth' in v:
	    		dx = (x-nose_x) * 1.2
	    		dy = (y-nose_y) * 1.2
	    		#print '%s: %5.2f %5.2f' % (v, x-nose_x, y-nose_y)
	    		x = dx + nose_x 
	    		y = dy + nose_y
    		contour.append([x, y])

    	contour = np.array(contour, dtype=np.int32)
    
    	extract_face = cv2.imread(sys.argv[1])
    	#print extract_face.shape
    	for x in xrange(img_width):
    		for y in xrange(img_height):
    			if cv2.pointPolygonTest(contour,(x,y),False) < 0:
    				#print x, y
    				extract_face[y][x][0] = 0
    				extract_face[y][x][1] = 0
    				extract_face[y][x][2] = 0
    	cv2.imshow('extract face', extract_face)

    	cv2.drawContours(im, [contour], 0, (0,255,0), 1)
    	cv2.imshow('contour', im)
    	cv2.moveWindow('contour', 600, 0)
    	cv2.waitKey(0)
