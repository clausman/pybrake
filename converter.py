"""
Helpers for converting files using handbrake
Main method supports either running as a service or as single pass
"""

import argparse
from queue import Queue, FileAction
import pybrake
import shutil
import os
import time

def convert(src, dest):
	# Ensure dest directory exists	
	print "Making directory for", dest
	dirname = os.path.dirname(dest)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	print "Converting from", src, "to", dest
	if not os.path.isfile(dest):
		pybrake.convert(src,dest,"config/pybrake/blueray.json")	
	else:
		print "ERROR:", dest, " already exists"

def complete(src, dest):
	print "Moving file from queue at", src, "to complete folder at", dest
	name = os.path.basename(src)
	shutil.move(src, os.path.join(dest, name))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("queue")
	parser.add_argument("complete")
	parser.add_argument("-s", "--service", action="store_true")
	parser.add_argument("-p", "--period", default=600, type=float)
	args = parser.parse_args()
	actions = [
		FileAction(
			r'(.*)/(\w+)[-_ ]s(\d\d)e(\d\d)\.mkv$',
			r'\1/../tv/\2/Season_\3/\2-s\3e\4.mp4',
			convert,
			name="convert tv episode"
			),
		FileAction(
			r'(.*)/([-\w ]+\(\d\d\d\d\))\.mkv$',
			r'\1/../movies/\2/\2.mp4',
			convert,
			name="convert movie"
			)
	]

	q = Queue(args.queue, actions=actions)
	q.process()

	if args.service:
		while(True):
                        print "sleeping for", args.period, "before checking again"
			time.sleep(args.period)
			q.process()


if __name__ == "__main__":
	main()
