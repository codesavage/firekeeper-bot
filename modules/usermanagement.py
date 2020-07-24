# Generates a chart showing how many times bot commands have been used
global actionchart
async def actionchart(message, args):
	matplotlib.use('Agg')
	import matplotlib.pyplot as plt
	plt.switch_backend('Agg')
	try:
		target = message.mentions[0].id
	except:
		target = message.guild.id
		targetType = 'server'
		name = message.guild.name
		title = 'Commands used in %s' % (name)
	else:
		targetType = 'user'
		name = message.mentions[0].mention
		title = 'Commands used globally by %s' % (message.mentions[0].name)
	words = _getactionlog(target, targetType)
	if len(words) > 0:
		sorted = []
		labels = []
		sizes = []
		for w,c in words.items():
			sorted.append((w, c))
		sorted.sort(key = lambda sorted: sorted[1])
		for item in sorted:
			labels.append(item[0])
			sizes.append(item[1])
		# Plot
		fig = plt.figure(1, figsize = (18, 12))
		ax = fig.add_subplot(111)
		ax.bar(labels, sizes)
		ax.tick_params(axis = 'x', labelrotation = 270.0)
		fig.suptitle(title, va = 'center', y = .95)
		rects = ax.patches
		for i, v in enumerate(sizes):
			yloc = v+1
			ax.text(rects[i].get_x() + rects[i].get_width() / 2, yloc, str(v), color = 'blue', fontweight = 'bold', ha = 'center', va = 'bottom')
		bio = io.BytesIO()
		plt.savefig(bio, format = 'png')
		bio.seek(0)
		#await client.send_file(message.channel, fp = bio, filename = 'actionchart.png', content = '')
		await message.channel.send(file=discord.File(fp=bio, filename='actionchart.png'))
		#embed = discord.Embed(title = 'Actionchart for ' + name, color = embedColor)
		#embed.set_image(url = bio)
		#await client.send(message.channel, embed = embed)
	else:
		await sendEmbed(message.channel, 'Actionchart', 'Sorry, no actions found for %s.' % (name))


global leaderboard
async def leaderboard(message, args):
	argument = args[0]
	arguments = {'arguments', 'currency', 'xp'}
	if argument.lower() not in arguments:
		await sendEmbed(message.channel, 'Leaderboard', 'Sorry, *%s* isn\'t a valid argument. Please use `%sleaderboard arguments` to see all available arguments.' % (argument, prefix))
		return
	members = {}
	oldoutput = ''
	if argument.lower() == 'arguments':
		title = 'Leaderboard Arguments'
		prettyArgs = []
		for i in arguments:
			prettyArgs.append(i.capitalize())
		prettyArgs.sort()
		oldoutput = '\n'.join(prettyArgs)
	elif argument.lower() == 'currency':
		title = 'Global %s Leaderboard' % currencyName[message.guild.id].capitalize()
		for member in client.get_all_members():
			if not member.bot:
				balance = _getbalance(member.id)
				if balance > 0:
					members[member] = balance
	elif argument.lower() == 'xp':
		title = 'XP Leaderboard for %s' % message.guild.name
		for member in message.guild.members:
			if not member.bot:
				xp = _getxp(message.guild.id, member.id)
				if xp > 0:
					members[member] = xp
	members = sorted(members.items(), key = lambda x: -x[1])
	output = ''
	position = 1
	for i in members:
		if argument.lower() == 'currency':
			if i[0] in message.guild.members:
				output += '%s: %s - %s %s\n' % (position, i[0].mention, prettyNums(i[1]), currencyName[message.guild.id])
			else:
				output += '%s: %s - %s %s\n' % (position, i[0].name+'#'+i[0].discriminator, prettyNums(i[1]), currencyName[message.guild.id])
		elif argument.lower() == 'xp':
			output += '%s: %s - Level %s (*%s XP*)\n' % (position, i[0].mention, calculateLevel(i[1]), prettyNums(i[1]))
		position += 1
		if len(output) > 2048:
			break
		oldoutput = output
	if oldoutput == '':
		oldoutput = 'There are no users that have earned %s in this guild.' % argument
	await sendEmbed(message.channel, title, oldoutput)


# Generates a random nickname for a user and locks them out of a nickname change for 30 minutes.
# Due to Discord permissions, this is not usable by the guild owner.
global nick
async def nick(message, args):

	async def setCustomNick(message, cost, nick):
		userBalance = _getbalance(message.author.id)
		if userBalance >= cost:
			await message.author.edit(nick=nick)
			userBalance = _incrementbalance(message.author.id, -cost)
			return '%s, your nickname has been changed as requested. You now have %s %s.' % (message.author.mention, prettyNums(userBalance), currencyName[message.guild.id])
		else:
			return '%s, you don\'t have enough %s to change your nickname (you have %s %s).' % (message.author.mention, currencyName[message.guild.id], prettyNums(userBalance), currencyName[message.guild.id])

	def generateNick():
		adjectives = ['Abundant','Acidic','Aggressive','Agreeable','Alive','Ambitious','Ancient','Angry','Ashen','Ashy','Attractive','Bald','Beautiful','Better','Bewildered','Big','Billions','Bitter','Black','Blue','Brave','Breezy','Brief','Broad','Bumpy','Calm','Careful','Chilly','Chubby','Chubby','Clean','Clever','Clumsy','Cold','Colossal','Cool','Cool','Crashing','Creamy','Crooked','Cuddly','Curved','Damaged','Damp','Dazzling','Dead','Deafening','Deep','Defeated','Delicious','Delightful','Dirty','Disgusting','Drab','Dry','Eager','Early','Easy','Echoing','Elegant','Embarrassed','Enough','Faint','Faithful','Famous','Fancy','Fast','Fat','Few','Fierce','Fit','Flabby','Flaky','Flat','Fluffy','Freezing','Fresh','Full','Future','Gentle','Gifted','Gigantic','Glamorous','Gorgeous','Gray','Greasy','Greasy','Great','Green','Grumpy','Hallowed','Handsome','Happy','Harsh','Helpful','Helpless','High','Hissing','Hollow','Hot','Hot','Howling','Huge','Hundreds','Icy','Icy','Immense','Important','Incalculable','Inexpensive','Itchy','Jealous','Jolly','Juicy','Kind','Large','Late','Lazy','Lemon','Limited','Little','Little','Lively','Long','Long','Loose','Loud','Low','Magnificent','Mammoth','Mango','Many','Massive','Mealy','Melodic','Melted','Microscopic','Millions','Miniature','Modern','Moldy','Most','Muscular','Mushy','Mysterious','Narrow','Nervous','Nice','Noisy','Numerous','Nutritious','Nutty','Obedient','Obnoxious','Odd','Old','Old-Fashioned','Orange','Panicky','Petite','Pitiful','Plain','Plump','Polite','Poor','Powerful','Prehistoric','Prickly','Proud','Puny','Purple','Purring','Putrid','Quaint','Quick','Quiet','Rancid','Rapid','Rapping','Raspy','Red','Refined','Repulsive','Rhythmic','Rich','Ripe','Rotten','Rough','Round','Salmon','Salty','Savory','Scarce','Scary','Scrawny','Screeching','Scruffy','Shaggy','Shallow','Shapely','Sharp','Short','Short','Short','Shrilling','Shy','Silly','Skinny','Skinny','Slimy','Slow','Small','Some','Sour','Sparse','Spicy','Spoiled','Square','Squeaking','Stale','Steep','Sticky','Stocky','Straight','Strong','Substantial','Sweet','Swift','Tall','Tangy','Tart','Tasteless','Tasty','Teeny','Tender','Thankful','Thoughtless','Thousands','Thundering','Tight','Tinkling','Tiny','Ugly','Uneven','Unimportant','Uninterested','Unkempt','Unsightly','Uptight','Vast','Victorious','Wailing','Warm','Weak','Wet','Whining','Whispering','White','Wide','Witty','Wonderful','Wooden','Worried','Wrong','Yellow','Young','Yummy','Zealous']
		specificObjects = ['Angle','Ant','Apple','Arch','Arm','Army','Baby','Bag','Ball','Band','Basin','Basket','Bath','Bed','Bee','Bell','Berry','Bird','Blade','Board','Boat','Bone','Book','Boot','Bottle','Box','Boy','Brain','Brake','Branch','Brick','Bridge','Brush','Bucket','Bulb','Button','Cactus','Cake','Camera','Card','Carriage','Cart','Cat','Chain','Cheese','Chess','Chin','Church','Circle','Clock','Cloud','Coat','Collar','Comb','Cord','Cow','Cup','Curtain','Cushion','Dog','Door','Drain','Drawer','Dress','Drop','Ear','Egg','Engine','Eye','Face','Farm','Feather','Finger','Fish','Flag','Floor','Fly','Foot','Fork','Fowl','Frame','Garden','Girl','Glove','Goat','Gun','Hair','Hammer','Hand','Hat','Head','Heart','Hook','Horn','Horse','Hospital','House','Island','Jewel','Kettle','Key','Knee','Knife','Knot','Leaf','Leg','Library','Line','Lip','Lock','Map','Match','Monkey','Moon','Mouth','Muscle','Nail','Neck','Needle','Nerve','Net','Nose','Nut','Octopus','Office','Orange','Oven','Parcel','Pen','Pencil','Picture','Pig','Pin','Pipe','Plane','Plate','Plough','Pocket','Pot','Potato','Prison','Pump','Rail','Rat','Receipt','Ring','Rod','Roof','Root','Sail','School','Scissors','Screw','Seed','Sheep','Shelf','Ship','Shirt','Shoe','Skin','Skirt','Snake','Sock','Spade','Sponge','Spoon','Spring','Square','Stamp','Star','Station','Stem','Stick','Stocking','Stomach','Store','Street','Sun','Table','Tail','Thread','Throat','Thumb','Ticket','Toe','Tongue','Tooth','Town','Train','Tray','Tree','Trousers','Umbrella','Wall','Watch','Wheel','Whip','Whistle','Window','Wing','Wire','Worm']
		generalObjects = ['Account','Act','Adjustment','Advertisement','Agreement','Air','Amount','Amusement','Animal','Answer','Apparatus','Approval','Argument','Art','Attack','Attempt','Attention','Attraction','Authority','Back','Balance','Base','Behavior','Belief','Birth','Bit','Bite','Blood','Blow','Body','Brass','Bread','Breath','Brother','Building','Burn','Burst','Business','Butter','Canvas','Care','Cause','Chalk','Chance','Change','Cloth','Coal','Color','Comfort','Committee','Company','Comparison','Competition','Condition','Connection','Control','Cook','Copper','Copy','Copy','Cork','Cough','Country','Cover','Crack','Credit','Crime','Crush','Cry','Current','Curve','Damage','Danger','Daughter','Day','Death','Debt','Decision','Degree','Design','Desire','Destruction','Detail','Development','Digestion','Direction','Discovery','Discussion','Disease','Disgust','Distance','Distribution','Division','Doubt','Drink','Driving','Dust','Earth','Edge','Education','Effect','End','Error','Event','Example','Exchange','Existence','Expansion','Experience','Expert','Fact','Fall','Family','Father','Fear','Feeling','Fiction','Field','Fight','Fire','Flame','Flight','Flower','Fold','Food','Force','Form','Friend','Front','Fruit','Glass','Gold','Government','Grain','Grass','Grip','Group','Growth','Guide','Harbor','Harmony','Hate','Hearing','Heat','Help','History','Hole','Hope','Hour','Humor','Ice','Idea','Impulse','Increase','Industry','Ink','Insect','Instrument','Insurance','Interest','Invention','Iron','Jelly','Join','Journey','Judge','Jump','Kick','Kiss','Knowledge','Land','Language','Laugh','Lead','Learning','Leather','Letter','Level','Lift','Light','Limit','Linen','Liquid','List','Look','Loss','Love','Low','Machine','Man','Manager','Mark','Market','Mass','Meal','Measure','Meat','Meeting','Memory','Metal','Middle','Milk','Mind','Mine','Minute','Mist','Money','Month','Morning','Mother','Motion','Mountain','Move','Music','Name','Nation','Need','News','Night','Noise','Note','Number','Observation','Offer','Oil','Operation','Opinion','Order','Organization','Ornament','Owner','Page','Pain','Paint','Paper','Part','Paste','Payment','Peace','Person','Place','Plant','Play','Pleasure','Point','Poison','Polish','Porter','Position','Powder','Power','Price','Print','Process','Produce','Profit','Property','Prose','Protest','Pull','Punishment','Purpose','Push','Quality','Question','Rain','Range','Rate','Ray','Reaction','Reading','Reason','Record','Regret','Relation','Religion','Representative','Request','Respect','Rest','Reward','Rhythm','Rice','River','Road','Roll','Room','Rub','Rule','Run','Salt','Sand','Scale','Science','Sea','Seat','Secretary','Selection','Self','Sense','Servant','Sex','Shade','Shake','Shame','Shock','Side','Sign','Silk','Silver','Sister','Size','Sky','Sleep','Slip','Slope','Smash','Smell','Smile','Smoke','Sneeze','Snow','Soap','Society','Son','Song','Sort','Sound','Soup','Space','Stage','Start','Statement','Steam','Steel','Step','Stitch','Stone','Stop','Story','Stretch','Structure','Substance','Sugar','Suggestion','Summer','Support','Surprise','Swim','System','Talk','Taste','Tax','Teaching','Tendency','Test','Theory','Thing','Thought','Thunder','Time','Tin','Top','Touch','Trade','Transport','Trick','Trouble','Turn','Twist','Unit','Use','Value','Verse','Vessel','View','Voice','Walk','War','Wash','Waste','Water','Wave','Wax','Way','Weather','Week','Weight','Wind','Wine','Winter','Woman','Wood','Wool','Word','Work','Wound','Writing','Year']
		objectNouns = list(specificObjects) + list(generalObjects)
		actionNouns = ['Agreement','Answering','Arrest','Attack','Auction','Awakening','Balancing','Bargaining','Baring','Battle','Bending','Benefit','Blaming','Blast','Blasting','Bleaching','Blooming','Blowing','Bombing','Bothering','Bounce','Bouncing','Christening','Comfort','Cost','Count','Counting','Credit','Crushing','Cure','Cutting','Damage','Dance','Dancing','Decaying','Decrease','Dream','Dressing','Drilling','Echo','Echoing','Emboldening','Escape','Excuse','Experience','Eyeing','Failing','Favor','Fear','Feeling','Fight','Finish','Finishing','Flap','Flapping','Flash','Flashing','Flood','Flow','Frightening','Gazing','Greasing','Handling','Harm','Heating','Hiding','Hope','Hosing','Hug','Humor','Hunt','Inch','Increase','Influence','Insult','Itching','Jailing','Joke','Judge','Jump','Kick','Kiss','Kissing','Laughing','Lie','Light','Lighting','Load','Love','Lying','Manning','March','Mating','Matter','Measure','Measuring','Missing','Mistake','Nailing','Need','Nesting','Orgy','Packing','Paddle','Paddling','Painting','Pause','Peeling','Plant','Play','Plow','Plowing','Poke','Poking','Pop','Production','Protest','Pulling','Punch','Push','Question','Questioning','Quiz','Rant','Rating','Reaping','Recording','Reign','Repair','Request','Rhyme','Riot','Rising','Risk','Rocking','Ruin','Ruination','Rule','Running','Sailing','Sawing','Saying','Scratch','Seasoning','Sharing','Shelter','Shock','Showing','Shrink','Silence','Silencing','Sin','Smoking','Spray','Spraying','Sting','Storm','Stroke','Stroking','Struggle','Study','Stuffing','Support','Surf','Surprise','Surprising','Swap','Talk','Taste','Tasting','Tearing','Tease','Teasing','Test','Thought','Tip','Tiring','Toasting','Touch','Touching','Tour','Trade','Training','Transport','Travel','Treat','Trick','Trim','Tug','Tugging','Twist','Twisting','Value','Visit','Voice','Wake','Walk','Waltz','Watching','Whip','Whisper','Whistle','Wish','Worry','Yawn','Yielding']
		descriptiveNouns = ['Ableism','Activism','Agnosticism','Alcoholism','Altruism','Animalism','Appropriateness','Assertiveness','Atheism','Attractiveness','Autism','Awareness','Awkwardness','Baptism','Bitterness','Blindness','Brightness','Business','Calamitousness','Cannibalism','Carelessness','Chauvinism','Cleanliness','Cleverness','Coldness','Commercialism','Completeness','Consciousness','Counterterrorism','Criticism','Cynicism','Darkness','Distinctiveness','Drunkeness','Dwarfism','Effectiveness','Egotism','Emptiness','Environmentalism','Eroticism','Escapism','Euphemism','Evangelism','Exhibitionism','Existentialism','Exorcism','Fairness','Fanaticism','Fascism','Favoritism','Feminism','Fetishism','Firmness','Fitness','Fondness','Foolishness','Forgiveness','Friendliness','Futurism','Giantism','Goodness','Greatness','Happiness','Heroism','Holiness','Homelessness','Homoeroticism','Humanism','Hpynotism','Idealism','Illness','Kindness','Loneliness','Madness','Materialism','Metabolism','Militarism','Mysticism','Narcism','Nationalism','Nervousness','Nihilism','Nudism','Occultism','Openness','Optimism','Pessimism','Plagiarism','Professionalism','Racism','Radicalism','Readiness','Ridiculousness','Sadism','Sadness','Self-criticism','Selfishness','Seriousness','Sexism','Sickness','Skepticism','Slowness','Softness','Spiritualism','Sweetness','Symbolism','Teetotalism','Tenderness','Terrorism','Tiredness','Thickness','Tourism','Unfairness','Unhappiness','Unkindness','Unwillingness','Usefulness','Vampirism','Vandalism','Ventriloquism','Voyeurism','Weakness','Weariness','Wickedness','Willingness']
		collectiveNouns = ['Armada','Army','Bank','Batch','Battery','Bed','Belt','Bevy','Bouquet','Brood','Bundle','Caravan','Cete','Chain','Clan','Class','Cloud','Clowder','Clutch','Clutter','Colony','Company','Congregation','Corps','Coven','Crowd','Cult','Culture','Deck','Den','Division','Drove','Fleet','Flight','Flock','Flotilla','Forest','Gaggle','Galaxy','Herd','Hive','Host','Keeper','Knot','Leap','Library','Litter','Lodge','Mob','Murder','Nest','Orchard','Order','Pack','Panel','Parliament','Pit','Platoon','Pod','Pride','Quiver','Range','School','Secret','Shrewdness','Slate','Sloth','Sounder','Squad','Stand','Swarm','Team','Thicket','Tribe','Trip','Troop','Troupe','Unit','Wad','Wealth','Yoke']

		styleChoice = random.randrange(0,7)
		word0 = 'abcd'
		word1 = 'abcd'
		word2 = 'abcd'
		newNick = 'abcdefghijklmnopqrstuvwxyzabcdefg'

		while word0[0:4] == word1[0:4]:
			if styleChoice == 0: # adjective + objectNoun (silly bean, wet dog)
				word0 = random.choice(adjectives)
				word1 = random.choice(objectNouns)
				newNick = word0 + ' ' + word1
			elif styleChoice == 1: # objectNoun + actionNoun (crab orgy, garlic cristening)
				word0 = random.choice(objectNouns)
				word1 = random.choice(actionNouns)
				newNick = word0 + ' ' + word1
			elif styleChoice == 2: # actionNoun + of + descriptiveNoun (awakening of firmness)
				word0 = random.choice(actionNouns)
				word1 = random.choice(descriptiveNouns)
				newNick = word0 + ' of ' + word1
			elif styleChoice == 3: # actionNoun + of the + objectNoun + s (emboldening of the zombies, frightening of the crows)
				word0 = random.choice(actionNouns)
				word1 = random.choice(objectNouns) # problem words: cloth (is 'cloths' really a problem though?)
				if word1 == 'man' or word1 == 'woman':
					newNick = word0 + ' of the ' + word1[:-3] + 'men'
				elif word1[-1] == 's' or word1[-2:] == 'ch':
					newNick = word0 + ' of the ' + word1 + 'es'
				elif word1[-1] == 'y':
					if word1[-2:] == 'ey':
						newNick = word0 + ' of the ' + word1[:-2] + 'ies'
					else:
						newNick = word0 + ' of the ' + word1[:-1] + 'ies'
				elif word1[-1] == 'f':
					newNick = word0 + ' of the ' + word1[:-1] + 'ves'
				else:
					newNick = word0 + ' of the ' + word1 + 's'
			elif styleChoice == 4: # adjective + descriptiveNoun (critical numbness, fond silliness)
				word0 = random.choice(adjectives)
				word1 = random.choice(descriptiveNouns)
				newNick = word0 + ' ' + word1
			elif styleChoice == 5: # collectiveNoun + of + descriptiveNoun (secret of objectiveness, cult of nationalism)
				word0 = random.choice(collectiveNouns)
				word1 = random.choice(descriptiveNouns)
				newNick = word0 + ' of ' + word1
			elif styleChoice == 6: # collectiveNoun + of the + adjective + objectNoun (order of the golden dog, keeper of the sacred clown)
				word0 = random.choice(collectiveNouns)
				word1 = random.choice(adjectives)
				word2 = random.choice(objectNouns)
				newNick = word0 + ' of the ' + word1 + ' ' + word2
			if len(newNick) > 32:
				word0 = 'abcd'
				word1 = 'abcd'
		return newNick

	timer = _gettimer(message.guild.id, message.author.id, 'nick')
	if(timer):
		await sendEmbed(message.channel, 'Nick', '%s, you have to wait %s before you can change/reset your nickname.' % (message.author.mention, prettyTime(timer, 'seconds')))
		return

	argument = args[0]
	
	def reactCheck(reaction, user):
		if debugMode:
			print('Reaction added: %s - %s - %s to %s by %s' % (str(reaction.emoji), hex(ord(str(reaction.emoji))), str(reaction.emoji).encode('raw_unicode_escape'), reaction.message.id, user.id))
			print('Looking for message: %s == %s, user: %s == %s' % (reaction.message.id, msg.id, user.id, message.author.id))
			print('Message match: %s' % (reaction.message.id == msg.id))
			print('User match: %s' % (user == message.author))
			print('Emoji match 1: %s' % (str(reaction.emoji) in ['✅', '❌']))
			print('Emoji match 2: %s' % (str(reaction.emoji) in ['\u2705', '\u274c']))
			print('Emoji match 3: %s' % (str(reaction.emoji) in ['\U00002705', '\U0000274C']))
		if reaction.message.id == msg.id and user == message.author and str(reaction.emoji) in ['\U00002705', '\U0000274C']:
			if debugMode:
				print("reactCheck passed")
			return True
		else:
			if debugMode:
				print("reactCheck failed")
			return False

	if message.author == message.guild.owner:
		output = '%s, unforunately Discord permissions don\'t allow me to modify the guild owner\'s nickname.' % message.author.mention
		if argument == '':
			nick = generateNick()
			output += ' However, the name I would have chosen for you is *%s*' % nick
		await sendEmbed(message.channel, 'Nick', output)
		return

	if argument.lower() == 'reset':
			await message.author.edit(nick=None)
			await sendEmbed(message.channel, 'Nick', '%s, your name has been reset.' % message.author.mention)
			return

	elif argument == '':
		nick = generateNick()
		await message.author.edit(nick=nick)
		await sendEmbed(message.channel, 'Nick for @%s' % message.author.name, 'Ashen One, henceforth you shall be called *%s*.' % nick)
		_settimer(message.guild.id, message.author.id, 'nick', '0.5')

	else:
		customCost = 2000
		userBalance = _getbalance(message.author.id)
		if userBalance < customCost:
			await sendEmbed(message.channel, 'Nick', '%s, you don\'t have enough %s to change your nickname (you have %s %s).' % (message.author.mention, currencyName[message.guild.id], prettyNums(userBalance), currencyName[message.guild.id]))
			return
		embed = discord.Embed(title = 'Nick', description = '%s, custom nicknames cost %s %s (you have %s %s). Are you sure you want to change your nickname to *%s*?' % (message.author.mention, prettyNums(customCost), currencyName[message.guild.id], prettyNums(userBalance), currencyName[message.guild.id], argument), color = embedColor)
		msg = await message.channel.send(embed = embed)
		await msg.add_reaction('\U00002705') #white heavy check mark
		await asyncio.sleep(0.1)
		await msg.add_reaction('\U0000274C') #cross mark
		try:
			reaction, user = await client.wait_for('reaction_add', timeout = 10, check = reactCheck)
		except asyncio.TimeoutError:
			await sendEmbed(message.channel, 'Nick', '%s, no answer was received. Your nickname change was cancelled.' % message.author.mention)
			return
		try:
			if str(reaction.emoji) == '\U00002705':
				output = await setCustomNick(message, customCost, argument)
				await sendEmbed(message.channel, 'Nick', output)
			elif str(reaction.emoji) == '\U0000274C':
				await sendEmbed(message.channel, 'Nick', '%s, your nickname change was cancelled.' % message.author.mention)
		except:
			if debugMode:
				print(traceback.format_exc())
			await sendEmbed(message.channel, 'Nick', '%s, an unknown error has occurred. Your nick has not been changed.' % message.author.mention)


# Shows information about a user, such as xp/level, currency balance, and account age
global profile
async def profile(message, args):
	if message.mentions != []:
		user = message.mentions[0]
	else:
		user = message.author
	guildAge = prettyTime(int((datetime.datetime.now() - user.joined_at).total_seconds()), 'days')
	accountAge = prettyTime(int((datetime.datetime.now() - user.created_at).total_seconds()), 'days')
	xp = _getxp(message.guild.id, user.id)
	level = calculateLevel(xp)
	nextLevel = calculateXP(level)
	neededXP = nextLevel - xp
	# Possible profile things: Guild rank (xp, currency, rep), Global rank, Reputation, Achievements
	output = '''
	`Soul level:` %s
	`XP:` %s (*%s to next level*)
	`Balance:` %s %s
	`Joined guild:` %s (*%s ago*)
	`Account created:` %s (*%s ago*)
	''' % (level, xp, neededXP, prettyNums(_getbalance(user.id)), currencyName[message.guild.id], str(user.joined_at)[:11], guildAge, str(user.created_at)[:11], accountAge)
	embed = discord.Embed(title = '%s#%s' % (user.name, user.discriminator), description = output, color = embedColor)
	embed.set_thumbnail(url = user.avatar_url)
	await message.channel.send(embed = embed)


# Lists roles for a user, or list, add, or remove self-assignable roles in a guild
# In the future, this will be used to create or delete roles and add/remove them from the DB as well
# Make sure to add newly created roles to the DB with lower() so the case-insensitivity works
# Might remove the self-assignable check if the user is a mod, so they can add any roles to other users
global roles
async def roles(message, args):
	arguments = ['add', 'remove']
	argument = args[0].lower()
	title = 'Roles'

	def listRoles():
		selfIDs = _getattrib(message.guild.id, 'server', 'selfroles')
		selfRoles = []
		if len(selfIDs) > 0:
			for i in selfIDs:
				for z in message.guild.roles:
					if i == z.id:
						selfRoles.append(z.name)
			selfRoles.sort()

		colorIDs = _getattrib(message.guild.id, 'server', 'colorroles')
		colorRoles = []
		if len(colorIDs) > 0:
			for i in colorIDs:
				for z in message.guild.roles:
					if i == z.id:
						colorRoles.append(z.name)
			colorRoles.sort()
		return selfRoles, colorRoles

	def formatRoles(selfRoles, colorRoles):
		if len(selfRoles) == 0:
			selfOutput = 'There are no self-assignable standard roles.'
		else:
			selfOutput = ''
			for i in selfRoles:
				selfOutput += i + '\n'
		if len(colorRoles) == 0:
			colorOutput = 'There are no self-assignable color roles.'
		else:
			colorOutput = ''
			for i in colorRoles:
				colorOutput += i + '\n'
		return selfOutput, colorOutput

	if argument in arguments:

		selfRoles, colorRoles = listRoles()
		colorRoles = list(map(str.lower, colorRoles))
		if debugMode:
			print('colorRoles: %s' % (colorRoles))
		selfRoles = list(map(str.lower, selfRoles))
		if debugMode:
			print('selfRoles: %s' % (selfRoles))
		roleName = args[1].lower()
		if debugMode:
			print('roleName: %s' % (roleName))
		role = ''

		if argument == 'add':
			# Check to see if a role to add was provided
			if roleName == '':
				await sendEmbed(message.channel, 'Roles', 'You must specify a role to add. Use `%sroles` to see available roles.' % prefix)
				return
			# Check to see if the role provided is valid
			if roleName not in selfRoles and roleName not in colorRoles:
				await sendEmbed(message.channel, 'Roles', '*%s* is not a valid role. Use `%sroles` to see available roles.' % (args[1], prefix))
				return
			# Check to see if role actually exists on the guild (there shouldn't be any inconsistencies here unless roles were added to the DB manually)
			for i in message.channel.guild.roles:
				if i.name.lower() == roleName:
					role = i
					break
			if role == '':
				await sendEmbed(message.channel, 'Roles', 'You must specify a role to add. Use `%sroles` to see available roles.' % prefix)
				return
			# Make sure the user doesn't already have the role
			for i in message.author.roles:
				if i.name.lower() == roleName:
					await sendEmbed(message.channel, 'Roles', '%s already has the *%s* role.' % (message.author.mention, i.name))
					return
			# If the role is a color role, any existing color roles have to be removed first
			if roleName in colorRoles:
				if debugMode:
					print('roleName in colorRoles, checking if a color role is already assigned to this user')
				for i in message.author.roles:
					if debugMode:
						print('Checking role %s - %s' % (i.id, i.name))
					if i.name.lower() in colorRoles:
						if debugMode:
							print('Found color role %s - %s' % (i.id, i.name))
						await message.author.remove_roles(i)
			# Add the role to the user
			await message.author.add_roles(role)
			await sendEmbed(message.channel, 'Roles', '%s has been given the *%s* role.' % (message.author.mention, role))

		elif argument == 'remove':
			# Check to see if a role to add was provided
			if roleName == '':
				await sendEmbed(message.channel, 'Roles', 'You must specify a role to remove. Use `%sroles %s` to see your roles.' % (prefix, message.author.mention))
				return
			# Make sure the role is valid / self-assignable
			if roleName not in selfRoles and roleName not in colorRoles:
				await sendEmbed(message.channel, 'Roles', '*%s* is not a valid role. Use `%sroles` to see all self-assignable roles.' % (roleName, prefix))
				return
			# Check to see if the user has the provided role
			for i in message.author.roles:
				if i.name.lower() == roleName:
					role = i
			if role == '':
				for i in message.guild.roles:
					if i.name.lower() == roleName:
						await sendEmbed(message.channel, 'Roles', 'You do not have the *%s* role. Use `%sroles @%s` to see your roles.' % (i.name, prefix, message.author.name))
						return
			# Remove the role from the user
			await message.author.remove_roles(role)
			await sendEmbed(message.channel, 'Roles', '%s has had the *%s* role removed.' % (message.author.mention, role.name))

	else:
		# If no arguments are provided, pull the list of available roles from the DB
		if args[0] == '':
			selfRoles, colorRoles = listRoles()
			selfRoles, colorRoles = formatRoles(selfRoles, colorRoles)
			embed = discord.Embed(title = 'Available Self-Assignable Roles', color = embedColor)
			embed.add_field(name = 'Standard Roles', value = selfRoles, inline = False)
			embed.add_field(name = 'Color Roles', value = colorRoles, inline = False)
			await message.channel.send(embed = embed)
		# If a username is provded as an argument, pull that user's current roles
		elif message.mentions != []:
			if args[0][2:-1] == message.mentions[0].id or args[0][3:-1] == message.mentions[0].id:
				print('args[0]: %s' % args[0])
				print('message.mentions[0]: %s' % message.mentions[0])
				user = message.mentions[0]
				output = ''
				for i in user.roles:
					if i.name != '@everyone':
						output += i.name + '\n'
				await sendEmbed(message.channel, 'Roles for %s' % user.name, output)
		# If an invalid argument is provided
		else:
			await sendEmbed(message.channel, 'Roles', '*%s* is not a valid argument (see `%shelp roles` for help with this command).' % (args[0], prefix))

global roleadmin
async def roleadmin(message, args):
	# args are action and arguments
	arguments = ['add', 'create', 'delete', 'remove', 'setdefault']
	argument = args[0].lower()
	title = 'Roles'
	selfIDs = _getattrib(message.guild.id, 'server', 'selfroles')
	colorIDs = _getattrib(message.guild.id, 'server', 'colorroles')

	def listRoles():
		selfIDs = _getattrib(message.guild.id, 'server', 'selfroles')
		selfRoles = []
		if len(selfIDs) > 0:
			for i in selfIDs:
				for z in message.guild.roles:
					if i == z.id:
						selfRoles.append('%s -> %s' % (z.name, z.id))
			selfRoles.sort()

		colorIDs = _getattrib(message.guild.id, 'server', 'colorroles')
		colorRoles = []
		if len(colorIDs) > 0:
			for i in colorIDs:
				for z in message.guild.roles:
					if i == z.id:
						colorRoles.append('%s -> %s' % (z.name, z.id))
			colorRoles.sort()

		discordRoles = []
		for z in message.guild.roles:
			if z.id not in colorIDs and z.id not in selfIDs and not z.is_default():
				discordRoles.append('%s -> %s' % (z.name, z.id))
		discordRoles.sort()
		return selfRoles, colorRoles, discordRoles

	def formatRoles(selfRoles, colorRoles, discordRoles):
		if len(selfRoles) == 0:
			selfOutput = 'There are no self-assignable standard roles.'
		else:
			selfOutput = ''
			for i in selfRoles:
				selfOutput += i + '\n'
		if len(colorRoles) == 0:
			colorOutput = 'There are no self-assignable color roles.'
		else:
			colorOutput = ''
			for i in colorRoles:
				colorOutput += i + '\n'
		if len(discordRoles) == 0:
			discordOutput = 'There are no unmanaged Discord roles.'
		else:
			discordOutput = ''
			for i in discordRoles:
				discordOutput += i + '\n'
		return selfOutput, colorOutput, discordOutput
	
	# If no arguments are provided, pull the list of available roles from the DB
	selfRoles, colorRoles, discordRoles = listRoles()
	if args[0] == '':
		selfRoles, colorRoles, discordRoles = formatRoles(selfRoles, colorRoles, discordRoles)
		embed = discord.Embed(title = 'Available Self-Assignable Roles', color = embedColor)
		embed.add_field(name = 'Standard Roles', value = selfRoles, inline = False)
		embed.add_field(name = 'Color Roles', value = colorRoles, inline = False)
		embed.add_field(name = 'Unmanaged Discord Roles', value = discordRoles, inline = False)
		await message.channel.send(embed = embed)

	argDetails = args[1].split()
	role = ''
	if argument == 'add':
		# Check to see if a role to add was provided
		roleId = ''
		try:
			roleId = int(argDetails[0])
			if len(argDetails) < 2 or (argDetails[1] != 'color' and argDetails[1] != 'self'):
				raise ValueError()
		except:
			await sendEmbed(message.channel, 'Roleadmin', 'You must specify a role to add and what type of role it is (self or color). Use `%sroleadmin` to see available roles.' % prefix)
			return
		# Check to see if the role provided is valid
		if roleId not in [role.id for role in message.channel.guild.roles]:
			await sendEmbed(message.channel, 'Roleadmin', '*%s* is not a valid roleid on this guild. Use `%sroleadmin` to see available roles.' % (roleId, prefix))
		else:
			for i in message.channel.guild.roles:
				if i.id == roleId:
					role = i
					break
			_insertattrib(message.channel.guild.id, 'server', argDetails[1]+'roles', roleId)
			await sendEmbed(message.channel, 'Roleadmin', '%s has been added to the managed %s roles list.' % (role.name, argDetails[1]))
	elif argument == 'create':
		pass
	elif argument == 'delete':
		pass
	elif argument == 'remove':
		# Check to see if a role to remove was provided
		try:
			roleId = int(argDetails[0])
		except:
			await sendEmbed(message.channel, 'Roleadmin', 'You must specify a role id to remove. Use `%sroleadmin` to see available roles.' % prefix)
			return
		# Check to see if the role provided is valid
		if roleId not in [role.id for role in message.channel.guild.roles]:
			await sendEmbed(message.channel, 'Roleadmin', '*%s* is not a valid roleid on this guild. Use `%sroleadmin` to see available roles.' % (args[1], prefix))
		else:
			if roleId not in colorIDs and roleId not in selfIDs:
				await sendEmbed(message.channel, 'Roleadmin', '*%s* is not a managed roleid on this guild. Use `%sroleadmin` to see available roles.' % (args[1], prefix))
			else:
				if roleId in colorIDs:
					_unsetattrib(message.channel.guild.id, 'server', 'colorroles', roleId)
					roleType = 'color'
				elif roleId in selfIDs:
					_unsetattrib(message.channel.guild.id, 'server', 'selfroles', roleId)
					roleType = 'self'
				await sendEmbed(message.channel, 'Roleadmin', '%s has been removed from the managed %s roles list.' % (roleId, roleType))
	elif argument == 'setdefault':
		roleId = args[1]
		if roleId == '':
			await sendEmbed(message.channel, 'Roleadmin', 'You must specify a role id to be added to all newly joining members. Use `%sroleadmin` to see available roles.' % (args[1], prefix))
		elif roleId not in [role.id for role in message.channel.guild.roles]:
			await sendEmbed(message.channel, 'Roleadmin', '*%s* is not a valid roleid on this guild. Use `%sroleadmin` to see available roles.' % (args[1], prefix))
		else:
			_setattrib(message.channel.guild.id, 'server', 'defaultrole', roleId)
			await sendEmbed(message.channel, 'Roleadmin', '*%s* has been set as the default role for all newly joining members.' % (roleId))
	# If an invalid argument is provided
	elif args[0] != '':
		await sendEmbed(message.channel, 'Roleadmin', '*%s* is not a valid argument (see `%shelp roleadmin` for help with this command).' % (args[0], prefix))