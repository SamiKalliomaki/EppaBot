import re
import json
import datetime
import humanize
from bs4 import BeautifulSoup
from urllib import request
from botmodule import BotModule
from permissionmodule import permission_required


class CodeForcesModule(BotModule):
	@permission_required('codeforces.nextcf')
	def handle_cmd_nextcf(self, conn, **kwargs):
		try:
			data = json.loads(request.urlopen('http://codeforces.com/api/contest.list', None, 1).read().decode('utf-8'))
		except (request.URLError, HTMLParseError, HTTPException, socket.timeout, socket.error, ValueError):
			conn.msg_privmsg(kwargs['respond'], 'Fetching data from API failed')
			return

		if data['status'] != 'OK':
			conn.msg_privmsg(kwargs['respond'], 'API call failed')
			return

		min_delta = 999999
		name = ''

		for res in data.get('result', []):
			delta = res.get('relativeTimeSeconds', 1) * -1

			if delta > 0 and delta <= min_delta:
				res_name = res.get('name', 'Unknown')

				if delta == min_delta:
					name += ' & ' + res_name
				else:
					name = res_name

				min_delta = delta

		if name != '':
			time = humanize.naturaltime(datetime.datetime.now() + datetime.timedelta(seconds=min_delta))
			conn.msg_privmsg(kwargs['respond'], humanize.naturaltime(time) + ': ' + name)
		else:
			conn.msg_privmsg(kwargs['respond'], 'Not scheduled')