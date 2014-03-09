"""
Processing queue for encoding tasks
Watches queue folder and processes any files it knows how to handle
"""

import argparse
import re
import os
import shutil
import sys

class UnsupportedActionError(Exception):
	""" Class for actions we aren't supported """
	MSG = "action was neither callable nor had a method do with two arguments"

class FileAction(object):
	def __init__(self, match_pattern, destination_pattern, action, name=None):
		self._matcher = re.compile(match_pattern, re.IGNORECASE)
		self._destination_pattern = destination_pattern
		self._action = action
		if name: 
			self._name = name
		else:
			self._name = match_pattern + " -> " + destination_pattern
	def _rewrite(self, filepath):
		if not self._matcher.search(filepath):
			return False
		return self._matcher.sub(self._destination_pattern, filepath)

	def apply(self, filepath):
		dest = self._rewrite(filepath)
		if not dest:
			return False
		try:
			self._action(filepath, dest)
		except AttributeError:
			print "action ", self._action, " was not callable with two arguments"
		except:
			#TODO handle errors gracefully
			print 'Unexpected error while executing action ', self._action, ":", sys.exc_info()[0]
			raise
		return True

	def __repr__(self):
		return self._name

class Queue(object):
	def __init__(self, folder, actions=[], complete="../complete"):
		self._folder = folder
		self._actions = actions
		self._complete = os.path.join(folder,complete)

	def process(self):
		files = list_files(self._folder)
		log("Processing", len(files), "files from", self._folder)
		log("Using actions ", self._actions)		
		actions_taken=0
		files_affected=0
		for file in files:
			log("Processing", file)
			some_action = False
			for action in self._actions:
				if action.apply(file):
					actions_taken += 1
					some_action = True
					log("Applied action", action)
			if some_action:
				files_affected += 1
				print "File", file, "was affected; moving to complete at", self._complete
				shutil.move(file, os.path.join(self._complete, os.path.basename(file)))
                        else:
                                print "File", file, "had not matching actions; leaving in place"

		print "Processing complete"
		print files_affected, "files affected"
		print actions_taken, "actions taken"		

def log(*kwargs):
	print " ".join(map(str, kwargs))

def list_files(dir):
	f = []
	for (dirpath, dirnames, filenames) in os.walk(dir):
		f.extend([ os.path.join(dirpath, fi) for fi in filenames])
	return f

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("queue", help="folder to use as queue")
	args = parser.parse_args()
	move = lambda src,dest: shutil.copy(src, dest)
	test_actions = [
		FileAction(
			r'(.*)\.mkv$',
			r'\1.mkv.bak',
			move
		)
	]

	q = Queue(args.queue, actions=test_actions)
	q.process()



if __name__ == "__main__":
	main()
