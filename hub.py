# https://trello.com/b/FZC9Iv7B/fire-keeper-bot

import asyncio
from bson.objectid import ObjectId
import collections
import datetime
import discord
import io
import json
import math
import matplotlib
import os
import pprint
import psutil
import pymongo
from pymongo import MongoClient
import random
import signal
import sys
import time
import traceback
from twilio.rest import Client
import unicodedata
import qrcode
from qrcode.image.pure import PymagingImage


# Globals
ansibleTargets = {}
configJSON = ''
modules = {}
moduleCommands = {}
namespace = __import__(__name__)
activeGames = []
unrestrictedUsers = [291304287307300867, 169268862901157888]
exemptCommands = ['quote']
exemptRoles = []
xpChannels = {}
guildResponses = {}
guildTimers = {}
xpLevelTiers = {}
debugMode = False
deleteCommands = False
logDeletedMessages = True
exemptLogDeletedMessages = []
# Database variables
dbConn = None
dbName = ''
collName = ''
# Bot variables
versionNumber = '2.0.0'
versionRelease = datetime.datetime(2020, 7, 24)
initialRelease = datetime.datetime(2018, 2, 14)
prefix = ''
token = ''
embedColor = 0xe69138
currencyName = {}
botID = ''
# guild variables
firelinkShrine = ''
devChannel = ''
errorChannel = ''
logsChannel = ''
mutedRole = {}
# Twilio variables
twilioSID = ''
twilioToken = ''
twilioPhone = ''
devPhone = ''
# Logfile path variables
cwd = os.getcwd()
logFile = ''
logFileName = 'firekeeper'
logFileNameExt = 'log'
logFileFullName = os.path.join(cwd, 'logs', logFileName + '.' + logFileNameExt)


exec(compile(open('dbhelper.py').read(), filename = 'dbhelper.py', mode = 'exec'), globals(), locals())


# Function runs upon receiving SIGHUP
def sighupHandler(sigNum, frame):
	log('hub', 'Received SIGHUP, reloading config')
	unloadModules()
	unloadConfig()
	loadConfig()
	loadModules()


# Function runs upon receiving SIGTERM
def sigtermHandler(sigNum, frame = False):
	log('hub', 'Received SIGTERM, shutting down')
	asyncio.ensure_future(client.close())
	time.sleep(2)

def loadguildConfig(guildid):
	try:
		guild = client.get_guild(guildid)
		guildid = guild.id
	except:
		log('hub', 'Unable to find guild %s' % guildid)
		return
	guildid = _getattrib(guildid, 'server', 'id')
	if not guildid:
		_setguild(guildid, guild.name)
	else:
		_setattrib(guildid, 'server', 'name', guild.name)
	getResponseText(guildid)
	getguildTimers(guildid)
	xpChannels[guildid] = getXpChannels(guildid)
	xpLevelTiers[guildid] = getXpLevelTiers(guildid)
	currencyName[guildid] = getCurrencyName(guildid)
	mutedRole[guildid] = getMutedRole(guildid)

# Variables and configurations that need to be set on startup
def loadConfig():
	global logFile
	global configJSON
	global collName
	global prefix
	global token
	global dbConn
	global dbName
	global botID
	global twilioSID
	global twilioToken
	global twilioPhone
	global devPhone
	global debugMode
	global deleteCommands
	# Load the JSON config and log file
	namespace = __import__(__name__)
	rotated = False
	if(os.path.exists(logFileFullName)):
		rotateLogFile()
		rotated = True
	logFile = open(logFileFullName, 'w+')
	if(rotated):
		log('hub', 'Found pre-existing logfile, shutdown may have been incomplete. Rotated logfile.')
	configFile = open(os.path.join(cwd, 'hub.json'), 'r')
	configJSON = json.load(configFile)
	configFile.close()
	os.system('clear')
	log('hub', 'Config loaded.')
	# Set up the database connection
	if os.path.isfile(os.path.join(os.getcwd(), 'testing')):
		dbConn = MongoClient('mongodb+srv://%s:%s@%s' % (configJSON['databaseuser'], configJSON['databasepass'], configJSON['databaseurl']), maxPoolSize=configJSON['testlimit'])
		dbName = configJSON['databasename']
		collName = configJSON['testcoll']
		prefix = configJSON['testprefix']
		token = configJSON['testtoken']
		botID = configJSON['bottestid']
		debugMode = True
		deleteCommands = False
	else:
		dbConn = MongoClient('mongodb+srv://%s:%s@%s' % (configJSON['databaseuser'], configJSON['databasepass'], configJSON['databaseurl']), maxPoolSize=configJSON['prodlimit'])
		dbName = configJSON['databasename']
		collName = configJSON['prodcoll']
		prefix   = configJSON['prodprefix']
		token = configJSON['prodtoken']
		botID = configJSON['botprodid']
	# Set up the Twilio client
	twilioSID = configJSON['twiliosid']
	twilioToken = configJSON['twiliotoken']
	twilioPhone = configJSON['twiliophone']
	devPhone = configJSON['devphone']
	print('Config loaded')
	return


# These variables can't be set until the client is loaded, so they can't go in loadConfig() with everything else
def setClientVariables():
	global firelinkShrine
	global devChannel
	global logsChannel
	global errorChannel
	global mutedRole
	# Find the logging / error reporting guild and various channels
	firelinkShrine = client.get_guild(configJSON['firelinkshrine'])
	devChannel = firelinkShrine.get_channel(configJSON['devchannel'])
	syntheticHub = client.get_guild(configJSON['synthetichub'])
	errorChannel = syntheticHub.get_channel(configJSON['errorchannel'])
	logsChannel = syntheticHub.get_channel(configJSON['logschannel'])

def unloadConfig():
	global configJSON
	configJSON	= ''
	dbConn = None
	dbName = ''
	collName = ''
	log('hub', 'Config unset.')
	log('hub', 'Closing logfile.')
	logFile.close()
	rotateLogFile()
	return


# Loads all module files
def loadModules():
	global modules
	global moduleCommands
	log('hub', 'CWD: %s' % (cwd))
	for fileName in os.listdir(os.path.join(cwd, 'modules')):
		if fileName.endswith('.json'):
			log('hub', 'Found json file ' + fileName + '. Parsing.')
			parseModule(os.path.join(cwd, 'modules', fileName))
		else:
			log('hub', 'Found non-json file ' + fileName + '. Continuing.')
			continue
	log('hub', 'Modules loaded.')
	return


def unloadModules():
	global modules
	global moduleCommands
	modules = {}
	moduleCommands = {}
	namespace = ''
	log('hub', 'Modules unloaded.')
	return


# Loads commands found within the previously loaded modules
def parseModule(path):
	global modules
	moduleFile = open(path, 'r')
	parsedJSON = json.load(moduleFile)
	moduleFile.close()
	moduleName = parsedJSON['moduleName']
	modules[moduleName] = parsedJSON
	# exec(open(os.path.join(cwd, 'modules', moduleName + '.py'),'r').read())
	exec(compile(open(os.path.join(cwd, 'modules', moduleName + '.py')).read(), filename = 'modules/' + moduleName + '.py', mode = 'exec'), globals(), locals())
	print("  M: %s" % (moduleName))
	output = []
	for x in modules[moduleName]['commands']:
		output.append(x)
		newFunction = modules[moduleName]['commands'][x]['functionName']
		if x in moduleCommands:
			log('hub', 'Error, command "%s" (from module "%s", calling function "%s") already exists from module "%s".' % (x, moduleName, newFunction, moduleCommands[x][0]))
		else:
			log('hub', 'Command "%s" (from module "%s", calling function "%s") successfully registered.' % (x, moduleName, newFunction))
			moduleCommands[x] = (moduleName, newFunction)
	print('	C: %s' % (', '.join(output)))
	return


def rotateLogFile():
	isoDate = datetime.datetime.utcnow().isoformat()
	isoDate = isoDate.replace(":", "")
	os.rename(logFileFullName, os.path.join(cwd, "logs", logFileName + '.' + isoDate + '.' + logFileNameExt))


def log(module, string):
	global logFile
	isoDate = datetime.datetime.utcnow().isoformat()
	logFile.write('%s\t%s\t%s\n' % (isoDate, module, string))
	return


# Calculates a user's level based on how much xp they have
def calculateLevel(usrXP):
	initXP = 150
	genXP = initXP
	level = 1
	while usrXP > genXP:
		level += 1
		genXP = math.floor(initXP * level + genXP * (level / 100))
	if usrXP != genXP:
		level -= 1
	return level


# Calculates how much xp a user will need to level up
def calculateXP(usrLevel):
	initXP = 150
	neededXP = initXP
	i = 1
	while i < usrLevel + 1:
		i += 1
		neededXP = math.floor(initXP * i + neededXP * (i / 100))
	return neededXP


def getCurrencyName(guildid):
	customName = _getattrib(guildid, 'server', 'currencyname')
	if not customName:
		customName = 'souls'
	return customName


def getMutedRole(guildid):
	guild = client.get_guild(guildid)
	roleId = _getattrib(guildid, 'server', 'mutedrole')
	if roleId:
		for role in guild.roles:
			if role.id == roleId:
				ret = role
				break
	if not roleId or not ret:
		ret = None
	return ret


# Pulls the list of text the bot should respond to from the DB and stores it as a variable
def getResponseText(guildid):
	global guildResponses
	dbData = _getresponses(guildid)
	tmp = []
	for i in dbData:
		userlist = []
		channellist = []
		for j in i['responses']['userlist']:
			userlist.append(j)
		targetmatch = i['responses']['targetmatch']
		for j in i['responses']['channellist']:
			channellist.append(j)
		targettext = i['responses']['targettext']
		responsetext = i['responses']['responsetext']
		matchpercent = i['responses']['matchpercent']
		objectid = i['responses']['_id']
		tmp.append({'userlist': userlist, 'targetmatch': targetmatch, 'channellist': channellist, 'targettext': targettext, 'responsetext': responsetext, 'matchpercent': matchpercent, 'objectid': objectid})
	guildResponses[guildid] = tmp


# Pulls the list of active timers from the DB and stores it as a variable
def getguildTimers(guildid):
	global guildTimers
	dbData = _getguildtimers(guildid)
	tmp = []
	for i in dbData:
		timertype = i['guildtimer']['timertype']
		subjectid = i['guildtimer']['subjectid']
		subjectname = i['guildtimer']['subjectname']
		operatorid = i['guildtimer']['operatorid']
		expiration = i['guildtimer']['expiration']
		objectid = i['guildtimer']['_id']
		tmp.append({'timertype': timertype, 'subjectid': subjectid, 'subjectname': subjectname, 'operatorid': operatorid, 'expiration': expiration, 'objectid': objectid})
	guildTimers[guildid] = tmp


def getXpChannels(guildid):
	global xpChannels
	xpcData = _getattrib(guildid, 'server', 'xpchannels')
	ret = []
	if xpcData is None:
		_setattrib(guildid, 'server', 'xpchannels', [])
	else:
		for c in xpcData:
			ret.append(int(c))
	return ret


def getXpLevelTiers(guildid):
	guild = client.get_guild(guildid)
	rawLevelTiers = _getattrib(guildid, 'server', 'xpleveltiers')
	levelTiers = {}
	if rawLevelTiers:
		for tier in rawLevelTiers:
			temp = tier.split(':')
			levelTiers[int(temp[0])] = guild.get_role(int(temp[1]))
	return levelTiers


def isXPValid(message):
	if message.guild.id in xpChannels and message.channel.id in xpChannels[message.guild.id] and not message.content.startswith(prefix):
		guildTimer = _gettimer(message.guild.id, message.author.id, 'xp')
		if not guildTimer:
			return True


def incrementXP(message):
	oldXP = _getxp(message.guild.id, message.author.id)
	amount = random.randrange(10, 30)
	newXP = _incrementxp(message.guild.id, message.author.id, amount)
	if not debugMode:
		_settimer(message.guild.id, message.author.id, 'xp', '0.016')
	return oldXP, newXP


async def processXPGain(message, oldXP, newXP):
	oldLevel = calculateLevel(oldXP)
	newLevel = calculateLevel(newXP)
	nextLevel = calculateXP(newLevel)
	if oldLevel < newLevel:
		if newLevel not in xpLevelTiers[message.guild.id]:
			await sendEmbed(message.channel, None, '%s has advanced to level %s.' % (message.author.mention, newLevel))
		else:
			newRole = xpLevelTiers[message.guild.id][newLevel]
			for tierLevel, role in xpLevelTiers[message.guild.id].items():
				if role in message.author.roles:
					await message.author.remove_roles(role)
					await asyncio.sleep(0.1)
			while newRole not in message.author.roles:
				await message.author.add_roles(newRole)
				await asyncio.sleep(0.1)
			await sendEmbed(message.channel, None, '%s has advanced to level %s and been given the *%s* role.' % (message.author.mention, newLevel, newRole.name))


# Checks the list of timers to see if any have expired and need to be acted upon
async def checkguildTimers():
	while True:
		output = ''
		actions = 0
		for guild in client.guilds:
			if len(guildTimers[guild.id]) > 0:
				if debugMode:
					#await sendEmbed(devChannel, None, 'Checking %s timers for tasks to be executed.' % len(guildTimers[guild.id]))
					print('%s (%s): Checking %s active timers for tasks to be performed.' % (guild.name, guild.id, len(guildTimers[guild.id])))
				for i in guildTimers[guild.id]:
					if (i['expiration'] - datetime.datetime.now()).total_seconds() < 0:
						actions += 1
						if debugMode: output += '%s: %s is ready to be un%sd and objectID %s is being removed.\n' % (actions, i['subjectname'], i['timertype'], i['objectid'])
						if i['timertype'] == 'mute':
							thisguild = client.get_guild(guild.id)
							userName = thisguild.get_member(i['subjectid'])
							try:
								await userName.remove_roles(mutedRole[guild.id])
							except:
								await sendEmbed(errorChannel, 'Timer Error', 'Error removing mutedRole from %s on %s\n\n%s' % (thisguild.name, userName.name, traceback.format_exc()))
						elif i['timertype'] == 'ban':
							thisguild = client.get_guild(guild.id)
							targetUser = await client.fetch_user(i['subjectid'])
							try:
								await thisguild.unban(targetUser)
							except:
								await sendEmbed(errorChannel, 'Timer Error', 'Error unbanning %s from %s\n\n%s' % (thisguild.name, userName.name, traceback.format_exc()))
						_unsetguildtimer(guild.id, i['objectid'])
						guildTimers[guild.id].remove(i)
				if debugMode:
					#await sendEmbed(devChannel, None, 'There are %s actions ready to be performed.\n' % actions + output)
					print('%s (%s): There are %s tasks ready to be performed.\n%s' % (guild.name, guild.id, actions, output))
			else:
				if debugMode:
					#await sendEmbed(devChannel, None, 'There are no active timers to check, checking again in 60 seconds.')
					print('%s (%s): There are no active timers, checking again in 60 seconds.' % (guild.name, guild.id))
		await asyncio.sleep(60)


# Uses the Twilio API to send the developer a text anytime the bot errors
def devText(msg):
	twClient = Client(twilioSID, twilioToken)
	twClient.messages.create(body = msg, from_ = twilioPhone, to = devPhone)


# Takes a length of time in the form of seconds and outputs it in a nice human-readable format
def prettyTime(seconds, magnitude):
	seconds = int(abs(seconds))
	years, seconds = divmod(seconds, 31536000)
	days, seconds = divmod(seconds, 86400)
	hours, seconds = divmod(seconds, 3600)
	minutes, seconds = divmod(seconds, 60)
	allMagnitudes = collections.OrderedDict([('years', years), ('days', days), ('hours', hours), ('minutes', minutes), ('seconds', seconds)])
	magnitudes = collections.OrderedDict([])
	total = 0
	for key, value in allMagnitudes.items():
		magnitudes[key] = value
		if value > 0:
			total += 1
		if key == magnitude:
			break
	count = 0
	output = ''
	for key, value in magnitudes.items():
		if value > 0:
			if value == 1:
				output += '%s %s' % (value, key[:-1])
			else:
				output += '%s %s' % (value, key)
			count += 1
			if count != total:
				if total > 2:
					output += ', '
				else:
					output += ' '
			if count == total - 1:
				output += 'and '
	if count == 0:
		output = '0 %s' % (magnitude)
	return output


# Takes a number and adds commas to separate the hundreds, thousands, millions, etc
def prettyNums(number):
	num = str('{0:,}'.format(number))
	return num


# Added this here to shorten the code everywhere else, as this is used in nearly every bot command
async def sendEmbed(channel, title, output):
	if title != None:
		embed = discord.Embed(title = title, description = output, color = embedColor)
	else:
		embed = discord.Embed(description = output, color = embedColor)
	await channel.send(embed = embed)

def isModuleForGod(moduleName):
	return moduleName == 'system' or moduleName == 'test'

def isUserGod(userId):
	return userId in unrestrictedUsers

def isModuleForAdmins(moduleName):
	return moduleName == 'moderation'

def isUserAdmin(guildId, userId):
	guild = client.get_guild(guildId)
	admins = _getattrib(guildId, 'server', 'admins')
	if admins == None:
		_setattrib(guildId, 'server', 'admins', [guild.owner.id])
		admins = [guild.owner.id]
	else:
		member = guild.get_member(userId)
		for admin in _getattrib(guildId, 'server', 'admins'):
			if admin in [role.id for role in member.roles]:
				admins.append(userId)
				break
	return userId in admins

def isCommandExempt(command):
	return command in exemptCommands

def isModuleAllowedHere(guildId, channelId, moduleName):
	return _getmodulerestriction(moduleName, guildId, channelId) == False

loadConfig()
loadModules()
client = discord.Client()

# This runs when the bot successfully logs into Discord
@client.event
async def on_ready():
	log('hub', 'Logged in as')
	log('hub', '	Username : %s' % (client.user.name))
	log('hub', '	User ID  : %s' % (client.user.id))
	log('hub', 'Connected to')
	for guild in client.guilds:
		log('hub', '	guild  : %s' % (guild.name))
		loadguildConfig(guild.id)
		for member in guild.members:
			_setattrib(member.id, 'user', 'name', '%s#%s' % (member.name, member.discriminator))
			_setattrib(member.id, 'user', '%s->nick' % (member.guild.id), member.nick)
			if guild.id == 335302037615017984:
				_getxp(guild.id, member.id)
		for channel in guild.channels:
			if channel.type != 4: # Ignore Channel Categories
				log('hub', '		Channel: %s' % (channel.name))
	setClientVariables()
	if configJSON['greeting'] != "false":
		await sendEmbed(devChannel, None, eval(configJSON['greeting']))
	task = asyncio.ensure_future(checkguildTimers())
	async for message in devChannel.history(limit=100):
		if message.content.startswith('?^?^'):
			await message.delete()


@client.event
async def on_guild_update(before, after):
	_setattrib(before.id, "guild", "name", after.name)


# This runs anytime a new message is sent in Discord, in a place that the bot can see it
@client.event
async def on_message(message):
	# Module-less quit and reload commands for the developers
	if message.author.id in unrestrictedUsers:
		if message.content == '%s^%s^quit' % (prefix, prefix):
				await message.delete()
				await client.close()
				time.sleep(1)
		elif message.content == '%s^%s^reload' % (prefix, prefix):
				await message.delete()
				unloadModules()
				unloadConfig()
				loadConfig()
				loadModules()
				for guild in client.guilds:
					loadguildConfig(guild.id)
	# Ignore DMs
	if message.guild == None:
		return
	# Ignore bot messages
	if message.author.bot:
		return
	# Delete messages if the author has the muted role
	if mutedRole[message.guild.id] in message.author.roles:
		await message.delete()
		return
	# Handle Ansible Messages
	if message.channel.id != 698247715431120947 and message.channel.id in ansibleTargets:
		try:
			func = getattr(namespace, 'ansible')
			await func(message, ["passmessage"])
			del(func)
		except:
			print('Error on ansible pass:\n%s\n\n%s' % (message.content, traceback.format_exc()))
	# Check the message for bot mentions
	if botID in message.raw_mentions:
		# :upside_down: :zany_face: :sob: :triumph: :rage: :scream: :sweat: :yawning_face: :shushing_face: :no_mouth: :expressionless: :grimacing: :rolling_eyes: :dizzy_face: :zipper_mouth: :poop: :ghost: :robot: :clap_tone1: :thumbsup_tone1: :thumbsdown_tone1: :fingers_crossed_tone1: :v_tone1: :love_you_gesture_tone1: :metal_tone1: :ok_hand_tone1: :pinching_hand_tone1: :vulcan_tone1: :wave_tone1: :call_me_tone1: :muscle_tone1: :middle_finger_tone1::orange_heart: :no_entry_sign: :100: :anger::interrobang: :mute:
		reactOptions = ['\U0001F643', '\U0001F92A', '\U0001F62D', '\U0001F624', '\U0001F621', '\U0001F631', '\U0001F613', '\U0001F971', '\U0001F92B', '\U0001F636', '\U0001F611', '\U0001F62C', '\U0001F644', '\U0001F635', '\U0001F910', '\U0001F4A9', '\U0001F47B', '\U0001F916', '\U0001F44F', '\U0001F44D', '\U0001F44E', '\U0001F91E', '\U0000270C', '\U0001F91F', '\U0001F918', '\U0001F44C', '\U0001F90F', '\U0001F596', '\U0001F44B', '\U0001F919', '\U0001F4AA', '\U0001F595', '\U0001F9E1', '\U0001F6AB', '\U0001F4AF', '\U0001F4A2', '\U00002049', '\U0001F507']
		reactChoice = random.choice(reactOptions)
		if debugMode:
			print('Reacting with %s' % (reactChoice))
		await message.add_reaction(reactChoice)
	# Handle xp
	if isXPValid(message):
		oldXP, newXP = incrementXP(message)
		await processXPGain(message, oldXP, newXP)
	# Actually look at the message content if it has the proper prefix, check for valid commands, check user permissions, etc
	if message.content.startswith(prefix) and len(message.content) > 0:
		matched = message.content[len(prefix):]
		matchedArr = matched.split()
		i = 0
		print('Prefix match on : "%s" from %s->%s' % (matchedArr[0], message.channel.guild.name, message.channel.name))
		command = matchedArr.pop(0)
		if command in moduleCommands:
			# Ignore invalid Ansible commands
			if command == "ansible":
				if debugMode: print('Checking for ansible command')
				if message.channel.id != 698247715431120947:
					return
			else:
				_incrementactionlog(message.guild.id, 'server', command)
				_incrementactionlog(message.author.id, 'user', command)
			moduleName = moduleCommands[command][0]
			funcName = moduleCommands[command][1]
			if isModuleForGod(moduleName) and not isUserGod(message.author.id):
				if debugMode: print('Checking isModuleForGod')
				return
			if isModuleForAdmins(moduleName) and not isUserAdmin(message.guild.id, message.author.id):
				if debugMode: print('Checking isModuleForAdmins')
				if not isUserGod(message.author.id):
					return
			if not isUserAdmin(message.guild.id, message.author.id) and not isCommandExempt(command) \
					and not isModuleAllowedHere(message.guild.id, message.channel.id, moduleName):
				if debugMode: print('Checking isUserAdmin/isCommandExempt/isModuleAllowedHere')
				if not isUserGod(message.author.id):
					return
			print('Command match on : "%s" from %s->%s' % (command, message.channel.guild.name, message.channel.name))
			print('	%s' % (message.content))
			matched = matched[len(command):].strip()
			outArgs	= []
			cmdArguments = modules[moduleName]['commands'][command]['arguments']
			for arg in sorted(cmdArguments.keys()):
				raw = False
				if 'raw' in cmdArguments[arg].keys() and cmdArguments[arg]['raw'] == 'true':
					raw = True
				outArg = cmdArguments[arg]['default']
				print('	Argument: >%s<, Default: >%s<, Raw: >%s<' % (cmdArguments[arg]['name'], outArg, raw))
				if 'prefix' in cmdArguments[arg].keys():
					if matchedArr[i].startswith(cmdArguments[arg]['prefix']):
						if raw:
							if len(matched) > 0:
								outArg = matched
						else:
							outArg = matchedArr.pop(0)[len(cmdArguments[arg]['prefix']):]
							matched = " ".join(matchedArr)
					else:
						raw = False
				elif raw:
					if len(matched) > 0:
						outArg = matched
				elif len(matchedArr) > 0:
					outArg = matchedArr.pop(0)
					matched = matched[len(outArg):].strip()
				outArgs.append(outArg)
				i = i + 1
				if raw:
					break
			print('	funcName: >%s<, outArgs: %s' % (funcName, outArgs))
			func = getattr(namespace, funcName)
			try:
				await func(message, outArgs)
			# Report exceptions that occur when the bot is lacking Discord permissions
			except discord.Forbidden:
				output = 'Permissions error from %s->%s running "%s"\nFull command: %s' % (message.channel.guild.name, message.channel.name, command, message.content)
				if token == configJSON['prodtoken']:
					await sendEmbed(errorChannel, 'Permissions Error', output)
				else:
					await sendEmbed(devChannel, 'Permissions Error', output)
				await sendEmbed(message.channel, None, 'Sorry, but it looks like I don\'t have permission to do that.')
			# Report any other kind of exception
			except:
				output = 'System error from %s->%s running "%s"\nFull command: %s\n```\n%s```\n\n' % (message.channel.guild.name, message.channel.name, command, message.content, traceback.format_exc())
				if token == configJSON['prodtoken']:
					await sendEmbed(logsChannel, 'System Error', output)
					devText(output)
				else:
					await sendEmbed(devChannel, 'System Error', output)
				await sendEmbed(message.channel, None, 'We apologize, we\'ve experienced a severe error. This error has been reported and we will troubleshoot.')
			del(func)
			if deleteCommands:
				exemptLogDeletedMessages.append(message.id)
				await message.delete()
		return
	# Check to see if any response conditions are met
	for i in guildResponses[message.guild.id]:
		# Check for user match
		if i['userlist'][0] == 'anyone' or message.author.id in i['userlist'] or [role.id for role in message.author.roles if role.id in i['userlist']]:
			# Check for channel match
			if i['channellist'][0] == 'all channels' or message.channel.id in i['channellist']:
				# Check for content match
				if ( i['targetmatch'] == 'contains' and i['targettext'].lower() in message.content.lower() ) or ( i['targetmatch'] == 'exact' and message.content.lower() == i['targettext'].lower() ):
					if i['matchpercent'] == '100' or (random.random() * 100) <= int(i['matchpercent']):
						await sendEmbed(message.channel, None, i['responsetext'])


# Log any message edits
@client.event
async def on_message_edit(before, after):
	# Ignore bot edits
	if before.author.bot == True:
		return
	# Ignore embeds
	elif before.content == after.content:
		return
	else:
		if before.guild == firelinkShrine:
			timestamp = after.edited_at.strftime("%Y-%m-%d %H:%M:%S")
			output = '**%s edited a message in %s**\n**Before:**\n*%s*\n**After:**\n*%s*' % (after.author.mention, after.channel.mention, before.content, after.content)
			embed = discord.Embed(title = None, description = output, color = embedColor)
			#embed.set_thumbnail(url = after.author.avatar_url)
			embed.set_author(name = 'Message Edited', icon_url = after.author.avatar_url)
			embed.set_footer(text = timestamp)
			await logsChannel.send(embed = embed)

# Log any deleted messages
@client.event
async def on_message_delete(message):
	if message.guild == firelinkShrine:
		# Respect the global
		global logDeletedMessages
		if logDeletedMessages == False:
			return
		if message.id in exemptLogDeletedMessages:
			exemptLogDeletedMessages.remove(message.id)
			return
		# Don't log deleted bot messages
		if message.author.bot:
			return
		timestamp =  message.created_at.strftime("%Y-%m-%d %H:%M:%S")
		output = '**Message from %s deleted in %s**:\n*%s*' % (message.author.mention, message.channel.mention, message.content)
		embed = discord.Embed(title = None, description = output, color = embedColor)
		#embed.set_thumbnail(url = message.author.avatar_url)
		embed.set_author(name = 'Message Deleted', icon_url = message.author.avatar_url)
		embed.set_footer(text = timestamp)
		await logsChannel.send(embed = embed)


@client.event
async def on_member_update(before, after):
	_setattrib(after.id, 'user', 'name', '%s#%s' % (after.name, after.discriminator))
	_setattrib(after.id, 'user', '%s->nick' % (after.guild.id), after.nick)


@client.event
async def on_member_join(member):
	_setattrib(member.id, 'user', 'name', member.name + '#' + member.discriminator)
	
	newUser = (len(member.roles) == 1)

	# give new users the default role
	defaultRole = _getattrib(member.guild.id, 'server', 'defaultrole')
	if defaultRole and defaultRole in [role.id for role in member.guild.roles] and newUser:
		for i in member.guild.roles:
			if i.id == defaultRole:
				role = i
				break
		while role not in member.roles:
			await member.add_roles(role)
			await asyncio.sleep(0.1)

	# give new users a random color role
	colorRoles = _getattrib(member.guild.id, 'server', 'colorroles')
	if colorRoles and newUser:
		colorRole = random.choice(colorRoles)
		for i in member.guild.roles:
			if i.id == colorRole:
				role = i
		while role not in member.roles:
			await member.add_roles(role)
			await asyncio.sleep(0.1)

	if member.guild == firelinkShrine:
		timestamp = str(member.joined_at)
		# Log the member joining
		output = '*User:* %s (%s)\n*Timestamp:* %s' % (member.name, member.id, timestamp[:-7])
		await sendEmbed(logsChannel, 'Member Joined', output)


@client.event
async def on_member_remove(member):
	# Log any users that leave FLS
	# _renameattrib(member.id, 'user', 'xp.' + member.guild.id, 'xp.' + member.guild.id + " " + str(datetime.datetime.now())[:-7])
	if member.guild == firelinkShrine:
		joinstamp = str(member.joined_at)
		#leftstamp = str(timestamp)
		#output = '*User:* %s (%s)\n*Joined:* %s\n*Left:* %s' % (member.name, member.id, joinstamp[:-7], leftstamp[:-7])
		output = '*User:* %s (%s)\n*Joined:* %s' % (member.name, member.id, joinstamp[:-7])
		await sendEmbed(logsChannel, 'Member Left', output)


# Register signal handlers
if os.name != 'nt':
	signal.signal(signal.SIGHUP, sighupHandler)
	signal.signal(signal.SIGTERM, sigtermHandler)
	signal.signal(signal.SIGINT, sigtermHandler)


log('hub', 'client.run()')


# Actually launch the Discord client loop
while True:
	try:
		client.run(token)
	except:
		unloadModules()
		unloadConfig()
	sys.exit()
