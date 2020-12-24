# Play a game of Blackjack / 21
global blackjack
async def blackjack(message, args):
	class InactiveError(Exception):
		pass

	class NotIdenticalRanksError(Exception):
		pass

	class TooManyCardsError(Exception):
		pass

	class Table:
		def __init__(self, user = None, bet = 0):
			self.seats = []
			self.insuranceOffered = False
			self.activeSeat = None
			self.user = user
			self.bet = bet

			self.shoe = getShoe(self.user.id)
			if self.shoe == None or len(self.shoe) < 30:
				self.shoe = newShoe()
				setShoe(self.user.id, self.shoe)
			if len(self.shoe) == 52*6:
				self.newShoe = True

			self.dealer = Seat(dealer = True, table = self)
			self.activeSeat = Seat(user = self.user, table = self, bet=self.bet)
			self.seats.append(self.activeSeat)
			
			self.activeSeat.activeHand().hit()
			self.dealer.activeHand().hit()
			self.activeSeat.activeHand().hit()
			self.dealer.activeHand().hit()
			if int(self.dealer.activeHand().cards[1]) == 11:
				self.insuranceOffered = True

		def __len__(self):
			return len(self.seats)
		
		def __iter__(self):
			return iter(self.seats)

		def __str__(self):
			output = []
			output.append('```Welcome to 21!')
			output.append('')
			output.append('Dealer: %s' % (self.dealer))
			handJustification = ''
			output.append('  Hand: %s' % (self.dealer.showactiveHand()))
			output.append('')
			i = 1
			for seat in self:
				output.append('Player: %s' % (seat))
				for hand in seat:
					if len(seat) == 1:
						handNumStr = ''
					else:
						handNumStr = ' %s' % (i)
					if hand == seat.activeHand() and len(hand.currentAllowedPlays):
						actions = [play.title() for play in hand.currentAllowedPlays]
						if self.insuranceOffered:
							actions.insert(0, "Insurance")
						actionsStr = ', '.join(actions)
						output.append('  Hand%s: %s - %s?' % (handNumStr, hand, actionsStr))
					else:
						output.append('  Hand%s: %s' % (handNumStr, hand))
					i += 1
			if self.seats[0].quit:
				output.append('\nPlayer quits.')
			output.append('```')
			return '\n'.join(output)

		def activePlayers(self):
			return [seat.user.id for seat in self if seat.isPlaying()]
			
		def dealCard(self):
			tempCard = self.shoe.pop()
			card = Card(tempCard[0], tempCard[1])
			return card

		def hasPossibleWinners(self):
			return (len([hand for seat in self for hand in seat if not hand.busted() and not hand.surrendered]) > 0)
		
		def finale(self):
			tablestr = str(self)
			output = ['```']
			if table.dealer.activeHand().busted():
				output.append('Dealer busted.\n')
			for seat in self:
				output.append('Player: %s' % (seat.name))
				if seat.insured:
					if seat.insurancePaid:
						winnings = seat.bet
						refund = seat.bet * .5
						_incrementbalance(message.author.id, int(winnings + refund))
						output.append('  Insurance pays out %s %s.' % (seat.bet, currencyName[message.guild.id]))
					else:
						output.append('  Insurance loses %s %s.' % (int(seat.bet * .5), currencyName[message.guild.id]))
				i = 1
				for hand in seat:
					if hand.surrendered:
						# on surrender, refund half the original bet
						winnings = 0
						refund = hand.bet * .5
						_incrementbalance(message.author.id, int(winnings + refund))
						output.append('  Hand %s surrendered. %s %s refunded.' % (i, int(hand.bet * .5), currencyName[message.guild.id]))
					elif hand.busted():
						# if player busts, payout nothing
						output.append('  Hand %s busts. %s %s lost.' % (i, hand.bet, currencyName[message.guild.id]))
						pass
					elif len(hand) >= charlie:
						# if player wins by charlie, payout 1:1
						winnings = hand.bet
						refund = hand.bet
						_incrementbalance(message.author.id, int(winnings + refund))
						output.append('  Hand %s charlie wins %s %s!' % (i, winnings, currencyName[message.guild.id]))
					elif table.dealer.activeHand().busted() or int(hand) > int(table.dealer.activeHand()):
						# if player wins by natural blackjack, payout 3:2
						if hand.natural():
							winnings = int(hand.bet * 1.5)
							refund = hand.bet
							_incrementbalance(message.author.id, int(winnings + refund))
							output.append('  Hand %s wins %s %s with natural blackjack!' % (i, winnings, currencyName[message.guild.id]))							
						# if player wins any other way, payout 1:1
						else:
							winnings = hand.bet
							refund = hand.bet
							_incrementbalance(message.author.id, int(winnings + refund))
							output.append('  Hand %s wins %s %s!' % (i, winnings, currencyName[message.guild.id]))	
					# any other scenario means dealer beat player, payout nothing.
					elif int(table.dealer.activeHand()) == int(hand):
						winnings = 0
						refund = hand.bet
						_incrementbalance(message.author.id, int(winnings + refund))
						output.append('  Hand %s pushes. %s %s refunded.' % (i, refund, currencyName[message.guild.id]))
					else:
						output.append('  Hand %s loses %s %s.' % (i, hand.bet, currencyName[message.guild.id]))
					i += 1
			output.append('\nCurrent balance: %s %s' % (prettyNums(_getbalance(table.seats[0].user.id)), currencyName[message.guild.id]))
			output.append('```')
			return tablestr + '\n'.join(output)

	class Seat:
		def __init__(self, user = None, table = None, dealer = False, bet = 0):
			if dealer:
				self.name 		= random.choice(['Wilbur', 'Charles', 'Lawrence', 'Eugene', 'Stanley', 'Lynn', 'Jessi', 'Karen', 'Peggy', 'Vicki'])
				self.showBoth   = False
			else:
				self.name 		= user.display_name
				self.id			= user.id
				self.user		= user
				self.showBoth   = True
			self.bet			= bet
			self.dealer 		= dealer
			self.currHand		= Hand(seat = self, bet = self.bet)
			self.hands			= []
			self.hands.append(self.currHand)
			self.quit			= False
			self.insured		= False
			self.insurancePaid	= False
			self.table 			= table

		def __len__(self):
			return len(self.hands)
		
		def __iter__(self):
			return iter(self.hands)

		def __str__(self):
			return self.name

		def __repr__(self):
			return '%s - %s' % (self.name, self.hands)

		def isPlaying(self):
			return (len([hand for hand in self if hand.active()]) > 0)
		
		def activeHand(self):
			if self.dealer:
				return self.hands[0]
			activeHands = [hand for hand in self if hand.active()]
			if len(activeHands):
				return activeHands[0]
			else:
				return None
		
		def showactiveHand(self):
			if self.showBoth or not self.dealer:
				return str(self.activeHand())
			else:
				return ', '.join(['??', str(self.activeHand().cards[1])])

	class Hand:

		beginningPlays = ['hit', 'stand', 'double', 'surrender']

		def __init__(self, seat = None, cards = [], bet = 0):
			self.seat = seat
			self.bet = bet
			self.cards = list(cards)
			self.currentAllowedPlays = list(self.beginningPlays)
			self.stood = False
			self.surrendered = False

		def __len__(self):
			return len(self.cards)
		
		def __iter__(self):
			return iter(self.cards)

		def __str__(self):
			return ', '.join([str(card) for card in self.cards])

		def __int__(self):
			handValue = 0
			aces = 0
			for card in self.cards:
				if card.rank == 'A':
					aces += 1
				handValue += int(card)
			while aces > 0 and handValue > 21:
				aces -= 1
				handValue -= 10
			return handValue

		def active(self):
			if self.seat.dealer:
				return (not self.busted() and not self.stood and not self.surrendered and not int(self) == 21)
			else:
				return (not self.busted() and not self.stood and not self.surrendered and len(self) < charlie and not int(self) == 21)
			

		def blackjack(self):
			return (int(self) == 21)
		
		def busted(self):
			return (int(self) > 21)
		
		def natural(self):
			return (self.blackjack() and len(self) == 2)

		def hit(self):
			#print(traceback.print_stack())
			#time.sleep(3)
			if not self.active():
				raise InactiveError("You can't play on this hand right now.")
			parentTable = self.seat.table
			tmpCard = parentTable.dealCard()
			#print("%s" % (tmpCard))
			self.cards.append(tmpCard)
			if len(self) == 2 and self.cards[0].rank == self.cards[1].rank:
					self.currentAllowedPlays.append('split')
			elif len(self) > 2:
				try:
					self.currentAllowedPlays.remove('split')
				except:
					pass
				try:
					self.currentAllowedPlays.remove('double')
				except:
					pass
				try:
					self.currentAllowedPlays.remove('surrender')
				except:
					pass
			if self.busted():
				self.currentAllowedPlays.clear()

		def stand(self):
			if not self.active():
				raise InactiveError("You can't play on this hand right now.")
			self.currentAllowedPlays.clear()
			self.stood = True

		def double(self):
			if not self.active():
				raise InactiveError("You can't play on this hand right now.")
			if(len(self) > 2):
				raise TooManyCardsError
			self.currentAllowedPlays.clear()
			self.hit()
			if self.active():
				self.stand()

		def split(self):
			if not self.active():
				raise InactiveError("You can't play on this hand right now.")
			if len(self) == 2:
				if int(self.cards[0]) == int(self.cards[1]):
					try:
						self.currentAllowedPlays.remove('split')
					except:
						pass
					newHand = Hand(seat = self.seat, cards = [self.cards.pop(1)], bet = self.bet)
					self.hit()
					newHand.hit()
					if(self.cards[0].rank == 'A'):
						if newHand.active():
							newHand.stand()
						if self.active():
							self.stand()
					self.seat.hands.append(newHand)
				else:
					raise NotIdenticalRanksError("You don't have two of the same card to split.")
			else:
				raise TooManyCardsError("You've been dealt too many cards to split now.")

		def surrender(self):
			if len(self.seat) > 1 or len(self) > 2:
				raise TooManyCardsError("You've been dealt too many cards to surrender now.")
			else:
				activeHand().allowedPlays.clear()
				self.surrendered = True

	class Card:
		def __init__(self, rank, suite):
			self.rank = rank
			self.suite = suite

		def __str__(self):
			return "%s%s" % (self.rank, self.suite)

		def __int__(self):
			try:
				val = int(self.rank)
			except:
				if self.rank == 'A':
					val = 11
				else:
					val = 10
			return val

	def getShoe(userId):
		userShoe = _getattrib(userId, 'user', 'bjShoe')
		if userShoe != None:
			userShoe = collections.deque(userShoe)
		return userShoe

	def newShoe():
		cards 		= [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
		suites 		= ['\U00002663', '\U00002666', '\U00002665', '\U00002660']
		subdecks	= [ [(card, suite) for card in cards] for suite in suites]
		deck   		= [card for sublist in subdecks for card in sublist]
		shoe 		= list(deck) + list(deck) + list(deck) + list(deck) + list(deck) + list(deck)
		random.shuffle(shoe)
		return collections.deque(shoe)

	def setShoe(userId, userShoe):
		_setattrib(userId, 'user', 'bjShoe', list(userShoe))

	def playCheck(msg):
		if not (msg.channel == message.channel and msg.author == message.author):
			return False
		actions = list(table.activeSeat.activeHand().currentAllowedPlays)
		if table.insuranceOffered:
			actions.append('insurance')
		actions.append('quit 21')
		actions.append('show 21')
		if msg.author.id in table.activePlayers() and (msg.content.lower() in actions):
			return True
	
	# Setup variables
	charlie = 5
	shoe = None

	# Check arguments
	if (message.guild.id, message.author.id, "blackjack") in activeGames:
		await message.channel.send("%s has an active blackjack game. Try typing `show 21`, or `quit 21`." % (message.author.name))
		return

	if args[0] == 'shuffle':
		setShoe(message.author.id, newShoe())
		await message.channel.send("Shoe shuffled for %s." % (message.author.name))
		return

	# Check bet
	betArgs = ['daily', 'weekly', 'annual', 'centennial']
	betCmds = ['bet = 500', 'bet = random.randrange(1750, 7000)', 'bet = random.randrange(91250, 365000)', 'bet = random.randrange(9125000, 36500000)']
	if bet in betArgs:
		timer = _gettimer(message.guild.id, message.author.id, bet)
		if (timer):
			await message.channel.send('You have to wait %s before you can claim your %s allowance.' % (prettyTime(timer, 'seconds'), bet))
			return
		else:
			_settimer(message.guild.id, message.author.id, bet, '24')
			exec(betCmds[betArgs.index(bet)])
	else:
		try:
			bet = int(args[0])
		except (ValueError, TypeError) as e:
			bet = -1

		if bet < 0:
			await message.channel.send("Bet must be either 0 or a positive number.")
			return

		userBalance = _getbalance(message.author.id)

		if bet > userBalance:
			await message.channel.send("You're a little short. Current balance: %s" % (prettyNums(userBalance)))
			return

	_incrementbalance(message.author.id, bet * -1)

	# Send intro message
	activeMessage = await message.channel.send("Welcome to 21, %s!" % (message.author.mention))
	time.sleep(1)
	activeGames.append((message.guild.id, message.author.id, "blackjack"))

	# Begin game
	table = Table(user = message.author, bet = bet)
	await activeMessage.edit(content=table)

	# Player plays
	while table.activePlayers():
		# Wait for player's message
		play = await client.wait_for('message', timeout = 900, check=playCheck)
		# Handle timeouts and quits
		if play == None or play.content.lower() == 'quit 21':
			table.seats[0].quit = True
			await activeMessage.edit(content=table)
			activeGames.remove((message.guild.id, message.author.id, "blackjack"))
			return

		# Handle requests to refresh the game message
		elif play.content.lower() == 'show 21':
			try:
				exemptLogDeletedMessages.append(activeMessage.id)
				await activeMessage.delete()
			except:
				pass
			activeMessage = await message.channel.send("Excuse me, %s? You were playing 21 here." % (table.seats[0].user.mention))
			time.sleep(2)

		# Handle insurance
		elif play.content.lower() == 'insurance':
			if not table.insuranceOffered:
				await message.channel.send("Insurance isn't currently offered.")
			else:
				userBalance = _getbalance(message.author.id)
				if int(bet*.5) > userBalance:
					await message.channel.send("You're a little short. Current balance: %s, Insurance: %s" % (prettyNums(userBalance), int(bet*.5)))
				else:
					_incrementbalance(message.author.id, int(bet * -.5))
					table.activeSeat.insured = True
					if int(table.dealer.activeHand().cards[0]) == 10:
						table.activeSeat.insurancePaid = True
					table.dealer.showBoth = True
				table.insuranceOffered = False
		elif table.insuranceOffered:
			table.insuranceOffered = False
		# Handle surrender
		if play.content.lower() == 'surrender':
			if len(table.activeSeat) == 1 and len(table.activeSeat.activeHand()) == 2:
				table.activeSeat.activeHand().surrendered = True
			else:
				await message.channel.send("You can't surrender right now.")

		# Handle double
		elif play.content.lower() == 'double':
			userBalance = _getbalance(message.author.id)
			if bet > userBalance:
				await message.channel.send("You're a little short. Current balance: %s, Bet: %s" % (prettyNums(userBalance), bet))
			else:
				_incrementbalance(message.author.id, bet * -1)
				table.activeSeat.activeHand().bet = table.activeSeat.activeHand().bet * 2
				table.activeSeat.activeHand().double()

		# Handle stand
		elif play.content.lower() == 'stand':
			table.activeSeat.activeHand().stand()

		# Handle hit
		elif play.content.lower() == 'hit':
			table.activeSeat.activeHand().hit()

		# Handle split
		elif play.content.lower() == 'split':
			userBalance = _getbalance(message.author.id)
			if bet > userBalance:
				await message.channel.send("You're a little short. Current balance: %s, Bet: %s" % (prettyNums(userBalance), bet))
			else:
				_incrementbalance(message.author.id, bet * -1)
				table.activeSeat.activeHand().split()
				#try:
				#	table.activeSeat.activeHand().split()
				#except:
				#	await message.channel.send("You can't split %s" % (table.activeSeat.activeHand()))

		await activeMessage.edit(content=table)

	time.sleep(1)

	#Dealer plays
	table.dealer.showBoth = True
	await activeMessage.edit(content=table)
	time.sleep(1)
	while table.hasPossibleWinners() and int(table.dealer.activeHand()) < 17:
		table.dealer.activeHand().hit()
		await activeMessage.edit(content=table)
		time.sleep(2)

	#Cleanup
	activeGames.remove((message.guild.id, message.author.id, "blackjack"))
	setShoe(message.author.id, table.shoe)

	await activeMessage.edit(content=table.finale())


# Flip a coin and guess which side it lands on
global flip
async def flip(message, args):
	playerBalance = _getbalance(message.author.id)
	try:
		betAmount = abs(int(args[0]))
		betFlip = str(args[1])
	except ValueError:
		await message.channel.send('Bet amount must be a number and you must choose heads or tails! (ex. flip 100 heads)')
		return
	betFlip = betFlip.lower()
	if betFlip == 'heads' or betFlip == 'h' or betFlip == 'tails' or betFlip == 't':
		#betFlip = betFlip[:1]
		if betAmount > playerBalance:
			await message.channel.send('Not enough money to cover the bet! You currently have '+str(playerBalance)+' '+currencyName[message.guild.id]+'.')
		else:
			tmp = await message.channel.send('The flip is...')
			await asyncio.sleep(1)
			flipResult = random.choice(['heads', 'tails'])
			if flipResult[:1] == betFlip[:1]:
				await tmp.edit(content='The flip is %s! You win %s %s.' % (flipResult, betAmount, currencyName[message.guild.id]))
				winnings = betAmount
			else:
				await tmp.edit(content='The flip is %s. You lose %s %s.' % (flipResult, betAmount, currencyName[message.guild.id]))
				winnings = betAmount * -1
			_incrementbalance(message.author.id, winnings)
	else:
		await message.channel.send('You must bet on either heads or tails! (ex. flip 100 heads)')


# Play the word-guessing game of Hangman
global hangman
async def hangman(message, args):
	class HangmanGame:

		userBalance = _getbalance(message.author.id)
		totalGuesses = 0
		correctGuesses = 0
		incorrectGuesses = 0
		lettersFound = 0
		accuracy = 100
		payout = 0
		hangman = [' ', ' ', ' ', ' ', ' ', ' ']
		hangmanFull = ['0', '/', '|', '\\', '/', '\\']
		allLetters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
		def GetBet():
			if args[1] == '':
				x = 0
			else:
				try:
					x = int(args[1])
				except:
					return None
				else:
					if x < 10 or x > 100000:
						return None
					elif x > s.userBalance:
						return NotImplemented
			return x

		def GetCategory():
			animals = ['BEAR', 'BISON', 'BLUE WHALE', 'BOA CONSTRICTOR', 'BUFFALO', 'CATFISH', 'CHICKEN', 'COYOTE', 'DEER', 'DINGO', 'DOLPHIN', 'DUCK', 'EAGLE', 'GORILLA', 'GREY WOLF', 'HAMMERHEAD SHARK', 'HORSE', 'HOUSECAT', 'JAGUAR', 'LION', 'LOBSTER', 'MONKEY', 'MOOSE', 'OCTOPUS', 'ORANGUTANG', 'PANTHER', 'PYTHON', 'RABBIT', 'SALMON', 'SPIDER', 'STALLION', 'STURGEON', 'SWINE', 'TIGER', 'TURKEY', 'WOLF', 'ZEBRA']
			anime = ['BACCANO', 'BAKEMONOGATARI', 'BERSERK', 'BLACK LAGOON', 'CHOBITS', 'CITY HUNTER', 'CLANNAD', 'CLAYMORE', 'CODE GEASS', 'COWBOY BEBOP', 'CREST OF THE STARS', 'DARKER THAN BLACK', 'DEATH NOTE', 'DURARARA', 'ELF: A TALE OF MEMORIES', 'ELFEN LIED', 'ERGO PROXY', 'EXCAFLOWNE', 'EUREKA SEVEN', 'FLCL', 'FIST OF THE NORTH STAR', 'FULLMETAL ALCHEMIST', 'FUTURE BOY CONAN', 'FUTURE DIARY', 'GAMBLING APOCALYPSE KAIJI', 'GHOST IN THE SHELL', 'GHOST IN THE SHELL: STAND ALONE COMPLEX', 'GOLDEN BOY', 'GOODBYE MR DESPAIR', 'GUARDIAN OF THE SACRED SPIRIT', 'GUNGRAVE', 'HAIBANE RENMEI', 'HAJIME NO IPPO', 'HELLSING ULTIMATE', 'HUNTER X HUNTER', 'INUYASHA', 'JOJO\'S BIZARRE ADVENTURE', 'KAIBA', 'KALEIDO STAR', 'KATANAGATARI', 'KIMAGURE ORANGE ROAD', 'KIMI NI TODOKE', 'KOI KAZE', 'LEGEND OF THE GALACTIC HEROES', 'MAISON IKKOKU', 'MICHIKO AND HATCHIN', 'MOBILE SUIT GUNDAM', 'MONONOKE', 'MONSTER', 'MUSHI-SHI', 'NATSUME YUJINCHO', 'NEON GENESIS EVANGELION', 'NOBODY\'S BOY REMI', 'NODAME KANTABIRE', 'NOW AND THEN, HERE AND THERE', 'OURAN HIGH SCHOOL HOST CLUB', 'PHANTOM: REQUIEM FOR THE PHANTOM', 'PLANETES', 'PRINCESS TUTU', 'RAINBOW: NISHAKUBOU NO SHICHININ', 'REVOLUTIONARY GIRL UTENA', 'RE:ZERO - STARTING LIFE IN ANOTHER WORLD', 'ROMEO\'S BLUE SKIES', 'RUPAN SANSEI', 'RUROUNI KENSHIN: WANDERING SAMURAI', 'SAMURAI CHAMPLOO', 'SAMURAI X: TRUST AND BETRAYAL', 'SCHOOL RUMBLE', 'SEITOKAI YAKUINDOMO', 'SERIAL EXPERIMENTS LAIN', 'SPACE PIRATE CAPTAIN HARLOCK', 'SPICE AND WOLF', 'SUPER DIMENSIONAL FORTRESS MACROSS', 'TENCHI MUYO', 'TENGEN TOPPA GURREN LAGANN', 'TEXHNOLYZE', 'THE IRRESPONSIBLE CAPTAIN TYLOR', 'THE MELANCHOLY OF HARUHI SUZUMIYA', 'THE MYSTERIOUS CITIES OF GOLD', 'THE ROSE OF VERSAILLES', 'THE SLAYERS', 'THE TATAMI GALAXY', 'THE TWELVE KINGDOMS', 'TOMORROW\'S JOE', 'TORADORA', 'TOUCH', 'TRIGUN', 'URUSEI YATSURA', 'USAGI DROP', 'WELCOME TO THE NHK', 'WHEN THEY CRY', 'WOLF\'S RAIN', 'XXXHOLIC', 'YU YU HAKUSHO: GHOST FILES']
			countries = ['AFGHANISTAN','AKROTIRI','ALBANIA','ALGERIA','AMERICAN SAMOA','ANDORRA','ANGOLA','ANGUILLA','ANTARCTICA','ANTIGUA AND BARBUDA','ARGENTINA','ARMENIA','ARUBA','ASHMORE AND CARTIER ISLANDS','AUSTRALIA','AUSTRIA','AZERBAIJAN','BAHAMAS, THE','BAHRAIN','BANGLADESH','BARBADOS','BELARUS','BELGIUM','BELIZE','BENIN','BERMUDA','BHUTAN','BOLIVIA','BOSNIA AND HERZEGOVINA','BOTSWANA','BOUVET ISLAND','BRAZIL','BRITISH INDIAN OCEAN TERRITORY','BRITISH VIRGIN ISLANDS','BRUNEI','BULGARIA','BURKINA FASO','BURMA','BURUNDI','CAMBODIA','CAMEROON','CANADA','CAPE VERDE','CAYMAN ISLANDS','CENTRAL AFRICAN REPUBLIC','CHAD','CHILE','CHINA','CHRISTMAS ISLAND','CLIPPERTON ISLAND','COCOS (KEELING) ISLANDS','COLOMBIA','COMOROS','CONGO, DEMOCRATIC REPUBLIC OF THE','CONGO, REPUBLIC OF THE','COOK ISLANDS','CORAL SEA ISLANDS','COSTA RICA','COTE D\'IVOIRE','CROATIA','CUBA','CYPRUS','CZECH REPUBLIC','DENMARK','DHEKELIA','DJIBOUTI','DOMINICA','DOMINICAN REPUBLIC','ECUADOR','EGYPT','EL SALVADOR','EQUATORIAL GUINEA','ERITREA','ESTONIA','ETHIOPIA','FALKLAND ISLANDS (ISLAS MALVINAS)','FAROE ISLANDS','FIJI','FINLAND','FRANCE','FRENCH POLYNESIA','FRENCH SOUTHERN AND ANTARCTIC LANDS','GABON','GAMBIA, THE','GAZA STRIP','GEORGIA','GERMANY','GHANA','GIBRALTAR','GREECE','GREENLAND','GRENADA','GUAM','GUATEMALA','GUERNSEY','GUINEA','GUINEA-BISSAU','GUYANA','HAITI','HONDURAS','HONG KONG','HUNGARY','ICELAND','INDIA','INDONESIA','IRAN','IRAQ','IRELAND','ISLE OF MAN','ISRAEL','ITALY','JAMAICA','JAN MAYEN','JAPAN','JERSEY','JORDAN','KAZAKHSTAN','KENYA','KIRIBATI','KOREA, NORTH','KOREA, SOUTH','KOSOVO','KUWAIT','KYRGYZSTAN','LAOS','LATVIA','LEBANON','LESOTHO','LIBERIA','LIBYA','LIECHTENSTEIN','LITHUANIA','LUXEMBOURG','MACAU','MACEDONIA','MADAGASCAR','MALAWI','MALAYSIA','MALDIVES','MALI','MALTA','MARSHALL ISLANDS','MAURITANIA','MAURITIUS','MAYOTTE','MEXICO','MICRONESIA, FEDERATED STATES OF','MOLDOVA','MONACO','MONGOLIA','MONTENEGRO','MONTSERRAT','MOROCCO','MOZAMBIQUE', 'NAMIBIA','NAURU','NAVASSA ISLAND','NEPAL','NETHERLANDS','NETHERLANDS ANTILLES','NEW CALEDONIA','NEW ZEALAND','NICARAGUA','NIGER','NIGERIA','NIUE','NORFOLK ISLAND','NORTHERN MARIANA ISLANDS','NORWAY','OMAN','PAKISTAN','PALAU','PANAMA','PAPUA NEW GUINEA','PARACEL ISLANDS','PARAGUAY','PERU','PHILIPPINES','PITCAIRN ISLANDS','POLAND','PORTUGAL','PUERTO RICO','QATAR','ROMANIA','RUSSIA','RWANDA','SAINT HELENA','SAINT KITTS AND NEVIS','SAINT LUCIA','SAINT PIERRE AND MIQUELON','SAINT VINCENT AND THE GRENADINES','SAMOA','SAN MARINO','SAO TOME AND PRINCIPE','SAUDI ARABIA','SENEGAL','SERBIA','SEYCHELLES','SIERRA LEONE','SINGAPORE','SLOVAKIA','SLOVENIA','SOLOMON ISLANDS','SOMALIA','SOUTH AFRICA','SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS','SPAIN','SPRATLY ISLANDS','SRI LANKA','SUDAN','SURINAME','SVALBARD','SWAZILAND','SWEDEN','SWITZERLAND','SYRIA','TAIWAN','TAJIKISTAN','TANZANIA','THAILAND','TIMOR-LESTE','TOGO','TOKELAU','TONGA','TRINIDAD AND TOBAGO','TUNISIA','TURKEY','TURKMENISTAN','TURKS AND CAICOS ISLANDS','TUVALU','UGANDA','UKRAINE','UNITED ARAB EMIRATES','UNITED KINGDOM','UNITED STATES','UNITED STATES PACIFIC ISLAND WILDLIFE REFUGES','URUGUAY','UZBEKISTAN','VANUATU','VENEZUELA','VIETNAM','VIRGIN ISLANDS','WAKE ISLAND','WALLIS AND FUTUNA','WEST BANK','WESTERN SAHARA','YEMEN','ZAMBIA','ZIMBABWE']
			games = ['ADVANCE WARS', 'ADVENTURE', 'AGE OF EMPIRES', 'ASSASIN\'S CREED', 'ASTEROIDS', 'BALDUR\'S GATE', 'BATMAN: ARKHAM ASYLUM', 'BATMAN: ARKHAM CITY', 'BIOSHOCK', 'BLOODBORNE', 'BRAID', 'BURNOUT', 'CALL OF DUTY', 'CASTLEVANIA', 'CHRONO TRIGGER', 'CIVILIZATION', 'COMMAND AND CONQUER', 'CONTRA', 'COUNTER-STRIKE', 'DARK SOULS', 'DAY OF THE TENTACLE', 'DAYTONA USA', 'DEAD SPACE', 'DEFENDER', 'DEUS EX', 'DEVIL MAY CRY', 'DIABLO', 'DONKEY KONG', 'DONKEY KONG COUNTRY', 'DWARF FORTRESS', 'DOOM', 'DOTA', 'DOUBLE DRAGON', 'EARTHBOUND', 'ELITE', 'ELITE: DANGEROUS', 'EVERQUEST', 'FALLOUT', 'FINAL FANTASY', 'FINAL FANTASY TACTICS', 'FIRE EMBLEM', 'GALAGA', 'GAUNTLET', 'GEARS OF WAR', 'GOD OF WAR', 'GRAN TURISMO', 'GRAND THEFT AUTO', 'GRIM FANDANGO', 'GUITAR HERO', 'GUNSTAR HEROES', 'HALF-LIFE', 'HALO', 'HOMEWORLD', 'HOTLINE MIAMI', 'IKARUGA', 'JET SET RADIO', 'JOURNEY', 'JOUST', 'KATAMARI DAMACY', 'LEMMINGS', 'LIMBO', 'LITTLEBIGPLANET', 'MASS EFFECT', 'MAX PAYNE', 'MEGA MAN', 'METAL GEAR SOLID', 'METROID PRIME', 'MINECRAFT', 'MORTAL KOMBAT', 'MS PAC-MAN', 'MYST', 'NBA JAM', 'NIGHTS INTO DREAMS', 'NINJA GAIDEN', 'OKAMI', 'OUT RUN', 'PAC-MAN', 'PANZER DRAGOON', 'PHANTASY STAR', 'PHANTASY STAR ONLINE', 'PHOENIX WRIGHT: ACE ATTORNEY', 'PITFALL', 'PLANESCAPE: TORMENT', 'PLAYERUNKNOWNS BATTLEGROUNDS', 'POKEMON RED AND BLUE', 'PONG', 'PORTAL', 'PRINCE OF PERSIA', 'PSYCHONAUTS', 'PUNCH-OUT', 'QUAKE', 'RED DEAD REDEMPTION', 'RESIDENT EVIL', 'RETURN TO CASTLE WOLFENSTEIN', 'ROCK BAND', 'SAM AND MAX HIT THE ROAD', 'SECRET OF MANA', 'SHADOW OF THE COLOSSUS', 'SHENMUE', 'SHIN MEGAMI TENSEI: PERSONA', 'SILENT HILL', 'SIMCITY', 'SONIC THE HEDGEHOG', 'SOULCALIBER', 'SPACE INVADERS', 'SPELUNKY', 'STAR FOX', 'STAR WARS JEDI KNIGHT', 'STAR WARS: KNIGHTS OF THE OLD REPUBLIC', 'STAR WARS: TIE FIGHTER', 'STARCRAFT', 'STREET FIGHTER', 'SUPER CASTLEVANIA', 'SUPER MARIO BROS', 'SUPER MARIO GALAXY', 'SUPER MARIO KART', 'SUPER MARIO RPG', 'SUPER MARIO WORLD', 'SUPER MEAT BOY', 'SUPER METROID', 'SUPER SMASH BROS', 'SUPER SMASH BROS MELEE', 'SYSTEM SHOCK', 'TEAM FORTRESS', 'TECMO BOWL', 'TEKKEN', 'TETRIS', 'THE ELDER SCROLLS', 'THE LAST OF US', 'THE LEGEND OF ZELDA', 'THE SECRET OF MONKEY ISLAND', 'THE SIMS', 'THE WALKING DEAD', 'THE WITCHER', 'THIEF', 'TOM CLANCY\'S SPLINTER CELL', 'TOMB RAIDER', 'TONY HAWK\'S PRO SKATER', 'TOWERFALL', 'UFO: ENEMY UNKNOWN', 'ULTIMA ONLINE', 'UNCHARTED: DRAKE\'S FORTUNE', 'UNREAL TOURNAMENT', 'WARCRAFT', 'WII SPORTS', 'WIPEOUT', 'WORLD OF WARCRAFT', 'YOSHI\'S ISLAND', 'ZORK']
			movies = ['ANGRY MEN', 'A CLOCKWORK ORANGE', 'A PLACE IN THE SUN', 'A STREETCAR NAMED DESIRE', 'ALL QUIET ON THE WESTERN FRONT', 'AMADEUS', 'AMERICAN GRAFFITI', 'AN AMERICAN IN PARIS', 'ANNIE HALL', 'APOCALYPSE NOW', 'BEN-HUR', 'BONNIE AND CLYDE', 'BRAVEHEART', 'BUTCH CASSIDY AND THE SUNDANCE KID', 'CASABLANCA', 'CHINATOWN', 'CITIZEN KANE', 'CITY LIGHTS', 'CLOSE ENCOUNTERS OF THE THIRD KIND', 'DANCES WITH WOLVES', 'DOCTOR ZHIVAGO', 'DONNIE DARKO', 'DOUBLE INDEMNITY', 'DR STRANGELOVE OR: HOW I LEARNED TO STOP WORRYING AND LOVE THE BOMB', 'ET THE EXTRA-TERRESTRIAL', 'FARGO', 'FORREST GUMP', 'FROM HERE TO ETERNITY', 'GIANT', 'GLADIATOR', 'GONE WITH THE WIND', 'GOOD WILL HUNTING', 'GOODFELLAS', 'HIGH NOON', 'IT HAPPENED ONE NIGHT', 'IT\'S A WONDERFUL LIFE', 'JAWS', 'JURASSIC PARK', 'LAWRENCE OF ARABIA', 'MIDNIGHT COWBOY', 'MR SMITH GOES TO WASHINGTON', 'MUTINY ON THE BOUNTY', 'MY FAIR LADY', 'NASHVILLE', 'NETWORK', 'NORTH BY NORTHWEST', 'ON THE WATERFRONT', 'ONE FLEW OVER THE CUCKOO\'S NEST', 'PATTON', 'PSYCHO', 'PULP FICTION', 'RAGING BULL', 'RAIDERS OF THE LOST ARK', 'RAIN MAN', 'REAR WINDOW', 'REBEL WITHOUT A CAUSE', 'ROCKY', 'SAVING PRIVATE RYAN', 'SCHINDLER\'S LIST', 'SHANE', 'SINGIN\' IN THE RAIN', 'SOME LIKE IT HOT', 'STAGECOACH', 'STAR WARS: EPISODE IV - A NEW HOPE', 'SUNSET BOULEVARD', 'TAXI DRIVER', 'TERMS OF ENDEARMENT', 'THE AFRICAN QUEEN', 'THE APARTMENT', 'THE BEST YEARS OF OUR LIVES', 'THE BRIDGE ON THE RIVER KWAI', 'THE DEER HUNTER', 'THE EXORCIST', 'THE FRENCH CONNECTION', 'THE GODFATHER', 'THE GOOD, THE BAD AND THE UGLY', 'THE GRADUATE', 'THE GRAPES OF WRATH', 'THE GREAT DICTATOR', 'THE GREEN MILE', 'THE LORD OF THE RINGS: THE RETURN OF THE KING', 'THE MALTESE FALCON', 'THE MATRIX', 'THE PHILADELPHIA STORY', 'THE PIANIST', 'THE SEARCHERS', 'THE SHAWSHANK REDEMPTION', 'THE SILENCE OF THE LAMBS', 'THE SOUND OF MUSIC', 'THE THIRD MAN', 'THE TREASURE OF THE SIERRA MADRE', 'THE WIZARD OF OZ', 'TITANIC', 'TO KILL A MOCKINGBIRD', 'UNFORGIVEN', 'VERTIGO', 'WEST SIDE STORY', 'WUTHERING HEIGHTS', 'YANKEE DOODLE DANDY', 'ZOOLANDER']
			music = ['AC/DC','AEROSMITH','ALABAMA','ALAN JACKSON','BACKSTREET BOYS','BARBARA STREISAND','BILLY JOEL','BOB DYLAN','BOB SEGER & THE SILVER BULLET BAND','BON JOVI','BRITNEY SPEARS','BRUCE SPRINGSTEEN','CELINE DION','CHICAGO','COBRA STARSHIP','DAVE MATTHEWS BAND','DEF LEPPARD','EAGLES','ELTON JOHN','ELVIS PRESLEY','EMINEM','ERIC CLAPTON','FLEETWOOD MAC','FOREIGNER','GARTH BROOKS','GEORGE STRAIT','GUNS N\' ROSES','JOURNEY','JUSTIN TIMBERLAKE','KELLY CLARKSON','KENNY G','KENNY ROGERS','LED ZEPPELIN','MADONNA','MARIAH CAREY','METALLICA','MICHAEL JACKSON','MIIKE SNOW','NEIL DIAMOND','PHIL COLLINS','PINK FLOYD','QUEEN','REBA MCENTIRE','ROD STEWART','SANTANA','SHANIA TWAIN','SIMON & GARFUNKEL','THE BEATLES','THE LONELY ISLAND','THE ROLLING STONES','TIM MCGRAW','TUPAC SHAKUR','VAN HALEN','WHITNEY HOUSTON']
			#plants = ['ALOE VERA', 'CACTUS']
			computerScientists = ['ALFRED AHO', 'CHARLES BABBAGE', 'GORDON BELL', 'TIM BERNERS LEE', 'DANIEL J BERNSTEIN', 'JEAN BARTIK', 'STEPHEN R BOURNE', 'STEPHEN COOK', 'JAMES COOLEY', 'SEYMOUR CRAY', 'EDSGER DIJKSTRA', 'WHITFIELD DIFFIE', 'CHARLES STARK DRAPER', 'BRENDAN EICH', 'BILL GATES', 'MARGARET HAMILTON', 'GERNOT HEISER', 'GRACE HOPPER', 'BILL JOY', 'BOB KAHN', 'BRIAN KERNIGHAN', 'DONALD KNUTH', 'CHRIS LATTNER', 'ADA LOVELACE', 'EDWARD F MOORE', 'JOHN VON NEUMANN', 'LARRY PAGE', 'DENNIS RITCHIE', 'GUIDO VAN ROSSUM', 'BRUCE SCHNEIER', 'GUY L STEELE, JR', 'ANDREW S TANENBAUM', 'KEN THOMPSON', 'LINUS TORVALDS', 'PAUL VIXIE', 'LARRY WALL', 'PETER J WEINBERGER', 'NIKLAUS WIRTH', 'STEPHEN WOLFRAM', 'STEVE WOZNIAK', 'MARK ZUCKERBERG']
			hackers = ['KEVIN MITNICK', 'SAMY KAMKAR', 'ADRIAN LAMO', 'KEVIN POULSEN', 'ANDREW AUERNHEIMER', 'KRISTINA SVECHINSKAYA']
			dataTypes = ['BOOLEAN', 'CHARACTER', 'FLOATING-POINT', 'DOUBLE', 'INTEGER', 'STRING', 'POINTER', 'ARRAY', 'ASSOCIATIVE ARRAY', 'STACK', 'QUEUE', 'DOUBLE-ENDED QUEUE', 'TREE', 'GRAPH', 'ARRAY LIST', 'LINKED LIST', 'BINARY TREE', 'CARTESIAN TREE', 'B-TREE', 'HEAP', 'BLOOM FILTER']
			programmingLanguages = ['ACTIONSCRIPT', 'ALGOL', 'APPLESCRIPT', 'ASSEMBLY', 'AUTOIT', 'BASIC', 'BEANSHELL', 'BATCH', 'BOURNE SHELL', 'CLOJURE', 'COBOL', 'COFFEESCRIPT', 'COLDFUSION', 'COMMON LISP', 'CUDA', 'DELPHI', 'ECMASCRIPT', 'ERLANG', 'FOXPRO', 'GOLANG', 'JAVA', 'JAVASCRIPT', 'JSCRIPT', 'JYTHON', 'KIXTART', 'LATEX', 'MATLAB', 'OPENCL', 'PASCAL', 'PERL', 'POWERSHELL', 'PYTHON', 'RUBY', 'RUST', 'SCALA', 'SCHEME', 'SWIFT', 'VERILOG', 'VISUAL BASIC']
			techSlang = ['CODE MONKEY', 'PEBCAK', 'RTFM']
			tech = list(computerScientists) + list(hackers) + list(dataTypes) + list(programmingLanguages) + list(techSlang)
			tv = ['13 REASONS WHY','48 HOURS','60 MINUTES','AGENTS OF S.H.I.E.L.D.','ALTERED CARBON','AMERICAN CRIME STORY','AMERICAN HORROR STORY','AMERICAN HOUSEWIFE','AMERICA\'S FUNNIEST HOME VIDEOS','ARROW','BETTER OFF TED','BETTER LATE THAN NEVER','BIG LITTLE LIES','BLACK LIGHTNING','BLACK MIRROR','BLACK-ISH','BLACKLIST','BLINDSPOT','BLUE BLOODS','BRAVE','BREAKING BAD','BRITANNIA','BROOKLYN NINE-NINE','BULL','CHICAGO FIRE','CHICAGO MED','CHICAGO P.D.','COBRA KAI','COLLATERAL','COUNTERPART','CRIMINAL MINDS','DANCING WITH THE STARS','DARK','DATELINE NBC','DEATH IN PARADISE','DESIGNATED SURVIVOR','DEXTER','DOCTOR WHO','EMPIRE','EVERYTHING SUCKS','FARGO','FRIENDS','GAME OF THRONES','GIFTED','GOTHAM','GRACE AND FRANKIE','GREY\'S ANATOMY','HAWAII FIVE-0','HERE AND NOW','HOMELAND','HOW I MET YOUR MOTHER','HOW TO GET AWAY WITH MURDER','IMPOSTERS','IT\'S ALWAYS SUNNY IN PHILADELPHIA','JESSICA JONES','KEVIN CAN WAIT','LAW & ORDER: SPECIAL VICTIMS UNIT','LAW & ORDER: TRUE CRIME','LEGENDS OF TOMORROW','LETHAL WEAPON','LIFE IN PIECES','LOST IN SPACE','LUCIFER','MACGYVER','MADAM SECRETARY','MAN WITH A PLAN','MCMAFIA','ME, MYSELF AND I','MINDHUNTER','MODERN FAMILY','MONEY HEIST','MOZART IN THE JUNGLE','NARCOS','NCIS','NCIS: LOS ANGELES','NCIS: NEW ORLEANS','NEW GIRL','ONCE UPON A TIME','ORANGE IS THE NEW BLACK','ORVILLE','OUTLANDER','OZARK','PARKS AND RECREATION','PEAKY BLINDERS','PSYCH','RICK AND MORTY','RIVERDALE','S.W.A.T.','SCANDAL','SCORPION','SEAL TEAM','SEVEN SECONDS','SHAMELESS','SHARK TANK','SHERLOCK','SONS OF ANARCHY','SPEECHLESS','STAR','STAR TREK: DISCOVERY','STRANGER THINGS','STRIKE BACK','SUITS','SUPERGIRL','SUPERIOR DONUTS','SUPERNATURAL','SUPERSTORE','SURVIVOR','TEEN WOLF','THE 100','THE ALIENIST','THE BIG BANG THEORY','THE BLACKLIST','THE CROWN','THE END OF THE F***ING WORLD','THE EXPANSE','THE FLASH','THE FRANKENSTEIN CHRONICLES','THE GOLDBERGS','THE GOOD DOCTOR','THE GOOD PLACE','THE HANDMAID\'S TALE','THE MAGICIANS','THE MIDDLE','THE OFFICE','THE PUNISHER','THE SIMPSONS','THE VAMPIRE DIARIES','THE VOICE','THE WALKING DEAD','THE WIRE','THE X-FILES','THIS IS US','TROY: FALL OF A CITY','TRUE DETECTIVE','VICTORIA','VIKINGS','WACO','WESTWORLD','WILL & GRACE','WISDOM OF THE CROWD','YOUNG SHELDON','ZOMBIES']
			allCategoriesStrings = ['animals', 'anime', 'countries', 'games', 'movies', 'music', 'tech', 'tv']
			allCategoriesLists = [animals, anime, countries, games, movies, music, tech, tv]
			a = args[0].lower()

			if a == 'all' or a == '':
				x = random.randrange(0, len(allCategoriesStrings))
				b = allCategoriesLists[x]
				a = allCategoriesStrings[x]
			elif a in allCategoriesStrings:
				b = list(vars()[args[0]])
			else:
				x = random.randrange(0, len(allCategoriesStrings))
				b = allCategoriesLists[x]
				a = allCategoriesStrings[x]
			return {'string':a, 'value':b}

		def GetWord(a): # (category['value'])
			x = ''
			y = random.choice(a)
			z = 0
			for i in y:
				if i == ' ':
					x += '  '
				elif i == ':':
					x += ': '
				elif i == '-':
					x += '- '
				elif i == '\'':
					x += '\' '
				elif i == '(':
					x += '( '
				elif i == ')':
					x += ') '
				elif i == ',':
					x += ', '
				elif i == '&':
					x += '& '
				elif i == '/':
					x += '/ '
				elif i == '*':
					x += '* '
				elif i == '.':
					x += '. '
				else:
					x += '_ '
					z += 1
			return {'displayed':x, 'value':y, 'count':z}

		def InitialOutput(a, b, c, d): # (word['displayed'], guessedLetters, category['string'], bet)
			graphic = '```\n	_________\n	|       |\n	|       %s\n	|      %s%s%s\n	|      %s %s\n	|\n	|\n|¯¯¯¯¯¯¯¯¯|\n|         |\n|_________|\n\n' % (s.hangman[0], s.hangman[1], s.hangman[2], s.hangman[3], s.hangman[4], s.hangman[5])
			info = 'Word: ' + a + '\nGuessed: ' + str(sorted(b)) + '\nCategory: '+ c + '\nAccuracy: ' + str(s.accuracy) + '%\n\n'
			console = s.UpdateConsole('initial', d)
			return graphic + info + console

		def UpdateConsole(a, b): # (console argument, bet)
			if a == 'correct':
				return 'Letter found!\n```' # update to include letter and how many were found
			elif a == 'incorrect':
				return 'Letter not found!\n```' # update to include letter
			#elif x == 'show':
				#return
			elif a == 'win':
				if b > 0:
					userBalance = _getbalance(message.author.id)
					return 'Congratulations, you won ' + str(s.payout) + ' ' + currencyName[message.guild.id] + '! (you now have ' + str(userBalance) + ' ' + currencyName[message.guild.id] + ')\n```'
				else:
					return 'Congratulations, you win!\n```'
			elif a == 'lose':
				if b > 0:
					userBalance = _getbalance(message.author.id)
					return 'Game over! You lost your bet of ' + str(b) + ' ' + currencyName[message.guild.id] + '. (you now have ' + str(userBalance) + ' ' + currencyName[message.guild.id] + ')\n```'
				else:
					return 'Game over, you lost!\n```'
			elif a == 'initial':
				if b > 0:
					return 'Welcome to Hangman! You have bet ' + str(b) + ' ' + currencyName[message.guild.id] + ' on this game. Guess a letter to begin.\n```'
				else:
					return 'Welcome to Hangman! Guess a letter to begin.\n```'
			elif a == 'quit':
				if b > 0:
					userBalance = _getbalance(message.author.id)
					return 'You have quit the game and forfeited your bet of ' + str(b) + ' ' + currencyName[message.guild.id] + '. (you now have ' + str(userBalance) + ' ' + currencyName[message.guild.id] + ')\n```'
				else:
					return 'You have quit the game.\n```'
			elif a == 'timeout':
				if b > 0:
					userBalance = _getbalance(message.author.id)
					return 'Time\'s up! Ending game. You have lost your bet of ' + str(b) + ' ' + currencyName[message.guild.id] + '. (you now have ' + str(userBalance) + ' ' + currencyName[message.guild.id] + ')\n```'
				else:
					return 'Time\'s up! Ending game.\n```'
			else:
				return '```\nOops, <@169268862901157888> didn\'t plan for this condition I guess.'

		def PlayCheck(msg):
			if msg.channel != message.channel:
				return False
			if msg.content.upper() in s.allLetters:
				return True
			elif msg.content.lower() == 'show hangman':
				return True
			elif msg.content.lower() == 'stats hangman':
				return True
			elif msg.content[0:5].lower() == 'guess':
				return True
			elif msg.content.lower() == 'quit hangman':
				return True

		def CheckLetter(a, b, c, d, e, f, g): # (word, play.content, guessedLetters, availableLetters, category, True/False, bet)
			if f:
				s.UpdateAccuracy(1)
				a['displayed'] = s.RevealLetter(b.upper(), a['value'], a['displayed'])
				contxt = 'correct'
			else:
				s.UpdateAccuracy(0)
				s.incorrectGuesses += 1
				contxt = 'incorrect'
			if b.upper() not in c:
				c.append(b.upper())
				d.remove(b.upper())
			c = sorted(c)
			output = s.UpdateOutput(a, c, e['string'], contxt, g)
			return output

		def UpdateAccuracy(a): # (0/1)
			s.totalGuesses += 1
			s.correctGuesses += a
			s.accuracy = int((s.correctGuesses / s.totalGuesses) * 100)
			return

		def RevealLetter(x, y, z): # (play.content.upper(), word['value'], word['displayed'])
			letters = [i for i, ltr in enumerate(y) if ltr == x]
			for i in letters:
				a = i * 2
				b = i * 2 + 1
				z = z[:a] + x.upper() + z[b:]
				s.lettersFound += 1
			return z

		def UpdateOutput(a, b, c, d, e): # (word, guessedLetters, category['string'], console argument, bet)
			if s.incorrectGuesses != 0:
				x = s.incorrectGuesses - 1
				s.hangman[x] = s.hangmanFull[x]
			if d == 'win' or d == 'lose':
				a['displayed'] = s.RevealWord(a['value'])
			graphic = '```\n	_________\n	|       |\n	|       %s\n	|      %s%s%s\n	|      %s %s\n	|\n	|\n|¯¯¯¯¯¯¯¯¯|\n|         |\n|_________|\n\n' % (s.hangman[0], s.hangman[1], s.hangman[2], s.hangman[3], s.hangman[4], s.hangman[5])
			info = 'Word: ' + a['displayed'] + '\nGuessed: ' + str(sorted(b)) + '\nCategory: '+ c + '\nAccuracy: ' + str(s.accuracy) + '%\n\n'
			console = s.UpdateConsole(d, e)
			return graphic + info + console

		def RevealWord(a): # (word['value'])
			x = ''
			for i in a:
				x += i + ' '
			return x

		def CalculatePayout(a, b): # (word, bet)
			base = b * 1.25
			# calculate accuracy bonus
			if s.accuracy == 100:
				abonus = b * .5
			elif s.accuracy >= 95:
				abonus = b * .25
			elif s.accuracy >= 90:
				abonus = b * .1
			else:
				abonus = 0
			# calculate guess bonus
			gbonus = (word['count'] - s.lettersFound) * b * .05
			# combine and return
			s.payout = int(base + abonus + gbonus)
			_incrementbalance(message.author.id, s.payout)
			return {'base':base, 'abonus':abonus, 'gbonus':gbonus}
	
	
	if (message.guild.id, message.author.id, "hangman") in activeGames:
		await message.channel.send("%s has an active hangman game. Try typing `show hangman`, or `quit hangman`." % (message.author.name))
		return
	
	# Initial Variable Setup
	s = HangmanGame
	availableLetters = list(s.allLetters)
	guessedLetters = []
	# Get player bet
	bet = s.GetBet()
	if bet == None:
		await message.channel.send('Bet amount must be a number between 10 and 100,000 (e.g. `hangman 100`).')
		return
	elif bet == NotImplemented:
		await message.channel.send('Not enough '+ currencyName[message.guild.id] + ' (you have ' + str(s.userBalance) + ').')
		return
	else:
		_incrementbalance(message.author.id, bet * -1)
		activeGames.append((message.guild.id, message.author.id, "hangman"))
	# Get category
	category = s.GetCategory()
	word = s.GetWord(category['value'])
	output = s.InitialOutput(word['displayed'], guessedLetters, category['string'], bet)
	msg = await message.channel.send(output)
	# Start the game input loop
	gameIsActive = True
	while gameIsActive:
		play = await client.wait_for('message', timeout=900, check=s.PlayCheck)
		if play == None:
			output = s.UpdateOutput(word, guessedLetters, category['string'], 'timeout', bet)
			await msg.edit(content=output)
			gameIsActive = False
			activeGames.remove((message.guild.id, message.author.id, "hangman"))
			return
		if play.content.lower() == 'show hangman':
			#output = s.UpdateOutput(word['displayed'], guessedLetters, category['string'], 'show')
			msg = await message.channel.send(output)
		if play.content.lower() == 'stats hangman':
			pass
		if play.content[0:5].lower() == 'guess':
			if play.content[6:].upper() == word['value']:
				s.CalculatePayout(word, bet)
				#await message.channel.send('base: ' + str(debug['base']) + '\nabonus: ' + str(debug['abonus']) + '\ngbonus: ' + str(debug['gbonus']))
				output = s.UpdateOutput(word, guessedLetters, category['string'], 'win', bet)
				await msg.edit(content=output)
				gameIsActive = False
				activeGames.remove((message.guild.id, message.author.id, "hangman"))
				return
			else:
				output = s.UpdateOutput(word, guessedLetters, category['string'], 'lose', bet)
				await msg.edit(content=output)
				gameIsActive = False
				activeGames.remove((message.guild.id, message.author.id, "hangman"))
				return
		if play.content.lower() == 'quit hangman':
			output = s.UpdateOutput(word, guessedLetters, category['string'], 'quit', bet)
			await msg.edit(content=output)
			gameIsActive = False
			activeGames.remove((message.guild.id, message.author.id, "hangman"))
			return
		if play.content.upper() in s.allLetters:
			if play.content.upper() in availableLetters:
				if play.content.upper() in word['value']:
					output = s.CheckLetter(word, play.content, guessedLetters, availableLetters, category, True, bet)
				else:
					output = s.CheckLetter(word, play.content, guessedLetters, availableLetters, category, False, bet)
			else:
				output = s.CheckLetter(word, play.content, guessedLetters, availableLetters, category, False, bet)
			await msg.edit(content=output)
			exemptLogDeletedMessages.append(play.id)
			await play.delete()
		if s.lettersFound == word['count']:
			s.CalculatePayout(word, bet)
			#await message.channel.send('base: ' + str(debug['base']) + '\nabonus: ' + str(debug['abonus']) + '\ngbonus: ' + str(debug['gbonus']))
			output = s.UpdateOutput(word, guessedLetters, category['string'], 'win', bet)
			await msg.edit(content=output)
			gameIsActive = False
			activeGames.remove((message.guild.id, message.author.id, "hangman"))
			return
		if s.incorrectGuesses == 6:
			output = s.UpdateOutput(word, guessedLetters, category['string'], 'lose', bet)
			await msg.edit(content=output)
			gameIsActive = False
			activeGames.remove((message.guild.id, message.author.id, "hangman"))
			return


# Play a virtual 3-reel slot machine
global slots
async def slots(message, args):
	#declare variables
	modifier = args[1]
	freeMode = False
	payout = 0
	userBalance = _getbalance(message.author.id)
	freeBalance = _getattrib(message.author.id, 'user', 'slotsFreeCredits')
	#create freeBalance DB entry if none exists
	if freeBalance == None:
		res = _setattrib(message.author.id, 'user', 'slotsFreeCredits', 0)
		freeBalance = res['slotsFreeCredits']
	#check for valid bet argument
	if args[0] == '':
		await message.channel.send('You must enter a bet. Bet amount can be between 10 and 100,000 '+currencyName[message.guild.id]+'.')
		return
	#elif args[0] == 'stats':
		#await message.channel.send('Win/loss statistics go here.')
		#return
	else:
		try:
			bet = int(args[0])
		except ValueError:
			await message.channel.send('Invalid bet. Bet amount can be between 10 and 100,000 '+currencyName[message.guild.id]+'.')
			return
	if bet < 10 or bet > 100000:
		await message.channel.send('Invalid bet amount. Bet amount can be between 10 and 100,000 '+currencyName[message.guild.id]+'.')
		return
	#check if user is trying to use free credits and if they have enough
	if modifier == 'free':
		freeMode = True
	#check if user has enough money
	if freeMode == True:
		if bet > freeBalance:
			await message.channel.send('Not enough free '+currencyName[message.guild.id]+'. You have '+str(freeBalance)+' free '+currencyName[message.guild.id]+'.')
			return
		else:
			#deduct bet from freeBalance
			freeBalance -= bet
			_setattrib(message.author.id, 'user', 'slotsFreeCredits', freeBalance)
	else:
		if bet > userBalance:
			await message.channel.send('Not enough '+currencyName[message.guild.id]+'. You have '+str(userBalance)+' '+currencyName[message.guild.id]+'.')
			return
		else:
			#deduct bet from userBalance
			_incrementbalance(message.author.id, -bet)
			userBalance = _getbalance(message.author.id)
	#set up the reels for this game
	#defaultReel = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
	defaultReel = ['1', '2', '3', '4', '5', '6', '7']
	reel0 = list(defaultReel)
	reel1 = list(defaultReel)
	reel2 = list(defaultReel)
	allReels = [reel0, reel1, reel2]
	pickPositions = []
	pickValues = []
	for i in allReels:
		#decide if there will be a wild symbol on this reel
		#if random.choice([True, False]): #fixed this because you were whining about it <3
		randomPosition = (random.randrange(0, len(i)))
		wild = i[randomPosition]
		i.remove(wild)
		i.insert(randomPosition, '~')
		i.append('+') #free credits symbol
		i.insert(random.randrange(0, len(i)), '$') #scatter symbol
		randomPosition = random.randrange(0,len(i))
		pickPositions.append(randomPosition)
		pickValues.append(i[randomPosition])
	#look for a winning game
	freeCount = 0
	scatterCount = 0
	wildCount = 0
	winningNumber = '0'
	if pickValues[0] == pickValues[1] == pickValues[2]:
		winningNumber = pickValues[0]
	else:
		tempValues = []
		for i in pickValues:
			if i == '~':
				wildCount += 1
			elif i == '+':
				freeCount += 1
				tempValues.append(i)
			elif i == '$':
				scatterCount += 1
				tempValues.append(i)
			else:
				tempValues.append(i)
		if wildCount == 1:
			if tempValues[0] == tempValues[1]:
				winningNumber = tempValues[0]
		elif wildCount == 2:
			winningNumber = tempValues[0]
	#score calculation
	if winningNumber != '0':
		if winningNumber == '1':
			payout = bet * 0.2
		elif winningNumber == '2':
			payout = bet * 0.4
		elif winningNumber == '3':
			payout = bet * 0.8
		elif winningNumber == '4':
			payout = bet * 1
		elif winningNumber == '5':
			payout = bet * 2
		elif winningNumber == '6':
			payout = bet * 3
		elif winningNumber == '7':
			payout = bet * 4
		#elif winningNumber == '8':
			#payout = bet * 2
		#elif winningNumber == '9':
			#payout = bet * 4
		elif winningNumber == '~':
			payout = bet * 10
		elif winningNumber == '+':
			freeBalance += pickValues.count('+') * 100
			_setattrib(message.author.id, 'user', 'slotsFreeCredits', freeBalance)
		elif winningNumber == '$':
			payout += bet * 5
	else:
		if freeCount > 0:
			freeBalance += pickValues.count('+') * 100
			_setattrib(message.author.id, 'user', 'slotsFreeCredits', freeBalance)
		if scatterCount > 0:
			if scatterCount == 1:
				payout = bet * 1
			else:
				payout = bet * 2
	#transact winnings if applicable and output results
	payout = int(payout)
	if payout > 0:
		_incrementbalance(message.author.id, payout)
		userBalance = _getbalance(message.author.id)
	rows  = [
		[reel0[ (pickPositions[0]-1) % len(reel0)], reel1[(pickPositions[1]-1) % len(reel1)], reel2[(pickPositions[2]-1) % len(reel2)] ],
		[reel0[ pickPositions[0]                 ], reel1[pickPositions[1]                 ], reel2[pickPositions[2]                 ] ],
		[reel0[ (pickPositions[0]+1) % len(reel0)], reel1[(pickPositions[1]+1) % len(reel1)], reel2[(pickPositions[2]+1) % len(reel2)] ]
	]
	if payout == bet:
		winLoseString = 'You broke even by winning your bet of %s %s back.\nYou have %s free credits.' % (bet, currencyName[message.guild.id], freeBalance)
	elif payout == 0:
		winLoseString = 'You lost your bet of %s %s. (you have %s remaining)\nYou have %s free credits.' % (bet, currencyName[message.guild.id], userBalance, freeBalance)
	elif payout > 0 and payout < bet:
		winLoseString = 'You bet %s %s and won %s %s back. (you have %s remaining)\nYou have %s free credits.' % (bet, currencyName[message.guild.id], payout, currencyName[message.guild.id], userBalance, freeBalance)
	elif payout > bet:
		winLoseString = 'You bet %s %s and won %s %s! (you have %s remaining)\nYou have %s free credits.' % (bet, currencyName[message.guild.id], payout, currencyName[message.guild.id], userBalance, freeBalance)
	outputString = '''```
.=============. __
| [%s] [%s] [%s] |(  )
|>[%s] [%s] [%s]<| ||
| [%s] [%s] [%s] | ||
|             |_||
|   :::::::   |--'
|   :::::::   |
|             |
|      __ === |
|_____/__\____|

%s```'''
	await message.channel.send(outputString % (rows[0][0], rows[0][1], rows[0][2], rows[1][0], rows[1][1], rows[1][2], rows[2][0], rows[2][1], rows[2][2], winLoseString))
	#await message.channel.send('Debug info: \nmodifier: '+modifier+'\nfreeMode: '+str(freeMode)+'\npayout: '+str(payout)+'\nreel0: '+str(reel0)+'\nreel1: '+str(reel1)+'\nreel2: '+str(reel2)+'\npickPositions: '+str(pickPositions)+'\npickValues: '+str(pickValues)+'\nfreeCount: '+str(freeCount)+'\nscatterCount: '+str(scatterCount)+'\nwildCount: '+str(wildCount)+'\nwinningNumber: '+winningNumber)
