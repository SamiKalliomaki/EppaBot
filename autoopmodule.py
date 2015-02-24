from botmodule import BotModule, CmdException

class AutoOPModule(BotModule):
	def is_autoop(self, user, channel):
		perm = self.bot.get_service('permission')
		return perm.has_permission(user, 'op.' + channel)

	def is_autovoice(self, user, channel):
		perm = self.bot.get_service('permission')
		return perm.has_permission(user, 'voice.' + channel)

	def handle_msg_join(self, conn, msg):
		user = msg['prefix']
		channel = msg['params'][0]

		if self.is_autoop(user, channel):
			conn.msg_chan_mode(channel, '+o', user['nick'])
		if self.is_autovoice(user, channel):
			conn.msg_chan_mode(channel, '+v', user['nick'])

	def handle_cmd_opme(self, conn, **kwargs):
		if self.is_autoop(kwargs['sender'], kwargs['target']):
			conn.msg_chan_mode(kwargs['target'], '+o', kwargs['sender']['nick'])
		else:
			conn.msg_privmsg(kwargs['respond'], 'Access denied')

	def handle_cmd_voiceme(self, conn, **kwargs):
		if self.is_autovoice(kwargs['sender'], kwargs['target']):
			conn.msg_chan_mode(kwargs['target'], '+v', kwargs['sender']['nick'])
		else:
			conn.msg_privmsg(kwargs['respond'], 'Access denied')