class CmdException(Exception):
	pass

class BotModule:
	def __init__(self, bot):
		self.bot = bot

	def handle_connect(self, conn):
		pass

	def handle_privmsg(self, conn, sender, target, msg, respond):
		if len(msg) > 0 and msg[0] == '.':
			split = msg.split()
			cmd = split[0][1:]
			params = split[1:]

			func = getattr(self, 'handle_cmd_' + cmd.lower(), None)
			if func:
				try:
					func(conn=conn, sender=sender, target=target, params=params, respond=respond)
				except CmdException as e:
					conn.msg_privmsg(respond, str(e))

	def handle_msg_privmsg(self, conn, msg):
		if msg['params'][0].lower() == self.bot.nick.lower():
			respond = msg['prefix']['nick']
		else:
			respond = msg['params'][0]

		self.handle_privmsg(conn, msg['prefix'], msg['params'][0], msg['params'][1], respond)

	def handle_msg(self, conn, msg):
		func = getattr(self, 'handle_msg_' + msg['command'].lower(), None)
		if func:
			func(conn, msg)

