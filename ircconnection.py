import asyncore, socket, re
import time

queue_delay = 1

class ParseException(Exception):
	pass

class IRCConnection(asyncore.dispatcher):
	def __init__(self, bot, network, server, port):
		asyncore.dispatcher.__init__(self)

		self.bot = bot
		self.network = network
		self.server = server
		self.port = port

		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((server, port))

		self.input_buffer = b''
		self.output_buffer = b''
		self.msg_queue = []
		self.last_message = time.time()

		self.check_msg_queue(True)

	def parse_prefix(self, prefix_str):
		match = re.match(r'^(([^!]+)!([^@]+)@)?(.*)$', prefix_str)

		if match == None:
			raise ParseException("Regex didn't match prefix")

		return {
			'data': prefix_str,
			'nick': match.group(2),
			'username': match.group(3),
			'server': match.group(4)
		}

	def parse_params(self, params_str):
		split = params_str.split(':')

		output = split[0].split()
		if len(split) > 1:
			output.append(':'.join(split[1:]))

		return output

	def parse(self, line):
		if len(line) == 0:
			return None

		prefix = {}

		words = line.split()

		if len(words) < 2:
			raise ParseException('Line has to have two words')

		if words[0][0] == ':':
			prefix = self.parse_prefix(words[0][1:])
			words = words[1:]

		command = words[0]
		params = self.parse_params(' '.join(words[1:]))

		return {
			'data': line,
			'prefix': prefix,
			'command': command,
			'params': params
		}

	def escape(self, s):
		return re.sub(r'\s', '', s)

	def escape_trailing(self, s):
		return re.sub(r'[\r\n]', '', s)

	def write(self, line):
		self.bot.log('{} -> {}'.format(self.network, line))
		self.output_buffer += (line + '\r\n').encode('utf-8')

	def msg_nick(self, nick):
		nick = self.escape(nick)

		self.write('NICK {}'.format(nick))

	def msg_user(self, username, realname):
		username = self.escape(username)
		realname = self.escape_trailing(realname)

		self.write('USER {} 8 * :{}'.format(username, realname))

	def msg_quit(self):
		self.write('QUIT')

	def msg_join(self, channel, password=''):
		channel = self.escape(channel)
		password = self.escape(password)

		self.write('JOIN {} {}'.format(channel, password))


	def msg_part(self, channel):
		channel = self.escape(channel)

		self.write('PART {}'.format(channel))

	def msg_pong(self, server, server2):
		server = self.escape(server)
		server2 = self.escape(server2)

		self.write('PONG {} {}'.format(server, server2))

	def msg_privmsg(self, target, msg):
		target = self.escape(target)
		msg = self.escape_trailing(msg)
		# Limit message length
		msg = msg[:256]

		self.msg_queue.append('PRIVMSG {} :{}'.format(target, msg))
		self.check_msg_queue()

	def msg_chan_mode(self, channel, mode, params=''):
		channel = self.escape(channel)
		mode = self.escape(mode)
		params = self.escape(params)

		self.write('MODE {} {} {}'.format(channel, mode, params))

	def handle_connect(self):
		self.bot.log('Connected to {} ({}:{})'.format(self.network, self.server, self.port))
		self.bot.handle_connect(self)

	def handle_close(self):
		self.bot.log('Connection closed to {} ({}:{})'.format(self.network, self.server, self.port))
		self.close()

		self.bot.handle_close(self)

	def handle_read(self):
		self.input_buffer += self.recv(1024)

		split = self.input_buffer.split(b'\n')
		self.input_buffer = split[-1]

		for line in split[:-1]:
			try:
				line = line.decode('utf-8').rstrip('\r\n')
			except UnicodeDecodeError:
				print('Warning: Invalid utf-8 received')

			self.bot.log('{} <- {}'.format(self.network, line))
			try:
				msg = self.parse(line)
			except ParseException as e:
				self.bot.log('Parse exception: ' + str(e))
			else:
				self.bot.handle_msg(self, msg)

	def check_msg_queue(self, repeat=False):
		if repeat:
			self.bot.scheduler.enter(queue_delay + 0.01, 1, self.check_msg_queue, (True,))

		now = time.time()

		if now - self.last_message < 0:
			self.bot.log('Clock was adjusted, fixing')
			self.last_message = now

		if len(self.msg_queue) > 0 and now - self.last_message >= queue_delay:
			if len(self.msg_queue) > 10:
				self.msg_queue = self.msg_queue[-10:]

			self.last_message = now

			self.write(self.msg_queue[0])
			self.msg_queue = self.msg_queue[1:]


	def writable(self):
		return len(self.output_buffer) > 0

	def handle_write(self):
		sent = self.send(self.output_buffer)
		self.output_buffer = self.output_buffer[sent:]
