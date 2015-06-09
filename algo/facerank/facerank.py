
# I think here I should support the database access
# ok not anymore
# here I should just use the simple data file, which could be ranked

# this function will simply take 2 parameters, first is the posebin
# and then the image

import sys
import os

if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print "usage: %s <image> <posebin_path>" % sys.argv[0]
		exit(1)
	