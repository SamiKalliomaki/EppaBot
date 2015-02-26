import re
import socket
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from html.parser import HTMLParseError
from http.client import HTTPException
from urllib import request
from botmodule import BotModule

# Time before showing title for the same url
repeat_time_limit = timedelta(minutes=5)

class TitleModule(BotModule):
	def __init__(self, bot):
		super().__init__(bot)

		self.last_seen = {}

	def handle_privmsg(self, conn, sender, target, msg, respond):
		super().handle_privmsg(conn, sender, target, msg, respond)

		match = re.search(r'https?://[\w\=\-\.\_\~\:\/\?\#]*', msg)

		if match == None:
			return

		url = match.group(0)
		identifier = respond + '@' + conn.network

		if not identfier in self.last_seen:
			self.last_seen[identifier] = {}

		last_seen_this = self.last_seen[identifier].get(url, datetime.min)
		if datetime.now() - last_seen_this < repeat_time_limit:
			self.bot.log('Already seen this url, skipping')
			return

		self.last_seen[identifier][url] = datetime.now()

		try:
			soup = BeautifulSoup(request.urlopen(url, None, 1))
		except (request.URLError, HTMLParseError, HTTPException, socket.timeout, socket.error) as e:
			self.bot.log('Error fetching title: ' + str(e))
		else:
			if soup.title != None:
				conn.msg_privmsg(respond, 'Title: {}'.format(soup.title.string))