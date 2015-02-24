from botmodule import BotModule
from permissionmodule import permission_required

class AdminModule(BotModule):
	@permission_required('admin.quit')
	def handle_cmd_quit(self, conn, **kwargs):
		self.bot.close()