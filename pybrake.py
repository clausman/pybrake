#!/usr/bin/python
"""
Python binding for HandBrakeCLI
"""

__author__ = "jclausman"
__since__ = "Jan 3, 2014"

import argparse
import os
import subprocess as proc
import json

class BinaryNotFoundError(Exception):
	""" Error for when a binary cannot be located """

def to_cli_args(obj, use_flags=True):
	args = []
	dicts = []
	if isinstance(obj, dict):
		dicts.append(obj) 
	if hasattr(obj, '_kwarg_names'):
		dicts.append(obj._kwarg_names)
	if hasattr(obj, '__dict__'):
		dicts.append(obj.__dict__)
	for adict in dicts:
		for k in adict:
			v = adict[k]
			if v:
				if not k.startswith("-"):
					k = "--"+k
				args.append(str(k))
				#map(str, list_of_ints)
				if not isinstance(v,bool) or not use_flags:
					# [1,2,3,4,...] -> 1,2,3,4,...
					if isinstance(v,list):
						v = s_join(v)
					args.append(str(v))
	return args

def find_binary(searchpath):
	for path in searchpath:
		location = os.path.join(path, 'HandBrakeCLI')
		if os.path.exists(location):
	  		break
	else:
		raise BinaryNotFoundError('HandBrakeCLI binary not found in search path: '+" ".join(searchpath))
	return location

def call_shell(args):
	#TODO Advanced error handling, logging, 
	print "Calling: ", s_join(args, " ")
	proc.check_call(args)

def s_join(items, delim=","):
	return delim.join(map(str, items))


class PyBrake(object):
	__PATH__ = ["/usr/bin","/usr/sbin","/usr/local/bin"]

	def convert(self, options={}):
		# In and out options
		option_args = to_cli_args(options)
		self._call(option_args)
		

	def _call(self, args):
		"""
		class the HandBrakeCLI binary
		args - list of arguments to pass to cli
		"""
		if not hasattr(self, '__binary'):
			self.__binary = find_binary(self.__PATH__)
		call_shell([self.__binary] + args)

def main():
	brake = PyBrake()
	parser = argparse.ArgumentParser()
	parser.add_argument("input", help="input file/device")
	parser.add_argument("output", help="output file")
	parser.add_argument("-Z", "--preset", help="Use built-in preset")
	parser.add_argument("-c", "--config", help="config file to use for settings")

	args = parser.parse_args()
	options = args
	if args.config:
		options = json.load(open(args.config))
		options["input"] = args.input
		options["output"] = args.output

	brake.convert(options)


if __name__ == "__main__":
	main()