#!/usr/bin/env python

import flask
import os
import socket
import threading
import time

app = flask.Flask(__name__)

def get_minecraft_server_info(host, port=25565):
	s = socket.socket()
	s.settimeout(5)
	try:
		s.connect((host, port))
		s.send('\xfe\x01')
		d = s.recv(1024)
		s.close()
		# check we've got a 0xFF Disconnect
		assert d[0] == '\xff'
		# remove the packet ident (0xFF) and the short containing the length of the string
		# decode UCS-2 string
		d = d[3:].decode('utf-16be')
		# check the first 3 characters of the string are what we expect
		assert d[:3] == u'\xa7\x31\x00'
		# split
		info = d[3:].split('\x00')

		return {'protocol_version': int(info[0]), 'server_version': info[1], 'motd': info[2], 'current_players': int(info[3]), 'max_players': int(info[4])}
	except Exception, e:
		s.close()
		return None

def update_info():
	while True:
		# minecraft
		minecraft_servers = [('Survival', 'survival')] # (name, hostname)
		new_info = []

		for server in minecraft_servers:
			info = get_minecraft_server_info(server[1])
			if info is not None:
				new_info.append((server[0], server[1], info))
			else:
				new_info.append((server[0], server[1]))

		global minecraft_info
		minecraft_info = new_info

		# downloads
		new_files = []
		try:
			for file in os.listdir('/srv/downloads'):
				new_files.append(file)
		except OSError as e:
			pass
		global files
		files = new_files

		time.sleep(10)

@app.route('/')
def index():
	return flask.render_template('index.html', files=files, minecraft_info=minecraft_info)

files = []
minecraft_info = []
thread = threading.Thread(target=update_info)
thread.daemon = True
thread.start()

port = int(os.environ.get('PORT', 5000))
if os.environ.get('PRODUCTION') != "true": app.debug = True

app.run(host='0.0.0.0')