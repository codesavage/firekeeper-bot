# Make a random choice from a list of options
global choose
async def choose(message, args):
	choices = args[0].split(' or ')
	if len(choices) < 2:
		choices = args[0].split(', ')
		if len(choices) < 2:
			choices = args[0].split(' ')
			if len(choices) < 2:
				await sendEmbed(message.channel, 'Choose', 'Please give me at least 2 options to choose from, separated by either commas or spaces.')
				return
	embed = discord.Embed(title = 'Choose', description = 'Hmmm, let me think. I choose...', color = embedColor)
	msg = await message.channel.send(embed = embed)
	choice = random.choice(choices)
	await asyncio.sleep(2)
	embed = discord.Embed(title = 'Choose', description = 'I choose ' + choice + '.', color = embedColor)
	await msg.edit(embed = embed)


# Displays various information about the Discord guild, such as number of users and age
global server
async def server(message, args):
	totalAge = 0
	memberCount = 0
	channelCount = 0
	for i in message.guild.members:
		if i.bot != True:
			a = (datetime.datetime.now() - i.joined_at).total_seconds()
			totalAge += int(a)
			memberCount += 1
	for i in message.guild.channels:
		if i.type != 4:
			channelCount += 1
	averageAge = prettyTime(int(totalAge // message.guild.member_count), 'days')
	guildAge = prettyTime(int((datetime.datetime.now() - message.guild.created_at).total_seconds()), 'days')
	output = '''
	`Owner:` %s
	`Created:` %s (*%s ago*)
	`Region:` %s
	`Channels:` %s
	`Members:` %s
	`Average Member Age:` %s
	''' % (message.guild.owner.mention, str(message.guild.created_at)[:11], guildAge, message.guild.region, channelCount, memberCount, averageAge)
	embed = discord.Embed(title = message.guild.name, description = output, color = embedColor)
	embed.set_thumbnail(url = message.guild.icon_url)
	await message.channel.send(embed = embed)


# Lists bot commands and help on how to use them
global help
async def help(message, args):
	command = args[0]
	if command == '':
		embed = discord.Embed(title = 'Fire Keeper Help', color = embedColor)
		for m in sorted(modules.keys()):
			if m not in ['currency', 'fun', 'games', 'usermanagement', 'utilities']:
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
	elif command in modules['currency']['commands'] or command in modules['fun']['commands'] or command in modules['games']['commands'] or command in modules['usermanagement']['commands'] or command in modules['utilities']['commands']:
		m = moduleCommands[command][0]
		try:
			helpText = modules[m]['commands'][command]['helpText']
		except:
			helpText = '*- no help found.*'
		output = '`%s` %s' % (command, helpText)
		await sendEmbed(message.channel, 'Help for %s command' % (command), output)
	else:
		output = command + ' is not a valid command. Try `%shelp` for a list of available commands.' % (prefix)
		await sendEmbed(message.channel, 'Help for unknown command %s' % (command), output)


# Test the latency between the bot guild and Discord guild
global ping
async def ping(message, args):
	timeThen = time.perf_counter()
	await message.channel.trigger_typing()
	timeNow = time.perf_counter()
	time_delta = round((timeNow - timeThen) * 1000)
	output = 'Response time: {}ms'.format(time_delta)
	await sendEmbed(message.channel, 'Ping', output)

# Upload a qr code based on data from the user
global qr
async def qr(message, args):
	data = args[0]
	qrimage = qrcode.make(data, image_factory=PymagingImage)
	filename = '/tmp/firekeeper-qr/%s.png' % int(random.random()*100000)
	fp = open(filename, 'wb')
	qrimage.save(fp)
	fp.close()
	await message.channel.send(file=discord.File(filename, filename='qrcode.png'))


# Displays information about the current bot version
global version
async def version(message, args):
	versionAge = prettyTime(int((datetime.datetime.now() - versionRelease).total_seconds()), 'days')
	botAge = prettyTime(int((datetime.datetime.now() - initialRelease).total_seconds()), 'days')
	output = '''
	`Current version:` %s
	`Latest release:` %s (*%s ago*)
	`Initial release:` %s (*%s ago*)
	Developed by <@169268862901157888> and <@291304287307300867>
	http://firekeeper.info
	''' % (versionNumber, str(versionRelease)[:11], versionAge, str(initialRelease)[:11], botAge)
	await sendEmbed(message.channel, 'Fire Keeper Info', output)


# Shows the weather for a certain city or zip code
global weather
async def weather(message, args):
	loc = args[0]
	try:
		locTest = int(loc)
	except ValueError:
		url = 'http://wttr.in/~' + loc + '.png?nTu1'
	else:
		url = 'http://wttr.in/' + loc + '.png?nTu1'
	embed = discord.Embed(title = 'Weather for %s ' % (args[0]), color = embedColor)
	embed.set_image(url = url.replace(' ', '%20'))
	await message.channel.send(embed = embed)