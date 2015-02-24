from botmodule import BotModule, CmdException
from permissionmodule import permission_required

class AdminModule(BotModule):
	@permission_required('admin.quit')
	def handle_cmd_quit(self, conn, **kwargs):
		self.bot.close()

	@permission_required('admin.nick')
	def handle_cmd_nick(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.nick newnick')

		self.bot.nick = params[0]
		for conn in self.bot.connections:
			conn.msg_nick(params[0])