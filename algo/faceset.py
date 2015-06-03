
import os
import sys
from faceproc import FaceProc
from faceposebin import FacePoseBin

def traverse(faceset_root, face_proc):
	for root, dirs, files in os.walk(faceset_root):
		for img_file in files:
			img_file, img_ext = os.path.splitext(img_file)
			if img_ext in ['.jpg', '.png']:
				# then its a image file
				img_path = root+'/'+img_file+img_ext
				print img_path
				face_proc.proc_image(img_path)

if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print "Usage: %s <dirname> <posebin>" % sys.argv[0]
		exit(1)

	pose_bin = FacePoseBin(sys.argv[2])
	# in this faceset program, the posebin should always be initialized
	# which means, cleared.
	pose_bin.init()

	face_proc = FaceProc(pose_bin)
	traverse(sys.argv[1], face_proc)