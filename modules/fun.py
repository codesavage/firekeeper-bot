# Generates a (usually weird) compliment for another user
global compliment
async def compliment(message, args):
	actionVerbs = ['caress', 'grab', 'kiss', 'massage', 'pull', 'smell', 'touch']
	adjectives = ['adventurous', 'affable', 'agreeable', 'ambitious', 'amiable', 'amicable', 'ample', 'awesome', 'beautiful', 'broad', 'captivating', 'charming', 'clever', 'confident', 'considerate', 'cool', 'courteous', 'creative', 'dear', 'deliberate', 'determined', 'diligent', 'dreamy', 'dynamic', 'easygoing', 'elegant', 'energetic', 'erotic', 'exuberant', 'fair', 'faithful', 'friendly', 'generous', 'gleeful', 'great', 'imaginative', 'inquisitive', 'intense', 'interesting', 'intuitive', 'joyful', 'kind', 'lively', 'lovely', 'neat', 'nice', 'passionate', 'persistent', 'pioneering', 'playful', 'plucky', 'polite', 'practical', 'pretty', 'proactive', 'realistic', 'reassuring', 'resourceful', 'romantic', 'safe', 'seductive', 'sensible', 'sexy', 'shiny', 'sick', 'sincere', 'sociable', 'soft', 'special', 'stellar', 'superior', 'supreme', 'sweet', 'tidy', 'thorough', 'thoughtful', 'tremendous', 'triumphant', 'valiant', 'vast', 'wicked', 'yearning', 'youthful', 'zealous', 'zesty']
	adverbs = ['adventurously', 'affably', 'affectionately', 'agreeably', 'ambitiously', 'amusingly', 'creatively', 'dearly', 'decisively', 'deliberately', 'dynamically', 'elegantly', 'entirely', 'enthusiasticly', 'especially', 'faithfully', 'fairly', 'famously', 'fearlessly', 'generously', 'gleefully', 'greatly', 'heavily', 'helplessly', 'honestly', 'hopelessly', 'impartially', 'independently', 'instantly', 'intensely', 'joyfully', 'kindly', 'kind of', 'lovingly', 'madly', 'majestically', 'mighty', 'modestly', 'mysteriously', 'nicely', 'officially', 'optimistically', 'passionately', 'persistently', 'playfully', 'politely', 'positively', 'proactively', 'quite', 'readily', 'realistically', 'really', 'reassuringly', 'regularly', 'seductively', 'sincerely', 'solemnly', 'sort of', 'specially', 'strictly', 'sweetly', 'swiftly', 'thoroughly', 'thoughtfully', 'tremendously', 'truthfully', 'ultimately', 'uniquely', 'utterly', 'valiantly', 'vastly', 'wholly', 'yearningly', 'zealously']
	nonPhysicalNouns = ['attitude', 'brain', 'heart', 'intellect', 'personality']
	singularNouns = ['bosom', 'butt', 'chest', 'chin', 'face', 'hair', 'hairdo', 'mane', 'mouth', 'neck', 'nose', 'skin', 'stomach', 'tongue']
	pluralNouns = ['abs', 'biceps', 'boobs', 'calves', 'cheeks', 'ears', 'eyebrows', 'eyelashes', 'eyes', 'feet', 'fingernails', 'fingers', 'forearms', 'hands', 'hips', 'legs', 'lips', 'shoulders', 'thighs']
	physicalNouns = list(singularNouns) + list(pluralNouns)
	allNouns = list(nonPhysicalNouns) + list(physicalNouns)
	verbs = ['appreciate', 'dig', 'enjoy', 'like']

	def verifyMention(message):
		mentionGood = False
		try:
			mentionedUser = message.mentions[0]
		except:
			output = 'Please mention a user to compliment.'
			mentionedUser = None
		else:
			if mentionedUser == message.author:
				output = 'I\'m sorry, but you can\'t compliment yourself (you narcissist).'
			elif mentionedUser.bot:
				output = 'I\'m sorry, but you can only compliment human users, not bots.'
			elif len(message.mentions) > 1:
				output = 'I\'m sorry, I can only compliment one user at a time.'
			else:
				mentionGood = True
				output = None
		return mentionedUser, output, mentionGood

	def constructCompliment():
		actionVerb = random.choice(actionVerbs)
		targetNoun = random.choice(allNouns)
		verb = random.choice(verbs)
		adjective = random.choice(adjectives)
		adverb = random.choice(adverbs)
		# Make sure we don't have a nearly identical adjective and adverb (i.e., generously generous)
		while adjective[0:4] == adverb[0:4]:
			adjective = random.choice(adjectives)
			adverb = random.choice(adverbs)
		# Set the correct article to use for the adverb
		article = 'a'
		if adverb[0] == 'a' or adverb[0] == 'e' or adverb[0] == 'i' or adverb[0] == 'o' or adverb[0] == 'u':
			article += 'n'
		# Pick a style
		style = random.randrange(0,3)
		if style == 0: # @someone thinks you have a really nice butt, @someone.
			if targetNoun not in pluralNouns or targetNoun != 'hair' or targetNoun != 'skin':
				adverb = article + ' ' + adverb
			elif adjective == 'quite' or adjective == 'such':
				adverb = adverb + ' ' + article
			output = '%s thinks you have %s %s %s, %s.' % (message.author.mention, adverb, adjective, targetNoun, mentionedUser.mention)
		elif style == 1: # Your hand is pretty stellar, @someone.
			if targetNoun in pluralNouns:
				linkingVerb = 'are'
			else:
				linkingVerb = 'is'
			output = '%s thinks your %s %s %s %s, %s.' % (message.author.mention, targetNoun, linkingVerb, adverb, adjective, mentionedUser.mention)
		elif style == 2: # I bet @someone would really like touching @someone's hair right now.
			# Verbs that end in 'b' need an extra consonant for the present participle
			if actionVerb[-1] == 'b':
				actionVerb += 'b'
			# Verbs ending in 'e' drop the vowel for the present participle
			elif actionVerb[-1] == 'e':
				actionVerb = actionVerb[:-1]
			# Reroll noun choice if target is nonPhysical so that you don't get something weird like "x would like touching your attitude"
			if targetNoun in nonPhysicalNouns:
				targetNoun = random.choice(physicalNouns)
			output = '%s would %s %s %sing %s\'s %s right now.' % (message.author.mention, adverb, verb, actionVerb, mentionedUser.mention, targetNoun)
		return output

	if message.author.id == '169268862901157888' and args[0] == 'count':
		output = 'actionVerbs: %s\nadjectives: %s\nadverbs: %s\nallNouns: %s\nverbs: %s' % (len(actionVerbs), len(adjectives), len(adverbs), len(allNouns), len(verbs))
	else:
		mentionedUser, output, mentionGood = verifyMention(message)
		if mentionGood:
			output = constructCompliment()
	await sendEmbed(message.channel, 'Compliment', output)


# Draws random cards from a standard card deck
global draw
async def draw(message, args):
	try:
		drawCount = int(args[0])
	except ValueError:
		drawCount = 0
	if drawCount > 0 and drawCount <= 10:
		deck = ['2 of \U00002663', '2 of \U00002666', '2 of \U00002665', '2 of \U00002660', '3 of \U00002663', '3 of \U00002666', '3 of \U00002665', '3 of \U00002660', '4 of \U00002663',
				'4 of \U00002666', '4 of \U00002665', '4 of \U00002660', '5 of \U00002663', '5 of \U00002666', '5 of \U00002665', '5 of \U00002660', '6 of \U00002663', '6 of \U00002666',
				'6 of \U00002665', '6 of \U00002660', '7 of \U00002663', '7 of \U00002666', '7 of \U00002665', '7 of \U00002660', '8 of \U00002663', '8 of \U00002666', '8 of \U00002665',
				'8 of \U00002660', '9 of \U00002663', '9 of \U00002666', '9 of \U00002665', '9 of \U00002660', '10 of \U00002663', '10 of \U00002666', '10 of \U00002665', '10 of \U00002660',
				'Jack of \U00002663', 'Jack of \U00002666', 'Jack of \U00002665', 'Jack of \U00002660', 'Queen of \U00002663', 'Queen of \U00002666', 'Queen of \U00002665', 'Queen of \U00002660',
				'King of \U00002663', 'King of \U00002666', 'King of \U00002665', 'King of \U00002660', 'Ace of \U00002663', 'Ace of \U00002666', 'Ace of \U00002665', 'Ace of \U00002660']
		if args[1] == 'jokers':
			deck.append('Joker \U0001F0CF')
			deck.append('Joker \U0001F0CF')
		random.shuffle(deck)
		output = '%s draws %s cards:\n' % (message.author.mention, drawCount)
		while drawCount > 0:
			output += '**%s**\n' % (deck[drawCount])
			drawCount -= 1
	else:
		output = 'Please enter a number of cards to draw between 1 and 10 (e.g. `%sdraw 4`).' % (prefix)
	await sendEmbed(message.channel, 'Draw', output)


# Gives fortune-telling answers like the Magic 8-Ball toy
global eightball
async def eightball(message, args):
	if args[0] != '':
		answers = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes, definitely.', 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don\'t count on it.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
		output = ':8ball: ' + random.choice(answers)
	else:
		output = 'You must ask a question to receive an answer.'
	await sendEmbed(message.channel, '8ball', output)


# Records or retrieves a user's quotable quotes
global quote
async def quote(message, args):
	output = ''
	if args[0] != '' and (message.mentions != [] or (message.channel_mentions != [] and args[1] != '')):
		if message.mentions != []:
			quoteUser = message.mentions[0]
			action = 'query'

			if quoteUser.id == botID:
				output = 'Sorry, I just can\'t bring myself to quote myself. It reeks of arrogance. \U0001F47C'
				await sendEmbed(message.channel, 'Quote', output)
				return

			if quoteUser.bot:
				output = 'Sorry, but that\'s a bot. It\'s just not worth the effort for a quote. \U0001F916'
				await sendEmbed(message.channel, 'Quote', output)
				return

			userQuotes = _getquotes(quoteUser.id, message.guild.id)
			if userQuotes is None:
				output = '%s has no quotes from this guild.' % (quoteUser.mention)
				await sendEmbed(message.channel, 'Quote', output)
				return

			selectedQuote = random.choice(userQuotes)
			if debugMode: print('Selected quote: ' + selectedQuote['messagetext'])

			quoteChannel = client.get_channel(selectedQuote['channelid'])
			if quoteChannel is None:
				channelname = selectedQuote['channelname']
			else:
				channelname = quoteChannel.name
			quoteMessage = None
			try:
				quoteMessage = await quoteChannel.fetch_message(selectedQuote['messageid'])
			except:
				pass
			if quoteMessage is None:
				url = ''
			else:
				url = '\n\n[Source](https://discordapp.com/channels/%s/%s/%s)' % (message.guild.id, selectedQuote['channelid'], selectedQuote['messageid'])
			quotecontent = selectedQuote['messagetext']
			quoteTimestamp = selectedQuote['messagetimestamp']

			embed = discord.Embed(title = None, description = quotecontent + url, color = embedColor)
			#embed.set_thumbnail(url = message.author.avatar_url)
			embed.set_author(name = quoteUser.display_name + ' in #' + channelname, icon_url = quoteUser.avatar_url)
			try:
				messageimage = selectedQuote['messageimage']
				embed.set_thumbnail(url = messageimage)
				#embed.set_image(url = messageimage)
			except:
				pass
			embed.set_footer(text = quoteTimestamp)
			await message.channel.send(embed = embed)
		elif message.channel_mentions != []:
			targetChannel = message.channel_mentions[0]
			targetMessage = int(args[1])
			try:
				targetMessage = await targetChannel.fetch_message(targetMessage)
				if targetMessage.author.id == botID:
					output = 'Sorry, I just can\'t bring myself to quote myself. It reeks of arrogance. \U0001F47C'
					await sendEmbed(message.channel, 'Quote', output)
					return
				if targetMessage.author.bot:
					output = 'Sorry, but that\'s a bot. It\'s just not worth the effort for a quote. \U0001F916'
					await sendEmbed(message.channel, 'Quote', output)
					return
			except:
				output = 'Unable to locate message %s. Are you sure that was the correct channel and message id?' % (args[1])
				await sendEmbed(message.channel, 'Quote', output)
				return
			targetUser = targetMessage.author
			action = 'save'
			userQuotes = _getquotes(targetUser.id, message.guild.id)
			exists = False
			if userQuotes:
				for quote in userQuotes:
					if quote['channelid'] == targetChannel.id and quote['messageid'] == targetMessage.id:
						exists = True
						break
			if exists:
				output = output + 'Not saving ' + targetUser.mention + '\'s quote because it was already quoted previously'
				if len(targetMessage.content) > 0:
					output += ':\n"' + targetMessage.content + '"'
				else:
					output += ': '
				embed = discord.Embed(title = 'Quote', description = output, color = embedColor)
				messageimage = ''
				if len(targetMessage.attachments) > 0:
					messageimage = targetMessage.attachments[0]['url']
					if messageimage == '':
						messageimage = targetMessage.attachments[0]['proxy_url']
					embed.set_thumbnail(url = messageimage)
				await message.channel.send(embed = embed)
			else:
				output = output + 'Saving ' + targetUser.mention + '\'s quote:\n'
				if len(targetMessage.content) > 0:
					output += '"' + targetMessage.content + '"'
				embed = discord.Embed(title = 'Quote', description = output, color = embedColor)
				messageimage = ''
				if len(targetMessage.attachments) > 0:
					messageimage = targetMessage.attachments[0]['url']
					if messageimage == '':
						messageimage = targetMessage.attachments[0]['proxy_url']
					embed.set_thumbnail(url = messageimage)
				print(messageimage + '\n\n')
				pp = pprint.PrettyPrinter(depth=6)
				pp.pprint(targetMessage.attachments)
				_savequote(targetUser.id, targetChannel.guild.id, targetChannel.id, targetChannel.name, targetMessage.id, targetMessage.content, messageimage, targetMessage.created_at.strftime('%Y-%m-%d %H:%M:%S'), message.created_at.strftime('%Y-%m-%d %H:%M:%S'), message.author.id, message.author.name + '#' + message.author.discriminator)
				await message.channel.send(embed = embed)
	else:
		output = 'Either supply a user mention (e.g. `%squote @X1#0666`) which will retrieve that user\'s quotes; or supply both a channel mention and message id (`%squote #general 1234567890`) to save a quote for posterity.' % (prefix, prefix)
		await sendEmbed(message.channel, 'Quote', output)

# Rolls dice; users can specify a number of sides and dice
global roll
async def roll(message, args):
	output = ''
	try:
		count = int(args[0])
		if count < 1 or count > 20:
			raise Exception()
	except:
		output = 'Please specify a number of dice to roll between 1 and 20 (e.g. `%sroll 4 d20`).' % (prefix)
	if output == '':
		try:
			sides = int(args[1][1:])
			if args[1][:1].lower() != 'd' or sides < 3 or sides > 100:
				raise Exception()
		except:
			output = 'Please specify a die between d3 and d100 (e.g. `%sroll 4 d20`).' % (prefix)
	if output == '':
		total = 0
		dieOutput = ''
		while count > 0:
			die = random.randrange(1, sides + 1)
			dieOutput += '\U0001F3B2 %s  ' % (die)
			total += die
			count -= 1
		output = '%s rolls %s d%s for a total of **%s**:\n' % (message.author.mention, args[0], sides, total) + dieOutput
	await sendEmbed(message.channel, 'Roll', output)