from ircbot import IRCBot
from channelmodule import ChannelModule
from permissionmodule import PermissionModule
from autoopmodule import AutoOPModule
from titlemodule import TitleModule
from calcmodule import CalcModule
from codeforcesmodule import CodeForcesModule
from adminmodule import AdminModule
from dynamicmoduleloadermodule import DynamicModuleLoaderModule

if __name__ == '__main__':
	bot = IRCBot('EppaBot', 'eppabot', 'EppaBot')
	bot.connect('IRCNet', 'rajaniemi.freenode.net', 6667)

	bot.install_module(ChannelModule, channels={
		'IRCNet': ['#eppabot']
	})
	bot.install_module(PermissionModule)
	bot.install_module(AutoOPModule)
	bot.install_module(TitleModule)
	bot.install_module(CalcModule)
	bot.install_module(CodeForcesModule)
	bot.install_module(AdminModule)
	bot.install_module(DynamicModuleLoaderModule)

	bot.run()