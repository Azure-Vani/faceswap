
import sys
from scipy import misc
import matplotlib.pyplot as plt
from facepp import API, File, APIError

# please don't copy this
API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)


from pprint import pformat
# copied from hello.py
def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')])


def proc_face(face, img_width, img_height, img_name):
	print 'proc_face: face id', face['face_id']
	face_id = face['face_id']
	landmark = api.detection.landmark(face_id = face_id, type='25p')
	# crop the image
	center = face['position']['center']
	w = face['position']['width'] / 100 * img_width
	h = face['position']['height'] / 100 * img_height
	
	img = plt.imread(img_name)
	x = center['x'] * img_width / 100
	y = center['y'] * img_height / 100
	(x0, x1) = (x-w/2, x+w/2)
	(y0, y1) = (y-h/2, y+h/2)
	face_img = img[y0:y1, x0:x1]
	# plt.imshow(face_img)
	# plt.show()
	# plt.imsave(face_id+'.png', face_img)
	# select corresponding pose bin
	pose = face['attribute']['pose']
	yaw = pose['yaw_angle']['value']
	pitch = pose['pitch_angle']['value']
	roll = pose['roll_angle']['value']

	# alignment 
	

def proc_image(img_name):
	print 'proc_image: image file', img_name
	rst = api.detection.detect(img = File(img_name), attribute='pose')
	for face in rst['face']:
		proc_face(face, rst['img_width'], rst['img_height'], img_name)
	print 'proc_image: done'

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		print 'Usage: %s [image name]' % sys.argv[0]
		exit(1)
	img_name = sys.argv[1]
	
	proc_image(img_name)
	