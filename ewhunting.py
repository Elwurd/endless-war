import time
import random
import math
import asyncio

import ewcfg
import ewutils
import ewitem
import ewrolemgr
import ewstats
import ewwep

from ew import EwUser
from ewitem import EwItem
from ewmarket import EwMarket
from ewplayer import EwPlayer
from ewdistrict import EwDistrict
from ewslimeoid import EwSlimeoid
from ewstatuseffects import EwEnemyStatusEffect

""" Enemy data model for database persistence """

class EwEnemy:
	id_enemy = 0
	id_server = ""

	combatant_type = "enemy"

	# The amount of slime an enemy has
	slimes = 0

	# The total amount of damage an enemy has sustained throughout its lifetime
	totaldamage = 0

	# The type of AI the enemy uses to select which players to attack
	ai = ""

	# The name of enemy shown in responses
	display_name = ""

	# Used to help identify enemies of the same type in a district
	identifier = ""

	# An enemy's level, which determines how much damage it does
	level = 0

	# An enemy's location
	poi = ""

	# Life state 0 = Dead, pending for deletion when it tries its next attack / action
	# Life state 1 = Alive / Activated raid boss
	# Life state 2 = Raid boss pending activation
	life_state = 0

	# Used to determine how much slime an enemy gets, what AI it uses, as well as what weapon it uses.
	enemytype = ""

	# The 'weapon' of an enemy
	attacktype = ""

	# An enemy's bleed storage
	bleed_storage = 0

	# Used for determining when a raid boss should be able to move between districts
	time_lastenter = 0

	# Used to determine how much slime an enemy started out with to create a 'health bar' ( current slime / initial slime )
	initialslimes = 0

	# Enemies despawn when this number reaches 10800 (3 hours)
	lifetime = 0

	# Used by the 'defender' AI to determine who it should retaliate against
	id_target = ""

	# Used by raid bosses to determine when they should activate
	raidtimer = 0
	
	# Determines if an enemy should use its rare variant or not
	rare_status = 0
	
	# What kind of weather the enemy is suited to
	weathertype = 0

	# Sap armor
	hardened_sap = 0
	
	# What faction the enemy belongs to
	faction = ""
	
	# What class the enemy belongs to
	enemyclass = ""

	""" Load the enemy data from the database. """

	def __init__(self, id_enemy=None, id_server=None, enemytype=None):
		self.combatant_type = ewcfg.combatant_type_enemy

		query_suffix = ""

		if id_enemy != None:
			query_suffix = " WHERE id_enemy = '{}'".format(id_enemy)
		else:

			if id_server != None:
				query_suffix = " WHERE id_server = '{}'".format(id_server)
				if enemytype != None:
					query_suffix += " AND enemytype = '{}'".format(enemytype)

		if query_suffix != "":
			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor();

				# Retrieve object
				cursor.execute(
					"SELECT {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {} FROM enemies{}".format(
						ewcfg.col_id_enemy,
						ewcfg.col_id_server,
						ewcfg.col_enemy_slimes,
						ewcfg.col_enemy_totaldamage,
						ewcfg.col_enemy_ai,
						ewcfg.col_enemy_type,
						ewcfg.col_enemy_attacktype,
						ewcfg.col_enemy_display_name,
						ewcfg.col_enemy_identifier,
						ewcfg.col_enemy_level,
						ewcfg.col_enemy_poi,
						ewcfg.col_enemy_life_state,
						ewcfg.col_enemy_bleed_storage,
						ewcfg.col_enemy_time_lastenter,
						ewcfg.col_enemy_initialslimes,
						ewcfg.col_enemy_lifetime,
						ewcfg.col_enemy_id_target,
						ewcfg.col_enemy_raidtimer,
						ewcfg.col_enemy_rare_status,
						ewcfg.col_enemy_hardened_sap,
						ewcfg.col_enemy_weathertype,
						ewcfg.col_faction,
						ewcfg.col_enemy_class,
						query_suffix
					))
				result = cursor.fetchone();

				if result != None:
					# Record found: apply the data to this object.
					self.id_enemy = result[0]
					self.id_server = result[1]
					self.slimes = result[2]
					self.totaldamage = result[3]
					self.ai = result[4]
					self.enemytype = result[5]
					self.attacktype = result[6]
					self.display_name = result[7]
					self.identifier = result[8]
					self.level = result[9]
					self.poi = result[10]
					self.life_state = result[11]
					self.bleed_storage = result[12]
					self.time_lastenter = result[13]
					self.initialslimes = result[14]
					self.lifetime = result[15]
					self.id_target = result[16]
					self.raidtimer = result[17]
					self.rare_status = result[18]
					self.hardened_sap = result[19]
					self.weathertype = result[20]
					self.faction = result[21]
					self.enemyclass = result[22]

			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	""" Save enemy data object to the database. """

	def persist(self):
		try:
			conn_info = ewutils.databaseConnect()
			conn = conn_info.get('conn')
			cursor = conn.cursor();

			# Save the object.
			cursor.execute(
				"REPLACE INTO enemies({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
					ewcfg.col_id_enemy,
					ewcfg.col_id_server,
					ewcfg.col_enemy_slimes,
					ewcfg.col_enemy_totaldamage,
					ewcfg.col_enemy_ai,
					ewcfg.col_enemy_type,
					ewcfg.col_enemy_attacktype,
					ewcfg.col_enemy_display_name,
					ewcfg.col_enemy_identifier,
					ewcfg.col_enemy_level,
					ewcfg.col_enemy_poi,
					ewcfg.col_enemy_life_state,
					ewcfg.col_enemy_bleed_storage,
					ewcfg.col_enemy_time_lastenter,
					ewcfg.col_enemy_initialslimes,
					ewcfg.col_enemy_lifetime,
					ewcfg.col_enemy_id_target,
					ewcfg.col_enemy_raidtimer,
					ewcfg.col_enemy_rare_status,
					ewcfg.col_enemy_hardened_sap,
					ewcfg.col_enemy_weathertype,
					ewcfg.col_faction,
					ewcfg.col_enemy_class
				), (
					self.id_enemy,
					self.id_server,
					self.slimes,
					self.totaldamage,
					self.ai,
					self.enemytype,
					self.attacktype,
					self.display_name,
					self.identifier,
					self.level,
					self.poi,
					self.life_state,
					self.bleed_storage,
					self.time_lastenter,
					self.initialslimes,
					self.lifetime,
					self.id_target,
					self.raidtimer,
					self.rare_status,
					self.hardened_sap,
					self.weathertype,
					self.faction,
					self.enemyclass,
				))

			conn.commit()
		finally:
			# Clean up the database handles.
			cursor.close()
			ewutils.databaseClose(conn_info)

	# Function that enemies use to attack or otherwise interact with players.
	async def kill(self):

		client = ewutils.get_client()

		last_messages = []
		should_post_resp_cont = True

		enemy_data = self

		time_now = int(time.time())
		resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
		district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
		market_data = EwMarket(id_server=enemy_data.id_server)
		ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel

		target_data = None
		target_player = None
		target_slimeoid = None

		used_attacktype = None

		if enemy_data.attacktype != ewcfg.enemy_attacktype_unarmed:
			used_attacktype = ewcfg.attack_type_map.get(enemy_data.attacktype)
		else:
			used_attacktype = ewcfg.enemy_attacktype_unarmed

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin})".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				if random.randrange(100) > 92:
					response = random.choice(ewcfg.coward_responses)
					response = response.format(enemy_data.display_name, enemy_data.display_name)
					resp_cont.add_channel_response(ch_name, response)
		if enemy_data.ai == ewcfg.enemy_ai_sandbag:
			target_data = None
		else:
			target_data = get_target_by_ai(enemy_data)

		if check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
			# Raid boss has activated!
			response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
					   "\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
				ewcfg.emote_megaslime,
				enemy_data.display_name,
				enemy_data.level,
				enemy_data.slimes,
				ewcfg.emote_megaslime
			)
			resp_cont.add_channel_response(ch_name, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_alive
			enemy_data.time_lastenter = time_now
			enemy_data.persist()

			target_data = None

		elif check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_alive:
			# Raid boss attacks.
			pass

		# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
		elif check_raidboss_countdown(enemy_data) == False:

			target_data = None

			timer = (enemy_data.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

			if timer < ewcfg.enemy_attack_tick_length and timer != 0:
				timer = ewcfg.enemy_attack_tick_length

			countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
			resp_cont.add_channel_response(ch_name, countdown_response)

			#TODO: Edit the countdown message instead of deleting and reposting
			last_messages = await resp_cont.post()
			asyncio.ensure_future(ewutils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))
			
			# Don't post resp_cont a second time while the countdown is going on.
			should_post_resp_cont = False

		if target_data != None:

			target_player = EwPlayer(id_user=target_data.id_user)
			target_slimeoid = EwSlimeoid(id_user=target_data.id_user)

			target_weapon = None
			target_weapon_item = None
			if target_data.weapon >= 0:
				target_weapon_item = EwItem(id_item = target_data.weapon)
				target_weapon = ewcfg.weapon_map.get(target_weapon_item.item_props.get("weapon_type"))
			
			server = client.get_server(target_data.id_server)
			# server = discord.Server(id=target_data.id_server)
			# print(target_data.id_server)
			# channel = discord.utils.get(server.channels, name=ch_name)

			# print(server)

			# member = discord.utils.get(channel.server.members, name=target_player.display_name)
			# print(member)

			target_mutations = target_data.get_mutations()

			miss = False
			crit = False
			backfire = False
			backfire_damage = 0
			strikes = 0
			sap_damage = 0
			sap_ignored = 0
			miss_mod = 0
			crit_mod = 0
			dmg_mod = 0

			# Weaponized flavor text.
			#randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]
			hitzone = ewwep.get_hitzone()
			randombodypart = hitzone.name
			if random.random() < 0.5:
				randombodypart = random.choice(hitzone.aliases)

			miss_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type = ewcfg.status_effect_type_miss, target = ewcfg.status_effect_target_self, shootee_data = target_data, hitzone = hitzone) + ewwep.apply_combat_mods(user_data=target_data, desired_type = ewcfg.status_effect_type_miss, target = ewcfg.status_effect_target_other, shooter_data = enemy_data, hitzone = hitzone), 2)
			crit_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type = ewcfg.status_effect_type_crit, target = ewcfg.status_effect_target_self, shootee_data = target_data, hitzone = hitzone) + ewwep.apply_combat_mods(user_data=target_data, desired_type = ewcfg.status_effect_type_crit, target = ewcfg.status_effect_target_other, shooter_data = enemy_data, hitzone = hitzone), 2)
			dmg_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type = ewcfg.status_effect_type_damage, target = ewcfg.status_effect_target_self, shootee_data = target_data, hitzone = hitzone) + ewwep.apply_combat_mods(user_data=target_data, desired_type = ewcfg.status_effect_type_damage, target = ewcfg.status_effect_target_other, shooter_data = enemy_data, hitzone = hitzone), 2)
			
			# maybe enemies COULD have weapon skills? could punishes players who die to the same enemy without mining up beforehand
			# slimes_damage = int((slimes_spent * 4) * (100 + (user_data.weaponskill * 10)) / 100.0)

			# since enemies dont use up slime or hunger, this is only used for damage calculation
			slimes_spent = int(ewutils.slime_bylevel(enemy_data.level) / 40 * ewcfg.enemy_attack_tick_length / 2)

			slimes_damage = int(slimes_spent * 4)

			if used_attacktype == ewcfg.enemy_attacktype_unarmed:
				slimes_damage /= 2  # specific to juvies
			if enemy_data.enemytype == ewcfg.enemy_type_microslime:
				slimes_damage *= 20  # specific to microslime
				
			if enemy_data.weathertype == ewcfg.enemy_weathertype_rainresist:
				slimes_damage *= 1.5

			slimes_damage += int(slimes_damage * dmg_mod)

			slimes_dropped = target_data.totaldamage + target_data.slimes

			target_iskillers = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_killers
			target_isrowdys = target_data.life_state == ewcfg.life_state_enlisted and target_data.faction == ewcfg.faction_rowdys
			target_isslimecorp = target_data.life_state in [ewcfg.life_state_lucky, ewcfg.life_state_executive]
			target_isjuvie = target_data.life_state == ewcfg.life_state_juvenile
			target_isnotdead = target_data.life_state != ewcfg.life_state_corpse
			target_isshambler = target_data.life_state == ewcfg.life_state_shambler

			if target_data.life_state == ewcfg.life_state_kingpin:
				# Disallow killing generals.
				response = "The {} tries to attack the kingpin, but is taken aback by the sheer girth of their slime.".format(enemy_data.display_name)
				resp_cont.add_channel_response(ch_name, response)

			elif (time_now - target_data.time_lastrevive) < ewcfg.invuln_onrevive:
				# User is currently invulnerable.
				response = "The {} tries to attack {}, but they have died too recently and are immune.".format(
					enemy_data.display_name,
					target_player.display_name)
				resp_cont.add_channel_response(ch_name, response)

			# enemies dont fuck with ghosts, ghosts dont fuck with enemies.
			elif (target_iskillers or target_isrowdys or target_isjuvie or target_isslimecorp or target_isshambler) and (target_isnotdead):
				was_killed = False
				was_hurt = False

				if target_data.life_state in [ewcfg.life_state_shambler, ewcfg.life_state_enlisted, ewcfg.life_state_juvenile, ewcfg.life_state_lucky, ewcfg.life_state_executive]:

					# If a target is being attacked by an enemy with the defender ai, check to make sure it can be hit.
					if (enemy_data.ai == ewcfg.enemy_ai_defender) and (ewutils.check_defender_targets(target_data, enemy_data) == False):
						return
					else:
						# Target can be hurt by enemies.
						was_hurt = True

				if was_hurt:
					# Attacking-type-specific adjustments
					if used_attacktype != ewcfg.enemy_attacktype_unarmed and used_attacktype.fn_effect != None:
						# Build effect container
						ctn = EwEnemyEffectContainer(
							miss=miss,
							backfire=backfire,
							crit=crit,
							slimes_damage=slimes_damage,
							enemy_data=enemy_data,
							target_data=target_data,
							sap_damage=sap_damage,
							sap_ignored=sap_ignored,
							backfire_damage=backfire_damage,
							miss_mod=miss_mod,
							crit_mod=crit_mod
						)

						# Make adjustments
						used_attacktype.fn_effect(ctn)

						# Apply effects for non-reference values
						miss = ctn.miss
						backfire = ctn.backfire
						crit = ctn.crit
						slimes_damage = ctn.slimes_damage
						strikes = ctn.strikes
						sap_damage = ctn.sap_damage
						sap_ignored = ctn.sap_ignored
						backfire_damage = ctn.backfire_damage

					# can't hit lucky lucy
					if target_data.life_state == ewcfg.life_state_lucky:
						miss = True

					if miss:
						slimes_damage = 0
						sap_damage = 0
						crit = False
	
					if crit:
						sap_damage += 1

					enemy_data.persist()
					target_data = EwUser(id_user = target_data.id_user, id_server = target_data.id_server, data_level = 1)

					# apply defensive mods
					slimes_damage *= ewwep.damage_mod_defend(
						shootee_data = target_data,
						shootee_mutations = target_mutations,
						shootee_weapon = target_weapon,
						market_data = market_data
					)

					if target_weapon != None:
						if sap_damage > 0 and ewcfg.weapon_class_defensive in target_weapon.classes:
							sap_damage -= 1

			
					# apply hardened sap armor
					sap_armor = ewwep.get_sap_armor(shootee_data = target_data, sap_ignored = sap_ignored)
					slimes_damage *= sap_armor
					slimes_damage = int(max(slimes_damage, 0))
    
					sap_damage = min(sap_damage, target_data.hardened_sap)

					injury_severity = ewwep.get_injury_severity(target_data, slimes_damage, crit)

					if slimes_damage >= target_data.slimes - target_data.bleed_storage:
						was_killed = True
						slimes_damage = max(target_data.slimes - target_data.bleed_storage, 0)

					sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

					# move around slime as a result of the shot
					if target_isjuvie:
						slimes_drained = int(3 * slimes_damage / 4)  # 3/4
					else:
						slimes_drained = 0

					damage = slimes_damage

					slimes_tobleed = int((slimes_damage - slimes_drained) / 2)
					if ewcfg.mutation_id_bleedingheart in target_mutations:
						slimes_tobleed *= 2

					slimes_directdamage = slimes_damage - slimes_tobleed
					slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained

					# Damage victim's wardrobe (heh, WARdrobe... get it??)
					victim_cosmetics = ewitem.inventory(
						id_user = target_data.id_user,
						id_server = target_data.id_server,
						item_type_filter = ewcfg.it_cosmetic
					)

					onbreak_responses = []

					for cosmetic in victim_cosmetics:
						c = EwItem(cosmetic.get('id_item'))

						# Damage it if the cosmetic is adorned and it has a durability limit
						if c.item_props.get("adorned") == 'true' and c.item_props['durability'] is not None:

							#print("{} current durability: {}:".format(c.item_props.get("cosmetic_name"), c.item_props['durability']))

							durability_afterhit = int(c.item_props['durability']) - slimes_damage

							#print("{} durability after next hit: {}:".format(c.item_props.get("cosmetic_name"), durability_afterhit))

							if durability_afterhit <= 0:  # If it breaks
								c.item_props['durability'] = durability_afterhit
								c.persist()


								target_data.persist()

								onbreak_responses.append(
									str(c.item_props['str_onbreak']).format(c.item_props['cosmetic_name']))

								ewitem.item_delete(id_item = c.id_item)

							else:
								c.item_props['durability'] = durability_afterhit
								c.persist()

						else:
							pass

					market_data.splattered_slimes += slimes_damage
					market_data.persist()
					district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
					target_data.bleed_storage += slimes_tobleed
					target_data.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
					target_data.hardened_sap -= sap_damage
					sewer_data.change_slimes(n=slimes_drained)

					if was_killed:

						# Dedorn player cosmetics
						#ewitem.item_dedorn_cosmetics(id_server=target_data.id_server, id_user=target_data.id_user)
						# Drop all items into district
						#ewitem.item_dropall(id_server=target_data.id_server, id_user=target_data.id_user)

						# Give a bonus to the player's weapon skill for killing a stronger player.
						# if target_data.slimelevel >= user_data.slimelevel and weapon is not None:
						# enemy_data.add_weaponskill(n = 1, weapon_type = weapon.id_weapon)

						explode_damage = ewutils.slime_bylevel(target_data.slimelevel) / 5
						# explode, damaging everyone in the district

						# release bleed storage
						slimes_todistrict = target_data.slimes

						district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

						# Player was killed. Remove its id from enemies with defender ai.
						enemy_data.id_target = ""
						target_data.id_killer = enemy_data.id_enemy

						#target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)

						kill_descriptor = "beaten to death"
						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							response = used_attacktype.str_damage.format(
								name_enemy=enemy_data.display_name,
								name_target=("<@!{}>".format(target_data.id_user)),
								hitzone=randombodypart,
								strikes=strikes
							)
							kill_descriptor = used_attacktype.str_killdescriptor
							if crit:
								response += " {}".format(used_attacktype.str_crit.format(
									name_enemy=enemy_data.display_name,
									name_target=target_player.display_name
								))

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n\n" + onbreak_response

							response += "\n\n{}".format(used_attacktype.str_kill.format(
								name_enemy=enemy_data.display_name,
								name_target=("<@!{}>".format(target_data.id_user)),
								emote_skull=ewcfg.emote_slimeskull
							))
							target_data.trauma = used_attacktype.id_type

						else:
							response = ""

							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response = onbreak_response + "\n\n"

							response = "{name_target} is hit!!\n\n{name_target} has died.".format(
								name_target=target_player.display_name)

							target_data.trauma = ewcfg.trauma_id_environment

						if target_slimeoid.life_state == ewcfg.slimeoid_state_active:
							brain = ewcfg.brain_map.get(target_slimeoid.ai)
							response += "\n\n" + brain.str_death.format(slimeoid_name=target_slimeoid.name)

						enemy_data.persist()
						district_data.persist()
						die_resp = target_data.die(cause=ewcfg.cause_killing_enemy) # moved after trauma definition so it can gurantee .die knows killer
						district_data = EwDistrict(district = district_data.name, id_server = district_data.id_server)

						target_data.persist()
						resp_cont.add_response_container(die_resp)
						resp_cont.add_channel_response(ch_name, response)

						# don't recreate enemy data if enemy was killed in explosion
						if check_death(enemy_data) == False:
							enemy_data = EwEnemy(id_enemy=self.id_enemy)

						target_data = EwUser(id_user = target_data.id_user, id_server = target_data.id_server, data_level = 1)
					else:
						# A non-lethal blow!
						# apply injury
						if injury_severity > 0:
							target_data.apply_injury(hitzone.id_injury, injury_severity, enemy_data.id_enemy)

						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							if miss:
								response = "{}".format(used_attacktype.str_miss.format(
									name_enemy=enemy_data.display_name,
									name_target=target_player.display_name
								))
							elif backfire:
								response = "{}".format(used_attacktype.str_backfire.format(
									name_enemy = enemy_data.display_name,
									name_target = target_player.display_name
								))
								if enemy_data.slimes - enemy_data.bleed_storage <= backfire_damage:
									loot_cont = drop_enemy_loot(enemy_data, district_data)
									resp_cont.add_response_container(loot_cont)
									enemy_data.life_state = ewcfg.enemy_lifestate_dead
									delete_enemy(enemy_data)
								else:
									enemy_data.change_slimes(n = -backfire_damage / 2)
									enemy_data.bleed_storage += int(backfire_damage / 2)
							else:
								response = used_attacktype.str_damage.format(
									name_enemy=enemy_data.display_name,
									name_target=("<@!{}>".format(target_data.id_user)),
									hitzone=randombodypart,
									strikes=strikes
								)
								if crit:
									response += " {}".format(used_attacktype.str_crit.format(
										name_enemy=enemy_data.display_name,
										name_target=target_player.display_name
									))
								sap_response = ""
								if sap_damage > 0:
									sap_response = " and {sap_damage} hardened sap".format(sap_damage = sap_damage)
								response += " {target_name} loses {damage:,} slime{sap_response}!".format(
									target_name=target_player.display_name,
									damage=damage,
									sap_response=sap_response
								)
								if len(onbreak_responses) != 0:
									for onbreak_response in onbreak_responses:
										response += "\n\n" + onbreak_response
						else:
							if miss:
								response = "{target_name} dodges the {enemy_name}'s strike.".format(
									target_name=target_player.display_name, enemy_name=enemy_data.display_name)
							else:
								response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
									target_name=target_player.display_name,
									damage=damage
								)
							if len(onbreak_responses) != 0:
								for onbreak_response in onbreak_responses:
									response += "\n" + onbreak_response

						resp_cont.add_channel_response(ch_name, response)
				else:
					response = '{} is unable to attack {}.'.format(enemy_data.display_name, target_player.display_name)
					resp_cont.add_channel_response(ch_name, response)

				# Persist user and enemy data.
				if enemy_data.life_state == ewcfg.enemy_lifestate_alive or enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
					enemy_data.persist()
				target_data.persist()

				district_data.persist()

				# Assign the corpse role to the newly dead player.
				if was_killed:
					member = server.get_member(target_data.id_user)
					await ewrolemgr.updateRoles(client=client, member=member)
					# announce death in kill feed channel
					# killfeed_channel = ewutils.get_channel(enemy_data.id_server, ewcfg.channel_killfeed)
					# killfeed_resp = resp_cont.channel_responses[ch_name]
					# for r in killfeed_resp:
					#	 resp_cont.add_channel_response(ewcfg.channel_killfeed, r)
					# resp_cont.format_channel_response(ewcfg.channel_killfeed, enemy_data)
					# resp_cont.add_channel_response(ewcfg.channel_killfeed, "`-------------------------`")
				# await ewutils.send_message(client, killfeed_channel, ewutils.formatMessage(enemy_data.display_name, killfeed_resp))

		# Send the response to the player.
		resp_cont.format_channel_response(ch_name, enemy_data)
		if should_post_resp_cont:
			await resp_cont.post()
			
	# Function that enemies used to attack each other.
	async def cannibalize(self):
		client = ewutils.get_client()

		last_messages = []
		should_post_resp_cont = True

		enemy_data = self

		time_now = int(time.time())
		resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
		district_data = EwDistrict(district=enemy_data.poi, id_server=enemy_data.id_server)
		market_data = EwMarket(id_server=enemy_data.id_server)
		ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel

		target_enemy = None

		used_attacktype = None

		if enemy_data.attacktype != ewcfg.enemy_attacktype_unarmed:
			used_attacktype = ewcfg.attack_type_map.get(enemy_data.attacktype)
		else:
			used_attacktype = ewcfg.enemy_attacktype_unarmed

		# Get target's info based on its AI.
		target_enemy = get_target_by_ai(enemy_data, cannibalize = True)

		if check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
			# Raid boss has activated!
			response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
					   "\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
				ewcfg.emote_megaslime,
				enemy_data.display_name,
				enemy_data.level,
				enemy_data.slimes,
				ewcfg.emote_megaslime
			)
			resp_cont.add_channel_response(ch_name, response)

			enemy_data.life_state = ewcfg.enemy_lifestate_alive
			enemy_data.time_lastenter = time_now
			enemy_data.persist()

			target_enemy = None

		elif check_raidboss_countdown(enemy_data) and enemy_data.life_state == ewcfg.enemy_lifestate_alive:
			# Raid boss attacks.
			pass

		# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
		elif check_raidboss_countdown(enemy_data) == False:

			target_enemy = None

			timer = (enemy_data.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

			if timer < ewcfg.enemy_attack_tick_length and timer != 0:
				timer = ewcfg.enemy_attack_tick_length

			countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
			resp_cont.add_channel_response(ch_name, countdown_response)

			# TODO: Edit the countdown message instead of deleting and reposting
			last_messages = await resp_cont.post()
			asyncio.ensure_future(ewutils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))

			# Don't post resp_cont a second time while the countdown is going on.
			should_post_resp_cont = False

		if target_enemy != None:

			server = client.get_server(target_enemy.id_server)

			miss = False
			crit = False
			backfire = False
			backfire_damage = 0
			strikes = 0
			sap_damage = 0
			sap_ignored = 0
			miss_mod = 0
			crit_mod = 0
			dmg_mod = 0

			# Weaponized flavor text.
			# randombodypart = ewcfg.hitzone_list[random.randrange(len(ewcfg.hitzone_list))]
			hitzone = ewwep.get_hitzone()
			randombodypart = hitzone.name
			if random.random() < 0.5:
				randombodypart = random.choice(hitzone.aliases)

			miss_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type=ewcfg.status_effect_type_miss, target=ewcfg.status_effect_target_self, shootee_data=target_enemy, hitzone=hitzone) + ewwep.apply_combat_mods(user_data=target_enemy, desired_type=ewcfg.status_effect_type_miss, target=ewcfg.status_effect_target_other, shooter_data=enemy_data, hitzone=hitzone), 2)
			crit_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type=ewcfg.status_effect_type_crit, target=ewcfg.status_effect_target_self, shootee_data=target_enemy, hitzone=hitzone) + ewwep.apply_combat_mods(user_data=target_enemy, desired_type=ewcfg.status_effect_type_crit, target=ewcfg.status_effect_target_other, shooter_data=enemy_data,  hitzone=hitzone), 2)
			dmg_mod += round(ewwep.apply_combat_mods(user_data=enemy_data, desired_type=ewcfg.status_effect_type_damage, target=ewcfg.status_effect_target_self, shootee_data=target_enemy, hitzone=hitzone) + ewwep.apply_combat_mods(user_data=target_enemy, desired_type=ewcfg.status_effect_type_damage, target=ewcfg.status_effect_target_other, shooter_data=enemy_data, hitzone=hitzone), 2)

			# since enemies dont use up slime or hunger, this is only used for damage calculation
			slimes_spent = int(ewutils.slime_bylevel(enemy_data.level) / 40 * ewcfg.enemy_attack_tick_length / 2)

			slimes_damage = int(slimes_spent * 4)

			if used_attacktype == ewcfg.enemy_attacktype_unarmed:
				slimes_damage /= 2  # specific to juvies
			if enemy_data.enemytype == ewcfg.enemy_type_microslime:
				slimes_damage *= 20  # specific to microslime

			if enemy_data.weathertype == ewcfg.enemy_weathertype_rainresist:
				slimes_damage *= 1.5

			slimes_damage += int(slimes_damage * dmg_mod)

			slimes_dropped = target_enemy.totaldamage + target_enemy.slimes

			# Enemies don't select for these types of lifestates in their AI, this serves as a backup just in case.
			if target_enemy.life_state != ewcfg.enemy_lifestate_unactivated and target_enemy.life_state != ewcfg.enemy_lifestate_dead:
				was_killed = False
				was_hurt = True

				if was_hurt:
					# Attacking-type-specific adjustments
					if used_attacktype != ewcfg.enemy_attacktype_unarmed and used_attacktype.fn_effect != None:
						# Build effect container
						ctn = EwEnemyEffectContainer(
							miss=miss,
							backfire=backfire,
							crit=crit,
							slimes_damage=slimes_damage,
							enemy_data=enemy_data,
							target_data=target_enemy,
							sap_damage=sap_damage,
							sap_ignored=sap_ignored,
							backfire_damage=backfire_damage,
							miss_mod=miss_mod,
							crit_mod=crit_mod
						)

						# Make adjustments
						used_attacktype.fn_effect(ctn)

						# Apply effects for non-reference values
						miss = ctn.miss
						backfire = ctn.backfire
						crit = ctn.crit
						slimes_damage = ctn.slimes_damage
						strikes = ctn.strikes
						sap_damage = ctn.sap_damage
						sap_ignored = ctn.sap_ignored
						backfire_damage = ctn.backfire_damage

					if miss:
						slimes_damage = 0
						sap_damage = 0
						crit = False

					if crit:
						sap_damage += 1

					enemy_data.persist()
					target_enemy = EwEnemy(id_enemy = target_enemy.id_enemy, id_server = target_enemy.id_server)

					# apply hardened sap armor
					sap_armor = ewwep.get_sap_armor(shootee_data=target_enemy, sap_ignored=sap_ignored)
					slimes_damage *= sap_armor
					slimes_damage = int(max(slimes_damage, 0))

					sap_damage = min(sap_damage, target_enemy.hardened_sap)

					if slimes_damage >= target_enemy.slimes - target_enemy.bleed_storage:
						was_killed = True
						slimes_damage = max(target_enemy.slimes - target_enemy.bleed_storage, 0)

					sewer_data = EwDistrict(district=ewcfg.poi_id_thesewers, id_server=enemy_data.id_server)

					slimes_drained = int(3 * slimes_damage / 4)  # 3/4

					damage = slimes_damage

					slimes_tobleed = int((slimes_damage - slimes_drained) / 2)

					slimes_directdamage = slimes_damage - slimes_tobleed
					slimes_splatter = slimes_damage - slimes_tobleed - slimes_drained


					market_data.splattered_slimes += slimes_damage
					market_data.persist()
					district_data.change_slimes(n=slimes_splatter, source=ewcfg.source_killing)
					target_enemy.bleed_storage += slimes_tobleed
					target_enemy.change_slimes(n=- slimes_directdamage, source=ewcfg.source_damage)
					target_enemy.hardened_sap -= sap_damage
					sewer_data.change_slimes(n=slimes_drained)

					if was_killed:
						# Enemy was killed.
						delete_enemy(target_enemy)
						
						# release bleed storage
						slimes_todistrict = target_enemy.slimes

						district_data.change_slimes(n=slimes_todistrict, source=ewcfg.source_killing)

						# target_data.change_slimes(n=-slimes_dropped / 10, source=ewcfg.source_ghostification)

						kill_descriptor = "beaten to death"
						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							response = used_attacktype.str_damage.format(
								name_enemy=enemy_data.display_name,
								name_target=target_enemy.display_name,
								hitzone=randombodypart,
								strikes=strikes
							)
							kill_descriptor = used_attacktype.str_killdescriptor
							if crit:
								response += " {}".format(used_attacktype.str_crit.format(
									name_enemy=enemy_data.display_name,
									name_target=target_enemy.display_name
								))

							response += "\n\n{}".format(used_attacktype.str_kill.format(
								name_enemy=enemy_data.display_name,
								name_target=target_enemy.display_name,
								emote_skull=ewcfg.emote_slimeskull
							))
							
						else:
							response = ""

							response = "{name_target} is hit!!\n\n{name_target} has died.".format(name_target=target_enemy.display_name)


						enemy_data.persist()
						district_data.persist()

						resp_cont.add_channel_response(ch_name, response)
						loot_cont = drop_enemy_loot(target_enemy, district_data)
						resp_cont.add_response_container(loot_cont)

						# don't recreate enemy data if enemy was killed in explosion
						if check_death(enemy_data) == False:
							enemy_data = EwEnemy(id_enemy=self.id_enemy)

					else:
						# A non-lethal blow!

						if used_attacktype != ewcfg.enemy_attacktype_unarmed:
							if miss:
								response = "{}".format(used_attacktype.str_miss.format(
									name_enemy=enemy_data.display_name,
									name_target=target_enemy.display_name
								))
							elif backfire:
								response = "{}".format(used_attacktype.str_backfire.format(
									name_enemy=enemy_data.display_name,
									name_target=target_enemy.display_name
								))
								if enemy_data.slimes - enemy_data.bleed_storage <= backfire_damage:
									loot_cont = drop_enemy_loot(enemy_data, district_data)
									resp_cont.add_response_container(loot_cont)
									enemy_data.life_state = ewcfg.enemy_lifestate_dead
									delete_enemy(enemy_data)
								else:
									enemy_data.change_slimes(n=-backfire_damage / 2)
									enemy_data.bleed_storage += int(backfire_damage / 2)
							else:
								response = used_attacktype.str_damage.format(
									name_enemy=enemy_data.display_name,
									name_target=target_enemy.display_name,
									hitzone=randombodypart,
									strikes=strikes
								)
								if crit:
									response += " {}".format(used_attacktype.str_crit.format(
										name_enemy=enemy_data.display_name,
										name_target=target_enemy.display_name
									))
								sap_response = ""
								if sap_damage > 0:
									sap_response = " and {sap_damage} hardened sap".format(sap_damage=sap_damage)
								response += " {target_name} loses {damage:,} slime{sap_response}!".format(
									target_name=target_enemy.display_name,
									damage=damage,
									sap_response=sap_response
								)

						else:
							if miss:
								response = "{target_name} dodges the {enemy_name}'s strike.".format(
									target_name=target_enemy.display_name, enemy_name=enemy_data.display_name)
							else:
								response = "{target_name} is hit!! {target_name} loses {damage:,} slime!".format(
									target_name=target_enemy.display_name,
									damage=damage
								)

						target_enemy.persist()
						resp_cont.add_channel_response(ch_name, response)
				else:
					response = '{} is unable to attack {}.'.format(enemy_data.display_name, target_enemy.display_name)
					resp_cont.add_channel_response(ch_name, response)

				# Persist user and enemy data.
				if enemy_data.life_state == ewcfg.enemy_lifestate_alive or enemy_data.life_state == ewcfg.enemy_lifestate_unactivated:
					enemy_data.persist()

				district_data.persist()

		# Send the response to the player.
		resp_cont.format_channel_response(ch_name, enemy_data)
		if should_post_resp_cont:
			await resp_cont.post()

	def move(self):
		resp_cont = ewutils.EwResponseContainer(id_server=self.id_server)

		old_district_response = ""
		new_district_response = ""
		gang_base_response = ""

		try:
			# Raid bosses can move into other parts of the outskirts as well as the city, including district zones.
			destinations = ewcfg.poi_neighbors.get(self.poi)
			
			if self.enemytype in ewcfg.gvs_enemies:
				path = [ewcfg.poi_id_assaultflatsbeach, ewcfg.poi_id_vagrantscorner, ewcfg.poi_id_greenlightdistrict, ewcfg.poi_id_downtown]
				
				if self.poi == path[0]:
					destinations = [path[1]]
				elif self.poi == path[1]:
					destinations = [path[2]]
				elif self.poi == path[2]:
					destinations = [path[3]]
				elif self.poi == path[3]:
					# Raid boss has finished its path
					return
			
			# Filter subzones and gang bases out.
			# Nudge raidbosses into the city.
			for destination in destinations:

				destination_poi_data = ewcfg.id_to_poi.get(destination)
				if destination_poi_data.is_subzone or destination_poi_data.is_gangbase:
					destinations.remove(destination)
				
				if self.poi in ewcfg.outskirts_depths:
					if destination in ewcfg.outskirts_depths:
						destinations.remove(destination)
				elif self.poi in ewcfg.outskirts:
					if (destination in ewcfg.outskirts) or (destination in ewcfg.outskirts_depths):
						destinations.remove(destination)
				elif self.poi in ewcfg.outskirts_edges: 
					if (destination in ewcfg.outskirts_edges) or (destination in ewcfg.outskirts):
						destinations.remove(destination)
					

			if len(destinations) > 0:
				
				old_poi = self.poi
				new_poi = random.choice(list(destinations))
					
				self.poi = new_poi
				self.time_lastenter = int(time.time())
				self.id_target = ""

				# print("DEBUG - {} MOVED FROM {} TO {}".format(self.display_name, old_poi, new_poi))

				#new_district = EwDistrict(district=new_poi, id_server=self.id_server)
				#if len(new_district.get_enemies_in_district() > 0:

				# When a raid boss enters a new district, give it a blank identifier
				self.identifier = ''

				new_poi_def = ewcfg.id_to_poi.get(new_poi)
				new_ch_name = new_poi_def.channel
				new_district_response = "*A low roar booms throughout the district, as slime on the ground begins to slosh all around.*\n {} **{} has arrived!** {}".format(
					ewcfg.emote_megaslime,
					self.display_name,
					ewcfg.emote_megaslime
				)
				resp_cont.add_channel_response(new_ch_name, new_district_response)

				old_district_response = "{} has moved to {}!".format(self.display_name, new_poi_def.str_name)
				old_poi_def = ewcfg.id_to_poi.get(old_poi)
				old_ch_name = old_poi_def.channel
				resp_cont.add_channel_response(old_ch_name, old_district_response)

				gang_base_response = "There are reports of a powerful enemy roaming around {}.".format(new_poi_def.str_name)
				resp_cont.add_channel_response(ewcfg.channel_rowdyroughhouse, gang_base_response)
				resp_cont.add_channel_response(ewcfg.channel_copkilltown, gang_base_response)
		finally:
			self.persist()
			return resp_cont

	def change_slimes(self, n=0, source=None):
		change = int(n)
		self.slimes += change

		if n < 0:
			change *= -1  # convert to positive number
			if source == ewcfg.source_damage or source == ewcfg.source_bleeding or source == ewcfg.source_self_damage:
				self.totaldamage += change

		self.persist()
	
	def getStatusEffects(self):
		values = []

		try:
			data = ewutils.execute_sql_query("SELECT {id_status} FROM enemy_status_effects WHERE {id_server} = %s and {id_enemy} = %s".format(
				id_status = ewcfg.col_id_status,
				id_server = ewcfg.col_id_server,
				id_enemy = ewcfg.col_id_enemy
			), (
				self.id_server,
				self.id_enemy
			))

			for row in data:
				values.append(row[0])

		except:
			pass
		finally:
			return values

	def applyStatus(self, id_status = None, value = 0, source = "", multiplier = 1, id_target = ""):
		response = ""
		if id_status != None:
			status = None

			status = ewcfg.status_effects_def_map.get(id_status)
			time_expire = status.time_expire * multiplier

			if status != None:
				statuses = self.getStatusEffects()

				status_effect = EwEnemyStatusEffect(id_status=id_status, enemy_data=self, time_expire=time_expire, value=value, source=source, id_target=id_target)
				
				if id_status in statuses:
					status_effect.value = value

					if status.time_expire > 0 and id_status in ewcfg.stackable_status_effects:
						status_effect.time_expire += time_expire
						response = status.str_acquire

					status_effect.persist()
				else:
					response = status.str_acquire
					
		return response		

	def clear_status(self, id_status = None):
		if id_status != None:
			try:
				conn_info = ewutils.databaseConnect()
				conn = conn_info.get('conn')
				cursor = conn.cursor()

				# Save the object.
				cursor.execute("DELETE FROM enemy_status_effects WHERE {id_status} = %s and {id_enemy} = %s and {id_server} = %s".format(
					id_status = ewcfg.col_id_status,
					id_enemy = ewcfg.col_id_enemy,
					id_server = ewcfg.col_id_server
				), (
					id_status,
					self.id_enemy,
					self.id_server
				))

				conn.commit()
			finally:
				# Clean up the database handles.
				cursor.close()
				ewutils.databaseClose(conn_info)

	def clear_allstatuses(self):
		try:
			ewutils.execute_sql_query("DELETE FROM enemy_status_effects WHERE {id_server} = %s AND {id_enemy} = %s".format(
					id_server = ewcfg.col_id_server,
					id_enemy = ewcfg.col_id_enemy
				),(
					self.id_server,
					self.id_enemy
				))
		except:
			ewutils.logMsg("Failed to clear status effects for enemy {}.".format(self.id_enemy))
	
	def dodge(self):
		enemy_data = self 

		resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
		
		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state} FROM users WHERE {poi} = %s AND {id_server} = %s AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin})".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user = random.choice(users)[0], id_server = enemy_data.id_server)
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != "":
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user = target_data.id_user, id_server = enemy_data.id_server)
			ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel 

			id_status = ewcfg.status_evasive_id

			enemy_data.clear_status(id_status = id_status)

			enemy_data.applyStatus(id_status = id_status, source = enemy_data.id_enemy, id_target = (target_data.id_user if target_data.combatant_type == "player" else target_data.id_enemy))

			response = "{} focuses on dodging {}'s attacks.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)
		
		return resp_cont

	def taunt(self):
		enemy_data = self 

		resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
		
		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			return
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != "":
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user = target_data.id_user, id_server = enemy_data.id_server)
			ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel 

			id_status = ewcfg.status_taunted_id

			target_statuses = target_data.getStatusEffects()

			if id_status in target_statuses:
				return
				
			target_data.applyStatus(id_status = id_status, source = enemy_data.id_enemy, id_target = enemy_data.id_enemy)

			response = "{} taunts {} into attacking it.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)
		
		return resp_cont

	def aim(self):
		enemy_data = self 

		resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
		
		target_data = None

		# Get target's info based on its AI.

		if enemy_data.ai == ewcfg.enemy_ai_coward:
			return
		elif enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != "":
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server)
		else:
			target_data = get_target_by_ai(enemy_data)

		if target_data != None:
			target = EwPlayer(id_user = target_data.id_user, id_server = enemy_data.id_server)
			ch_name = ewcfg.id_to_poi.get(enemy_data.poi).channel 

			id_status = ewcfg.status_aiming_id

			enemy_data.clear_status(id_status = id_status)

			enemy_data.applyStatus(id_status = id_status, source = enemy_data.id_enemy, id_target = (target_data.id_user if target_data.combatant_type == "player" else target_data.id_enemy))

			enemy_data.persist()

			response = "{} aims at {}'s weak spot.".format(enemy_data.display_name, target.display_name)
			resp_cont.add_channel_response(ch_name, response)
		
		return resp_cont

# Reskinned version of effect container from ewwep.
class EwEnemyEffectContainer:
	miss = False
	backfire = False
	backfire_damage = 0
	crit = False
	strikes = 0
	slimes_damage = 0
	enemy_data = None
	target_data = None
	sap_damage = 0
	sap_ignored = 0
	miss_mod = 0
	crit_mod = 0

	# Debug method to dump out the members of this object.
	def dump(self):
		print(
			"effect:\nmiss: {miss}\ncrit: {crit}\nbackfire: {backfire}\nstrikes: {strikes}\nslimes_damage: {slimes_damage}\nslimes_spent: {slimes_spent}".format(
				miss=self.miss,
				backfire=self.backfire,
				crit=self.crit,
				strikes=self.strikes,
				slimes_damage=self.slimes_damage,
				slimes_spent=self.slimes_spent
			))

	def __init__(
			self,
			miss=False,
			backfire=False,
			crit=False,
			strikes=0,
			slimes_damage=0,
			slimes_spent=0,
			enemy_data=None,
			target_data=None,
			sap_damage=0,
			sap_ignored=0,
			backfire_damage=0,
			miss_mod=0,
			crit_mod=0
	):
		self.miss = miss
		self.backfire = backfire
		self.crit = crit
		self.strikes = strikes
		self.slimes_damage = slimes_damage
		self.slimes_spent = slimes_spent
		self.enemy_data = enemy_data
		self.target_data = target_data
		self.sap_damage = sap_damage
		self.sap_ignored = sap_ignored
		self.backfire_damage = backfire_damage
		self.miss_mod = miss_mod
		self.crit_mod = crit_mod

# Debug command. Could be used for events, perhaps?

async def summonenemy(cmd, is_bot_spawn = False):

	author = cmd.message.author

	if not author.server_permissions.administrator and is_bot_spawn == False:
		return

	time_now = int(time.time())
	response = ""
	user_data = EwUser(member=cmd.message.author)

	enemytype = None
	enemy_location = None
	poi = None
	enemy_slimes = None
	enemy_displayname = None
	enemy_level = None

	if len(cmd.tokens) >= 3:

		enemytype = cmd.tokens[1]

		enemy_location = cmd.tokens[2]
		if len(cmd.tokens) >= 6:
			enemy_slimes = cmd.tokens[3]
			enemy_level = cmd.tokens[4]
			enemy_displayname = " ".join(cmd.tokens[5:])
	
		poi = ewcfg.id_to_poi.get(enemy_location)

	if enemytype != None and poi != None:

		enemy = get_enemy_data(enemytype)

		# Assign enemy attributes that weren't assigned in get_enemy_data
		enemy.id_server = user_data.id_server
		enemy.poi = poi.id_poi
		enemy.level = level_byslime(enemy.slimes)
		enemy.lifetime = time_now
		enemy.identifier = set_identifier(poi.id_poi, user_data.id_server)
		enemy.weathertype = ewcfg.enemy_weathertype_normal
		
		# Re-assign rare_status to 0 so custom names don't confuse the dict in ewcfg
		enemy.rare_status = 0
		
		if enemy_slimes != None and enemy_displayname != None and enemy_level != None:
			enemy.initialslimes = enemy_slimes
			enemy.slimes = enemy_slimes
			enemy.display_name = enemy_displayname
			enemy.level = enemy_level

		enemy.persist()

		response = "**DEBUG**: You have summoned **{}**, a level {} enemy of type **{}**. It has {} slime. It spawned in {}.".format(
			enemy.display_name,
			enemy.level,
			enemy.enemytype,
			enemy.slimes,
			enemy.poi
		)
		
	else:
		response = "**DEBUG**: PLEASE RE-SUMMON WITH APPLICABLE TYPING / LOCATION. ADDITIONAL OPTIONS ARE SLIME / LEVEL / DISPLAYNAME"
	if not is_bot_spawn:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))


async def delete_all_enemies(cmd):
	author = cmd.message.author

	if not author.server_permissions.administrator:
		return
	
	id_server = cmd.message.server.id
	
	ewutils.execute_sql_query("DELETE FROM enemies WHERE id_server = {id_server}".format(
		id_server=id_server
	))
	
	ewutils.logMsg("Deleted all enemies from database connected to server {}".format(id_server))

# Gathers all enemies from the database (that are either raid bosses or have users in the same district as them) and has them perform an action
async def enemy_perform_action(id_server):
	#time_start = time.time()
	
	client = ewcfg.get_client()

	despawn_timenow = int(time.time()) - ewcfg.time_despawn

	enemydata = ewutils.execute_sql_query(
		"SELECT {id_enemy} FROM enemies WHERE ((enemies.poi IN (SELECT users.poi FROM users WHERE NOT (users.life_state = %s OR users.life_state = %s) AND users.id_server = {id_server})) OR (enemies.enemytype IN %s) OR (enemies.life_state = %s OR enemies.lifetime < %s) OR (enemies.id_target != '')) AND enemies.id_server = {id_server}".format(
		id_enemy=ewcfg.col_id_enemy,
		id_server=id_server
	), (
		ewcfg.life_state_corpse,
		ewcfg.life_state_kingpin,
		ewcfg.raid_bosses,
		ewcfg.enemy_lifestate_dead,
		despawn_timenow
	))
	#enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE id_server = %s".format(
	#	id_enemy = ewcfg.col_id_enemy
	#),(
	#	id_server,
	#))

	# Remove duplicates from SQL query
	#enemydata = set(enemydata)

	for row in enemydata:
		enemy = EwEnemy(id_enemy=row[0], id_server=id_server)
		enemy_statuses = enemy.getStatusEffects()
		resp_cont = ewutils.EwResponseContainer(id_server=id_server)

		# If an enemy is marked for death or has been alive too long, delete it
		if enemy.life_state == ewcfg.enemy_lifestate_dead or (enemy.lifetime < despawn_timenow):
			delete_enemy(enemy)
		else:
			# If an enemy is an activated raid boss, it has a 1/20 chance to move between districts.
			if enemy.enemytype in ewcfg.raid_bosses and enemy.life_state == ewcfg.enemy_lifestate_alive and check_raidboss_movecooldown(enemy):
				if random.randrange(20) == 0:
					resp_cont = enemy.move()
					if resp_cont != None:
						await resp_cont.post()

			# If an enemy is alive and not a sandbag, make it perform the kill function.
			if enemy.enemytype != ewcfg.enemy_type_sandbag:
				
				ch_name = ewcfg.id_to_poi.get(enemy.poi).channel 

				# Check if the enemy can do anything right now
				if check_raidboss_countdown(enemy) and enemy.life_state == ewcfg.enemy_lifestate_unactivated:
					# Raid boss has activated!
					response = "*The ground quakes beneath your feet as slime begins to pool into one hulking, solidified mass...*" \
							"\n{} **{} has arrived! It's level {} and has {} slime!** {}\n".format(
						ewcfg.emote_megaslime,
						enemy.display_name,
						enemy.level,
						enemy.slimes,
						ewcfg.emote_megaslime
					)
					resp_cont.add_channel_response(ch_name, response)

					enemy.life_state = ewcfg.enemy_lifestate_alive
					enemy.time_lastenter = int(time.time())
					enemy.persist()

				# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
				elif check_raidboss_countdown(enemy) == False:
					timer = (enemy.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

					if timer < ewcfg.enemy_attack_tick_length and timer != 0:
						timer = ewcfg.enemy_attack_tick_length

					countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
					resp_cont.add_channel_response(ch_name, countdown_response)

					#TODO: Edit the countdown message instead of deleting and reposting
					last_messages = await resp_cont.post()
					asyncio.ensure_future(ewutils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))
					resp_cont = None

				elif any([ewcfg.status_evasive_id, ewcfg.status_aiming_id]) not in enemy_statuses and random.randrange(10) == 0:
					resp_cont = random.choice([enemy.dodge, enemy.taunt, enemy.aim])()
				else:
					resp_cont = await enemy.kill()
			else:
				resp_cont = None
				
			if resp_cont != None:
				await resp_cont.post()

	#time_end = time.time()
	#ewutils.logMsg("time spent on performing enemy actions: {}".format(time_end - time_start))

async def enemy_perform_action_gvs(id_server):

	client = ewcfg.get_client()

	despawn_timenow = int(time.time()) - ewcfg.time_despawn

	condition_gaia_sees_shambler_player = "enemies.poi IN (SELECT users.poi FROM users WHERE (users.life_state = '{}'))".format(ewcfg.life_state_shambler)
	condition_gaia_sees_shampler_enemy = "enemies.poi IN (SELECT enemies.poi FROM enemies WHERE (enemies.enemyclass = '{}'))".format(ewcfg.enemy_class_shambler)
	condition_shambler_sees_alive_player = "enemies.poi IN (SELECT users.poi FROM users WHERE (users.life_state IN {}))".format(tuple([ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive]))
	condition_shambler_sees_gaia_enemy = "enemies.poi IN (SELECT enemies.poi FROM enemies WHERE (enemies.enemyclass = '{}'))".format(ewcfg.enemy_class_gaiaslimeoid)

	#print(despawn_timenow)
	
	enemydata = ewutils.execute_sql_query(
		"SELECT {id_enemy} FROM enemies WHERE (enemies.enemytype IN %s) AND (({condition_1}) OR ({condition_2}) OR ({condition_3}) OR ({condition_4}) OR (enemies.enemytype IN %s) OR (enemies.life_state = %s OR enemies.lifetime < %s) OR (enemies.id_target != '')) AND enemies.id_server = {id_server}".format(
			id_enemy=ewcfg.col_id_enemy,
			id_server=id_server,
			condition_1 = condition_gaia_sees_shambler_player,
			condition_2 = condition_gaia_sees_shampler_enemy,
			condition_3 = condition_shambler_sees_alive_player,
			condition_4 = condition_shambler_sees_gaia_enemy
		), (
			ewcfg.gvs_enemies,
			ewcfg.raid_bosses,
			ewcfg.enemy_lifestate_dead,
			despawn_timenow
		))
	# enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE id_server = %s".format(
	#	id_enemy = ewcfg.col_id_enemy
	# ),(
	#	id_server,
	# ))

	# Remove duplicates from SQL query
	# enemydata = set(enemydata)

	for row in enemydata:
		
		enemy = EwEnemy(id_enemy=row[0], id_server=id_server)
		resp_cont = ewutils.EwResponseContainer(id_server=id_server)

		# If an enemy is marked for death or has been alive too long, delete it
		if enemy.life_state == ewcfg.enemy_lifestate_dead or (enemy.lifetime < despawn_timenow):
			delete_enemy(enemy)
		else:
			# The GvS raidboss has pre-determined pathfinding
			if enemy.enemytype in ewcfg.raid_bosses and enemy.life_state == ewcfg.enemy_lifestate_alive and check_raidboss_movecooldown(enemy):
				resp_cont = enemy.move()
				if resp_cont != None:
					await resp_cont.post()

			# If an enemy is alive, make it perform the kill (or cannibalize) function.
			ch_name = ewcfg.id_to_poi.get(enemy.poi).channel

			# Check if the enemy can do anything right now
			if check_raidboss_countdown(enemy) and enemy.life_state == ewcfg.enemy_lifestate_unactivated:
				# Raid boss has activated!
				response = "*The dreaded creature of Dr. Downpour claws its way into {}.*" \
						   "\n{} **{} has arrived! It's level {} and has {} slime. Good luck.** {}\n".format(
					enemy.poi,
					ewcfg.emote_megaslime,
					enemy.display_name,
					enemy.level,
					enemy.slimes,
					ewcfg.emote_megaslime
				)
				resp_cont.add_channel_response(ch_name, response)

				enemy.life_state = ewcfg.enemy_lifestate_alive
				enemy.time_lastenter = int(time.time())
				enemy.persist()

			# If a raid boss is currently counting down, delete the previous countdown message to reduce visual clutter.
			elif check_raidboss_countdown(enemy) == False:
				timer = (enemy.raidtimer - (int(time.time())) + ewcfg.time_raidcountdown)

				if timer < ewcfg.enemy_attack_tick_length and timer != 0:
					timer = ewcfg.enemy_attack_tick_length

				countdown_response = "A sinister presence is lurking. Time remaining: {} seconds...".format(timer)
				resp_cont.add_channel_response(ch_name, countdown_response)

				# TODO: Edit the countdown message instead of deleting and reposting
				last_messages = await resp_cont.post()
				asyncio.ensure_future(
					ewutils.delete_last_message(client, last_messages, ewcfg.enemy_attack_tick_length))
				resp_cont = None
			else:
				district_data = EwDistrict(district = enemy.poi, id_server = enemy.id_server)
				
				# Look for enemies of the opposing 'class'. If none are found, look for players instead.
				if enemy.enemytype in ewcfg.gvs_enemies_gaiaslimeoids:
					if len(district_data.get_enemies_in_district(classes = [ewcfg.enemy_class_shambler])) > 0:
						await enemy.cannibalize()
					elif len(district_data.get_players_in_district(life_states = [ewcfg.life_state_shambler])) > 0:
						await enemy.kill()
				elif enemy.enemytype in ewcfg.gvs_enemies_shamblers:
					life_states = [ewcfg.life_state_juvenile, ewcfg.life_state_enlisted, ewcfg.life_state_executive]
					
					if len(district_data.get_enemies_in_district(classes = [ewcfg.enemy_class_gaiaslimeoid])) > 0:
						await enemy.cannibalize()
					elif len(district_data.get_players_in_district(life_states = life_states, pvp_only = True)) > 0:
						await enemy.kill()
				else:
					return
				
			if resp_cont != None:
				await resp_cont.post()

# Spawns an enemy in a randomized outskirt district. If a district is full, it will try again, up to 5 times.
def spawn_enemy(id_server, pre_chosen_type = None, pre_chosen_poi = None, weather = None):
	time_now = int(time.time())
	response = ""
	ch_name = ""
	resp_cont = ewutils.EwResponseContainer(id_server = id_server)
	chosen_poi = ""
	threat_level = ""
	boss_choices = []

	enemies_count = ewcfg.max_enemies
	try_count = 0

	rarity_choice = random.randrange(10000)

	if rarity_choice <= 5200:
		# common enemies
		enemytype = random.choice(ewcfg.common_enemies)
	elif rarity_choice <= 8000:
		# uncommon enemies
		enemytype = random.choice(ewcfg.uncommon_enemies)
	elif rarity_choice <= 9700:
		# rare enemies
		enemytype = random.choice(ewcfg.rare_enemies)
	else:
		# raid bosses
		threat_level_choice = random.randrange(1000)
		
		if threat_level_choice <= 450:
			threat_level = "Micro"
		elif threat_level_choice <= 720:
			threat_level = "Monstrous"
		elif threat_level_choice <= 900:
			threat_level = "Mega"
		else:
			threat_level = "Mega"
			#threat_level = "Nega"
		
		boss_choices = ewcfg.raid_boss_tiers[threat_level]
		enemytype = random.choice(boss_choices)
		
	if pre_chosen_type is not None:
		enemytype = pre_chosen_type

	# debug manual reassignment
	# enemytype = 'juvie'

	while enemies_count >= ewcfg.max_enemies and try_count < 5:

		# Sand bags only spawn in the dojo
		if enemytype == ewcfg.enemy_type_sandbag:
			potential_chosen_poi = ewcfg.poi_id_dojo
		else:
			potential_chosen_poi = random.choice(ewcfg.outskirts)
			
		if pre_chosen_poi is not None:
			potential_chosen_poi = pre_chosen_poi

		# potential_chosen_poi = 'cratersvilleoutskirts'
		potential_chosen_district = EwDistrict(district=potential_chosen_poi, id_server=id_server)
		enemies_list = potential_chosen_district.get_enemies_in_district()
		enemies_count = len(enemies_list)

		if enemies_count < ewcfg.max_enemies:
			chosen_poi = potential_chosen_poi
			try_count = 5
		else:
			# Enemy couldn't spawn in that district, try again
			try_count += 1

	# If it couldn't find a district in 5 tries or less, back out of spawning that enemy.
	if chosen_poi == "":
		return resp_cont
	
	# If an enemy spawns in the Nuclear Beach, it should be remade as a 'pre-historic' enemy.
	if potential_chosen_poi == ewcfg.poi_id_nuclear_beach:
		enemytype = random.choice(ewcfg.pre_historic_enemies)
		# If the enemy is a raid boss, re-roll it once to make things fair
		if enemytype in ewcfg.raid_bosses:
			enemytype = random.choice(ewcfg.pre_historic_enemies)
	
	# Recursively spawn enemies that belong to groups.
	if enemytype in ewcfg.enemy_group_leaders:
		sub_enemies_list = ewcfg.enemy_spawn_groups[enemytype]
		sub_enemies_list_item_max = len(sub_enemies_list)
		sub_enemy_list_item_count = 0
		
		while sub_enemy_list_item_count < sub_enemies_list_item_max:
			sub_enemy_type = sub_enemies_list[sub_enemy_list_item_count][0] 
			sub_enemy_spawning_max = sub_enemies_list[sub_enemy_list_item_count][1] 
			sub_enemy_spawning_count = 0
			
			sub_enemy_list_item_count += 1
			while sub_enemy_spawning_count < sub_enemy_spawning_max:
				
				sub_enemy_spawning_count += 1
				
				sub_resp_cont = spawn_enemy(id_server=id_server, pre_chosen_type=sub_enemy_type, pre_chosen_poi = chosen_poi)

				resp_cont.add_response_container(sub_resp_cont)

	if enemytype != None:
		enemy = get_enemy_data(enemytype)

		# Assign enemy attributes that weren't assigned in get_enemy_data
		enemy.id_server = id_server
		enemy.level = level_byslime(enemy.slimes)
		enemy.lifetime = time_now
		enemy.initialslimes = enemy.slimes
		enemy.poi = chosen_poi
		enemy.identifier = set_identifier(chosen_poi, id_server)
		enemy.hardened_sap = int(enemy.level / 2)
		enemy.weathertype = weather
		
		if weather != ewcfg.enemy_weathertype_normal:
			if weather == ewcfg.enemy_weathertype_rainresist:
				enemy.display_name = "Bicarbonate {}".format(enemy.display_name)
				enemy.slimes *= 2

		enemy.persist()

		if enemytype not in ewcfg.raid_bosses:
			response = "**An enemy draws near!!** It's a level {} {}, and has {} slime.".format(enemy.level, enemy.display_name, enemy.slimes)
			if enemytype == ewcfg.enemy_type_sandbag:
				response = "A new {} just got sent in. It's level {}, and has {} slime.\n*'Don't hold back!'*, the Dojo Master cries out from afar.".format(enemy.display_name, enemy.level, enemy.slimes)
			
		ch_name = ewcfg.id_to_poi.get(enemy.poi).channel

	if len(response) > 0 and len(ch_name) > 0:
		resp_cont.add_channel_response(ch_name, response)

	return resp_cont

# Finds an enemy based on its regular/shorthand name, or its ID.
def find_enemy(enemy_search=None, user_data=None):
	enemy_found = None
	enemy_search_alias = None
	

	if enemy_search != None:

		enemy_search_tokens = enemy_search.split(' ')
		enemy_search_tokens_upper = enemy_search.upper().split(' ')

		for enemy_type in ewcfg.enemy_data_table:
			aliases = ewcfg.enemy_data_table[enemy_type]["aliases"]
			if enemy_search.lower() in aliases:
				enemy_search_alias = enemy_type
				break
			if not set(enemy_search_tokens).isdisjoint(set(aliases)):
				enemy_search_alias = enemy_type
				break

		# Check if the identifier letter inputted was a user's captcha. If so, ignore it.
		if user_data.weapon >= 0:
			weapon_item = EwItem(id_item=user_data.weapon)
			weapon = ewcfg.weapon_map.get(weapon_item.item_props.get("weapon_type"))
			captcha = weapon_item.item_props.get('captcha')

			if weapon != None and ewcfg.weapon_class_captcha in weapon.classes and captcha not in [None, ""] and captcha in enemy_search_tokens_upper:
				enemy_search_tokens_upper.remove(captcha)

		tokens_set_upper = set(enemy_search_tokens_upper)
		
		identifiers_found = tokens_set_upper.intersection(set(ewcfg.identifier_letters))
		

		if len(identifiers_found) > 0:

			# user passed in an identifier for a district specific enemy

			searched_identifier = identifiers_found.pop()

			enemydata = ewutils.execute_sql_query(
				"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {identifier} = %s AND {life_state} = 1".format(
					id_enemy=ewcfg.col_id_enemy,
					poi=ewcfg.col_enemy_poi,
					identifier=ewcfg.col_enemy_identifier,
					life_state=ewcfg.col_enemy_life_state
				), (
					user_data.poi,
					searched_identifier,
				))

			for row in enemydata:
				enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
				enemy_found = enemy
				break
		else:
			# last token was a string, identify enemy by name

			enemydata = ewutils.execute_sql_query("SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {life_state} = 1".format(
				id_enemy=ewcfg.col_id_enemy,
				poi=ewcfg.col_enemy_poi,
				life_state=ewcfg.col_enemy_life_state
			), (
				user_data.poi,
			))

			# find the first (i.e. the oldest) item that matches the search
			for row in enemydata:
				enemy = EwEnemy(id_enemy=row[0], id_server=user_data.id_server)
				
				if (enemy.display_name.lower() == enemy_search) or (enemy.enemytype == enemy_search_alias):
					enemy_found = enemy
					break

				if (enemy.display_name.lower() in enemy_search) or (enemy.enemytype in enemy_search_tokens):
					enemy_found = enemy
					break


	return enemy_found

# Deletes an enemy the database.
def delete_enemy(enemy_data):
	# print("DEBUG - {} - {} DELETED".format(enemy_data.id_enemy, enemy_data.display_name))
	enemy_data.clear_allstatuses()
	ewutils.execute_sql_query("DELETE FROM enemies WHERE {id_enemy} = %s".format(
		id_enemy=ewcfg.col_id_enemy
	), (
		enemy_data.id_enemy,
	))
	

# Drops items into the district when an enemy dies.
def drop_enemy_loot(enemy_data, district_data):
	loot_poi = ewcfg.id_to_poi.get(district_data.name)
	loot_resp_cont = ewutils.EwResponseContainer(id_server=enemy_data.id_server)
	response = ""

	item_counter = 0
	loot_multiplier = 1

	poudrin_dropped = False
	poudrin_amount = 0
	
	dragonsoul_dropped = False
	dragonsoul_amount = 0

	pleb_dropped = False
	pleb_amount = 0

	patrician_dropped = False
	patrician_amount = 0

	crop_dropped = False
	crop_amount = 0

	meat_dropped = False
	meat_amount = 0

	card_dropped = False
	card_amount = 0
	
	drop_chance = None
	drop_min = None
	drop_max = None
	drop_range = None
	
	poudrin_values = None
	dragonsoul_values = None
	pleb_values = None
	patrician_values = None
	crop_values = None
	meat_values = None
	card_values = None
	
	drop_table = ewcfg.enemy_drop_tables[enemy_data.enemytype]
	
	# Go through all the possible drops in the drop table and catch exceptions when necessary
	for item in drop_table:
		try:
			if item["poudrin"]:
				poudrin_values = item["poudrin"]
		except:
			pass
		try:
			if item["pleb"]:
				pleb_values = item["pleb"]
		except:
			pass
		try:
			if item["patrician"]:
				patrician_values = item["patrician"]
		except:
			pass
		try:
			if item["crop"]:
				crop_values = item["crop"]
		except:
			pass
		try:
			if item["meat"]:
				meat_values = item["meat"]
		except:
			pass
		try:
			if item["card"]:
				card_values = item["card"]
		except:
			pass
		try:
			if item['dragonsoul']:
				dragonsoul_values = item['dragonsoul']
		except:
			pass

	if poudrin_values != None:
		drop_chance = poudrin_values[0]
		drop_min = poudrin_values[1]
		drop_max = poudrin_values[2]
		
		poudrin_dropped = random.randrange(100) <= (drop_chance - 1)
		
		if poudrin_dropped:
			drop_range = list(range(drop_min, drop_max+1))
			poudrin_amount = random.choice(drop_range)
	if dragonsoul_values != None:
		drop_chance = dragonsoul_values[0]
		drop_min = dragonsoul_values[1]
		drop_max = dragonsoul_values[2]
		
		dragonsoul_dropped = random.randrange(100) <= (drop_chance - 1)
		
		if dragonsoul_dropped:
			drop_range = list(range(drop_min, drop_max+1))
			dragonsoul_amount = random.choice(drop_range)
			
	if pleb_values != None:
		drop_chance = pleb_values[0]
		drop_min = pleb_values[1]
		drop_max = pleb_values[2]
		
		pleb_dropped = random.randrange(101) < drop_chance
		
		if pleb_dropped:
			drop_range = list(range(drop_min, drop_max + 1))
			pleb_amount = random.choice(drop_range)

	if patrician_values != None:
		drop_chance = patrician_values[0]
		drop_min = patrician_values[1]
		drop_max = patrician_values[2]

		patrician_dropped = random.randrange(101) < drop_chance

		if patrician_dropped:
			drop_range = list(range(drop_min, drop_max + 1))
			patrician_amount = random.choice(drop_range)

	if crop_values != None:
		drop_chance = crop_values[0]
		drop_min = crop_values[1]
		drop_max = crop_values[2]

		crop_dropped = random.randrange(101) < drop_chance

		if crop_dropped:
			drop_range = list(range(drop_min, drop_max + 1))
			crop_amount = random.choice(drop_range)

	if meat_values != None:
		drop_chance = meat_values[0]
		drop_min = meat_values[1]
		drop_max = meat_values[2]

		meat_dropped = random.randrange(101) < drop_chance

		if meat_dropped:
			drop_range = list(range(drop_min, drop_max + 1))
			meat_amount = random.choice(drop_range)

	if card_values != None:
		drop_chance = card_values[0]
		drop_min = card_values[1]
		drop_max = card_values[2]

		card_dropped = random.randrange(101) < drop_chance

		if card_dropped:
			drop_range = list(range(drop_min, drop_max + 1))
			card_amount = random.choice(drop_range)

	if pleb_dropped or patrician_dropped:
		cosmetics_list = []

		for result in ewcfg.cosmetic_items_list:
			if result.ingredients == "":
				cosmetics_list.append(result)
			else:
				pass
			
	# Multiply the amount of loot if an enemy is its rare variant
	# Loot is also multiplied for the UFO raid boss, since it's a special case with the increased variety of slime it can have.
	if enemy_data.rare_status == 1:
		loot_multiplier *= 1.5
		
	if enemy_data.enemytype == ewcfg.enemy_type_unnervingfightingoperator:
		loot_multiplier *= math.ceil(enemy_data.slimes / 1000000)
		
	poudrin_amount = math.ceil(poudrin_amount * loot_multiplier)
	pleb_amount = math.ceil(pleb_amount * loot_multiplier)
	patrician_amount = math.ceil(patrician_amount * loot_multiplier)
	crop_amount = math.ceil(crop_amount * loot_multiplier)
	meat_amount = math.ceil(meat_amount * loot_multiplier)
	card_amount = math.ceil(card_amount * loot_multiplier)
	# Drops items one-by-one
	if poudrin_dropped:
		item_counter = 0

		while item_counter < poudrin_amount:
			for item in ewcfg.item_list:
				if item.context == "poudrin":
					ewitem.item_create(
						item_type=ewcfg.it_item,
						id_user=district_data.name,
						id_server=district_data.id_server,
						item_props={
							'id_item': item.id_item,
							'context': item.context,
							'item_name': item.str_name,
							'item_desc': item.str_desc,
						}
					),
					item = EwItem(id_item=item.id_item)
					item.persist()
			response = "They dropped a slime poudrin!"
			loot_resp_cont.add_channel_response(loot_poi.channel, response)

			item_counter += 1

			
	if dragonsoul_dropped:
		item_counter = 0

		while item_counter < dragonsoul_amount:
			for item in ewcfg.item_list:
				if item.context == "dragon soul":
					ewitem.item_create(
						item_type=ewcfg.it_item,
						id_user=district_data.name,
						id_server=district_data.id_server,
						item_props={
							'id_item': item.id_item,
							'context': item.context,
							'item_name': item.str_name,
							'item_desc': item.str_desc,
						}
					),
					item = EwItem(id_item=item.id_item)
					item.persist()
			response = "They dropped their **SOUL!!**"
			loot_resp_cont.add_channel_response(loot_poi.channel, response)

			item_counter += 1

	if pleb_dropped:
		item_counter = 0

		while item_counter < pleb_amount:
			items = []

			for cosmetic in cosmetics_list:
				if cosmetic.rarity == ewcfg.rarity_plebeian:
					items.append(cosmetic)

			item = items[random.randint(0, len(items) - 1)]

			item_props = ewitem.gen_item_props(item)

			ewitem.item_create(
				item_type = ewcfg.it_cosmetic,
				id_user = district_data.name,
				id_server = district_data.id_server,
				item_props = item_props
			)

			response = "They dropped a {item_name}!".format(item_name=item.str_name)
			loot_resp_cont.add_channel_response(loot_poi.channel, response)

			item_counter += 1

	if patrician_dropped:
		item_counter = 0

		while item_counter < patrician_amount:
			items = []

			for cosmetic in cosmetics_list:
				if cosmetic.rarity == ewcfg.rarity_patrician:
					items.append(cosmetic)

			item = items[random.randint(0, len(items) - 1)]

			item_props = ewitem.gen_item_props(item)

			ewitem.item_create(
				item_type = ewcfg.it_cosmetic,
				id_user = district_data.name,
				id_server = district_data.id_server,
				item_props = item_props
			)

			response = "They dropped a {item_name}!".format(item_name=item.str_name)
			loot_resp_cont.add_channel_response(loot_poi.channel, response)

			item_counter += 1

	if crop_dropped:
		item_counter = 0

		while item_counter < crop_amount:

			vegetable = random.choice(ewcfg.vegetable_list)

			ewitem.item_create(
				id_user=district_data.name,
				id_server=district_data.id_server,
				item_type=ewcfg.it_food,
				item_props={
					'id_food': vegetable.id_food,
					'food_name': vegetable.str_name,
					'food_desc': vegetable.str_desc,
					'recover_hunger': vegetable.recover_hunger,
					'str_eat': vegetable.str_eat,
					'time_expir': time.time() + ewcfg.farm_food_expir
				}
			)
			response = "They dropped a bushel of {vegetable_name}!".format(vegetable_name=vegetable.str_name)
			loot_resp_cont.add_channel_response(loot_poi.channel, response)

			item_counter += 1

	# Drop dinoslime meat
	if meat_dropped:
		meat = None
		item_counter = 0

		for food in ewcfg.food_list:
			if food.id_food == ewcfg.item_id_dinoslimemeat:
				meat = food
				
		while item_counter < meat_amount:  
			ewitem.item_create(
				id_user=district_data.name,
				id_server=district_data.id_server,
				item_type=ewcfg.it_food,
				item_props={
					'id_food': meat.id_food,
					'food_name': meat.str_name,
					'food_desc': meat.str_desc,
					'recover_hunger': meat.recover_hunger,
					'str_eat': meat.str_eat,
					'time_expir': time.time() + ewcfg.std_food_expir
				}
			)
			response = "They dropped a piece of meat!"
			loot_resp_cont.add_channel_response(loot_poi.channel, response)
			
			item_counter += 1
	
	# Drop trading cards
	if card_dropped:
		cards = None
		item_counter = 0
		
		for item in ewcfg.item_list:
			if item.id_item == ewcfg.item_id_tradingcardpack:
				cards = item

		while item_counter < card_amount:
			ewitem.item_create(
				id_user=district_data.name,
				id_server=district_data.id_server,
				item_type=ewcfg.it_item,
				item_props={
					'id_item': cards.id_item,
					'context': cards.context,
					'item_name': cards.str_name,
					'item_desc': cards.str_desc,
				}
			)
			response = "They dropped a pack of trading cards!"
			loot_resp_cont.add_channel_response(loot_poi.channel, response)
			
			item_counter += 1

	if not poudrin_dropped and not pleb_dropped and not patrician_dropped and not crop_dropped and not meat_dropped and not card_dropped:
		response = "They didn't drop anything...\n"
		loot_resp_cont.add_channel_response(loot_poi.channel, response)

	return loot_resp_cont

# Determines what level an enemy is based on their slime count.
def level_byslime(slime):
	return int(abs(slime) ** 0.25)

# Reskinned version of weapon class from ewwep.
class EwAttackType:

	# An name used to identify the attacking type
	id_type = ""

	# Displayed when this weapon is used for a !kill
	str_kill = ""

	# Displayed to the dead victim in the sewers. Brief phrase such as "gunned down" etc.
	str_killdescriptor = ""

	# Displayed when viewing the !trauma of another player.
	str_trauma = ""

	# Displayed when viewing the !trauma of yourself.
	str_trauma_self = ""

	# Displayed when a non-lethal hit occurs.
	str_damage = ""

	# Displayed when an attack backfires
	str_backfire = ""

	# Function that applies the special effect for this weapon.
	fn_effect = None

	# Displayed when a weapon effect causes a critical hit.
	str_crit = ""

	# Displayed when a weapon effect causes a miss.
	str_miss = ""

	def __init__(
			self,
			id_type="",
			str_kill="",
			str_killdescriptor="",
			str_trauma="",
			str_trauma_self="",
			str_damage="",
			fn_effect=None,
			str_crit="",
			str_miss="",
			str_backfire = "",
	):
		self.id_type = id_type
		self.str_kill = str_kill
		self.str_killdescriptor = str_killdescriptor
		self.str_trauma = str_trauma
		self.str_trauma_self = str_trauma_self
		self.str_damage = str_damage
		self.str_backfire = str_backfire
		self.fn_effect = fn_effect
		self.str_crit = str_crit
		self.str_miss = str_miss
		

# Check if an enemy is dead. Implemented to prevent enemy data from being recreated when not necessary.
def check_death(enemy_data):
	if enemy_data.slimes <= 0 or enemy_data.life_state == ewcfg.enemy_lifestate_dead:
		# delete_enemy(enemy_data)
		return True
	else:
		return False

# Assigns enemies most of their necessary attributes based on their type.
def get_enemy_data(enemy_type):
	enemy = EwEnemy()
	
	rare_status = 0
	if random.randrange(5) == 0 and enemy_type not in ewcfg.overkill_enemies and enemy_type not in ewcfg.gvs_enemies:
		rare_status = 1

	enemy.id_server = ""
	enemy.slimes = 0
	enemy.totaldamage = 0
	enemy.level = 0
	enemy.life_state = ewcfg.enemy_lifestate_alive
	enemy.enemytype = enemy_type
	enemy.bleed_storage = 0
	enemy.time_lastenter = 0
	enemy.initialslimes = 0
	enemy.id_target = ""
	enemy.raidtimer = 0
	enemy.rare_status = rare_status
	enemy.weathertype = ""
		
	if enemy_type in ewcfg.raid_bosses:
		enemy.life_state = ewcfg.enemy_lifestate_unactivated
		enemy.raidtimer = int(time.time())

	slimetable = ewcfg.enemy_data_table[enemy_type]["slimerange"]
	minslime = slimetable[0]
	maxslime = slimetable[1]

	slime = random.randrange(minslime, (maxslime + 1))
	
	enemy.slimes = slime
	enemy.ai = ewcfg.enemy_data_table[enemy_type]["ai"]
	enemy.display_name = ewcfg.enemy_data_table[enemy_type]["displayname"]
	enemy.attacktype = ewcfg.enemy_data_table[enemy_type]["attacktype"]
	
	try:
		enemy.enemyclass = ewcfg.enemy_data_table[enemy_type]["class"]
	except:
		enemy.enemyclass = ewcfg.enemy_class_normal
		
	if rare_status == 1:
		enemy.display_name = ewcfg.enemy_data_table[enemy_type]["raredisplayname"]
		enemy.slimes *= 2

	return enemy


# Selects which non-ghost user to attack based on certain parameters.
def get_target_by_ai(enemy_data, cannibalize = False):

	target_data = None

	time_now = int(time.time())

	# If a player's time_lastenter is less than this value, it can be attacked.
	targettimer = time_now - ewcfg.time_enemyaggro
	raidbossaggrotimer = time_now - ewcfg.time_raidbossaggro

	if not cannibalize:
		if enemy_data.ai == ewcfg.enemy_ai_defender:
			if enemy_data.id_target != "":
				target_data = EwUser(id_user=enemy_data.id_target, id_server=enemy_data.id_server, data_level = 1)
	
		elif enemy_data.ai == ewcfg.enemy_ai_attacker_a:
			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state}, {time_lastenter} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({time_expirpvp} > {time_now} OR {life_state} = {life_state_shambler}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {time_lastenter} ASC".format(
					id_user = ewcfg.col_id_user,
					life_state = ewcfg.col_life_state,
					time_lastenter = ewcfg.col_time_lastenter,
					poi = ewcfg.col_poi,
					id_server = ewcfg.col_id_server,
					targettimer = targettimer,
					life_state_corpse = ewcfg.life_state_corpse,
					life_state_kingpin = ewcfg.life_state_kingpin,
					life_state_shambler = ewcfg.life_state_shambler,
					repel_status = ewcfg.status_repelled_id,
					time_expirpvp = ewcfg.col_time_expirpvp,
					time_now = time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level = 1)
	
		elif enemy_data.ai == ewcfg.enemy_ai_attacker_b:
			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({time_expirpvp} > {time_now} OR {life_state} = {life_state_shambler}) AND NOT ({life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin} OR {id_user} IN (SELECT {id_user} FROM status_effects WHERE id_status = '{repel_status}')) ORDER BY {slimes} DESC".format(
					id_user = ewcfg.col_id_user,
					life_state = ewcfg.col_life_state,
					slimes = ewcfg.col_slimes,
					poi = ewcfg.col_poi,
					id_server = ewcfg.col_id_server,
					time_lastenter = ewcfg.col_time_lastenter,
					targettimer = targettimer,
					life_state_corpse = ewcfg.life_state_corpse,
					life_state_kingpin = ewcfg.life_state_kingpin,
					life_state_shambler = ewcfg.life_state_shambler,
					repel_status = ewcfg.status_repelled_id,
					time_expirpvp = ewcfg.col_time_expirpvp,
					time_now = time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level = 1)
				
		elif enemy_data.ai == ewcfg.enemy_ai_gaiaslimeoid:
			
			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND ({life_state} = {life_state_shambler}) ORDER BY {slimes} DESC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					slimes=ewcfg.col_slimes,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					time_lastenter=ewcfg.col_time_lastenter,
					targettimer=targettimer,
					life_state_shambler=ewcfg.life_state_shambler,
					time_now=time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)
				
		elif enemy_data.ai == ewcfg.enemy_ai_shambler:

			users = ewutils.execute_sql_query(
				"SELECT {id_user}, {life_state}, {slimes} FROM users WHERE {poi} = %s AND {id_server} = %s AND {time_lastenter} < {targettimer} AND NOT ({life_state} = {life_state_shambler} OR {life_state} = {life_state_corpse} OR {life_state} = {life_state_kingpin}) ORDER BY {slimes} DESC".format(
					id_user=ewcfg.col_id_user,
					life_state=ewcfg.col_life_state,
					slimes=ewcfg.col_slimes,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					time_lastenter=ewcfg.col_time_lastenter,
					targettimer=targettimer,
					life_state_shambler=ewcfg.life_state_shambler,
					life_state_corpse=ewcfg.life_state_corpse,
					life_state_kingpin=ewcfg.life_state_kingpin,
					time_now=time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server
				))
			if len(users) > 0:
				target_data = EwUser(id_user=users[0][0], id_server=enemy_data.id_server, data_level=1)
				
		# If an enemy is a raidboss, don't let it attack until some time has passed when entering a new district.
		if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.time_lastenter > raidbossaggrotimer:
			target_data = None
			
	elif cannibalize:
		if enemy_data.ai == ewcfg.enemy_ai_gaiaslimeoid:
			enemies = ewutils.execute_sql_query(
				"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {id_server} = %s AND ({time_lastenter} < {targettimer}) AND NOT ({life_state} = {life_state_dead} OR {life_state} = {life_state_unactivated}) AND ({enemyclass} = %s) ORDER BY {time_lastenter} ASC".format(
					id_enemy=ewcfg.col_id_enemy,
					life_state=ewcfg.col_life_state,
					time_lastenter=ewcfg.col_time_lastenter,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					targettimer=targettimer,
					life_state_dead=ewcfg.enemy_lifestate_dead,
					life_state_unactivated=ewcfg.enemy_lifestate_unactivated,
					enemyclass=ewcfg.col_enemy_class,
					time_expirpvp=ewcfg.col_time_expirpvp,
					time_now=time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server,
					ewcfg.enemy_class_shambler
				))
			if len(enemies) > 0:
				target_data = EwEnemy(id_enemy=enemies[0][0], id_server=enemy_data.id_server)
		elif enemy_data.ai == ewcfg.enemy_ai_shambler:
			enemies = ewutils.execute_sql_query(
				"SELECT {id_enemy} FROM enemies WHERE {poi} = %s AND {id_server} = %s AND ({time_lastenter} < {targettimer}) AND NOT ({life_state} = {life_state_dead} OR {life_state} = {life_state_unactivated}) AND ({enemyclass} = %s) ORDER BY {time_lastenter} ASC".format(
					id_enemy=ewcfg.col_id_enemy,
					life_state=ewcfg.col_life_state,
					time_lastenter=ewcfg.col_time_lastenter,
					poi=ewcfg.col_poi,
					id_server=ewcfg.col_id_server,
					targettimer=targettimer,
					life_state_dead=ewcfg.enemy_lifestate_dead,
					life_state_unactivated=ewcfg.enemy_lifestate_unactivated,
					enemyclass=ewcfg.col_enemy_class,
					time_expirpvp=ewcfg.col_time_expirpvp,
					time_now=time_now,
				), (
					enemy_data.poi,
					enemy_data.id_server,
					ewcfg.enemy_class_gaiaslimeoid
				))
			if len(enemies) > 0:
				target_data = EwEnemy(id_enemy=enemies[0][0], id_server=enemy_data.id_server)
		
		# If an enemy is a raidboss, don't let it attack until some time has passed when entering a new district.
		if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.time_lastenter > raidbossaggrotimer:
			target_data = None

	return target_data

# Check if raidboss is ready to attack / be attacked
def check_raidboss_countdown(enemy_data):
	time_now = int(time.time())

	# Wait for raid bosses
	if enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer <= time_now - ewcfg.time_raidcountdown:
		# Raid boss has activated!
		return True
	elif enemy_data.enemytype in ewcfg.raid_bosses and enemy_data.raidtimer > time_now - ewcfg.time_raidcountdown:
		# Raid boss hasn't activated.
		return False

def check_raidboss_movecooldown(enemy_data):
	time_now = int(time.time())
	
	if enemy_data.enemytype in ewcfg.raid_bosses:
		if enemy_data.enemytype in ewcfg.gvs_enemies:
			if enemy_data.time_lastenter <= time_now - 600:
				# Raid boss can move
				return True
			elif enemy_data.time_lastenter > time_now - 600:
				# Raid boss can't move yet
				return False
		else:
			if enemy_data.time_lastenter <= time_now - ewcfg.time_raidboss_movecooldown:
				# Raid boss can move
				return True
			elif enemy_data.time_lastenter > time_now - ewcfg.time_raidboss_movecooldown:
				# Raid boss can't move yet
				return False

# Gives enemy an identifier so it's easier to pick out in a crowd of enemies
def set_identifier(poi, id_server):
	district = EwDistrict(district=poi, id_server=id_server)
	enemies_list = district.get_enemies_in_district()

	# A list of identifiers from enemies in a district
	enemy_identifiers = []

	new_identifier = ewcfg.identifier_letters[0]

	if len(enemies_list) > 0:
		for enemy_id in enemies_list:
			enemy = EwEnemy(id_enemy=enemy_id)
			enemy_identifiers.append(enemy.identifier)

		# Sort the list of identifiers alphabetically
		enemy_identifiers.sort()

		for checked_enemy_identifier in enemy_identifiers:
			# If the new identifier matches one from the list of enemy identifiers, give it the next applicable letter
			# Repeat until a unique identifier is given
			if new_identifier == checked_enemy_identifier:
				next_letter = (ewcfg.identifier_letters.index(checked_enemy_identifier) + 1)
				new_identifier = ewcfg.identifier_letters[next_letter]
			else:
				continue

	return new_identifier


