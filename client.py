#!/usr/bin/python3
#
# endless-war
# mperron (2018)
#
# a chat bot for the RFCK discord server

import discord
import asyncio
import random
import sys
import time
import json
import subprocess
import traceback
import re

import ewutils
import ewcfg
import ewcmd
import ewcasino
import ewfood
import ewwep
import ewjuviecmd
import ewmarket
import ewspooky
import ewkingpin
import ewplayer
import ewserver
import ewitem
from ewitem import EwItem

from ew import EwUser, EwMarket

ewutils.logMsg('Starting up...')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# A map containing user IDs and the last time in UTC seconds since we sent them
# the help doc via DM. This is to prevent spamming.
last_helped_times = {}

# Map of server ID to a map of active users on that server.
active_users_map = {}

# Map of all command words in the game to their implementing function.
cmd_map = {
	# Attack another player
	ewcfg.cmd_kill: ewwep.attack,
	ewcfg.cmd_shoot: ewwep.attack,

	# Choose your weapon
	ewcfg.cmd_equip: ewwep.equip,

	# Kill yourself
	ewcfg.cmd_suicide: ewwep.suicide,

	# Spar with an ally
	ewcfg.cmd_spar: ewwep.spar,

	# Name your current weapon.
	ewcfg.cmd_annoint: ewwep.annoint,


	# move from juvenile to one of the armies (rowdys or killers)
	ewcfg.cmd_enlist: ewjuviecmd.enlist,

	# gives slime to the miner (message.author)
	ewcfg.cmd_mine: ewjuviecmd.mine,

	# Show the current slime score of a player.
	ewcfg.cmd_score: ewcmd.score,
	ewcfg.cmd_score_alt1: ewcmd.score,

	# Show a player's combat data.
	ewcfg.cmd_data: ewcmd.data,

	#check what time it is, and the weather
	ewcfg.cmd_time: ewcmd.weather,
	ewcfg.cmd_clock: ewcmd.weather,
	ewcfg.cmd_weather: ewcmd.weather,


	# Show the total of negative slime in the world.
	ewcfg.cmd_negaslime: ewspooky.negaslime,

	# revive yourself as a juvenile after having been killed.
	ewcfg.cmd_revive: ewspooky.revive,

	# Ghosts can haunt enlisted players to reduce their slime score.
	ewcfg.cmd_haunt: ewspooky.haunt,


	# Play slime pachinko!
	ewcfg.cmd_slimepachinko: ewcasino.pachinko,

	# Toss the dice at slime craps!
	ewcfg.cmd_slimecraps: ewcasino.craps,

	# Pull the lever on a slot machine!
	ewcfg.cmd_slimeslots: ewcasino.slots,


	# See what's for sale in the Food Court.
	ewcfg.cmd_menu: ewfood.menu,

	# Order refreshing food and drinks!
	ewcfg.cmd_order: ewfood.order,

	# Transfer slime between players. Shares a cooldown with investments.
	ewcfg.cmd_transfer: ewmarket.xfer,
	ewcfg.cmd_transfer_alt1: ewmarket.xfer,

	# Invest in the slime market!
	ewcfg.cmd_invest: ewmarket.invest,

	# Withdraw your investments!
	ewcfg.cmd_withdraw: ewmarket.withdraw,

	# Show the current slime market exchange rate (slime per credit).
	ewcfg.cmd_exchangerate: ewmarket.rate,
	ewcfg.cmd_exchangerate_alt1: ewmarket.rate,

	# Show the player's slime credit.
	ewcfg.cmd_slimecredit: ewmarket.slimecoin,
	ewcfg.cmd_slimecredit_alt1: ewmarket.slimecoin,

	# faction leader consumes the mentioned players of their own faction to absorb their slime count
	# kills the mentioned players
	ewcfg.cmd_devour: ewkingpin.devour,

	# rowdy fucker and cop killer (leaders) can give slimes to anybody
	ewcfg.cmd_giveslime: ewkingpin.giveslime,
	ewcfg.cmd_giveslime_alt1: ewkingpin.giveslime,

	# Remove a megaslime (1 mil slime) from a general.
	ewcfg.cmd_deadmega: ewkingpin.deadmega,


	# awoooooo
	ewcfg.cmd_howl: ewcmd.cmd_howl,
	ewcfg.cmd_howl_alt1: ewcmd.cmd_howl,


	# show player inventory
	ewcfg.cmd_inventory: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt1: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt2: ewitem.inventory_print,
	ewcfg.cmd_inventory_alt3: ewitem.inventory_print,


	# Misc bullshit
	ewcfg.cmd_harvest: ewcmd.harvest,
	ewcfg.cmd_patchnotes: ewcmd.patchnotes,
	ewcfg.cmd_help: ewcmd.help,
	ewcfg.cmd_help_alt1: ewcmd.help,
	ewcfg.cmd_help_alt2: ewcmd.help
}

debug = False
while sys.argv:
	if sys.argv[0].lower() == '--debug':
		debug = True

	sys.argv = sys.argv[1:]

# When debug is enabled, additional commands are turned on.
if debug == True:
	ewutils.logMsg('Debug mode enabled.')

@client.event
async def on_ready():

	ewutils.logMsg('Logged in as {} ({}).'.format(client.user.name, client.user.id))
	ewutils.logMsg('Ready.')


	try:
		await client.change_presence(activity=discord.Game(name="EW " + ewcfg.version))
	except:
		ewutils.logMsg("Failed to change_presence!")

	# Look for a Twitch client_id on disk.
	twitch_client_id = None#ewutils.getTwitchClientId()

	# If no twitch client ID is available, twitch integration will be disabled.
	if twitch_client_id == None: #or len(twitch_client_id) == 0:
		ewutils.logMsg('No twitch_client_id file found. Twitch integration disabled.')
	else:
		ewutils.logMsg("Enabled Twitch integration.")

	# Channels in the connected discord servers to announce to.
	channels_announcement = []

	# Channels in the connected discord servers to send stock market updates to. Map of server ID to channel.
	channels_stockmarket = {}

	for server in client.guilds:
		# Update server data in the database
		ewserver.server_update(server = server)

		# Grep around for channels
		ewutils.logMsg("connected to: {}".format(server.name))
		for channel in server.channels:
			if(channel.type == discord.ChannelType.text):
				if(channel.name == ewcfg.channel_twitch_announcement):
					channels_announcement.append(channel)
					ewutils.logMsg("• found for announcements: {}".format(channel.name))

				elif(channel.name == ewcfg.channel_stockexchange):
					channels_stockmarket[server.id] = channel
					ewutils.logMsg("• found for stock exchange: {}".format(channel.name))

	time_now = int(time.time())
	time_last_twitch = time_now
	time_twitch_downed = 0
	time_last_pvp = time_now
	time_last_market = time_now


	# Every three hours we log a message saying the periodic task hook is still active. On startup, we want this to happen within about 60 seconds, and then on the normal 3 hour interval.
	time_last_logged = time_now - ewcfg.update_hookstillactive + 60

	stream_live = None
	while True:
		time_now = int(time.time())

		# Periodic message to log that this stuff is still running.
		if (time_now - time_last_logged) >= ewcfg.update_hookstillactive:
			time_last_logged = time_now

			ewutils.logMsg("Periodic hook still active.")

		# Check to see if a stream is live via the Twitch API.
		if twitch_client_id != None and (time_now - time_last_twitch) >= ewcfg.update_twitch:
			time_last_twitch = time_now

			try:
				# Twitch API call to see if there are any active streams.
				json_string = ""
				p = subprocess.Popen("curl -H 'Client-ID: {}' -X GET 'https://api.twitch.tv/helix/streams?user_login=rowdyfrickerscopkillers' 2>/dev/null".format(twitch_client_id), shell=True, stdout=subprocess.PIPE)
				for line in p.stdout.readlines():
					json_string += line.decode('utf-8')
				json_parsed = json.loads(json_string)

				# When a stream is up, data is an array of stream information objects.
				data = json_parsed.get('data')
				if data != None:
					data_count = len(data)
					stream_was_live = stream_live
					stream_live = True if data_count > 0 else False

					if stream_was_live == True and stream_live == False:
						time_twitch_downed = time_now

					if stream_was_live == False and stream_live == True and (time_now - time_twitch_downed) > 600:
						ewutils.logMsg("The stream is now live.")

						# The stream has transitioned from offline to online. Make an announcement!
						for channel in channels_announcement:
							await ewutils.send_message(
								channel,
								"ATTENTION CITIZENS. THE **ROWDY FUCKER** AND THE **COP KILLER** ARE **STREAMING**. BEWARE OF INCREASED KILLER AND ROWDY ACTIVITY.\n\n@everyone\n{}".format(
									"https://www.twitch.tv/rowdyfrickerscopkillers"
								)
							)
			except:
				ewutils.logMsg('Twitch handler hit an exception (continuing):')
				traceback.print_exc(file=sys.stdout)

		# Clear PvP roles from players who are no longer flagged.
		if (time_now - time_last_pvp) >= ewcfg.update_pvp:
			time_last_pvp = time_now

			try:
				for server in client.guilds:
					roles_map = ewutils.getRoleMap(server.roles)

					role_juvenile_pvp = roles_map[ewcfg.role_juvenile_pvp]
					role_rowdyfuckers_pvp = roles_map[ewcfg.role_rowdyfuckers_pvp]
					role_copkillers_pvp = roles_map[ewcfg.role_copkillers_pvp]

					# Monitor all user roles and update if a user is no longer flagged for PvP.
					for member in server.members:
						pvp_role = None

						if role_juvenile_pvp in member.roles:
							pvp_role = role_juvenile_pvp
						elif role_copkillers_pvp in member.roles:
							pvp_role = role_copkillers_pvp
						elif role_rowdyfuckers_pvp in member.roles:
							pvp_role = role_rowdyfuckers_pvp

						if pvp_role != None:
							# Retrieve user data from the database.
							user_data = EwUser(member=member)

							# If the user's PvP expire time is historical, remove the PvP role.
							if user_data.time_expirpvp < int(time.time()):
								await member.remove_roles(pvp_role)

			except:
				ewutils.logMsg('An error occurred in the scheduled role update task:')
				traceback.print_exc(file=sys.stdout)

		# Adjust the exchange rate of slime for the market.
		try:
			for server in client.guilds:
				# Load market data from the database.
				try:
					conn_info = ewutils.databaseConnect()
					conn = conn_info.get('conn')
					cursor = conn.cursor()

					market_data = EwMarket(id_server=server.id, conn=conn, cursor=cursor)
					credit_totals = ewutils.getRecentTotalSlimeCoins(id_server=server.id, conn=conn, cursor=cursor)
				finally:
					cursor.close()
					ewutils.databaseClose(conn_info)

				if market_data.time_lasttick + ewcfg.update_market < time_now:
					market_data.time_lasttick = time_now

					# Nudge the value back to stability.
					rate_market = market_data.rate_market
					if rate_market >= 1030:
						rate_market -= 10
					elif rate_market <= 970:
						rate_market += 10

					# Add participation bonus.
					active_bonus = 0
					active_map = active_users_map.get(server.id)
					if active_map != None:
						active_bonus = len(active_map)

						if active_bonus > 20:
							active_bonus = 20

					active_users_map[server.id] = {}
					rate_market += (active_bonus / 4)

					# Invest/Withdraw effects
					credit_rate = 0
					if credit_totals[0] != credit_totals[1]:
						# Positive if net investment, negative if net withdrawal.
						credit_change = (credit_totals[0] - credit_totals[1])
						credit_rate = ((credit_change * 1.0) / credit_totals[1])

						if credit_rate > 1.0:
							credit_rate = 1.0
						elif credit_rate < -0.5:
							credit_rate = -0.5

						credit_rate = int((credit_rate * ewcfg.max_iw_swing) if credit_rate > 0 else (credit_rate * 2 * ewcfg.max_iw_swing))

					rate_market += credit_rate

					# Tick down the boombust cooldown.
					if market_data.boombust < 0:
						market_data.boombust += 1
					elif market_data.boombust > 0:
						market_data.boombust -= 1

					# Adjust the market rate.
					fluctuation = 0 #(random.randrange(5) - 2) * 100
					noise = (random.randrange(19) - 9) * 2
					subnoise = (random.randrange(13) - 6)

					# Some extra excitement!
					if noise == 0 and subnoise == 0:
						boombust = (random.randrange(3) - 1) * 200

						# If a boombust occurs shortly after a previous boombust, make sure it's the opposite effect. (Boom follows bust, bust follows boom.)
						if (market_data.boombust > 0 and boombust > 0) or (market_data.boombust < 0 and boombust < 0):
							boombust *= -1

						if boombust != 0:
							market_data.boombust = ewcfg.cd_boombust

							if boombust < 0:
								market_data.boombust *= -1
					else:
						boombust = 0

					rate_market += fluctuation + noise + subnoise + boombust
					if rate_market < 300:
						rate_market = (300 + noise + subnoise)

					percentage = ((rate_market / 10) - 100)
					percentage_abs = percentage * -1

					# If the value hits 0, we're stuck there forever.
					if market_data.rate_exchange <= 100:
						market_data.rate_exchange = 100

					# Apply the market change to the casino balance and exchange rate.
					market_data.slimes_casino = int(market_data.slimes_casino * (rate_market / 1000.0))
					market_data.rate_exchange = int(market_data.rate_exchange * (rate_market / 1000.0))
					
					# Advance the time and potentially change weather.
					market_data.clock += 1
					if market_data.clock >= 24 or market_data.clock < 0:
						market_data.clock = 0
					weatherchange = random.randrange(30)
					if weatherchange >= 29:
						pattern_count = len(ewcfg.weather_list)
						if pattern_count > 1:
							weather_old = market_data.weather

							# Randomly select a new weather pattern. Try again if we get the same one we currently have.
							while market_data.weather == weather_old:
								pick = random.randrange(len(ewcfg.weather_list))
								market_data.weather = ewcfg.weather_list[pick].name

						# Log message for statistics tracking.
						ewutils.logMsg("The weather changed. It's now {}.".format(market_data.weather))

					try:
						conn_info = ewutils.databaseConnect()
						conn = conn_info.get('conn')
						cursor = conn.cursor()

						# Persist new data.
						market_data.rate_market = rate_market
						market_data.persist(conn=conn, cursor=cursor)

						# Create a historical snapshot.
						ewutils.persistMarketHistory(market_data=market_data, conn=conn, cursor=cursor)

						# Increase stamina for all players below the max.
						ewutils.pushupServerStamina(id_server = server.id, conn = conn, cursor = cursor)

						# Decrease inebriation for all players above min (0).
						ewutils.pushdownServerInebriation(id_server = server.id, conn = conn, cursor = cursor)

						conn.commit()
					finally:
						cursor.close()
						ewutils.databaseClose(conn_info)

					# Give some indication of how the market is doing to the users.
					response = "..."

					# Market is up ...
					if rate_market > 1200:
						response = 'The slimeconomy is skyrocketing!!! Slime stock is up {p:.3g}%!!!'.format(p=percentage)
					elif rate_market > 1100:
						response = 'The slimeconomy is booming! Slime stock is up {p:.3g}%!'.format(p=percentage)
					elif rate_market > 1000:
						response = 'The slimeconomy is doing well. Slime stock is up {p:.3g}%.'.format(p=percentage)
					# Market is down ...
					elif rate_market < 800:
						response = 'The slimeconomy is plummetting!!! Slime stock is down {p:.3g}%!!!'.format(p=percentage_abs)
					elif rate_market < 900:
						response = 'The slimeconomy is stagnating! Slime stock is down {p:.3g}%!'.format(p=percentage_abs)
					elif rate_market < 1000:
						response = 'The slimeconomy is a bit sluggish. Slime stock is down {p:.3g}%.'.format(p=percentage_abs)
					# Perfectly balanced
					else:
						response = 'The slimeconomy is holding steady. No change in slime stock value.'
					
					if market_data.clock == 6:
						response += ' The Slime Stock Exchange is now open for business.'
					elif market_data.clock == 18:
						response += ' The Slime Stock Exchange has closed for the night.'

					# Send the announcement.
					channel = channels_stockmarket.get(server.id)
					if channel != None:
						await client.send_message(channel, ('**' + response + '**'))
					else:
						ewutils.logMsg('No stock market channel for server {}'.format(server.name))
		except:
			ewutils.logMsg('An error occurred in the scheduled slime market update task:')
			traceback.print_exc(file=sys.stdout)

		# Wait a while before running periodic tasks.
		await asyncio.sleep(15)

@client.event
async def on_member_join(member):
	roles_map = ewutils.getRoleMap(member.guild.roles)
	role_juvenile = roles_map[ewcfg.role_juvenile]

	ewutils.logMsg("New member \"{}\" joined. Assigned Juveniles role.".format(member.display_name))

	member.edit(roles=role_juvenile)

	#await client.replace_roles(member, role_juvenile)

@client.event
async def on_message_delete(message):
	if message != None and message.guild != None and message.author.id != client.user.id and message.content.startswith(ewcfg.cmd_prefix):
		ewutils.logMsg("deleted message from {}: {}".format(message.author.display_name, message.content))
		await ewutils.send_message(message.channel, ewutils.formatMessage(message.author, '**I SAW THAT.**'))

@client.event
async def on_message(message):
	time_now = int(time.time())

	""" do not interact with our own messages """
	if message.author.id == client.user.id or message.author.bot == True:
		return

	if message.guild != None:
		# Note that the user posted a message.
		active_map = active_users_map.get(message.guild.id)
		if active_map == None:
			active_map = {}
			active_users_map[message.guild.id] = active_map
		active_map[message.author.id] = True

		# Update player information.
		ewplayer.player_update(
			member = message.author,
			server = message.guild
		)

	content_tolower = message.content.lower()
	re_awoo = re.compile('.*![a]+[w]+o[o]+.*')

	if message.content.startswith(ewcfg.cmd_prefix) or message.guild == None or len(message.author.roles) < 2:
		"""
			Wake up if we need to respond to messages. Could be:
				message starts with !
				direct message (server == None)
				user is new/has no roles (len(roles) < 2)
		"""

		# tokenize the message. the command should be the first word.
		tokens = message.content.split(' ')
		tokens_count = len(tokens)
		cmd = tokens[0].lower()

		# remove mentions to us
		mentions = list(filter(lambda user : user.id != client.user.id, message.mentions))
		mentions_count = len(mentions)

		# Create command object
		cmd_obj = ewcmd.EwCmd(
			tokens = tokens,
			message = message,
			client = client,
			mentions = mentions
		)

		""" reply to DMs with help document """
		if message.guild == None:
			# Direct message the player their inventory.
			if ewitem.cmd_is_inventory(cmd):
				return await ewitem.inventory_print(cmd_obj)
			else:
				time_last = last_helped_times.get(message.author.id, 0)

				# Only send the help doc once every thirty seconds. There's no need to spam it.
				if (time_now - time_last) > 30:
					last_helped_times[message.author.id] = time_now
					await ewutils.send_message(message.channel, 'Check out the guide for help: https://ew.krakissi.net/guide/')

			# Nothing else to do in a DM.
			return

		# common data we'll need
		roles_map = cmd_obj.roles_map
#ff
		# assign the juveniles role to a user with only 1 or 0 roles.
		if len(message.author.roles) < 2:
			role_juvenile = roles_map[ewcfg.role_juvenile]
			#await message.author.edit(roles=[role_juvenile])
			await ewutils.editRoles(new_roles=[role_juvenile], member=message.author, cmd=cmd)
			#await client.replace_roles(message.author, role_juvenile)
			return

		# Scold/ignore offline players.
		if message.author.status == discord.Status.offline:
			resp = await ewcmd.start(cmd = cmd_obj)
			response = "You cannot participate in the ENDLESS WAR while offline."

			if resp != None:
				await ewutils.editmessage(resp, ewutils.formatMessage(message.author, response))
			else:
				await ewutils.send_message(message.channel, ewutils.formatMessage(message.author, response))

			return

		# Check the main command map for the requested command.
		global cmd_map
		cmd_fn = cmd_map.get(cmd)

		if cmd_fn != None:
			# Execute found command
			return await cmd_fn(cmd_obj)

		# FIXME debug
		# Test item creation
		elif cmd == '!create':
			item_id = ewitem.item_create(
				item_type = 'medal',
				id_user = message.author.id,
				id_server = message.guild.id,
				item_props = {
					'medal_name': 'Test Award',
					'medal_desc': '**{medal_name}**: *Awarded to Krak by Krak for testing shit.*'
				}
			)

			ewutils.logMsg('Created item: {}'.format(item_id))
			item = EwItem(id_item = item_id)
			item.item_props['test'] = 'meow'
			item.persist()

			item = EwItem(id_item = item_id)

			await ewutils.send_message(message.channel, ewutils.formatMessage(message.author, ewitem.item_look(item)))

		# FIXME debug
		# Test item deletion
		elif cmd == '!delete':
			items = ewitem.inventory(
				id_user = message.author.id,
				id_server = message.guild.id
			)

			for item in items:
				ewitem.item_delete(
					id_item = item.get('id_item')
				)

			await ewutils.send_message(message.channel, ewutils.formatMessage(message.author, 'ok'))

		# AWOOOOO
		elif re_awoo.match(cmd):
			return await ewcmd.cmd_howl(cmd_obj)

		# Debug command to override the role of a user
		elif debug == True and cmd == (ewcfg.cmd_prefix + 'setrole'):
			resp = await ewcmd.start(cmd = cmd_obj)
			response = ""

			if mentions_count == 0:
				response = 'Set who\'s role?'
			else:
				role_target = tokens[1]
				role = roles_map.get(role_target)

				if role != None:
					for user in mentions:
						try:
							await user.edit(roles=role)
						except:
							ewutils.logMsg(
								'Failed to replace_roles for user {} with {}.'.format(user.display_name, role.name))

					response = 'Done.'
				else:
					response = 'Unrecognized role.'

			await ewutils.editmessage(resp, ewutils.formatMessage(message.author, response))

		# didn't match any of the command words.
		else:
			resp = await ewcmd.start(cmd = cmd_obj)

			""" couldn't process the command. bail out!! """
			""" bot rule 0: be cute """
			randint = random.randint(1,3)
			msg_mistake = "ENDLESS WAR is growing frustrated."
			if randint == 2:
				msg_mistake = "ENDLESS WAR denies you his favor."
			elif randint == 3:
				msg_mistake = "ENDLESS WAR pays you no mind."

			await asyncio.sleep(1)
			await ewutils.editmessage(resp, msg_mistake)
			await asyncio.sleep(2)
			resp.delete()
			#await client.delete_message(resp)

	elif content_tolower.find(ewcfg.cmd_howl) >= 0 or content_tolower.find(ewcfg.cmd_howl_alt1) >= 0 or re_awoo.match(content_tolower):
		""" Howl if !howl is in the message at all. """
		return await ewcmd.cmd_howl(ewcmd.EwCmd(
			message = message,
			client = client
		))

# find our REST API token
token = ewutils.getToken()

if token == None or len(token) == 0:
	ewutils.logMsg('Please place your API token in a file called "token", in the same directory as this script.')
	sys.exit(0)

# connect to discord and run indefinitely
client.run(token)
