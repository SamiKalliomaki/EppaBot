import re
import socket
from bs4 import BeautifulSoup
from html.parser import HTMLParseError
from http.client import HTTPException
from urllib import request
from botmodule import BotModule


class TitleModule(BotModule):
	def handle_privmsg(self, conn, sender, target, msg, respond):
		super().handle_privmsg(conn, sender, target, msg, respond)

		match = re.search(r'https?://[\w\=\-\.\_\~\:\/\?\#]*', msg)

		if match != None:
			try:
				soup = BeautifulSoup(request.urlopen(match.group(0), None, 1))
			except (request.URLError, HTMLParseError, HTTPException, socket.timeout):
				pass
			else:
				if soup.title != None:
					conn.msg_privmsg(respond, 'Title: {}'.format(soup.title.string))