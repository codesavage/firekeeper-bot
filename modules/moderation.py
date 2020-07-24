# Allows you to view or change the bot admins for a guild
global admins
async def admins(message, args):
	arguments = ['add', 'remove', 'set']

	def format(input):
		users = [i for i in input if i in [member.id for member in message.guild.members]]
		roles = [i for i in input if i in [role.id for role in message.guild.roles]]
		output = ''
		if users != []:
			output += '**Users**\n'
			for i in users:
				for member in message.guild.members:
					if member.id == i:
						output += '%s\n' % (member.mention)
		if roles != []:
			output += '**Roles**\n'
			for i in roles:
				for role in message.guild.roles:
					if role.id == i:
						output += '%s\n' % (role.mention)
		if output == '':
			output = 'There are no admins set for this guild.'
		return output

	def getAdmins():
		output = _getattrib(message.guild.id, 'server', 'admins')
		return output

	def setAdmins(admins):
		_setattrib(message.guild.id, 'server', 'admins', admins)

	# If the command is run with a valid argument
	if args[0] in arguments:
		# If the user wants to add admins to the existing set
		if args[0] == 'add':
			if message.mentions != [] or message.role_mentions != []:
				newAdmins = getAdmins()
				for i in message.mentions:
					if i.id not in newAdmins:
						newAdmins.append(i.id)
				for i in message.role_mentions:
					if i.id not in newAdmins:
						newAdmins.append(i.id)
				setAdmins(newAdmins)
				#output = getAdmins()
				await sendEmbed(message.channel, 'Admins', 'Admins have been added. The new admin list is as follows:\n%s' % (format(getAdmins())))
			else:
				await sendEmbed(message.channel, 'Admins', 'No new admins have been added. Please specify a valid guild member or role after the argument (e.g. `%sadmins remove @Code`).' % (prefix))
		# If the user wwants to remove admins from the existing set
		elif args[0] == 'remove':
			if message.mentions != [] or message.role_mentions != []:
				oldAdmins = getAdmins()
				newAdmins = getAdmins()
				for i in message.mentions:
					if i.id in newAdmins:
						newAdmins.remove(i.id)
				for i in message.role_mentions:
					if i.id in newAdmins:
						newAdmins.remove(i.id)
				if newAdmins != oldAdmins:
					setAdmins(newAdmins)
					output = 'Admins have been removed. The new admin list is as follows:\n%s' % (format(getAdmins()))
				else:
					output = 'No admins have been removed. Please specify a valid guild member or role after the argument (e.g. `%sadmins remove @Code`).' % (prefix)
				await sendEmbed(message.channel, 'Admins', output)
			else:
				await sendEmbed(message.channel, 'Admins', 'No admins have been removed. Please specify a valid guild member or role after the argument (e.g. `%sadmins remove @Code`).' % (prefix))
		# If the user wants to make a new set of admins
		elif args[0] == 'set':
			addList = []
			for i in message.mentions:
				addList.append(i.id)
			for i in message.role_mentions:
				addList.append(i.id)
			setAdmins(addList)
			if message.mentions != [] or message.role_mentions != []:
				await sendEmbed(message.channel, 'Admins', 'The following have been set as admins:\n%s' % (format(getAdmins())))
			else:
				await sendEmbed(message.channel, 'Admins', 'The admin list for the guild has been cleared.')
	# If the command is run without any valid arguments, it pulls the list of current admins
	else:
		await sendEmbed(message.channel, 'Admins', format(getAdmins()))


# Bans a user from a guild, makes a record of it, and deletes the banned user's messages from the last 7 days
global ban
async def ban(message, args):
	global guildTimers
	if args[0] == '' or args[1] == '':
		await sendEmbed(message.channel, None, 'Ban removes a user from the guild and prevents them from rejoining (based on IP). A reason for the ban is required and will be sent to the user via DM.\n*Syntax:* `%sban @Code Repeatedly ignoring moderator warnings.`' % prefix)
		return
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, 'Please mention a valid guild member and a reason for this ban (e.g. `%sban @Code Repeatedly ignoring moderator warnings`).' % prefix)
		return
	# Make sure the user isn't on the exempt list
	for i in mentionedUser.roles:
		if i.id in exemptRoles:
			await sendEmbed(message.channel, None, 'Sorry, I can\'t ban a %s!' % i.mention)
			return
	# Check if the user has any mute timers and remove them
	for i in guildTimers[message.guild.id]:
		if i['subjectid'] == mentionedUser.id and i['timertype'] == 'mute':
			guildTimers[message.guild.id].remove(i)
			_unsetguildtimer(message.guild.id, i['objectid'])
			if debugMode: await sendEmbed(message.channel, None, 'Unsetting timer with objectID %s' % i['objectid'])
	reason = args[1]
	_setlog(message.guild.id, message.author.id, mentionedUser.id, 'ban', reason)
	# DM user
	await sendEmbed(mentionedUser, None, 'You have been banned from Ruffleneck\'s Den.\n*"%s"*' % reason)
	# Ban user
	await mentionedUser.ban(delete_message_days = 0)
	await sendEmbed(message.channel, None, '%s has been banned!\n*"%s"*' % (mentionedUser.mention, reason))


# Deletes a certain number of messages in a channel, either from a specific user or from everyone
global delete
async def delete(message, args):
	queue = []
	count = 0
	users = message.mentions
	try:
		limit = int(args[0]) + 1
	except:
		await sendEmbed(message.channel, 'Delete', 'Please specify a number of messages to delete (e.g. `%sdelete 10`).' % (prefix))
		return
	if users == []:
		async for i in message.channel.history(limit=limit):
			queue.append(i)
	else:
		async for i in message.channel.history():
			if i.author in users:
				queue.append(i)
				count += 1
				if count == limit:
					break
	await message.channel.delete_messages(queue)


# Kicks a user from a guild and makes a record of it
global kick
async def kick(message, args):
	if args[0] == '' or args[1] == '':
		await sendEmbed(message.channel, None, 'Kick removes a user from the guild. A reason is required for the kick is required and will be sent to the user via DM.\n*Syntax:* `%skick @Code for refusing to follow guild rules.`' % prefix)
		return
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, 'Please mention a valid guild member and a reason for this kick (e.g. `%skick @Code for refusing to follow guild rules`).' % (prefix))
		return
	# Make sure the user isn't on the exempt list
	for i in mentionedUser.roles:
		if i.id in exemptRoles:
			await sendEmbed(message.channel, None, 'Sorry, I can\'t kick a %s!' % i.mention)
			return
	# Check if the user has any mute timers and remove them
	for i in guildTimers[message.guild.id]:
		if i['subjectid'] == mentionedUser.id and i['timertype'] == 'mute':
			guildTimers[message.guild.id].remove(i)
			_unsetguildtimer(message.guild.id, i['objectid'])
			if debugMode: await sendEmbed(message.channel, None, 'Unsetting timer with objectID %s' % i['objectid'])
	reason = args[1]
	_setlog(message.guild.id, message.author.id, mentionedUser.id, 'kick', reason)
	if reason[-1] != '.':
		reason += '.'
	# DM user
	await sendEmbed(mentionedUser, None, 'You have been kicked from Ruffleneck\'s Den.\n*"%s"*' % reason)
	# Kick user
	await mentionedUser.kick()
	await sendEmbed(message.channel, None, '%s has been kicked!\n*"%s"*' % (mentionedUser.mention, args[1]))


global logs
async def logs(message, args):
	if args[0] == '':
		await sendEmbed(message.channel, None, 'Logs displays the disciplinary logs for a user (from warns, kicks, and bans). You can also use an ID for a user if they are not longer in the guild.\n*Syntax:* `%slogs @Code`' % prefix)
		return
	try:
		mentionedUser = message.mentions[0].id
	except:
		mentionedUser = args[0]
	warnings = _getlog(message.guild.id, None, mentionedUser, 'warn')
	kicks = _getlog(message.guild.id, None, mentionedUser, 'kick')
	bans = _getlog(message.guild.id, None, mentionedUser, 'ban')
	unbans = _getlog(message.guild.id, None, mentionedUser, 'unban')
	fullLog = warnings + kicks + bans + unbans
	fullLog.sort(key = lambda k: k['log']['time'], reverse = True)
	#pprint.pprint(fullLog)
	mentionedUser = '<@%s>' % mentionedUser
	if fullLog != []:
		output = 'Disciplinary logs for %s:\n' % (mentionedUser)
		count = len(fullLog)
		for i in fullLog:
			if i in warnings:
				action = 'Warned'
			elif i in kicks:
				action = 'Kicked'
			elif i in bans:
				action = 'Banned'
			elif i in unbans:
				action = 'Unbanned'
			moderator = message.guild.get_member(i['log']['operatorid'])
			warnTime = i['log']['time']
			warnAge = datetime.datetime.now() - warnTime
			if i['log']['description'] != '':
				reason = i['log']['description']
			else:
				reason = 'No reason given.'
			output = output + '%s: %s by %s on %s (%s days ago): *%s*\n' % (str(count), action, moderator.mention, str(warnTime)[:11], str(warnAge.days), reason)
			count -= 1
	else:
		output = 'There are no logs for this user, or they are no longer in the guild (in that case, try their user ID instead).'
	await sendEmbed(message.channel, None, output)


# Lists available moderator commands and explains how to use them
global modhelp
async def modhelp(message, args):
	command = args[0]
	if command == '':
		embed = discord.Embed(title = 'Fire Keeper Moderator Help', color = embedColor)
		output = []
		output.append('\n')
		for i in sorted(modules['moderation']['commands'].keys()):
			try:
				text = modules['moderation']['commands'][i]['shortHelp']
			except:
				text = '*- no help found.*'
			output.append('`%s%s` %s' % (prefix, i, text))
		embed.add_field(name = '***%s***' % (modules['moderation']['friendlyName']), value = '\n'.join(output), inline = False)
		await message.channel.send(embed = embed)
	elif command in modules['moderation']['commands']:
		try:
			helpText = modules['moderation']['commands'][command]['helpText']
		except:
			helpText = '*- no help found.*'
		output = '`%s` %s' % (command, helpText)
		await sendEmbed(message.channel, 'Moderator help for %s command' % (command), output)
	else:
		output = command + ' is not a valid command. Try `%smodhelp` for a list of available moderation commands.' % (prefix)
		await sendEmbed(message.channel, 'Moderator help for unknown command %s' % (command), output)


# View or change module permissions for the guild
global module
async def module(message, args):
	arguments = ['allow', 'block', 'check']
	argument = args[0].lower()
	title = 'Modules'

	def getModules():
		moduleName = args[1].lower()
		if moduleName in modules or moduleName == 'all':
			if moduleName == 'all':
				moduleName = [i for i in modules]
			else:
				moduleName = [args[1].lower()]
		else:
			moduleName = 'fail'
		return moduleName

	def getChannels(message):
		channelName = args[2].lower()
		channelIDs = []
		if channelName == 'all' or channelName == '':
			channelIDs = [i.id for i in message.guild.channels]
		else:
			for i in message.channel_mentions:
				channelIDs.append(i.id)
		return channelIDs

	if argument in arguments:

		if argument == 'allow':
			moduleName = getModules()
			if moduleName != 'fail':
				channelIDs = getChannels(message)
				for i in moduleName: # Should take this out if I don't add support for allowing/blocking multiple modules at once
					_unsetmodulerestriction(i, message.guild.id, channelIDs)
					if args[1].lower() != 'all':
						output = 'The *%s* module has been allowed in the following channel(s):\n' % i
					else:
						output = 'All modules have been allowed in the following channels:\n'
					tmpList = []
					for channelID in channelIDs:
						channel = client.get_channel(channelID)
						if str(channel.type) == 'text':
							tmpList.append('%s %s' % (channel.name, channel.mention))
					tmpList.sort()
					tmpOut = [i.split()[1] for i in tmpList]
					output += '\n'.join(tmpOut)
			else:
				output = '*%s* is not a recognized module.' % (args[1])

		elif argument == 'block':
			moduleName = getModules()
			if moduleName != 'fail':
				channelIDs = getChannels(message)
				for i in moduleName: # Should take this out if I don't add support for allowing/blocking multiple modules at once
					_setmodulerestriction(i, message.guild.id, channelIDs)
					if args[1].lower() != 'all':
						output = 'The *%s* module has been blocked in the following channel(s):\n' % i
					else:
						output = 'All modules have been blocked in the following channels:\n'
					tmpList = []
					for channelID in channelIDs:
						channel = client.get_channel(channelID)
						if str(channel.type) == 'text':
							tmpList.append('%s %s' % (channel.name, channel.mention))
					tmpList.sort()
					tmpOut = [i.split()[1] for i in tmpList]
					output += '\n'.join(tmpOut)
			else:
				output = '*%s* is not a recognized module.' % (args[1])

		elif argument == 'check':
			moduleName = getModules()
			if moduleName != 'fail' and args[1].lower() != 'all':
				channelIDs = getChannels(message)
				output = []
				for channelID in channelIDs:
					# Look up permissions for the module in each text channel. Commands can't be issued in voice channels, so they don't matter.
					channel = client.get_channel(channelID)
					if str(channel.type) == 'text':
						restricted = _getmodulerestriction(args[1], message.guild.id, channelID)
						if restricted:
							status = 'Blocked'
						else:
							status = 'Allowed'
						# Using the channel name here, because trying to sort by mentions ends up sorting numerically by IDs
						output.append('%s %s - %s' % (channel.name, channel.mention, status))
				output.sort()
				output = [' '.join(i.split()[1:]) for i in output]
				output = '\n'.join(output)
				title = '%s Module Channel Permissions' % (args[1].capitalize())
			else:
				output = '*%s* is not a recognized module.' % (args[1])
	else:
		title = 'Available Modules'
		prettyModules = []
		for i in modules:
			prettyModules.append(i.capitalize())
		prettyModules.sort()
		output = '\n'.join(prettyModules)
	await sendEmbed(message.channel, title, output)


# Prevents a user from being able to send messages for a certain amount of time
global mute
async def mute(message, args):
	global guildTimers
	if args[0] == '':
		await sendEmbed(message.channel, None, 'Mute prevents a user from speaking by deleting any messages that they post as long as they\'re muted. You can optionally enter a time limit (in minutes) after the username.\n*Syntax:* `%smute @Code` or `%smute @Code 10`' % (prefix, prefix))
		return
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, 'You must mention a user to mute. *Example:* `%smute @Code 10`' % prefix)
		return
	# Make sure the user isn't on the exempt list
	for i in mentionedUser.roles:
		if i.id in exemptRoles:
			await sendEmbed(message.channel, None, 'Sorry, I can\'t mute a %s!' % i.mention)
			return
	try:
		duration = int(args[1])
	except:
		await sendEmbed(message.channel, None, 'You must enter a duration (in minutes) to mute this user. *Example:* `%smute @Code 10`' % prefix)
		return
	if debugMode:
		print('mutedRole[%s]: %s' % (message.guild.id, mutedRole[message.guild.id]))
		print('mentionedUser: %s' % (mentionedUser.id))
	if mutedRole[message.guild.id] == None:
		output = 'Unable to mute %s, no mute role has been set.' % mentionedUser.mention
		await sendEmbed(message.channel, None, output)
		return
	if mutedRole[message.guild.id] in mentionedUser.roles:
		output = '%s is already muted indefinitely.' % mentionedUser.mention
		for i in guildTimers[message.guild.id]:
			if i['subjectid'] == mentionedUser.id and i['timertype'] == 'mute':
				time = i['expiration']
				age = prettyTime(int((datetime.datetime.now() - time).total_seconds()), 'minutes')
				output = output[:-13] + '(%s remaining).' % age
		await sendEmbed(message.channel, None, output)
		return
	expiration = datetime.datetime.now() + datetime.timedelta(minutes = duration)
	# Give the muted role
	await mentionedUser.add_roles(mutedRole[message.guild.id])
	# Some code here
	if duration != 0:
		# add a DB entry with the details
		objectid = _setguildtimer(message.guild.id, message.author.id, mentionedUser.id, mentionedUser.name, expiration, 'mute')
		# add an entry to the timer list with the details
		guildTimers[message.guild.id].append({'timertype': 'mute', 'subjectid': mentionedUser.id, 'subjectname': mentionedUser.name, 'operatorid': message.author.id, 'expiration': expiration, 'objectid': objectid})
	# Send confirmation
	output = '%s has been muted!' % mentionedUser.mention
	if duration > 0:
		output = output[:-1] + ' for %s minutes!' % duration
	await sendEmbed(message.channel, None, output)


# Bans a user from a guild for a certain number of days, makes a record of it, and deletes the banned user's messages from the last 7 days
global timedban
async def timedban(message, args):
	global guildTimers
	# Check that all arguments are accounted for
	if args[0] == '' or args[1] == '' or args[2] == '':
		await sendEmbed(message.channel, None, 'Timedban removes a user from the guild and prevents them from rejoining for a certain number of days. A reason for the ban is required and will be sent to the user via DM.\n*Syntax:* `%stimedban 7 @Code Repeatedly ignoring moderator warnings.`' % prefix)
		return
	# Check for a valid guild member
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, 'Please mention a valid guild member and a reason for this ban (e.g. `%stimeban 7 @Code for repeatedly ignoring moderator warnings`).' % (prefix))
		return
	# Make sure the user isn't on the exempt list
	for i in mentionedUser.roles:
		if i.id in exemptRoles:
			await sendEmbed(message.channel, None, 'Sorry, I can\'t ban a %s!' % i.mention)
			return
	# Check for a valid duration
	try:
		duration = int(args[0])
	except:
		await sendEmbed(message.channel, None, 'Please mention a valid guild member, a duration (in days), and a reason for this ban (e.g. `%stimeban 7 @Code for repeatedly ignoring moderator warnings`).' % (prefix))
		return
	# Check if the user has any mute timers and remove them
	for i in guildTimers[message.guild.id]:
		if i['subjectid'] == mentionedUser.id and i['timertype'] == 'mute':
			guildTimers[message.guild.id].remove(i)
			_unsetguildtimer(message.guild.id, i['objectid'])
			if debugMode: await sendEmbed(message.channel, None, 'Unsetting timer with objectID %s' % i['objectid'])
	reason = 'for %s days ' % duration + args[2]
	# Save ban in DB log and set timer
	_setlog(message.guild.id, message.author.id, mentionedUser.id, 'ban', reason)
	expiration = datetime.datetime.now() + datetime.timedelta(days = duration)
	objectid = _setguildtimer(message.guild.id, message.author.id, mentionedUser.id, mentionedUser.name, expiration, 'ban')
	guildTimers[message.guild.id].append({'timertype': 'ban', 'subjectid': mentionedUser.id, 'subjectname': mentionedUser.name, 'operatorid': message.author.id, 'expiration': expiration, 'objectid': objectid})
	# DM user
	await sendEmbed(mentionedUser, None, 'You have been banned from Ruffleneck\'s Den for %s days.\n*"%s"*' % (duration, args[2]))
	# Ban user
	await mentionedUser.ban(delete_message_days = 0)
	await sendEmbed(message.channel, None, '%s has been banned for %s days!\n*"%s"*' % (mentionedUser.mention, duration, args[2]))


# Revokes a user's ban and removes any active ban timers
global unban
async def unban(message, args):
	if args[0] == '':
		await sendEmbed(message.channel, None, 'Unban removes a user\'s ban, allowing them to rejoin the guild. It requires a user ID instead of a mention. A reason is optional and will be saved in the user\'s logs.\n*Syntax:* `%sunban 491644020976648203` or `%sunban 491644020976648203 They have served their time and may now rejoin society.`' % (prefix, prefix))
		return
	thisGuild = client.get_guild(message.guild.id)
	try:
		targetUser = await client.get_user_info(args[0])
	except:
		await sendEmbed(message.channel, None, 'You must give a valid user ID that you wish to unban (e.g. `%sunban 491644020976648203`).')
		return
	await thisGuild.unban(targetUser)
	_setlog(message.guild.id, message.author.id, targetUser.id, 'unban', args[1])
	for i in guildTimers[message.guild.id]:
		if i['subjectid'] == targetUser.id and i['timertype'] == 'ban':
			guildTimers[message.guild.id].remove(i)
			_unsetguildtimer(message.guild.id, i['objectid'])
			if debugMode: await sendEmbed(message.channel, None, 'Unsetting timer with objectID %s' % i['objectid'])
	await sendEmbed(message.channel, None, '%s has been unbanned from the guild.' % targetUser.mention)


# Warns a user and makes a record of it
global warn
async def warn(message, args):
	errorOutput = 'Please mention a valid guild member or user ID and a reason for this warning.\n*Syntax:* `%swarn <user mention> <reason>`\n*Example:* `%swarn @Code for spamming #general with memes`' % (prefix, prefix)
	# Check that all arguments are accounted for
	if args[0] == '' or args[1] == '':
		await sendEmbed(message.channel, None, 'Warn alerts a user of misconduct/rule-breaking. It requires a reason that will be saved in the user\'s logs.\n*Syntax:* `%swarn @Code for spamming #general with memes.`' % prefix)
		return
	else:
		try:
			mentionedUser = message.mentions[0]
		except:
			await sendEmbed(message.channel, None, errorOutput)
			return
	# Set the warning
	_setlog(message.guild.id, message.author.id, mentionedUser.id, 'warn', args[1])
	# Send the confirmation
	await sendEmbed(message.channel, None, '%s has been warned!\n*"%s"*' % (message.mentions[0].mention, args[1]))
