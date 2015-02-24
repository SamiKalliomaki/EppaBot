import time
from ircconnection import IRCConnection
from asynschedcore import asynschedcore

class IRCBot:
	def __init__(self, nick, username, realname):
		self.modules = []
		self.connections = []
		self.services = {}
		self.scheduler = asynschedcore()

		self.nick = nick
		self.username = username
		self.realname = realname

	def connect(self, network, server, port):
		self.connections.append(IRCConnection(self, network, server, port))

	def log(self, entry):
		print(entry)

	def handle_connect(self, conn):
		conn.msg_nick(self.nick)
		conn.msg_user(self.username, self.realname)

		for module in self.modules:
			module.handle_connect(conn)

	def handle_close(self, conn):
		self.connections.remove(conn)

	def handle_msg_ping(self, conn, msg):
		server2 = ''

		if len(msg['params']) >= 2:
			server2 = msg['params'][1]

		conn.msg_pong(self.nick, server2)

	def handle_msg(self, conn, msg):
		func = getattr(self, 'handle_msg_' + msg['command'].lower(), None)
		if func:
			func(conn, msg)

		for module in self.modules:
			module.handle_msg(conn, msg)

	def install_module(self, module_class, **kwargs):
		self.modules.append(module_class(self, **kwargs))

	def register_service(self, name, service):
		self.services[name] = service

	def get_service(self, name):
		return self.services[name]

	def run(self):
		try:
			self.scheduler.run()
		except KeyboardInterrupt:
			self.close()

	def close(self):
		for conn in self.connections:
			conn.msg_quit()

		for event in self.scheduler.queue:
			self.scheduler.cancel(event)

		self.scheduler.run()