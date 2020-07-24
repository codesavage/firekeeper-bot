# Can be used once every 8,760 hours (365 days / 1 year) to receive a random annual allowance
global annual
async def annual(message, args):
	timer = _gettimer(message.guild.id, message.author.id, 'annual')
	if (timer):
		output = 'You have to wait %s before you can claim your annual allowance.' % (prettyTime(timer, 'seconds'))
	else:
		grant = random.randrange(91250, 365000)
		balance = prettyNums(_incrementbalance(message.author.id, grant))
		grant = prettyNums(grant)
		_settimer(message.guild.id, message.author.id, 'annual', '8760')
		output = '%s, you claimed your annual allowance of %s %s. You currently have %s %s.' % (message.author.mention, grant, currencyName[message.guild.id], balance, currencyName[message.guild.id])
	await sendEmbed(message.channel, 'Annual', output)


# Shows a user's global currency balance
global balance
async def balance (message, args):
	if message.mentions != []:
		balance = prettyNums(_getbalance(message.mentions[0].id))
		output = '%s has %s %s.' % (message.mentions[0].mention, balance, currencyName[message.guild.id])
	else:
		balance = prettyNums(_getbalance(message.author.id))
		output = '%s, you have %s %s.' % (message.author.mention, balance, currencyName[message.guild.id])
	if balance == '1':
		output = output[:-2] + '.'
	await sendEmbed(message.channel, 'Balance', output)


# Can be used once every 876,000 hours (36,500 days / 100 years) to receive a random centennial allowance
global centennial
async def centennial(message, args):
	timer = _gettimer(message.guild.id, message.author.id, 'centennial')
	if (timer):
		output = 'You have to wait %s before you can claim your centennial allowance.' % (prettyTime(timer, 'seconds'))
	else:
		grant = random.randrange(9125000, 36500000)
		balance = prettyNums(_incrementbalance(message.author.id, grant))
		grant = prettyNums(grant)
		_settimer(message.guild.id, message.author.id, 'centennial', '876000')
		output = '%s, you claimed your centennial allowance of %s %s. You currently have %s %s.' % (message.author.mention, grant, currencyName[message.guild.id], balance, currencyName[message.guild.id])
	await sendEmbed(message.channel, 'Centennial', output)


# Can be used once every 24 hours (1 day) to receive a daily allowance
global daily
async def daily (message, args):
	timer = _gettimer(message.guild.id, message.author.id, 'daily')
	if (timer):
		output = 'You have to wait %s before you can claim your daily allowance.' % (prettyTime(timer, 'seconds'))
	else:
		allowance = 500
		balance = prettyNums(_incrementbalance(message.author.id, allowance))
		_settimer(message.guild.id, message.author.id, 'daily', '24')
		output = '%s, you claimed your daily allowance of %s %s. You currently have %s %s.' % (message.author.mention, allowance, currencyName[message.guild.id], balance, currencyName[message.guild.id])
	await sendEmbed(message.channel, 'Daily', output)


# Give currency to single or multiple other users
global give
async def give (message, args):
	users = message.mentions
	# Make sure there's at least 2 arguments and 1 mention
	if args[1] == '' or not users:
		output = 'Please mention an amount of %s to give and who to give it to (e.g. `%sgive 1000 @Code`).' % (currencyName[message.guild.id], prefix)
	# Make sure the user isn't trying to give to themselves
	elif message.author in users and len(users) == 1:
		output = 'You can\'t give %s to yourself.' % (currencyName[message.guild.id])
	else:
		# Didn't see a more sensible way to do this, putting it here for now
		if message.author in users:
			users.remove(message.author)
		# Make sure we have a valid number
		try:
			amount = int(args[0])
		except:
			output = 'Please mention an amount of %s to give and who to give it to (e.g. `%sgive 1000 @Code`).' % (currencyName[message.guild.id], prefix)
		else:
			# Make sure we have a positive number
			if amount < 1:
				output = 'The amount to give must be a postive number (e.g. `%sgive 1000 @Code`).' % (prefix)
			else:
				# Check the balance of the user and make sure they have enough to cover the total
				balance = _getbalance(message.author.id)
				total = amount * len(users)
				if total <= balance:
					# Run the database transactions
					balance = _incrementbalance(message.author.id, -total)
					for i in users:
						_incrementbalance(i.id, amount)
					if len(users) == 1 and amount > 1:
						output = '%s, you gave %s %s to %s. You have %s %s remaining.' % (message.author.mention, prettyNums(amount), currencyName[message.guild.id], users[0].name, prettyNums(balance), currencyName[message.guild.id])
					elif len(users) == 1 and amount == 1:
						output = '%s, you gave %s %s to %s. You have %s %s remaining.' % (message.author.mention, prettyNums(amount), currencyName[message.guild.id][:-1], users[0].name, prettyNums(balance), currencyName[message.guild.id])
					else:
						output = '%s, you gave a total of %s %s to %s users. You have %s %s remaining.' % (message.author.mention, prettyNums(amount * len(users)), currencyName[message.guild.id], len(users), prettyNums(balance), currencyName[message.guild.id])
				else:
					output = '%s, you don\'t have enough %s to give %s. You currently have %s %s.' % (message.author.mention, currencyName[message.guild.id], total, prettyNums(balance), currencyName[message.guild.id])
	await sendEmbed(message.channel, 'Give', output)

# Can be used once every 168 hours (7 days / 1 week) to receive a random weekly allowance
global weekly
async def weekly(message, args):
	timer = _gettimer(message.guild.id, message.author.id, 'weekly')
	if (timer):
		output = 'You have to wait %s before you can claim your weekly allowance.' % (prettyTime(timer, 'seconds'))
	else:
		grant = random.randrange(1750, 7000)
		balance = prettyNums(_incrementbalance(message.author.id, grant))
		grant = prettyNums(grant)
		_settimer(message.guild.id, message.author.id, 'weekly', '168')
		output = '%s, you claimed your weekly allowance of %s %s. You currently have %s %s.' % (message.author.mention, grant, currencyName[message.guild.id], balance, currencyName[message.guild.id])
	await sendEmbed(message.channel, 'Weekly', output)