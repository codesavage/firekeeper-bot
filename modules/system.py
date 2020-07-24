global addresponse
async def addresponse(message, args):
	
	global guildResponses
	cancelText = 'Got it %s, I\'ll stop adding this response. ^^' % message.author.mention
	debugOutput = ''
    
	def waitCheck(newMessage):
		#channel = message.channel, author = message.author
		return message.channel == newMessage.channel and message.author == newMessage.author

	# Ask the user for the targetSpeaker(s)
	output = 'Okay %s, who should this respond to (roles or users)? Please use mentions or IDs in your response (only one or the other), or you can say `anyone`. FYI, you can also say `cancel` at any time to quit this command.' % message.author.mention
	await sendEmbed(message.channel, 'Add Response: Step 1 of 6', output)
	goodResponse = False
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		# Parse content and look for mentions, IDs, or "anyone"
		userCount = 0
		ignored = 0
		userList = []
		if response.content == 'anyone':
			userCount += 1
			userList.append(response.content)
			debugOutput = response.content
		# Let's start with if the user is using IDs
		elif len(response.mentions) == 0:
			response = response.content.split()
			if debugMode: await sendEmbed(message.channel, None, 'No mentions found, trying IDs from the following list:\n%s' % response)
			for i in response:
				if i not in userList:
					# Try to find it in the guild members
					print('Trying member lookup.')
					#try:
					lookup = message.guild.get_member(i)
					#except:
					if hasattr(lookup, 'id') == False:
						print('Member lookup failed, trying role lookup.')
						# If that doesn't work, try to find it in the guild roles
						for x in message.guild.roles:
							if x.id == i:
								print('Role found.')
								userCount += 1
								userList.append(i)
								debugOutput += '%s (%s)\n' % (x.mention, x.id)
						# If we didn't find it in roles, ignore it and move on
						if i not in userList:
							print('Role lookup failed, ignoring input.')
							ignored += 1
							if debugMode: await sendEmbed(message.channel, None, 'Lookup failed on `%s`!' % i)
					# This runs if we found the ID in guild members
					else:
						print('Member found.')
						userCount += 1
						userList.append(lookup.id)
						debugOutput += '%s (%s)\n' % (lookup.mention, lookup.id)
				# If the ID was already added, ignore it
				else:
					print('ID already used, ignoring input.')
					ignored += 1
		# If the message is using mentions
		else:
			for i in response.mentions:
				if i.id not in userList:
					userCount += 1
					userList.append(i.id)
					debugOutput += '%s (%s)\n' % (i.mention, i.id)
				else:
					ignored += 1
		if debugMode: await sendEmbed(message.channel, None, '%s good responses were found (%s responses were ignored):\n' % (userCount, ignored) + debugOutput)
		# Check to see if we successfully got any users, rinse and repeat if not
		if len(userList) == 0:
			await sendEmbed(message.channel, 'Add Response', 'Sorry %s, I couldn\'t find any valid roles/users in that response. Who should this respond to? Please use mentions or IDs in your response (only one or the other), or you can say `anyone`.' % message.author.mention)
		else:
			goodResponse = True
	friendlyUserList = ''
	for i in userList:
		if i == 'anyone':
			friendlyUserList = i
		else:
			lookup = message.guild.get_member(i)
			if hasattr(lookup, 'id') == False:
				for x in message.guild.roles:
					if x.id == i:
						friendlyUserList += x.mention + '\n'
			else:
				friendlyUserList += lookup.mention + '\n'

	# Ask the user for the targetChannel(s)
	output = 'Okay %s, I\'ll respond to the following users:\n%s\nWhat channel(s) do you want me to respond to them in? Please use channel mentions or IDs in your response (only one or the other), or you can say `all channels`.' % (message.author.mention, friendlyUserList)
	await sendEmbed(message.channel, 'Add Response: Step 2 of 6', output)
	goodResponse = False
	debugOutput = ''
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		# Parse content and look for mentions, IDs, or "all channels"
		channelCount = 0
		ignored = 0
		channelList = []
		if response.content == 'all channels':
			channelCount += 1
			channelList.append(response.content)
			debugOutput = response.content
		# Start with if the user is using IDs
		elif len(response.channel_mentions) == 0:
			response = response.content.split()
			if debugMode: await sendEmbed(message.channel, None, 'No mentions found, trying IDs from the following list:\n%s' % response)
			for i in response:
				if i not in channelList:
					# Try to find the channel
					print('Trying channel lookup.')
					lookup = message.guild.get_channel(i)
					# If it's not a valid ID, ignore and move on
					if hasattr(lookup, 'id') == False:
						print('Channel lookup failed, ignoring input.')
					# If we found the ID in guild channels
					else:
						print('Channel found.')
						channelCount += 1
						channelList.append(lookup.id)
						debugOutput += '%s (%s)\n' % (lookup.mention, lookup.id)
				# If the ID was already added, ignore it
				else:
					print('ID already used, ignoring input.')
					ignored += 1
		# If the user is using mentions
		else:
			for i in response.channel_mentions:
				if i.id not in channelList:
					channelCount += 1
					channelList.append(i.id)
					debugOutput += '%s (%s)\n' % (i.mention, i.id)
				else:
					ignored += 1
		if debugMode: await sendEmbed(message.channel, None, '%s good responses were found (%s responses were ignored):\n' % (channelCount, ignored) + debugOutput)
		# Check to see if we successfully got any channels, rinse and repeat if not
		if len(channelList) == 0:
			await sendEmbed(message.channel, 'Add Response', 'Sorry %s, I couldn\'t find any valid channels in that response. What channel(s) do you want me to respond to them in? Please use channel mentions or IDs in your response (only one or the other), or you can say `all channels`.' % message.author.mention)
		else:
			goodResponse = True
	friendlyChannelList = ''
	for i in channelList:
		if i == 'all channels':
			friendlyChannelList = i
		else:
			lookup = message.guild.get_channel(i)
			friendlyChannelList += lookup.mention + '\n'

	# Ask the user for the targetText
	output = 'Okay %s, I\'ll respond to %s users/roles when they speak in the following channels:\n%s\nWhat is the text that you want me to respond to? Keep in mind, this may not contain any bot commands or user/role mentions.' % (message.author.mention, len(userList), friendlyChannelList)
	await sendEmbed(message.channel, 'Add Response: Step 3 of 6', output)
	goodResponse = False
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		# Check for mentions
		elif len(response.mentions) > 0:
			await sendEmbed(message.channel, None, 'Sorry %s, the text I respond to can\'t contain any mentions or bot commands! What is the text that you want me to respond to?' % message.author.mention)
		# Check for commands
		elif any('!' + command in response.content for command in moduleCommands):
			await sendEmbed(message.channel, None, 'Sorry %s, the text I respond to can\'t contain any mentions or bot commands! What is the text that you want me to respond to?' % message.author.mention)
		else:
			targetText = response.content
			goodResponse = True

	# Ask the user for the targetMatch
	output = 'Okay %s, I\'ll respond to %s users/roles when they say "%s" in %s channels. Should I respond if any part of their message contains this text, or match messages that only have that exact text? Please respond with `contains` or `exact`.' % (message.author.mention, len(userList), targetText, len(channelList))
	await sendEmbed(message.channel, 'Add Response: Step 4 of 6', output)
	goodResponse = False
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		# Make sure response is either 'contains' or 'exact'
		elif response.content == 'contains':
			targetMatch = response.content
			friendlyMatch = 'part of a message contains'
			goodResponse = True
		elif response.content == 'exact':
			targetMatch = response.content
			friendlyMatch = 'a message exactly matches'
			goodResponse = True
		else:
			await sendEmbed(message.channel, 'Add Response', 'Sorry %s, I couldn\'t find a valid match in that response. Should I respond if any part of their message contains this text, or match messges that only have that exact text? Please respond with `contains` or `exact`.' % message.author.mention)



	# Ask the user for the targetMatch
	output = 'Okay %s, I\'ll respond to %s users/roles when they say something in %s channels that ' % (message.author.mention, userCount, channelCount)
	if friendlyMatch == 'a message exactly matches':
		output += 'exactly matches'
	else:
		output += 'contains'
	output += ' the text you entered. What percentage of the time should I respond? (1-100)'
	await sendEmbed(message.channel, 'Add Response: Step 5 of 6', output)
	goodResponse = False
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		# Make sure response is either 'contains' or 'exact'
		try:
			if (int(response.content) > 0 and int(response.content) <= 100):
				matchPercent = int(response.content)
				goodResponse = True
			else:
				await sendEmbed(message.channel, 'Add Response', 'Sorry %s, I couldn\'t find a valid percentage in that response. What percentage of the time should I respond? (1-100)' % message.author.mention)
		except:
			await sendEmbed(message.channel, 'Add Response', 'Sorry %s, I couldn\'t find a valid percentage in that response. What percentage of the time should I respond? (1-100)' % message.author.mention)

	output = 'Okay %s, I\'ll respond to %s users/roles when they say something in %s channels that %s' % (message.author.mention, userCount, channelCount, friendlyMatch)
	if friendlyMatch == 'exact':
		output += 'ly matches'
	output += ' the text you entered %s%% of the time. What would you like me to respond with? (1000 character limit)' % (matchPercent)
	await sendEmbed(message.channel, 'Add Response: Step 6 of 6', output)
	goodResponse = False
	while not goodResponse:
		response = await client.wait_for('message', check = waitCheck, timeout = 120)
		# Check for cancel
		if response.content == 'cancel':
			await sendEmbed(message.channel, None, cancelText)
			return
		elif len(response.content) > 1000:
			await sendEmbed(message.channel, None, 'Sorry, that response is too long by %s characters. What would you like me to respond with? (1000 character limit)' % (len(response.content) - 1000))
		else:
			responseText = response.content
			goodResponse = True

	# Add a DB entry with the details
	objectid = _setresponse(message.guild.id, userList, targetMatch, channelList, targetText, responseText, matchPercent)
	# Add an entry to the response list with the details
	guildResponses[message.guild.id].append({'userlist': userList, 'targetmatch': targetMatch, 'channellist': channelList, 'targettext': targetText, 'responsetext': responseText, 'matchpercent': matchPercent, 'objectid': objectid})

	# Send confirmation
	embed = discord.Embed(title = None, description = 'All done %s, your response has been added!' % message.author.mention, color = embedColor)
	output = 'This response will be triggered by '
	if friendlyUserList == 'anyone':
		output += 'anyone. '
	else:
		output += 'the folowing users/roles:\n%s' % friendlyUserList
	output += 'It will trigger in '
	if friendlyChannelList == 'all channels':
		output += 'all channels. '
	else:
		output += 'the following channels:\n%s' % friendlyChannelList
	output += 'It will trigger %s%% of the time. ' % matchPercent
	output += 'It will trigger when '
	if targetMatch == 'contains':
		output += 'any part of a message contains the text '
	else:
		output += 'a message exacty matches the text '
	output += '"%s", to which I\'ll respond "%s".' % (targetText, responseText)
	embed.add_field(name = 'Response Summary', value = output, inline = False)
	await message.channel.send(embed = embed)


global ansible
async def ansible(message, args):
	homeChannelId = 698247715431120947
	homeChannel = client.get_channel(homeChannelId)
	results = []
	if debugMode:
		print(args)
	action = args[0]
	if len(args) > 1:
		parameter = args[1]
	else:
		parameter = ""

	async def forwardMessage(message):
		embed = discord.Embed(title = None, description = message.content, color = embedColor)
		embed.set_author(name = '%s' % (message.author.name), icon_url = message.author.avatar_url)
		embed.set_footer(text = 'Time: %s\nMessage ID: %s\nGuild: %s (%s)\nChannel: %s (%s)' % (message.created_at.strftime('%Y-%m-%d %H:%M:%S'), message.id, message.guild.name, message.guild.id, message.channel.name, message.channel.id))
		#message = await client.get_message(message.channel, message.id)
		if len(message.attachments) > 0:
			messageimage = message.attachments[0].proxy_url
			if messageimage == '':
				messageimage = message.attachments[0].url
			embed.set_thumbnail(url = messageimage)
		await homeChannel.send(embed = embed)

	if action == 'passmessage':
		#await homeChannel.send('Guild: %s - Channel: %s - Author: %s\n%s' % (message.guild.name, message.channel.name, message.author.name, message.content))
		await forwardMessage(message)
	elif action == 'listguilds':
		for guild in client.guilds:
			if guild.id in ansibleTargets.values():
				results.append('__**%s**__ - %s' % (guild.name, guild.id))
			else:
				results.append('%s - %s' % (guild.name, guild.id))
		#await homeChannel.send('\n'.join(results))
		await sendEmbed(homeChannel, 'Ansible-Ready Guilds', '\n'.join(results))
	elif action == 'listchannels':
		if len(parameter) == 0:
			await sendEmbed(homeChannel, 'Error! Ansible listchannels failed.', 'listchannels requires a guildid')
		else:
			guild = client.get_guild(int(parameter))
			output = ''
			tchannels = []
			for i in guild.channels:
				if i.type == discord.ChannelType.text and i.type != 4:
					if i.permissions_for(i.guild.get_member(botID)).read_messages:
						tchannels.append(i)
			embed = discord.Embed(title = 'Ansible-Ready Channels on %s' % (guild.name), color = embedColor)
			for i in sorted(tchannels, key=lambda x:x.position):
				if i.id in ansibleTargets:
					output += '__**%s**__ -> %s\n' % (i.name, i.id)
				else:
					output += '%s -> %s\n' % (i.name, i.id)
			embed.add_field(name = '\U0001F4DD ' + str(len(tchannels)) + ' Text Channels', value = output, inline = False)
			await homeChannel.send(embed = embed)
	elif action == 'connect':
		if len(parameter) == 0:
			await sendEmbed(homeChannel, 'Error! Ansible connect failed.', 'connect requires a channelid or "all guildid"')
		else:
			if parameter[0:3] == 'all':
				parameter = parameter[4:]
				try:
					targetGuild = client.get_guild(int(parameter))
					for channel in targetGuild.channels:
						if channel.id not in ansibleTargets:
							botPerms = channel.permissions_for(targetGuild.get_member(botID))
							if botPerms.read_messages:
								ansibleTargets[channel.id] = channel.guild.id
					await sendEmbed(homeChannel, 'Ansible Connected!', 'Connected to all channels in %s' % (targetGuild.name))
				except:
					await sendEmbed(homeChannel, 'Error! Ansible not connected.','Failed to connect to all channels on %s\n%s' % (parameter, traceback.format_exc()))
			elif parameter in ansibleTargets:
					await sendEmbed(homeChannel, 'Error! Ansible already connected.','Already connected to channel %s' % (parameter))
			else:
				try:
					targetChannel = client.get_channel(int(parameter))
					targetGuild = targetChannel.guild
					botPerms = targetChannel.permissions_for(targetGuild.get_member(botID))
					if botPerms.read_messages:
						ansibleTargets[targetChannel.id] = targetChannel.guild.id
						await sendEmbed(homeChannel, 'Ansible Connected!', 'Connected to #%s in %s' % (targetChannel.name, targetGuild.name))
					else:
						await sendEmbed(homeChannel, 'Error! Ansible connect failed.', 'I don\'t have the "read messages" permission to the %s channel in %s' % (targetChannel.name, targetGuild.name))
				except:
					await sendEmbed(homeChannel, 'Error! Ansible not connected.','Failed to connect to channel %s\n%s' % (parameter, traceback.format_exc()))
	elif action == 'disconnect':
		if len(parameter) == 0:
			await sendEmbed(homeChannel, 'Error! Ansible disconnect failed.', 'disconnect requires a guildid')
		elif parameter == 'all':
			ansibleTargets.clear()
			await sendEmbed(homeChannel, 'Ansible Disconnected!', 'Disconnected from all channels')
		else:
			try:
				ansibleTargets.pop(parameter)
				targetChannel = client.get_channel(parameter)
				targetGuild = targetChannel.guild
				await sendEmbed(homeChannel, 'Ansible Disconnected!', 'Disconnected from #%s in %s' % (targetChannel.name, targetGuild.name))
			except:
				await sendEmbed(homeChannel, 'Error! Ansible not disconnected.','Failed to disconnect from channel %s\n%s' % (parameter, traceback.format_exc()))
	elif action == 'replay':
		parameter = parameter.split()
		targetChannelID = int(parameter[0])
		limit = 10
		beforeMsg = None
		try:
			targetChannel = client.get_channel(targetChannelID)
			targetGuild = targetChannel.guild
			beforeID = None
			if len(parameter) > 1:
				beforeID = int(parameter[1])
			botPerms = targetChannel.permissions_for(targetGuild.get_member(botID))
			queue = []
			if not botPerms.read_messages:
				await sendEmbed(homeChannel, 'Error! Ansible replay failed.', 'I don\'t have the "read messages" permission to the %s channel in %s' % (targetChannel.name, targetGuild.name))		
			else:
				if beforeID:
					async for i in targetChannel.history(limit = limit, before = beforeID):
						queue.append(i)
				else:
					async for i in targetChannel.history(limit = limit):
						queue.append(i)
				queue.reverse()
				embed = discord.Embed(title = 'Replay\nGuild: %s (%s)\nChannel: %s (%s)' % (targetGuild.name, targetGuild.id, targetChannel.name, targetChannel.id), description = '', color = embedColor)
				for m in queue:
					messageimage = ''
					if len(m.attachments) > 0:
						messageimage = m.attachments[0].proxy_url
						if messageimage == '':
							messageimage = m.attachments[0].url
					i = 0
					embed.add_field(name = '**%s**' % (m.author.name), value = '%s\n%s\n\n*ID: %s*\n*Time: %s*\n----------' % (m.content, messageimage, m.id, m.created_at.strftime('%Y-%m-%d %H:%M:%S')), inline = False)
					for file in m.attachments:
						fileurl = file.proxy_url
						if fileurl == '':
							fileurl = file.url
						embed.add_field(name = 'Message Attachment %s' % (i), value = fileurl, inline = False)
						i += 1
				await homeChannel.send(embed = embed)
		except:
			await sendEmbed(homeChannel, 'Error! Ansible replay failed.', 'Error replaying from %s\n%s' % (parameter[0], traceback.format_exc()))
	elif action == 'say':
		if len(parameter) == 0:
			await sendEmbed(homeChannel, 'Error! Ansible say failed.', 'say requires a channelid')
		else:
			paramArr = parameter.split(" ")
			if len(paramArr) <= 1:
				await sendEmbed(homeChannel, 'Error! Ansible say failed.', 'say requires a channelid and a message')
			else:
				try:
					targetChannel = client.get_channel(paramArr.pop(0))
					targetGuild = targetChannel.guild
					await sendEmbed(targetChannel, None, " ".join(paramArr))
				except:
					await sendEmbed(homeChannel, 'Error! Ansible say failed.', traceback.format_exc())

# Executes arbitrary python code, which is useful for testing. Not very safe to
# leave in production, but this whole module is hardcoded to the developer user
# IDs, so I'm not sure how it could be abused. I'd still take it out if the bot
# was used in any guilds other than my own.
global ee
async def ee(message, args):
	exec(args[0], globals(), locals())


# Logs out of Discord and shuts down the bot
global quit
async def quit(message, args):
	global intentionalExit
	intentionalExit = True
	if configJSON['farewell'] != 'false':
		await sendEmbed(message.channel, 'Quit', eval(configJSON['farewell']))
	await message.add_reaction('\U0001F480')
	await client.close()


# Reloads the configuration file and modules
global reload
async def reload(message, args):
	unloadModules()
	unloadConfig()
	loadConfig()
	loadModules()
	await message.add_reaction('\U0000267B')


global responses
async def responses(message, args):
	if len(guildResponses[message.guild.id]) == 0:
		await sendEmbed(message.channel, 'Responses', 'There are currently no responses configured.')
		return
	output = ''
	count = 0
	for i in guildResponses[message.guild.id]:
		count += 1
		# Parse user list
		if i['userlist'][0] == 'anyone':
			userName = 'anyone'
		else:
			if len(i['userlist']) > 1:
				userName = 'a specific user ('
				for j in i['userlist']:
					if debugMode:
						print('Looking up userid: %s' % (j))
					if j == '287070496724484108':
						userName = '@everyone, '
					else:
						try:
							lookup = await client.fetch_user(j)
						except:
							if debugMode:
								print('Exception on client.fetch_user(%s)' % (j))
							lookup = None
						try:
							userName += lookup.mention + ', '
						except:
							userName += 'ID %s' % j + ', '
					await asyncio.sleep(0.1)
				userName = userName[:-2] + ')'
			else:
				try:
					lookup = await client.fetch_user(i['userlist'][0])
				except:
					pass
				try:
					userName = lookup.mention
				except:
					allLookupsFailed = True
					for r in message.guild.roles:
						if r.id == i['userlist'][0]:
							userName = r.mention
							allLookupsFailed = False
					if allLookupsFailed:
						userName = 'ID %s' % i['userlist'][0]
		# Parse channel list
		if i['channellist'][0] == 'all channels':
			channelName = 'all channels'
		else:
			if len(i['channellist']) > 1:
				channelName = 'a specific channel ('
				for j in i['channellist']:
					print('Looking up channel: %s' % j)
					lookup = message.guild.get_channel(j)
					channelName += lookup.mention + ', '
				channelName = channelName[:-2] + ')'
			else:
				print('Looking up channel: %s' % i['channellist'][0])
				lookup = message.guild.get_channel(i['channellist'][0])
				channelName = lookup.mention
		if i['targetmatch'] == 'contains':
			output += '**%s**: When %s says something containing the phrase \"%s\" in %s, I\'ll respond with \"%s\" %s%% of the time.\n' % (count, userName, i['targettext'], channelName, i['responsetext'], i['matchpercent'])
		else:
			output += '**%s**: When %s says the exact phrase \"%s\" in %s, I\'ll respond with \"%s\" %s%% of the time.\n' % (count, userName, i['targettext'], channelName, i['responsetext'], i['matchpercent'])
	await sendEmbed(message.channel, 'Responses', output)


global removeresponse
async def removeresponse(message, args):
	global guildResponses
	if len(guildResponses[message.guild.id]) == 0:
		await sendEmbed(message.channel, 'Remove Response', 'There are currently no responses configured!')
		return
	if args[0] == '':
		await sendEmbed(message.channel, 'Remove Response', 'You must specify a response number to remove! See `%sresponses` for the current list.\n(*Example:* `%sremoveresponse 3`)' % (prefix, prefix))
		return
	try:
		index = int(args[0]) - 1
	except:
		await sendEmbed(message.channel, 'Remove Response', 'You must specify a response number to remove! See `%sresponses` for the current list.\n(*Example:* `%sremoveresponse 3`)' % (prefix, prefix))
		return
	if index + 1 > len(guildResponses[message.guild.id]) or index < 0:
		await sendEmbed(message.channel, 'Remove Response', 'Sorry, that\'s an invalid response number! See `%sresponses` for the current list.' % prefix)
		return
	_unsetresponse(message.guild.id, guildResponses[message.guild.id][index]['objectid'])
	guildResponses[message.guild.id].pop(index)
	await sendEmbed(message.channel, 'Remove Response', 'Okay %s, that response has been removed!' % message.author.mention)


# Makes the bot send a message in a specific channel
global say
async def say(message, args):
	if args[1] == '' or len(message.channel_mentions) == 0:
		await sendEmbed(message.channel, None, 'You must specify a channel and a message to send.\n*Syntax:* `!say #general Hello everyone!`')
		return
	target = message.channel_mentions[0]
	output = args[1]
	await sendEmbed(target, None, output)


# Reports resource usage and uptime of the bot guild
global serverhealth
async def serverhealth(message, args):
	timeThen = time.perf_counter()
	await message.channel.trigger_typing()
	timeNow = time.perf_counter()
	time_delta = round((timeNow - timeThen) * 1000)
	#output = 'Response time: {}ms'.format(time_delta)
	ping = format(time_delta)
	cpu = psutil.cpu_percent(interval = 1)
	vmem = psutil.virtual_memory()
	smem = psutil.swap_memory()
	disk = psutil.disk_usage('/')
	boot = prettyTime(int((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()), 'seconds')
	output = '`Response Time:` %sms\n`CPU usage:` %s%%\n`Memory usage:` %s%%\n`Swap usage:` %s%%\n`Disk usage:` %s%%\n`Uptime:` %s' % (ping, cpu, vmem.percent, smem.percent, disk.percent, boot)
	await sendEmbed(message.channel, 'Guild Health', output)


# Lists all Discord guilds the bot is in
global serverlist
async def serverlist(message, args):
	guildCount = len(client.guilds)
	memberCount = 0
	listOut = ''
	for i in sorted(client.guilds, reverse=True, key=lambda x:x.member_count):
		listOut += '`%s` (*%s*) - %s members\n' % (i.name, i.id, i.member_count)
		memberCount += i.member_count

	output = listOut[:-1]
	embed = discord.Embed(title = 'Guild List', color = embedColor)
	embed.add_field(name = 'Utilized in %s guilds by %s users:' % (guildCount, memberCount), value = output, inline = False)
	await message.channel.send(embed = embed)


# Lists commands in the system and test modules that are only usable by developers
global syshelp
async def syshelp(message, args):
	command = args[0]
	if command == '':
		embed = discord.Embed(title = 'Fire Keeper System/Test Help', color = embedColor)
		for m in sorted(modules.keys()):
			if m not in ['system', 'test']:
				continue
			output = []
			output.append('\n')
			for c in sorted(modules[m]['commands'].keys()):
				try:
					text = modules[m]['commands'][c]['shortHelp']
				except:
					text = '*- no help found.*'
				output.append('`%s%s` %s' % (prefix, c, text))
			embed.add_field(name = '***%s***' % (modules[m]['friendlyName']), value = '\n'.join(output), inline = False)
		await message.channel.send(embed = embed)
	elif command in modules['system']['commands'] or command in modules['test']['commands']:
		m = moduleCommands[command][0]
		try:
			helpText = modules[m]['commands'][command]['helpText']
		except:
			helpText = '*- no help found.*'
		output = '`%s` %s' % (command, helpText)
		await sendEmbed(message.channel, '%s help for %s command' % (m.capitalize(), command), output)
	else:
		output = command + ' is not a valid command. Try `%ssyshelp` for a list of available system/test commands.' % (prefix)
		await sendEmbed(message.channel, 'System/Test help for unknown command %s' % (command), output)


# Tests the connection to the database
global testdb
async def testdb(message, args):
	await sendEmbed(message.channel, 'DB Test Results', str(dbConn.test))


# Displays the list of active timers in the guild
global timers
async def timers(message, args):
	if len(guildTimers[message.guild.id]) == 0:
		await sendEmbed(message.channel, 'Timers', 'There are no active timers.')
		return
	muteOutput = ''
	banOutput = ''
	mCount = 0
	bCount = 0
	for i in guildTimers[message.guild.id]:
		operator = message.guild.get_member(i['operatorid'])
		time = i['expiration']
		age = prettyTime(int((datetime.datetime.now() - time).total_seconds()), 'minutes')
		try:
			subject = message.guild.get_member(i['subjectid'])
		except:
			subject = None
		subjectname = i['subjectname']
		subjectid = i['subjectid']
		if i['timertype'] == 'mute':
			mCount += 1
			if subject == None:
				muteOutput += '**%s:** %s (*%s*)\nMuted by %s\nExpires in %s at %s EST\n' % (str(mCount), subjectname, subjectid, operator.mention, age, str(time)[11:-10])
			else:
				muteOutput += '**%s:** %s (*%s*)\nMuted by %s\nExpires in %s at %s EST\n' % (str(mCount), subject.mention, subject.id, operator.mention, age, str(time)[11:-10])
		elif i['timertype'] == 'ban':
			bCount += 1
			if subject == None:
				banOutput += '**%s:** *User:* %s (%s)\n*Banned by:* %s\n*Expires:* %s (in %s)\n' % (str(bCount), subjectname, subjectid, operator.mention, str(time)[:-10], age)
			else:
				banOutput += '**%s:** *User:* %s (%s)\n*Banned by:* %s\n*Expires:* %s (in %s)\n' % (str(bCount), subject.mention, subject.id, operator.mention, str(time)[:-10], age)
	output = discord.Embed(title = 'Active Timers', color = embedColor)
	if mCount > 0:
		output.add_field(name = 'Mutes', value = ''.join(muteOutput), inline = False)
	if bCount > 0:
		output.add_field(name = 'Bans', value = ''.join(banOutput), inline = False)
	await message.channel.send(embed = output)


# Lists the configured XP channels in the guild
global xpchannels
async def xpchannels(message, args):
	if args[0] == '':
		if len(xpChannels[message.guild.id]) == 0:
			await sendEmbed(message.channel, 'XP Channels', 'There are currently no XP channels configured.')
			return
		output = 'Users can generate XP in the following channels:\n'
		for i in xpChannels[message.guild.id]:
			lookup = message.guild.get_channel(i)
			output += lookup.mention + '\n'
	elif args[0] == 'add' or args[0] == 'remove':
		# Parse channel lists
		channelList = _getattrib(message.guild.id, 'server', 'xpchannels')
		newChannels = []
		for i in message.channel_mentions:
			newChannels.append(i.id)
		if args[0] == 'add':
			for i in newChannels:
				if i not in channelList:
					channelList.append(i)
					_setattrib(message.guild.id, 'server', 'xpchannels', channelList)
		else:
			for i in newChannels:
				if i in channelList:
					channelList.remove(i)
					_setattrib(message.guild.id, 'server', 'xpchannels', channelList)
		output = 'Users can now generate XP in the following channels:\n'
		for i in channelList:
			lookup = message.guild.get_channel(i)
			output += lookup.mention + '\n'
	else:
		output = '\"%s\" is not a valid argument.' % args[0]
	await sendEmbed(message.channel, 'XP Channels', output)