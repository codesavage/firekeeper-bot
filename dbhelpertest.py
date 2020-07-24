# Like helper, this file contains functions that perform various database
# operations. These functions are all currently conceptual / unused.


def _unsetattrib(userid, attribname):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res = coll.update(
		{
			"id": userid
		},
		{
			"$unset":
			{
				attribname: ""
			}
		}
	)
	res  = coll.find_one(
		{
			"id": str(userid)
		}
	)
	return res


def _setbalance(userid, amount):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res = coll.update(
		{
			"id": userid
		},
		{
			"$set":
			{
				"type": "user",
				"balance": amount
			}
		},
		upsert=True
	)
	res  = coll.find_one(
		{
			"id": str(userid)
		}
	)
	return res['balance']


def _getjailroles(serverid, userid):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res  = coll.find_one(
		{
			"id": str(serverid),
			"type": "server",
			"jailroles.userid": str(userid)
		}
	)
	if(res == None):
		ret = False
	else:
		ret = res['jailroles'][0]['roles']
	return ret


def _setjailroles(serverid, userid, roles):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$jailroles",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : serverid,
					"jailroles.user" : userid
				}
			}
		]
	)
	if res.alive:
		return False
	res = coll.update(
		{
			"id": str(serverid),
			"type": "server"
		},
		{
			"$addToSet": 
			{
				"jailroles":
				{
					"_id": "$ObjectId()",
					"user": str(userid),
					"roles": roles
				}
			}
		},
		upsert=True
	)
	return res


def _unsetjailroles(serverid, userid):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$jailroles",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"id" : serverid,
					"type": "server",
					"jailroles.user" : userid
				}
			}
		]
	)
	if not res.alive:
		return False
	delres = coll.update(
		{
			"id": str(serverid),
			"type": "server"
		},
		{
			"$pull":
			{
				"jailroles": res['jailroles']
			}
		}
	)
	return delres


def _unsetlog(serverid, logentryid):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$log",
					"includeArrayIndex": "arrayIndex"
				}
			},
			{
				"$match" :
				{
					"_id" : logentryid
				}
			}
		]
	)
	for doc in res:
		delres = coll.update(
			{
				"id": str(serverid),
				"type": "server"
			},
			{
				"$pull":
				{
					"log":
					{
						doc['log']
					}
				}
			}
		)
	return delres


def _getraffle(serverid):
db   = dbConn['firekeeperDB']
coll = db[collName]
doc  = coll.find_one(
	{
		"id": str(serverid),
		"type": "server"
	}
)
if(doc == None or "raffle" not in doc):
	ret = None
else:
	now = datetime.datetime.now()
	start = doc['raffle']['start']
	length = datetime.timedelta(hours=1)
	finish = start + length
	if(now > finish):
		ret = None
	else:
		ret = doc['raffle']
return ret


def _setraffle(serverid, gambler, bet):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	doc  = coll.find_one(
		{
			"id": str(serverid),
			"type": "server"
		}
	)
	existing = _getraffle(serverid)
	if(existing):
		if(gambler in existing['gamblers']):
			ret = False
		else:
			res = coll.update(
				{
					"id": serverid,
					"type": "server"
				},
				{
					"$inc":
					{
						"raffle.pot": existing['bet']
					},
					"$addToSet":
					{
						"raffle.gamblers":gambler
					}
				},
				upsert=True
			)
			ret = _getraffle(serverid)
	else:
		res = coll.update(
			{"id": serverid,
			"type": "server"
			},
			{
				"$set":
				{
					"type": "server",
					"raffle.start": datetime.datetime.now(),
					"raffle.bet": bet,
					"raffle.pot": bet,
					"raffle.gamblers": [gambler]
				}
			},
			upsert=True
		)
		ret = _getraffle(serverid)
		ret['new'] = True
	return ret


def _getwords(id):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	results  = coll.aggregate(
		[
			{
				"$unwind" :
				{
					"path" : "$wordcloud"
				}
			},
			{
				"$match" :
				{
					"id" : id
				}
			},
			{
					"$project":
					{
							"wordcloud": 1
					}
			},
			{
				"$limit" : 1
			}
		]
	)
	ret = {}
	for record in results:
		ret = record['wordcloud']
	return ret


def _logwords(serverid, userid, word):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res = coll.update(
		{
			"id": serverid
		},
		{
			"$inc":
			{
				"wordcloud." + word: 1
			}
		},
		upsert=True
	)
	res = coll.update(
		{
			"id": userid
		},
		{
			"$inc":
			{
				"wordcloud." + word: 1
			}
		},
		upsert=True
	)
	return


def _setxp(userid, amount):
	db   = dbConn['firekeeperDB']
	coll = db[collName]
	res = coll.update(
		{
			"id": str(userid),
			"type": "user"
		},
		{
			"$set":
			{
				"xp": amount
			}
		},
		upsert=True
	)
	res  = coll.find_one(
		{
			"id": str(userid)
		}
	)
	ret = res['xp']
	return ret