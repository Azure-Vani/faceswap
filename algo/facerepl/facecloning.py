
import os
import sys
import cv2
import numpy as np
import contour
from facepp import API, File, APIError

API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

feature_list = [
	'left_eye_center',
	'right_eye_center',
	'contour_chin',
]
def get_feature_points(face, w, h, dw, dh):
    landmark = api.detection.landmark(face_id=face['face_id'], type='83p')
    result = []
    for v in feature_list:
        print v
        x = landmark['result'][0]['landmark'][v]['x'] * w / 100
        y = landmark['result'][0]['landmark'][v]['y'] * h / 100
        print x,y
        x += dw
        y += dh
        result.append([x,y])
        #print result
    return result

def faceclone(src_name, dst_name):
    src_img = cv2.imread(src_name)
    dst_img = cv2.imread(dst_name)

    src_rst = api.detection.detect(img = File(src_name), attribute='pose')
    src_img_width   = src_rst['img_width']
    src_img_height  = src_rst['img_height']
    src_face        = src_rst['face'][0]

    dst_rst = api.detection.detect(img = File(dst_name), attribute='pose')
    dst_img_width   = dst_rst['img_width']
    dst_img_height  = dst_rst['img_height']
    dst_face        = dst_rst['face'][0]

       # here we will change our coordinate system
    # by moving the left top point
    dw = 100
    dh = 100
   
    nsrc_img = copy_image(src_img, dw, dh)
    ndst_img = copy_image(dst_img, dw, dh)
    ss = np.array(get_feature_points(src_face, src_img_width, src_img_height, dw, dh), dtype=np.float32)
    ps = np.array(get_feature_points(dst_face, dst_img_width, dst_img_height, dw, dh), dtype=np.float32)

    map_matrix = cv2.getAffineTransform(ps, ss)

    nsrc_img_width = src_img_width + dw * 2
    nsrc_img_height = src_img_height + dh * 2
    map_result = cv2.warpAffine(ndst_img, map_matrix, dsize=(nsrc_img_width,nsrc_img_height))
    
    extract_mask, center = contour.extract_face_mask(src_face['face_id'], src_img_width, src_img_height, src_name)
    next_mask = copy_image(extract_mask, dw, dh)
   
    center = (map_result.shape[0]/2, map_result.shape[1]/2)
    map_result = cv2.seamlessClone(nsrc_img, map_result, next_mask, center, flags=cv2.NORMAL_CLONE)

    imap_matrix = cv2.invertAffineTransform(map_matrix)
    final = cv2.warpAffine(map_result, imap_matrix, dsize=(ndst_img.shape[0:2]))

    new_final = copy_back_image(final, dw, dh)

    return new_final

def copy_image(image, dw, dh):
    img_height, img_width = (image.shape[0], image.shape[1])
    print "copying image with height %d width %d ..." % (img_height, img_width)
    new_img = np.zeros((img_height+dh*2, img_width+dw*2, 3), np.uint8)
    for x in xrange(img_width):
        for y in xrange(img_height):
            new_img[dh+y][dw+x] = image[y][x]
    
    #cv2.imshow('newimage', new_img)
    #cv2.waitKey(0)
    return new_img
    #new_src_img = np.zeros((src_img_height, src_img_width, 3), np.uint8)
def copy_back_image(image, dw, dh):
    img_height, img_width = (image.shape[0], image.shape[1])
    print "copying back image with height %d width %d ..." % (img_height, img_width)
    new_img = np.zeros((img_height-dh*2, img_width-dw*2, 3), np.uint8)
    new_height = img_height-dh*2
    new_width = img_width-dw*2
    for x in xrange(new_width):
        for y in xrange(new_height):
            new_img[y][x] = image[dh+y][dw+x]
    return new_img

def crop_face(src_name):
    src_rst = api.detection.detect(img = File(src_name), attribute='pose')
    src_img_width   = src_rst['img_width']
    src_img_height  = src_rst['img_height']
    src_face        = src_rst['face'][0]

    center = src_face['position']['center']
    img = cv2.imread(src_name)
    print img.shape
    x = center['x'] * src_img_width / 100
    y = center['y'] * src_img_height / 100
    w = 150
    h = 150
    (x0, x1) = (x-w/2, x+w/2)
    (y0, y1) = (y-h/2, y+h/2)
    face_img = img[y0:y1, x0:x1, :]
    print face_img.shape
    return face_img

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "usage: %s <image src> <image dst>" % sys.argv[0]
        exit(1)
    # we assume that these a images are in the same pose bin
    src_name = sys.argv[1]
    dst_name = sys.argv[2]
    src_img = cv2.imread(sys.argv[1])
    dst_img = cv2.imread(sys.argv[2])

    src_rst = api.detection.detect(img = File(src_name), attribute='pose')
    src_img_width 	= src_rst['img_width']
    src_img_height 	= src_rst['img_height']
    src_face 		= src_rst['face'][0]

    dst_rst = api.detection.detect(img = File(dst_name), attribute='pose')
    dst_img_width 	= dst_rst['img_width']
    dst_img_height 	= dst_rst['img_height']
    dst_face 		= dst_rst['face'][0]

    # here we will change our coordinate system
    # by moving the left top point
    dw = 100
    dh = 100
   
    nsrc_img = copy_image(src_img, dw, dh)
    ndst_img = copy_image(dst_img, dw, dh)
    cv2.imshow('nsrc', nsrc_img)
    cv2.imshow('ndst', ndst_img)
    #cv2.waitKey(0)
    # there's only one face in this case
    ss = np.array(get_feature_points(src_face, src_img_width, src_img_height, dw, dh), dtype=np.float32)
    ps = np.array(get_feature_points(dst_face, dst_img_width, dst_img_height, dw, dh), dtype=np.float32)

    print ss
    print ps
    #ss = []
    map_matrix = cv2.getAffineTransform(ps, ss)
    print map_matrix

    #dsize = (300,300)
    nsrc_img_width = src_img_width + dw * 2
    nsrc_img_height = src_img_height + dh * 2
    ndst_img_width = dst_img_width + dw * 2
    ndst_img_height = dst_img_height + dh * 2
    print "height=%d width=%d" % (nsrc_img_height, nsrc_img_width)
    map_result = cv2.warpAffine(ndst_img, map_matrix, dsize=(nsrc_img_width,nsrc_img_height))
    
    extract_mask, center = contour.extract_face_mask(src_face['face_id'], src_img_width, src_img_height, src_name)
    next_mask = copy_image(extract_mask, dw, dh)
    #cv2.imshow('contour', extract_mask)
    # merge 
    #cv2.imshow('src', src_img)

    ## first blending the border
    #extract_alpha = contour.extract_face_alpha(src_face['face_id'], src_img_width, src_img_height, src_name)
    #cv2.imshow('contour', extract_alpha)
   
    center = (map_result.shape[0]/2, map_result.shape[1]/2)
    map_result = cv2.seamlessClone(nsrc_img, map_result, next_mask, center, flags=cv2.NORMAL_CLONE)

    #cv2.imshow('merge', map_result)

    imap_matrix = cv2.invertAffineTransform(map_matrix)
    print map_result.shape
    print imap_matrix
    final = cv2.warpAffine(map_result, imap_matrix, dsize=(ndst_img_width, ndst_img_height))
    cv2.imshow('final', final);
    
    tmp_final_name = "tmp_final_%s.png" % dst_name
    cv2.imwrite(tmp_final_name, final)
    #new_final = crop_face(tmp_final_name)
    new_final = copy_back_image(final, dw, dh)

    cv2.imshow('final.png', new_final)
    cv2.imwrite(src_name+dst_name+'final.png', new_final)

    cv2.waitKey(0)
