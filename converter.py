"""
Helpers for converting files using handbrake
Main method supports either running as a service or as single pass
"""

import argparse
from queue import Queue, FileAction
import pybrake
import shutil
import os

def convert(src, dest):
	# Ensure dest directory exists
	print "Creating blueray from", src, "to", dest
	print "Making directory for", dest
	os.makedirs(os.path.dirname(dest))
	pybrake.convert(src,dest,"config/pybrake/blueray.json")	

def complete(src, dest):
	print "Moving file from queue at", src, "to complete folder at", dest
	name = os.path.basename(src)
	shutil.move(src, os.path.join(dest, name))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("queue")
	parser.add_argument("complete")
	args = parser.parse_args()
	actions = [
		FileAction(
			r'(.*)/(\w+)-s(\d\d)e(\d\d)\.mkv$',
			r'\1/../tv/\2/Season_\3/\2-s\3e\4.mp4',
			convert,
			name="convert tv episode"
		),		
		FileAction(
			r'(.*/[^/]+.mkv)$',
			args.complete,
			complete,
			name="move completed"
		)	
	]

	q = Queue(args.queue, actions=actions)
	q.process()

class Foo():
	def __call__(self, src, dest):
		complete(src, dest)


if __name__ == "__main__":
	main()