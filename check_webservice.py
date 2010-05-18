#!/usr/bin/env python

###################################################
# Author: Levy Carneiro Jr. <levy@levycarneiro.com>
# URL: levycarneiro.com
# Created: 2010/04/29
# Version: 0.0.1
###################################################

# TODO
# - better description of errors
# - chained calls (a webservice provide some info needed to test a second webservice)
# - http basic auth

###################################################
## Imports ########################################
###################################################

from getopt import getopt
from urllib2 import Request, urlopen, URLError, HTTPError
import os, re, socket, sys, urllib, urllib2

try:
	import yaml
except:
	sys.exit('The python lib YAML is not installed. Please install from http://pyyaml.org/wiki/PyYAMLDocumentation#Installation')

###################################################
## Functions ######################################
###################################################

def read_config(config_file):

	config_file = config_file.strip()

 	if config_file == '':
		sys.exit("Config file not specified.")

	if not os.path.exists(config_file):
		sys.exit('Config file does not exist.')

	file = open(config_file, "r")
	contents = file.read()

	config = {}
	try:
		config = yaml.load (contents)
	except:
		sys.exit('Parsing error in config file. Hint: replace TABs for spaces.')

	return config

def array_to_dict(arr):
	dict = {}
	for i in arr:
		for k, v in i.iteritems():
			dict[k] = v
	return dict

def send_request(server, path, verb, timeout, content={}, headers={}):

	# No need for keeping the connection alive.
	headers['Connection'] = 'Close'
	headers['User-Agent'] = 'Nagios Webservice Tester Plugin'

	url = 'http://' + server + ":" + str(port) + path
	if verbose: print "URL: " + url + "\n"

	if verb.upper() == 'POST':
		if isinstance(content, dict):
			content = urllib.urlencode(content)
		req = urllib2.Request (url, content, headers)
	else:
		req = urllib2.Request (url, None, headers)

	socket.setdefaulttimeout(timeout)

	resp = None
	data = {}
	try:
		resp = urllib2.urlopen (req)

		data['response_headers'] = resp.info()
		data['response_content'] = resp.read()

		resp.close()
	except URLError, e:
		if hasattr(e, 'reason'):
			print "CRIT: Failed to reach the server. Reason:", e.reason
			sys.exit (2)
		elif hasattr(e, 'code'):
			print "CRIT: Request failed. Code:", e.code
			sys.exit (2)

	return data

###################################################
## Beginning ######################################
###################################################

opts, args  = getopt(sys.argv[1:], "f:dv", ["file=", "verbose"])
config_file = ""
verbose     = False

for o,v in opts:
	if o in ("-f", "--file"):
		config_file = v
	if o == '-v':
		verbose = True

config = read_config (config_file)
if verbose: print "CONFIG:\n" + repr(config) + "\n"

ws       = config.get('webservice', {})
request  = ws.get('request', {})
response = ws.get('response', {})

server  = request.get('server', '')
path    = request.get('path', '')
port    = request.get('port', '')
verb    = request.get('verb', '')
content = request.get('content', '')
headers = request.get('headers', {})
headers = array_to_dict(headers)

timeout   = response.get('timeout', 5)
match     = response.get('match', [])
match_all = response.get('match_all', '')

if verb.upper() == 'POST' and len(content) == 0:
	sys.exit("You want a POST request, but provided no Content to post.")

# Send the actual request.
data = send_request(server, path, verb, timeout, content, headers)

request_headers  = data.get('request_headers', '')
response_headers = data.get('response_headers', '')
response_content = data.get('response_content', '')

if verbose:
	print "REQUEST HEADERS:\n" + repr(request_headers) + "\n"
	print "REQUEST CONTENT:\n" + repr(content) + "\n"
	print "RESPONSE HEADERS:\n"
	print response_headers
	print "\n"
	print "RESPONSE CONTENT:\n"
	print response_content
	print "\n"
	print "TESTING:\n"
	print "MATCH:\n" + repr(match) + "\n"

# Test if any or all of the matches are found in the response.
matches_found = 0
tests_failed = ""
for test in match:

	if verbose: print "Testing: " + test

	regex = re.compile(r''+test, re.MULTILINE)
	m = regex.search(response_content)

	if m != None:
		matches_found+=1
	else:

		if tests_failed == "":
			tests_failed += test
		else:
			tests_failed += " | " + test

		if verbose: print "Test failed: " + test

success = False
if match_all == True:
	if len(match) == matches_found:
		success = True
else:
	if matches_found > 0:
		success = True

# 0: OK
# 2: CRITICAL
if success:
	print "OK"
	sys.exit(0)
else:
	print "CRIT: the following tests have failed: " + tests_failed
	sys.exit(2)
