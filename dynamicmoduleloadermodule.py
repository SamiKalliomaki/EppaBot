import importlib
import imp
from botmodule import BotModule, CmdException
from permissionmodule import permission_required

class DynamicModuleLoaderModule(BotModule):
	@permission_required('admin.module.load')
	def handle_cmd_loadmodule(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.loadmodule module')

		name = params[0]

		try:
			module = importlib.import_module(name.lower())
			imp.reload(module)
		except ImportError as e:
			raise CmdException('Failed to load the module: ' + str(e))

		module_class = module.__dict__.get(name, None)

		if module_class == None:
			raise CmdException("Module doesn't have the class")

		for installed_module in self.bot.modules[:]:
			if installed_module.__class__.__name__ == name:
				self.bot.uninstall_module(installed_module)

		self.bot.install_module(module_class)