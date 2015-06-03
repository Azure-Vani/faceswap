
import sys
from scipy import misc
import matplotlib.pyplot as plt

from faceinfo import FaceInfo, FaceLandmark, FacePoint, FacePose
from faceposebin import FacePoseBin
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


class FaceProc:
	def __init__(self, pose_bin):
		self.pose_bin = pose_bin

	def proc_face(self, face, img_width, img_height, img_name):
		print 'proc_face: face id', face['face_id']
		face_id = face['face_id']
		landmark = api.detection.landmark(face_id = face_id, type='25p')
		# crop the image
		center = face['position']['center']
		w = face['position']['width'] / 100 * img_width
		h = face['position']['height'] / 100 * img_height
		# scale a little bit
		w *= 1.5
		h *= 1.5 
		img = plt.imread(img_name)
		x = center['x'] * img_width / 100
		y = center['y'] * img_height / 100
		(x0, x1) = (x-w/2, x+w/2)
		(y0, y1) = (y-h/2, y+h/2)
		face_img = img[y0:y1, x0:x1]
		if face_img.shape[0] == 0 or face_img.shape[1] == 0:
			print "Image broken..."
			return 
	 	#plt.imshow(face_img)
		#plt.show()
		# plt.imsave(face_id+'.png', face_img)
		
		# select corresponding pose bin
		pose = face['attribute']['pose']
		face_pose = FacePose(pose)
		
		# get alignment data
		face_landmark = FaceLandmark(landmark['result'][0]['landmark'], img_width, img_height)
		face_landmark.transform(x0, y0)
		self.pose_bin.save(face_img, face_id, face_pose, face_landmark)

	def proc_image(self, img_name):
		print 'proc_image: image file', img_name
		rst = api.detection.detect(img = File(img_name), attribute='pose')
		for face in rst['face']:
			self.proc_face(face, rst['img_width'], rst['img_height'], img_name)
		print 'proc_image: done'

if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print 'Usage: %s <image name> <pose bin>' % sys.argv[0]
		exit(1)
	img_name = sys.argv[1]
	pose_bin = FacePoseBin(sys.argv[2])

	face_proc = FaceProc(pose_bin)
	face_proc.proc_image(img_name)
	