# This file contains functions that perform various database operations.
# Function names are preceeded by _get, _increment, and _set based on what
# actions they perform. _get retrieves data, _increment adds to existing data,
# and _set replaces existing data.

# The actionlog counts how many times commands have been used per guild/user.
# Used by actionchart and actioncloud
def _getactionlog(id, type):
	db   = dbConn[dbName]
	coll = db[collName]
	results  = coll.aggregate(
		[
			{
				"$unwind":
				{
					"path": "$actionlog"
				}
			},
			{
				"$match":
				{
					"id": id,
					"type": type
				}
			},
			{
					"$project":
					{
							"actionlog": 1
					}
			},
			{
				"$limit": 1
			}
		]
	)
	ret = {}
	for record in results:
		ret = record['actionlog']
	return ret


# Used by on_message event in hub
def _incrementactionlog(id, type, action):
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": id,
			"type": type
		},
		{
			"$inc":
			{
				"actionlog." + action: 1
			}
		},
		upsert=True
	)
	return


# attrib is generally used for unique sets of data that only one command will 
# ever need to access. Used by on_message and on_member_join events in hub, 21,
# slots, admins, and roles (list/add/remove).
def _getattrib(id, type, attribname):
	db   = dbConn[dbName]
	coll = db[collName]
	doc  = coll.find_one(
		{
			"id": id,
			"type": type
		}
	)
	if(doc == None or attribname not in doc):
		ret = None
	else:
		ret = doc[attribname]
	return ret


def _insertattrib(id, type, arrayname, arrayvalue):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.find_one_and_update(
		{
			"id": id,
			"type": type
		},
		{
			"$push": { str(arrayname): arrayvalue }
		}
	)
	res  = coll.find_one(
		{
			"id": id
		}
	)
	return res


def _renameattrib(id, type, attribname, newname):
	db   = dbConn[dbName]
	coll = db[collName]
	doc  = coll.update(
		{
			"id": id,
			"type": type
		},
		{
			"$rename": {str(attribname): str(newname)}
		}
	)
	return doc


# Used by on_message event in hub, 21, slots, admins, and roles (add/remove).
def _setattrib(id, type, attribname, attribvalue):
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": id,
			"type": type
		},
		{
			"$set":
			{
				str(attribname): attribvalue
			}
		},
		upsert=True
	)
	res  = coll.find_one(
		{
			"id": id
		}
	)
	return res


def _unsetattrib(id, type, attribname, attribvalue):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.find_one_and_update(
		{
			"id": id,
			"type": type
		},
		{
			"$pull": { str(attribname): attribvalue }
		}
	)
	return


# Used by balance, give, 21, flip, hangman, slots, nick, and profile.
def _getbalance(userid):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.find_one(
		{
			"id": userid
		}
	)
	if(res == None or "balance" not in res):
		res = coll.update(
			{
				"id": userid
			},
			{
				"$set":
				{
					"type": "user",
					"balance": 10000
				}
			},
			upsert=True
		)
		res  = coll.find_one(
			{
				"id": userid
			}
		)
	return res['balance']


# Used by daily, give, weekly, 21, flip, hangman, flip, and nick.
def _incrementbalance(userid, amount):
	current = _getbalance(userid)
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": userid
		},
		{
			"$set":
			{
				"type": "user"
			},
			"$inc":
			{
				"balance": amount
			}
		},
		upsert=True
	)
	res  = coll.find_one(
		{
			"id": userid
		}
	)
	return res['balance']


# log is used for disciplinary notes. Used by logs.
def _getlog(guildid, operatorid, subjectid, logtype):
	db   = dbConn[dbName]
	coll = db[collName]
	querya = {
		"$unwind" :
		{
			"path" : "$log",
			"includeArrayIndex": "arrayIndex"
		}
	}
	queryb = {
		"$match" :
		{
			"id" : guildid
		}
	}
	queryc = {
		"$project" :
		{
			"log": 1,
			"_id": 0
		}
	}
	if operatorid is not None:
		queryb['$match']['log.operatorid'] = operatorid
	if subjectid is not None:
		queryb['$match']['log.subjectid'] = subjectid
	if len(logtype) > 0:
		queryb['$match']['log.type'] = logtype
	query = [querya, queryb, queryc]
	res  = coll.aggregate(query)
	results = []
	for entry in res:
		results.append(entry)
	return results


# Used by ban, kick, and warn.
def _setlog(guildid, operatorid, subjectid, logtype, description):
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": guildid,
			"type": "server"
		},
		{
			"$addToSet": 
			{
				"log":
				{
					"_id": ObjectId(),
					"operatorid": operatorid,
					"subjectid": subjectid,
					"type": logtype,
					"time": datetime.datetime.now(),
					"description": description
				}
			}
		},
		upsert=True
	)
	return res

def _getquotes(userid, guildid):
	guildid = str(guildid)
	db   = dbConn[dbName]
	coll = db[collName]
	doc  = coll.find_one(
		{
			"id": userid,
			"type": "user"
		}
	)
	if(doc == None or 'quotes' not in doc or guildid not in doc['quotes']):
		ret = None
	else:
		ret = doc['quotes'][guildid]
	return ret


def _savequote(userid, guildid, channelid, channelname, messageid, messagetext, messageimage, messagetimestamp, quotedtimestamp, quotedbyid, quotedbyname):
	guildid = str(guildid)
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			'id': userid,
			'type': 'user'
		},
		{
			'$push':
			{
				'quotes.' + guildid:
				{
					'$each':
					[{'_id': ObjectId(),
					'channelid': channelid,
					'channelname': channelname,
					'messageid': messageid,
					'messagetext': messagetext,
					'messageimage': messageimage,
					'messagetimestamp': messagetimestamp,
					'quotedtimestamp': quotedtimestamp,
					'quotedbyid': quotedbyid,
					'quotedbyname': quotedbyname}]
				}
			}
		},
		upsert=True
	)
	return res


# responses are words or phrases that the bot automatically responds to.
def _getresponses(guildid):
	db   = dbConn[dbName]
	coll = db[collName]
	querya  = {
		"$unwind" :
		{
			"path" : "$responses",
			"includeArrayIndex": "arrayIndex"
		}
	}
	queryb = {
		"$match" :
		{
			"id" : guildid
		}
	}
	queryc = {
		"$project" :
		{
			"responses": 1,
			"_id": 0
		}
	}
	query = [querya, queryb, queryc]
	res = coll.aggregate(query)
	results = []
	for entry in res:
		results.append(entry)
	return results


def _setresponse(guildID, userList, targetMatch, channelList, targetText, responseText, matchPercent):
	objectid = ObjectId()
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": guildID,
			"type": "server"
		},
		{
			"$addToSet": 
			{
				"responses":
				{
					"_id": objectid,
					"userlist": userList,
					"targetmatch": targetMatch,
					"channellist": channelList,
					"targettext": targetText,
					"responsetext": responseText,
					"matchpercent": matchPercent
				}
			}
		},
		upsert = True
	)
	return objectid


def _unsetresponse(guildid, targetid):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.find_one_and_update(
		{
			"id": guildid
		},
		{
			"$pull": { "responses": { "_id": ObjectId(targetid) } }
		}
	)
	return


# rep is reputation, a limited resource that can be given out to other users.
# Not currently implemented in any commands.
def _getrep(userid):
	db = dbConn[dbName]
	coll = db[collName]
	res = coll.find_one(
		{
		'id': userid
		}
	)
	if (res == None or 'reputation' not in res):
		res = coll.update(
			{
				'id': userid
			},
			{
				'$set':
				{
					'type': 'user',
					'reputation': 0
				}
			},
			upsert = True
		)
		res = coll.find_one(
			{
				'id': userid
			}
		)
	return res['reputation']


# Not currently implemented in any commands.
def _incrementrep(userid):
	db = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			'id': userid
		},
		{
			'$inc':
			{
				'reputation': 1
			}
		},
		upsert = True
	)
	res = coll.find_one(
		{
			'id': userid
		}
	)
	return res['reputation']


# timers are used to restrict how often certain commands can be used.
# Used by daily, weekly, and nick.
def _gettimer(guildid, userid, timername):
	db   = dbConn[dbName]
	coll = db[collName]
	results  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$usertimer",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : guildid,
					"usertimer.userid" : userid,
					"usertimer.timername" : timername
				}
			},
			{
				"$sort" : 
				{
					"usertimer.expires" : -1
				}
			},
			{
				"$limit" : 1
			}
		]
	)
	if not results.alive:
		ret = None
	for doc in results:
		now = datetime.datetime.now()
		finish = doc['usertimer']['expires']
		if(finish > now):
			ret = (finish - datetime.datetime.now()).total_seconds()
		else:
			ret = False
	return ret


# Used by daily, weekly, and nick.
def _settimer(guildid, userid, timername, duration):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$usertimer",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : guildid,
					"type": "server",
					"usertimer.userid" : userid,
					"usertimer.timername" : timername
				}
			},
			{
				"$sort" : 
				{
					"usertimer.expires" : -1
				}
			}
		]
	)
	for doc in res:
		delres = coll.update(
			{
				"id": guildid,
				"type": "server"
			},
			{
				"$pull":
				{
					"usertimer":
					{
						"userid": doc['usertimer']['userid'],
						"timername": doc['usertimer']['timername'],
						"expires": doc['usertimer']['expires']
					}
				}
			}
		)
	res = coll.update(
		{
			"id": guildid,
			"type": "server"
		},
		{
			"$addToSet": 
			{
				"usertimer":
				{
					"userid": userid,
					"timername": timername,
					"expires": datetime.datetime.now() + datetime.timedelta(hours=float(duration))
				}
			}
		},
		upsert=True
	)
	return res


# guildtimers are used for mutes and bans.
# Used by ???
def _getguildtimers(guildid):
	db   = dbConn[dbName]
	coll = db[collName]
	querya  = {
		"$unwind" :
		{
			"path" : "$servertimer",
			"includeArrayIndex": "arrayIndex"
		}
	}
	queryb = {
		"$match" :
		{
			"id" : guildid
		}
	}
	queryc = {
		"$project" :
		{
			"servertimer": 1,
			"_id": 0
		}
	}
	query = [querya, queryb, queryc]
	res = coll.aggregate(query)
	results = []
	for entry in res:
		results.append(entry)
	return results


# Used by mute and ban.
def _setguildtimer(guildid, operatorid, subjectid, username, expiration, timertype):
	objectid = ObjectId()
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			"id": guildid,
			"type": "server"
		},
		{
			"$addToSet": 
			{
				"servertimer":
				{
					"_id": objectid,
					"operatorid": operatorid,
					"subjectid": subjectid,
					"subjectname": username,
					"timertype": timertype,
					"expiration": expiration
				}
			}
		},
		upsert = True
	)
	return objectid


def _unsetguildtimer(guildid, targetid):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.find_one_and_update(
		{
			"id": guildid
		},
		{
			"$pull": { "servertimer": { "_id": ObjectId(targetid) } }
		}
	)
	return


# modulerestriction stores permissions for modules so that they can be
# restricted in certain channels. This allows logging and admin use of commands
# in any channel, but not general member usage.
# Used by on_message event in hub and modules.
def _getmodulerestriction(module, guildid, channelid):
	db   = dbConn[dbName]
	coll = db[collName]
	results  = coll.aggregate(
		[
			{
				"$match" :
				{
					"id" : guildid
				}
			},
			{
				"$unwind" :
				{
					"path" : "$modulerestrictions"
				}
			},
			{
				"$project":
				{
					"modulerestrictions": 1
				}
			},
			{
				"$match" :
				{
					"modulerestrictions.module" : module,
					"modulerestrictions.channel" : channelid
				}
			}
		]
	)
	return results.alive


# Used by modules.
def _setmodulerestriction(module, guildid, channelids):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$modulerestrictions",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : guildid,
					"modulerestrictions.module" : module
				}
			}
		]
	)
	#for doc in res:
	for doc in []:
		delres = coll.update(
			{
				"id": guildid,
				"type": "server"
			},
			{
				"$pull":
				{
					"modulerestrictions":
					{
						"module": doc['modulerestrictions']['module'],
						"channel": doc['modulerestrictions']['channel']
					}
				}
			}
		)
	constructed = []
	if len(channelids) > 0:
		for channel in channelids:
			constructed.append({
				"module": module,
				"channel": channel
			})
		db   = dbConn[dbName]
		coll = db[collName]
		res = coll.update(
			{
				"id": guildid,
				"type": "server"
			},
			{
				"$addToSet":
				{
					"modulerestrictions":
					{
						"$each" : constructed
					}
				}
			},
			upsert=True
		)
		return res


# Used by modules.
def _unsetmodulerestriction(module, guildid, channelids):
	db   = dbConn[dbName]
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$modulerestrictions",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : guildid,
					"type": "server",
					"modulerestrictions.module" : module
				}
			}
		]
	)
	for doc in res:
		if(doc['modulerestrictions']['channel'] in channelids):
			delres = coll.update(
				{
					"id": guildid,
					"type": "server"
				},
				{
					"$pull":
					{
						"modulerestrictions":
						{
							"module": doc['modulerestrictions']['module'],
							"channel": doc['modulerestrictions']['channel']
						}
					}
				}
			)

# insert a document for this guild
def _setguild(guildid, name):
	db   = dbConn[dbName]
	coll = db[collName]
	res = coll.insert_one(
		{
			"id": guildid,
			"type": "server",
			"name": name
		}
	)
	return res

# xp is member experience in a guild, gained by sending messages in certain
# channels. It can be used to automatically set new user roles.
# Used by ???
def _getxp(guildid, userid):
	guildid = str(guildid)
	db = dbConn[dbName]
	coll = db[collName]
	res = coll.find_one(
		{
		'id': userid
		}
	)
	#pp = pprint.PrettyPrinter(depth=6)
	#pp.pprint(res)
	if (res == None or 'xp' not in res or guildid not in res['xp']):
		if 'oldxp' in res:
			newxp = int(res['oldxp'])
		else:
			newxp = 0
		res = coll.update(
			{
				'id': userid
			},
			{
				'$set':
				{
					'type': 'user',
					'xp': {guildid: newxp}
				}
			},
			upsert = True
		)
		res = coll.find_one(
			{
				'id': userid
			}
		)
	return res['xp'][guildid]


# Used by ???
def _incrementxp(guildid, userid, amount):
	guildid = str(guildid)
	db = dbConn[dbName]
	coll = db[collName]
	res = coll.update(
		{
			'id': userid
		},
		{
			'$inc':
			{
				'xp.' + guildid: amount
			}
		},
		upsert = True
	)
	res = coll.find_one(
		{
			'id': userid
		}
	)
	return res['xp'][guildid]

def _getxpchannels(guildid):
	guildid = str(guildid)
	db   = dbConn[dbName]
	coll = db[collName]
	querya  = {
		"$unwind" :
		{
			"path" : "$xpchannels",
			"includeArrayIndex": "arrayIndex"
		}
	}
	queryb = {
		"$match" :
		{
			"id" : guildid
		}
	}
	queryc = {
		"$project" :
		{
			"xpchannels": 1,
			"_id": 0
		}
	}
	query = [querya, queryb, queryc]
	res = coll.aggregate(query)
	results = []
	for entry in res:
		results.append(entry)
	return results