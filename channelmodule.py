from botmodule import BotModule, CmdException
from permissionmodule import permission_required

class ChannelModule(BotModule):
	def __init__(self, bot, channels):
		super().__init__(bot)
		self.channels = channels

	def handle_msg_001(self, conn, msg):
		for channel in self.channels.get(conn.network, []):
			conn.msg_join(channel)

	@permission_required('admin.channel.join')
	def handle_cmd_join(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) < 1:
			raise CmdException('.join #channel [password]')

		conn.msg_join(params[0], params.get[1] if len(params) >= 2 else '')

	@permission_required('admin.channel.part')
	def handle_cmd_part(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.part #channel')

		conn.msg_part(params[0])