import asyncio
import random

import discord

import ewcfg
import ewstats
import ewutils

class EwQuadrantFlavor:
	id_quadrant = ""
	
	aliases = []

	resp_add_onesided = ""

	resp_add_relationship = ""

	resp_view_onesided = ""

	resp_view_onesided_self = ""

	resp_view_relationship = ""

	resp_view_relationship_self = ""

	def __init__(self,
		id_quadrant = "",
		aliases = [],
		resp_add_onesided = "",
		resp_add_relationship = "",
		resp_view_onesided = "",
		resp_view_onesided_self = "",
		resp_view_relationship = "",
		resp_view_relationship_self = ""
	    ):
		self.id_quadrant = id_quadrant
		self.aliases = aliases
		self.resp_add_onesided = resp_add_onesided
		self.resp_add_relationship = resp_add_relationship
		self.resp_view_onesided = resp_view_onesided
		self.resp_view_onesided_self = resp_view_onesided_self
		self.resp_view_relationship = resp_view_relationship
		self.resp_view_relationship_self = resp_view_relationship_self 

class EwQuadrant:

	id_server = ""

	id_user = ""

	quadrant = ""

	id_target = ""

	id_target2 = ""


	def __init__(self, id_server = None, id_user = None, quadrant = None, id_target = None, id_target2 = None):
		if id_server is not None and id_user is not None and quadrant is not None:
			self.id_server = id_server
			self.id_user = id_user
			self.quadrant = quadrant

			if id_target is not None:
				
				self.id_target = id_target
				if quadrant == ewcfg.quadrant_ashen and id_target2 is not None:
					self.id_target2 = id_target2

				ewutils.execute_sql_query("REPLACE INTO quadrants ({col_id_server}, {col_id_user}, {col_quadrant}, {col_target}, {col_target2}) VALUES (%s, %s, %s, %s, %s)".format(
					col_id_server = ewcfg.col_id_server,
					col_id_user = ewcfg.col_id_user,
					col_quadrant = ewcfg.col_quadrant,
					col_target = ewcfg.col_quadrants_target,
					col_target2 = ewcfg.col_quadrants_target2
					), (    
					self.id_server,
					self.id_user,
					self.quadrant,
					self.id_target,
					self.id_target2
				))

			else:
				data = ewutils.execute_sql_query("SELECT {col_target}, {col_target2} FROM quadrants WHERE {col_id_server} = %s AND {col_id_user} = %s AND {col_quadrant} = %s".format(
					col_target = ewcfg.col_quadrants_target,
					col_target2 = ewcfg.col_quadrants_target2,
					col_id_server = ewcfg.col_id_server,
					col_id_user = ewcfg.col_id_user,
					col_quadrant = ewcfg.col_quadrant
					), (
					self.id_server,
					self.id_user,
					self.quadrant
				))
				
				if len(data) > 0:
					self.id_target = data[0][0]
					self.id_target2 = data[0][1]



	def persist(self):
		ewutils.execute_sql_query("REPLACE INTO quadrants ({col_id_server}, {col_id_user}, {col_quadrant}, {col_target}, {col_target2}) VALUES (%s, %s, %s, %s, %s)".format(
			col_id_server = ewcfg.col_id_server,
			col_id_user = ewcfg.col_id_user,
			col_quadrant = ewcfg.col_quadrant,
			col_target = ewcfg.col_quadrants_target,
			col_target2 = ewcfg.col_quadrants_target2
			), (    
			self.id_server,
			self.id_user,
			self.quadrant,
			self.id_target,
			self.id_target2
		))
	
	def check_if_onesided(self):
		target_quadrant = EwQuadrant(id_server = self.id_server, id_user = self.id_target, quadrant = self.quadrant)

		if self.quadrant == ewcfg.quadrant_ashen:
			if self.id_target2 is not None:
				target2_quadrant = EwQuadrant(id_server = self.id_server, id_user = self.id_target2, quadrant = self.quadrant)
				target_targets = [target_quadrant.id_target, target_quadrant.id_target2]
				target2_targets = [target2_quadrant.id_target, target2_quadrant.id_target2]

				if self.id_user in target_targets and \
				    self.id_user in target2_targets and \
				    self.id_target in target2_targets and \
				    self.id_target2 in target_targets:
					return False
			return True

		elif target_quadrant.id_target == self.id_user:
			return False
		else:
			return True

async def add_quadrant(cmd):
	response = ""
	author = cmd.message.author
	quadrant = None

	for token in cmd.tokens[1:]:
		if token.lower() in ewcfg.quadrants_map:
			quadrant = ewcfg.quadrants_map[token.lower()]
		if quadrant is not None:
			break
	
	if quadrant is None:
		response = "Please select a quadrant for your romantic feelings."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	if cmd.mentions_count == 0:
		response = "Please select a target for your romantic feelings."
		return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

	target = cmd.mentions[0].id
	target2 = None
	if quadrant.id_quadrant == ewcfg.quadrant_ashen and cmd.mentions_count > 1:
		target2 = cmd.mentions[1].id

	quadrant_data = EwQuadrant(id_server = author.server.id, id_user = author.id, quadrant = quadrant.id_quadrant, id_target = target, id_target2 = target2)
	
	onesided = quadrant_data.check_if_onesided()

	if onesided:
		comment = random.choice(ewcfg.quadrants_comments_onesided)
		resp_add = quadrant.resp_add_onesided

	else:
		comment = random.choice(ewcfg.quadrants_comments_relationship)
		resp_add = quadrant.resp_add_relationship

	if target2 is None:
		resp_add = resp_add.format(cmd.mentions[0].display_name)
	else:
		resp_add = resp_add.format("{} and {}".format(cmd.mentions[0].display_name, cmd.mentions[1].display_name))
	response = "{} {}".format(resp_add, comment)

		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	

async def get_quadrants(cmd):
	response = ""
	author = cmd.message.author
	if cmd.mentions_count > 0:
		member = cmd.mentions[0]
	else:
		member = author
	for quadrant in ewcfg.quadrant_ids:
		quadrant_data = EwQuadrant(id_server = member.server.id, id_user = member.id, quadrant = quadrant)
		if quadrant_data.id_target != "":
			response += "\n"
			response += get_quadrant(cmd, quadrant)

	if response == "":
		response = "{} quadrants are completely empty. " + ewcfg.emote_broken_heart

		if cmd.mentions_count > 0:
			response = response.format("Their")
		else:
			response = response.format("Your")

	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def get_flushed(cmd):
	response = get_quadrant(cmd, ewcfg.quadrant_flushed)
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def get_pale(cmd):
	response = get_quadrant(cmd, ewcfg.quadrant_pale)
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def get_caliginous(cmd):
	response = get_quadrant(cmd, ewcfg.quadrant_caliginous)
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def get_ashen(cmd):
	response = get_quadrant(cmd, ewcfg.quadrant_ashen)
		
	return await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

def get_quadrant(cmd, id_quadrant):

	author = cmd.message.author
	quadrant = ewcfg.quadrants_map[id_quadrant]
	if cmd.mentions_count == 0:
		quadrant_data = EwQuadrant(id_server = author.server.id, id_user = author.id, quadrant = quadrant.id_quadrant)
		if author.server.get_member(quadrant_data.id_target) is None:
			quadrant_data.id_target = ""
		if author.server.get_member(quadrant_data.id_target2) is None:
			quadrant_data.id_target2 = ""

		quadrant_data.persist()
		

		if quadrant_data.id_target == "":
			response = "You have no one in this quadrant."
		else:
			onesided = quadrant_data.check_if_onesided()

			if quadrant.id_quadrant == ewcfg.quadrant_ashen and quadrant_data.id_target2 != "":
				target_name = "{} and {}".format(author.server.get_member(quadrant_data.id_target).display_name, author.server.get_member(quadrant_data.id_target2).display_name)
			else:
				target_name = author.server.get_member(quadrant_data.id_target).display_name

			if not onesided:
				response = quadrant.resp_view_relationship_self.format(target_name)
			else:
				response = quadrant.resp_view_onesided_self.format(target_name)

	else:
		member = cmd.mentions[0]
		quadrant_data = EwQuadrant(id_server = member.server.id, id_user = member.id, quadrant = quadrant.id_quadrant)

		if author.server.get_member(quadrant_data.id_target) is None:
			quadrant_data.id_target = ""
		if author.server.get_member(quadrant_data.id_target2) is None:
			quadrant_data.id_target2 = ""

		quadrant_data.persist()

		if quadrant_data.id_target == "":
			response = "They have no one in this quadrant."
		else:

			onesided = quadrant_data.check_if_onesided()

			if quadrant.id_quadrant == ewcfg.quadrant_ashen and quadrant_data.id_target2 != "":
				target_name = "{} and {}".format(author.server.get_member(quadrant_data.id_target).display_name, author.server.get_member(quadrant_data.id_target2).display_name)
			else:
				target_name = author.server.get_member(quadrant_data.id_target).display_name

			if not onesided:
				response = quadrant.resp_view_relationship.format(member.display_name, target_name)
			else:
				response = quadrant.resp_view_onesided.format(member.display_name, target_name)
		
		
	return response
