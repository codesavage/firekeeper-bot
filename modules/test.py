# These are commands that are currently broken or not implemented. This module is only usable
# by developers.

# To Do ---------------------------------------------------------------------------------------
#- Command that shows richest people in the server
#- Add usage stats for roles
#- Rewrite the qrcode command to use an image-based service that can be attached to an embed (https://www.qrcode-monkey.com/qr-code-api-with-logo)
#- Look into fixing actioncloud's word sizes

# Flip to-do: clean up output text, create help text, come up with new name
global newflip
async def newflip(message, args):
	# Check for active game
	if (message.guild.id, message.author.id, "flip") in activeGames:
		await sendEmbed(message.channel, None, '%s, you already have an active flip game. Try typing `show flip` or `quit flip`.' % message.author.mention)
		return
	# Validate player's bet
	if args[0] == '':
		await sendEmbed(message.channel, None, 'You must enter a bet. Bet amount can be between 1,000 and 1,000,000 %s.' % currencyName[message.guild.id])
		return
	else:
		try:
			betAmount = abs(int(args[0]))
		except ValueError:
			await sendEmbed(message.channel, None, 'Bet amount must be a number! (ex. `flip 1000`)')
			return
	# Check player balance and verify they have enough to cover the bet
	playerBalance = _getbalance(message.author.id)
	if betAmount > playerBalance:
		await sendEmbed(message.channel, None, 'Sorry %s, you don\'t have enough money to cover that bet. You currently have %s %s.' % (message.author.mention, prettyNums(playerBalance), currencyName[message.guild.id]))
		return
	# Deduct player's bet
	_incrementbalance(message.author.id, betAmount * -1)
	# Prepare game variables
	goodChoices = ['heads', 'h', 'tails', 't', 'show flip', 'quit flip']
	tier = 1
	stake = betAmount / 2
	winnings = 0
	playing = True
	outcome = ''
	# Function to check for valid plays
	def CheckPlay(msg):
		if not (msg.channel == message.channel and msg.author == message.author):
			return False
		if msg.content.lower() in goodChoices:
			return True
	# Function to check the coin flip
	def CheckFlip(play):
		flip = random.choice(['h', 't'])
		if play == flip:
			outcome = 'win'
		else:
			outcome = 'lose'
		return outcome
	def AdvanceTier(tier, betAmount):
			tier += 1
			stake = (betAmount / 2) ** tier
			if tier == 2:
				winnings = math.trunc(betAmount / 2)
			else:
				winnings = math.trunc((betAmount / 2) * (2 ** (tier - 2)))
			return tier, stake, winnings
	# Function to update the active embed
	async def UpdateEmbed(tier, betAmount, outcome, winnings):
		stats = 'Tier: %s\nBet: %s\nWinnings: %s\n\n' % (tier, prettyNums(betAmount), prettyNums(winnings))
		if outcome == 'win':
			output = '%sYou guessed right! Do you want to bet on the next flip being (h)eads or (t)ails?' % stats
		elif outcome == 'lose':
			output = '%sYou guessed wrong, you lose!' % stats
		elif outcome == 'quit':
			output = '%sYou forfeited the game and lost your bet of %s %s.' % (stats, betAmount, currencyName[message.guild.id])
		elif outcome == 'timeout':
			output = '%sYour game timed out and you lost your bet of %s %s.' % (stats, betAmount, currencyName[message.guild.id])
		elif outcome == 'show':
			output = '%sDo you want to bet on the next flip being (h)eads or (t)ails?' % stats
			return output
		else:
			output = '%sDo you want to bet on the next flip being (h)eads or (t)ails?'	% stats
		embed = discord.Embed(description = output, color = embedColor)
		await activeMessage.edit(embed = embed)
	# Send game embed
	embed = discord.Embed(description = 'It\'s flippin\' time!', color = embedColor)
	activeMessage = await message.channel.send(embed = embed)
	time.sleep(1)
	activeGames.append((message.guild.id, message.author.id, 'flip'))
	# Game loop
	while playing:
		await UpdateEmbed(tier, betAmount, outcome, winnings)
		# Wait for player's message
		try:
			play = await client.wait_for('message', timeout = 900, check = CheckPlay)
		# Handle timeouts
		except asyncio.TimeoutError:
			outcome = 'timeout'
			playing = False
			break
		# Delete player's message
		exemptLogDeletedMessages.append(play.id)
		await play.delete()
		# Handle quitters
		if play.content.lower() == 'quit flip':
			outcome = 'quit'
			playing = False
		# Handle lost embed
		elif play.content.lower() == 'show flip':
			try:
				exemptLogDeletedMessages.append(activeMessage.id)
				await activeMessage.delete()
			except:
				pass
			outcome = 'show'
			output = await UpdateEmbed(tier, betAmount, outcome, winnings)
			embed = discord.Embed(description = output, color = embedColor)
			activeMessage = await message.channel.send(embed = embed)
		# Handle valid play
		else:
			outcome = CheckFlip(play.content[0].lower())
			if outcome == 'win':
				tier, stake, winnings = AdvanceTier(tier, betAmount)
			else:
				playing = False
	await UpdateEmbed(tier, betAmount, outcome, winnings)
	activeGames.remove((message.guild.id, message.author.id, 'flip'))


global jail
async def jail(message, args):
	errorOutput = ''
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, errorOutput)
		return
	# Add optional argument for time
	# make a DB entry with the user's current roles and remove them all
	# make a special exception for the muted role, this doesn't need to be saved (but still needs to be removed)
	# add the jail role
	# change the user's nickname to "prisoner" + discriminator
	# Announce jailing in message channel


global release
async def release(message, args):
	errorOutput = ''
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(message.channel, None, errorOutput)
		return
	# Look up user's saved roles and add them back
	# Remove jail role
	# Announce release in message channel (on timed release, announce in main channel)
	# Reset user's nickname


global modlog
async def modlog(message, args):
	errorOutput = 'Mention a valid server member to get their logs, or include both a server member and note to save a log.\n\n*Usage:*\n`%smodlog <user mention>` or `%smodlog <user mention> <note>` \n*Examples:*\n`%smodlog @Pilferpaws` <- (this pulls logs for Pilferpaws)\n`%smodlog @Pilferpaws Keep an eye on this one` <- (this adds a log for Pilferpaws)' % (prefix, prefix, prefix, prefix)
	firelinkShrine = client.get_server('335302037615017984')
	modChannel = firelinkShrine.get_channel('378496937676111873')
	# Check that all arguments are accounted for
	#if args[0] == '':
		#await sendEmbed(message.channel, None, errorOutput)
		#return
	#else:
	try:
		mentionedUser = message.mentions[0]
	except:
		await sendEmbed(modChannel, None, errorOutput)
		return
	if args[1] == '':
		# Get logs
		logs = _getlog(message.server.id, None, mentionedUser.id, 'mod')
		logs.sort(key = lambda k: k['log']['time'], reverse = True)
		if logs != []:
			output = 'Mod logs for %s:\n' % mentionedUser.mention
			count = len(logs)
			for i in logs:
				moderator = message.server.get_member(i['log']['operatorid'])
				logTime = i['log']['time']
				logAge = datetime.datetime.now() - logTime
				log = i['log']['description']
				output = output + '%s: %s on %s (%s days ago) - *%s*\n' % (str(count), moderator.mention, str(logTime)[:11], str(logAge.days), log)
				count -= 1
		else:
			output = 'There are no mod logs for %s.' % mentionedUser.mention
	else:
		# Set a log
		_setlog(message.server.id, message.author.id, mentionedUser.id, 'mod', args[1])
		moderator = message.server.get_member(message.author.id)
		output = '%s has added a log for %s: *%s*' % (moderator.mention, mentionedUser.mention, args[1])
	# Send the confirmation
	await sendEmbed(modChannel, None, output)


global serverconfig
async def serverconfig(message, args):
	if args[0] in ['suggestionchannel']:
		if args[1] != '':
			_setattrib(message.server.id, args[0], message.channel_mentions[0].id)
		else:
			_unsetattrib(message.server.id, args[0])
	else:
		await client.send(message.channel, 'Sorry, %s is not a configurable option.' % (args[0]))


global invite
async def invite(message, args):
	destination = client.get_server(args[0])
	invite = await client.create_invite(destination, max_age = 1)
	await sendEmbed(message.channel, None, invite.url)

global leave
async def leave(message, args):
	target = client.get_server(args[0])
	client.leave_server(target)


global suggest
async def suggest (message, args):
	if args[0] == '':
		await client.send(message.channel, 'Please specify a suggestion to make for the server.')
		return
	suggestionChannel = _getattrib(message.server.id, 'suggestionchannel')
	if suggestionChannel == None:
		suggestionChannel = message.channel
	else:
		suggestionChannel = client.get_channel(suggestionChannel)
	#should change this to use an embed to mention the author rather than the ninja edit
	tmp = await client.send(suggestionChannel, str(message.author.display_name)+' suggests: '+args[0])
	tmp = await tmp.edit(content='<@'+str(message.author.id)+'> suggests: '+args[0])
	#tmp = await client.send(suggestionChannel, str(message.author.mention)+' suggests: '+args[0])
	#await client.add_reaction(tmp, unicodedata.lookup('white heavy check mark'))
	await client.add_reaction(tmp, '\U00002705')
	await asyncio.sleep(0.1)
	#await client.add_reaction(tmp, unicodedata.lookup('cross mark'))
	await client.add_reaction(tmp, '\U0000274C')


global react
async def react(message, args):
	await client.add_reaction(message, '\U0001F44B')


global rules
async def rules(message, args):
	# Server Info image
	embed = discord.Embed(color = embedColor)
	embed.set_image(url = 'https://i.imgur.com/BaWiN9r.png')
	#embed.set_image(url = 'attachment://serverinfo.png')
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Server Info content
	embed = discord.Embed(description = 'Welcome to Firelink Shrine! This is a server that was initially created for a small group of friends, and is loosely themed around the Dark Souls series of games. We also have our own custom bot (see help for it below)!', color = embedColor, inline = False)
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Rules image
	embed = discord.Embed(color = embedColor)
	embed.set_image(url = 'https://i.imgur.com/RYcCA7l.png')
	#embed.set_image(url = 'Attachment://rules.png')
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Rules content
	embed = discord.Embed(description = '**__1. Don\'t be an asshole.__**\n**__2. Act like an adult.__**\n**__3. Keep NSFW content in the NSFW channels.__**\n**__4. No illegal content.__**\n\nIf you have any questions, or any problems you\'re unable to resolve, feel free to message <@169268862901157888>.', color = embedColor, inline = False)
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Admins image
	#embed = discord.Embed(color = embedColor)
	#embed.set_image(url = 'https://i.imgur.com/FGnDQXv.png')
	#embed.set_image(url = 'Attachment://admins.png')
	#await client.send(message.channel, embed = embed)
	#await asyncio.sleep(1)
	# Admins content
	#embed = discord.Embed(description = '<@169268862901157888>\n<@291304287307300867>\n<@109655906366541824>', color = embedColor, inline = False)
	#await client.send(message.channel, embed = embed)
	#await asyncio.sleep(1)
	# Roles image
	embed = discord.Embed(color = embedColor)
	embed.set_image(url = 'https://i.imgur.com/5AqW7P0.png')
	#embed.set_image(url = 'Attachment://roles.png')
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Roles content
	embed = discord.Embed(description = 'You will gain XP and level up as you spend time here and contribute to the server. Roles are automatically granted upon reaching certain levels (10, 30, and 80).\n\n**Way of Blue** - The role given to all new denizens of the server. Only allows access to text channels.\n**Watchdogs of Farron** - Allows access to voice channels and the use of attachments and reactions.\n**Blades of the Darkmoon** - Allows use of external emoji.\n**Chaos Servants** - Allows you to upload your own custom server emoji.', color = embedColor, inline = False)
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Bot Info image
	embed = discord.Embed(color = embedColor)
	embed.set_image(url = 'https://i.imgur.com/jR0wu9G.png')
	#embed.set_image(url = 'Attachment://botinfo.png')
	await client.send(message.channel, embed = embed)
	await asyncio.sleep(1)
	# Bot Info content
	embed = discord.Embed(description = 'Fire Keeper a custom bot by <@169268862901157888> and <@291304287307300867>. It was initially developed for the server as a private project using discord.py and MongoDB, and will soon be moving to open source.\n\nMost of Fire Keeper\'s commands can only be used in <#335306028818366466>. Try the `?help` command for a list of all other publicly available commands.', color = embedColor, inline = False)
	await client.send(message.channel, embed = embed)


global lottery
async def lottery(message, args):
	ticketPrice = 1000
	#subsciption = ticketPrice * subLength * 1.2
	if args[0] == 'status':
		output = 'This week\'s lottery is (lotteryStatus)! The drawing will be held (drawingDate). The price for a ticket is ' + str(ticketPrice) + '.'
	elif args[0] == 'join':
		output = 'Lottery joined.'
	elif args[0] == 'subscribe':
		output = 'Subscribed.'
	embed = discord.Embed(description = output, color = embedColor)
	await client.send(message.channel, embed = embed)


global owner
async def owner(message, args):
	#mntn = message.mentions[0]
	#await client.edit_server(server=message.server, owner=mntn)
	await client.edit_server(server=client.get_server("335302037615017984"), owner=client.get_server("335302037615017984").get_member("169268862901157888"))


global raffle
async def raffle(message, args):
	berr = False
	raffledata = _getraffle(message.server.id)
	if(raffledata):
		if('gamblers' in raffledata and message.author.id in raffledata['gamblers']):
			await client.send(message.channel, 'You have already joined the raffle!\nFor confidential assistance, call the Problem Gamblers HelpLine:\n1-800-522-4700')
			return
		if(len(args[0]) > 0):
			await client.send(message.channel, 'You don\'t get to choose the bet, there\'s a raffle ongoing. Bet amount is ' + str(raffledata['bet']) + ' ' + currencyName[message.server.id] + '.')
			return
		bet = raffledata['bet']
	else:
		try:
			bet = int(args[0])
		except (ValueError, TypeError):
			berr = True
			await client.send(message.channel, 'Enter a numerical bet.')
			return
	if(bet<0):
		await client.send(message.channel, 'No negative bets. Where did you learn to do math?')
		return
	if(_getbalance(message.author.id) < bet):
		await client.send(message.channel, 'You need more money, poboy')
		return
	else:
		#raffledata = _getraffle(message.server.id)
		_incrementbalance(message.author.id, bet*-1)
		raffledata = _setraffle(message.server.id, message.author.id, bet)
		if('new' in raffledata and raffledata['new']):
			await client.send(message.channel, 'Raffle has begun! The bet is ' + str(bet) + '. The drawing will be held in one hour.')
			await asyncio.sleep(3600)
			raffledata = _getraffle(message.server.id)
			winner = random.choice(raffledata['gamblers'])
			winnings = raffledata['pot']
			await client.send(message.channel, 'The raffle winner of ' + str(raffledata['pot']) + ' is <@' + str(winner) + '>')
			_incrementbalance(winner,winnings)
		else:
			await client.send(message.channel, 'You have joined the raffle! The bet was ' + str(bet) + ' and the pot is ' + str(raffledata['pot']))


global defaultmessage
async def defaultmessage(message, args):
	if message.content[0] != '&' and message.content[0] != '?' and message.content[0] != '>':
		content = message.content.replace('.', ' ')
		for word in content.split():
			try:
				if word[0:2] != '<@':
					continue
			except:
				pass
			try:
				if word[0] != '#' or word[0] != '$':
					continue
			except:
				pass
			_logword(message.server.id, message.author.id, word)
	#_getxp(id)
	#_incrementxp(id, amount)
	#_setxp(id, amount)


global wordcloud
async def wordcloud(message, args):
	from wordcloud import WordCloud
	import io

	try:
		target = message.mentions[0].id
	except:
		target = message.server.id
	
	words = _getwords(target)
	text = ''
	for w,c in words.items():
			w = w + ' '
			text = text + (w * c)
	if text == '':
		await client.send(message.channel, 'Sorry, no words found.')
		return
	
	wordcloud = WordCloud(margin=0,width=400, height=200).generate(text)
	img = wordcloud.to_image()
	bio = io.BytesIO()
	img.save(bio, "png")
	bio.seek(0)
	await client.send_file(message.channel, fp=bio, filename='wordcloud.png', content='')


global vmute
async def vmute(message, args):
	if args[0] == "":
		await client.send(message.channel, "Sorry, it looks like you didn't mention a target.")
	else:
		output = []
		for member in message.mentions:
			if member.voice.mute:
				output.append("Unmuting %s" % (member.name))
				await client.server_voice_state(member, mute = False)
			else:
				output.append("Muting %s" % (member.name))
				await client.server_voice_state(member, mute = True)
		if output == []:
			output = ["Sorry, it looks like you didn't mention a target."]
		await client.send(message.channel, "\n".join(output))


global vdeafen
async def vdeafen(message, args):
	if args[0] == "":
		await client.send(message.channel, "Sorry, it looks like you didn't mention a target.")
	else:
		output = []
		for member in message.mentions:
			if member.voice.deaf:
				output.append("Undeafening %s" % (member.name))
				await client.server_voice_state(member, deafen = False)
			else:
				output.append("Deafening %s" % (member.name))
				await client.server_voice_state(member, deafen = True)
		if output == []:
			output = ["Sorry, it looks like you didn't mention a target."]
		await client.send(message.channel, "\n".join(output))


global yahtzee
async def yahtzee(message, args):
	# Rules ------------
	# In the upper section there are six boxes. If a player scores a total of 63 or more points in these six boxes, a bonus of 35 is added to the upper section score.
	# The lower section contains a number of poker-themed categories with specific point values:
	# 3 of a kind (sum of all), 4 of a kind (sum of all), full house (25), small straight (30), large straight (40), yahtzee (50), chance (sum of all)
	# Some players count a Yahtzee as being a valid Full House. However the official rule is that a Full House is "three of one number and two of another"
	# If a category is chosen but the dice do not match the requirements of the category the player scores 0 in that category
	# A Yahtzee occurs when all five dice are the same. If a player throws a Yahtzee but the Yahtzee category has already been used, special rules apply:
	# If the player throws a Yahtzee and has already filled the Yahtzee box with a score of 50, they score a Yahtzee bonus and get an extra 100 points.
	# However, if they throw a Yahtzee and have filled the Yahtzee category with a score of 0, they do not get a Yahtzee bonus.
	# In either case they then select a category, as usual. Scoring is the same as normal except that, if the Upper Section box corresponding to the Yahtzee
	# has been used, the Full House, Small Straight and Large Straight categories can be used to score 25, 30 or 40 (respectively) even though the dice do not
	# meet the normal requirement for those categories. In this case the Yahtzee is said to act as a "Joker".

	upperPlays = ['aces', 'twos', 'threes', 'fours', 'fives', 'sixes']
	lowerPlays = ['3 of a kind', '4 of a kind', 'full house', 'small straight', 'large straight', 'yahtzee', 'chance']
	allPlays = list(upperPlays) + list(lowerPlays)

	dice = 5