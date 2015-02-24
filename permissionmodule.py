import yaml
from botmodule import BotModule, CmdException
from hashlib import sha256

def permission_required(permission):
	def permission_required_decorator(func):
		def permission_required_wrapper(self, **kwargs):
			user = kwargs['sender']

			perm_serv = self.bot.get_service('permission')

			if perm_serv.has_permission(user, permission):
				func(self, **kwargs)
			else:
				raise CmdException('Permission ' + permission + ' is required')

		return permission_required_wrapper
	return permission_required_decorator

class PermissionModule(BotModule):
	def __init__(self, bot):
		super().__init__(bot)
		bot.register_service('permission', self)

		self.auths = {}
		try:
			f = open('users.yaml')
		except FileNotFoundError:
			self.users = {}
		else:
			self.users = yaml.load(f)
			f.close()

		try:
			f = open('groups.yaml')
		except FileNotFoundError:
			self.groups = {}
		else:
			self.groups = yaml.load(f)
			f.close()

	def save(self):
		f = open('users.yaml', 'w')
		yaml.dump(self.users, f)
		f.close()

		f = open('groups.yaml', 'w')
		yaml.dump(self.groups, f)
		f.close()

	def hash_password(self, password):
		return sha256(password.encode('utf-8')).hexdigest()

	def handle_cmd_login(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.login username password')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		passhash = self.hash_password(params[1])

		if passhash == user['password']:
			self.auths[kwargs['sender']['data'].lower()] = params[0]
			conn.msg_privmsg(kwargs['respond'], 'Done')
		else:
			conn.msg_privmsg(kwargs['respond'], 'Wrong password')

	def handle_cmd_logout(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 0:
			raise CmdException('.logout')

		user = self.get_auth(kwargs['sender'])

		if user == None:
			raise CmdException('Not logged in')

		self.auths.pop(kwargs['sender']['data'].lower())
		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('permission.changepassword')
	def handle_cmd_changepassword(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.changepassword newpassword')

		user = self.get_auth(kwargs['sender'])
		user = self.users.get(user, None)

		if user == None:
			raise CmdException('Not logged in')

		passhash = self.hash_password(params[0])
		user['password'] = passhash
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.setpassword')
	def handle_cmd_setpassword(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.setpassword user password')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		passhash = self.hash_password(params[1])
		user['password'] = passhash
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.setgroup')
	def handle_cmd_setgroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.setgroup user group')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		user['group'] = params[1]
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.createuser')
	def handle_cmd_createuser(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.createuser user')

		if params[0] in self.users:
			raise CmdException('User already exists')

		self.users[params[0]] = {
			'granted': set(),
			'banned': set(),
			'password': None,
			'group': None,
			'hosts': set()
		}
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.grant.user')
	def handle_cmd_grantuser(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.grantuser user permission')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		user['granted'].add(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.ungrant.user')
	def handle_cmd_ungrantuser(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.ungrantuser user permission')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")
		
		user['granted'].remove(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.ban.user')
	def handle_cmd_banuser(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.banuser user permission')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		user['banned'].add(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.unban.user')
	def handle_cmd_unbanuser(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.unbanuser user permission')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")
		
		user['banned'].remove(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.list.user')
	def handle_cmd_listuserperms(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.listuserperms user')

		try:
			user = self.users[params[0]]
		except KeyError:
			raise CmdException("User doesn't exist")

		granted = ', '.join(user['granted'])
		banned  = ', '.join(user['banned'])
		
		conn.msg_privmsg(kwargs['respond'], 'User permissions: {}'.format(granted))
		conn.msg_privmsg(kwargs['respond'], 'Banned commands: {}'.format(banned))

	@permission_required('admin.permission.setparent')
	def handle_cmd_setparent(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.setparent group parent')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")

		group['parent'] = params[1]
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.create.group')
	def handle_cmd_creategroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.creategroup group')

		if params[0] in self.groups:
			raise CmdException('Group already exists')

		self.groups[params[0]] = {
			'granted': set(),
			'banned': set(),
			'parent': None,
		}
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.grant.group')
	def handle_cmd_grantgroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.grantgroup group permission')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")

		group['granted'].add(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.ungrant.group')
	def handle_cmd_ungrantgroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.ungrantgroup group permission')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")
		
		group['granted'].remove(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.ban.group')
	def handle_cmd_bangroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.bangroup group permission')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")

		group['banned'].add(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.unban.group')
	def handle_cmd_unbangroup(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 2:
			raise CmdException('.unbangroup group permission')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")
		
		group['banned'].remove(params[1])
		self.save()

		conn.msg_privmsg(kwargs['respond'], 'Done')

	@permission_required('admin.permission.list.group')
	def handle_cmd_listgroupperms(self, conn, **kwargs):
		params = kwargs['params']

		if len(params) != 1:
			raise CmdException('.listgroupperms group')

		try:
			group = self.groups[params[0]]
		except KeyError:
			raise CmdException("Group doesn't exist")

		granted = ', '.join(group['granted'])
		banned  = ', '.join(group['banned'])
		
		conn.msg_privmsg(kwargs['respond'], 'Group permissions: {}'.format(granted))
		conn.msg_privmsg(kwargs['respond'], 'Banned commands: {}'.format(banned))

	def get_auth(self, user):
		return self.auths.get(user['data'].lower(), None)

	def permission_matches(self, permission, rule):
		perm_parts = permission.split('.')
		rule_parts = rule.split('.')

		for i, rule_part in enumerate(rule_parts):
			if rule_part != '*':
				if len(perm_parts) <= i or perm_parts[i] != rule_part:
					return False

		return True

	def entity_perm_status(self, entity, permission):
		for grant in entity.get('banned', []):
			if self.permission_matches(permission, grant):
				return 'banned'

		for grant in entity.get('granted', []):
			if self.permission_matches(permission, grant):
				return 'granted'

		return None

	def has_group_permission(self, name, permission):
		if name == None:
			name = 'default'

		group = self.groups.get(name, None)

		if group == None:
			return False

		status = self.entity_perm_status(group, permission)

		if status == 'granted':
			return True
		elif status == 'banned':
			return False
		else:
			parent = group.get('parent', None)

			if parent == None:
				return False

			return self.has_group_permission(parent, permission)

	def has_user_permission(self, username, permission):
		user = self.users.get(username, None)

		if user == None:
			return self.has_group_permission(None, permission)

		status = self.entity_perm_status(user, permission)

		if status == 'granted':
			return True
		elif status == 'banned':
			return False
		else:
			return self.has_group_permission(user.get('group', None), permission)


	def has_permission(self, user, permission):
		auth = self.get_auth(user)
		return self.has_user_permission(auth, permission)