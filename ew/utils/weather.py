import asyncio
import random
import time

from . import core as ewutils
from .combat import EwEnemy
from .combat import EwUser
from .district import EwDistrict
from .frontend import EwResponseContainer
from .slimeoid import EwSlimeoid
from ..backend import core as bknd_core
from ..backend import hunting as bknd_hunt
from ..backend import item as bknd_item
from ..backend import worldevent as bknd_worldevent
from ..backend.item import EwItem
from ..backend.market import EwMarket
from ..backend.player import EwPlayer
from ..static import cfg as ewcfg
from ..static import community_cfg as comm_cfg
from ..static import poi as poi_static
from ..static import weather as weather_static
from ..static import weapons as weapons_static
from ..static import items as items_static
from ..utils import frontend as fe_utils
from ..utils import rolemgr as ewrolemgr
from ..utils import item as item_utils
from ..cmd.move.movecmds import one_eye_dm

try:    
    from ew.utils import rutils 
except:
    from ew.utils import rutils_dummy as rutils

"""
	Coroutine that continually calls weather_tick; is called once per server, and not just once globally
"""


async def weather_tick_loop(id_server):
    interval = ewcfg.weather_tick_length
    while not ewutils.TERMINATE:
        await asyncio.sleep(interval)
        await weather_tick(id_server=id_server)


""" Bleed slime for all users """


async def weather_tick(id_server = None):
    if id_server != None:
        try:
            market_data = EwMarket(id_server=id_server)
            
            if market_data.weather == ewcfg.weather_sunny:
                exposed_pois = []
                exposed_pois.extend(poi_static.capturable_districts)
                exposed_pois.extend(poi_static.outskirts)
                exposed_pois = tuple(exposed_pois)

                users = bknd_core.execute_sql_query(
                    "SELECT id_user FROM users WHERE id_server = %s AND {poi} IN %s AND {life_state} > 0".format(
                        poi=ewcfg.col_poi,
                        life_state=ewcfg.col_life_state
                    ), (
                        id_server,
                        exposed_pois

                    ))
                for user in users:
                    try:
                        user_data = EwUser(id_user=user[0], id_server=id_server)
                        if user_data.life_state == ewcfg.life_state_kingpin:
                            continue
                        else:
                            mutations = user_data.get_mutations()
                            if ewcfg.mutation_id_airlock in mutations:
                                user_data.hunger -= min(user_data.hunger, 5)
                    except:
                        ewutils.logMsg("Error occurred in weather tick for server {}".format(id_server))

            client = ewutils.get_client()
            world_events = bknd_worldevent.get_world_events(id_server=id_server, active_only=True)
            resp_cont_poi_event = EwResponseContainer(client=client, id_server=id_server)

            # For all presently-happening world events
            for id_event in world_events:
                # If the world event has an effect corresponding to a weather tick
                if world_events.get(id_event) in [ewcfg.event_type_firestorm, ewcfg.event_type_tornado, ewcfg.event_type_poudrin_hail, ewcfg.event_type_meteor_shower, ewcfg.event_type_jape_storm]:
                    # Get the EVENT DATA
                    event_data = bknd_worldevent.EwWorldEvent(id_event=id_event)
                    
                    # If the event is a firestorm
                    if event_data.event_type == ewcfg.event_type_firestorm:
                        district = event_data.event_props.get('poi')
                        district_data = EwDistrict(district=district, id_server=id_server)
                        players = district_data.get_players_in_district(life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_juvenile]) # Ghosts can't get set on fire ):
                        # For all the players in the district of the firestorm
                        for player in players:
                            user_data = EwUser(id_user=player, id_server=id_server)
                            mutations = user_data.get_mutations()

                            # If the user has Napalm Snot, applying burn is unnecessary
                            if ewcfg.mutation_id_napalmsnot in mutations:
                                continue

                            # If the user hasn't been set burned by the firestorm yet, tell them they're being burned
                            statuses = user_data.getStatusEffects()
                            if ewcfg.status_burning_id not in statuses:
                                district_object = poi_static.id_to_poi.get(district)
                                player_data = EwPlayer(id_user=user_data.id_user, id_server=id_server)

                                # Figure out the player's name and account for amnesia
                                player_name = player_data.display_name
                                if ewcfg.mutation_id_amnesia in mutations:
                                    player_name = "?????"

                                response = "*{}*: You've been set alight by the **RAGING FIRESTORM**, <@{}>! ".format(player_name, player)
                                resp_cont_poi_event.add_channel_response(district_object.channel, response)

                            # Actually burn the user
                            user_data.applyStatus(id_status=ewcfg.status_burning_id, value=ewcfg.firestorm_slime_burn, source=-1)

                    elif event_data.event_type == ewcfg.event_type_tornado:
                        district = event_data.event_props.get('poi')
                        district_data = EwDistrict(district=district, id_server=id_server)
                        district_object = poi_static.id_to_poi.get(district)

                        players = district_data.get_players_in_district(life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_juvenile]) # Ghosts are immune to tornadoes so inhabitants don't act weirdly
                        # For all the players in the district of the tornado
                        for player in players:
                            user_data = EwUser(id_user=player, id_server=id_server)
                            mutations = user_data.get_mutations()
                            eligible_districts = []

                            # If the user has Big Bones they're too heavy.
                            if ewcfg.mutation_id_bigbones in mutations:
                                continue
                            
                            # Create a list of eligible neighbor districts
                            for district in poi_static.poi_neighbors[district]:
                                if district in poi_static.capturable_districts:
                                    eligible_districts.append(district)
                            # If there are no eligible districts, ignore.
                            if eligible_districts == []:
                                continue
                            # Pick a district
                            deposited_district = random.choice(eligible_districts)
                            deposited_district_object = poi_static.id_to_poi.get(deposited_district)

                            # The member of the user
                            guild = client.get_guild(id_server)
                            member = guild.get_member(user_data.id_user)
                            # Stop movement
                            ewutils.moves_active[user_data.id_user] = 0
                            rutils.movement_checker(user_data, poi_static.id_to_poi.get(user_data.poi), deposited_district)
                            # Move the player into the neighbor
                            await ewrolemgr.updateRoles(client=client, member=member, new_poi=deposited_district)
                            user_data.poi = deposited_district_object.id_poi
                            user_data.time_lastenter = int(time.time())
                            # Move ghosts and make possible oeo dms.
                            await one_eye_dm(id_user=user_data.id_user, id_server=user_data.id_server, poi=deposited_district)
                            await user_data.move_inhabitants(id_poi=deposited_district)
                            
                            # Take player's slime and put it into the neighbor district.
                            if user_data.slimes > 0:
                                deposited_district_data = EwDistrict(district=district, id_server=id_server)
                                # Splat
                                splatter = user_data.slimes // 3
                                user_data.change_slimes(n=-splatter, source=ewcfg.source_weather)
                                deposited_district_data.change_slimes(n=splatter, source=ewcfg.source_weather)

                                deposited_district_data.persist()
                            
                            response = "You are flung into {} by the **RAGING TORNADO** in {}, splattering slime everywhere. Watch out!".format(deposited_district_object.str_name, district_object.str_name)
                            resp_cont_poi_event.add_channel_response(deposited_district_object.channel, fe_utils.formatMessage(member, response))

                            user_data.persist()

                    elif event_data.event_type == ewcfg.event_type_poudrin_hail:
                        if random.random() <= 0.007: # 99.3% chance for nothing to occur
                            district = event_data.event_props.get('poi')
                            district_data = EwDistrict(district=district, id_server=id_server)
                            district_object = poi_static.id_to_poi.get(district)
                            players = district_data.get_players_in_district(life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_juvenile]) # Ghosts are incorporeal to falling debris                            
                            
                            # If there are players in the district, pick one to have a poudrin fall on
                            if len(players) >= 1:
                                player = random.choice(players)
                                user_data = EwUser(id_user=player, id_server=id_server)
                                player_data = EwPlayer(id_user=user_data.id_user, id_server=id_server)
                                umbrella = False

                                # Check if the player has an umbrella equipped
                                equipped_weapon = EwItem(id_item=user_data.weapon)
                                weapon = weapons_static.weapon_map.get(equipped_weapon.item_props.get("weapon_type"))
                                if weapon != None:
                                    if weapon.id_weapon == ewcfg.weapon_id_umbrella:
                                        umbrella = True

                                # If the player does not have an umbrella equipped, kill them
                                if not umbrella:
                                    # !kill and make Sewers response
                                    die_resp = user_data.die(cause=ewcfg.cause_debris)
                                    resp_cont_poi_event.add_response_container(die_resp)
                                    user_data.persist()

                                    # Make channel response
                                    response = "A poudrin falls from the sky, landing squarely on {}'s soft, supple scalp. They are crushed to the pavement, dead on impact. {}".format(player_data.display_name, ewcfg.emote_slimeskull)
                                else:
                                    # Make channel response
                                    response = "A poudrin falls from the sky, landing squarely on {}'s strong, sturdy umbrella. The pure crystal of slime harmlessly falls to the ground.".format(player_data.display_name)
                            else:
                                response = "A poudrin falls from the sky."
                            
                            # Get poudrin item props
                            item = items_static.item_map.get('slimepoudrin')
                            item_props = item_utils.gen_item_props(item)
                            # Create poudrin on the ground
                            bknd_item.item_create(
                                item_type=item.item_type,
                                id_user=district,
                                id_server=id_server,
                                item_props=item_props,
                            )
                            # Create channel response for poudrin falling
                            resp_cont_poi_event.add_channel_response(district_object.channel, response)

                    elif event_data.event_type == ewcfg.event_type_meteor_shower:
                        district = event_data.event_props.get('poi')
                        district_data = EwDistrict(district=district, id_server=id_server)
                        players = district_data.get_players_in_district(life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_juvenile]) # Ghosts can't see
                            
                        for player in players:
                            if random.random() <= 0.08: # 92% chance for no flavor for that player
                                district_object = poi_static.id_to_poi.get(district)
                                user_data = EwUser(id_user=player, id_server=id_server)
                                player_data = EwPlayer(id_user=player, id_server=id_server)

                                mutations = user_data.get_mutations()

                                # Figure out the player's name and account for amnesia
                                player_name = player_data.display_name
                                if ewcfg.mutation_id_amnesia in mutations:
                                    player_name = "?????"
                                
                                meteor_shower_flavor = random.choice(comm_cfg.meteor_shower_responses)
                                response = "*{}*: {}".format(player_name, meteor_shower_flavor)
                                resp_cont_poi_event.add_channel_response(district_object.channel, response)
                                
                                item_recieved = random.random()
                                if (ewcfg.mutation_id_lucky in mutations and item_recieved <= 0.15) or item_recieved <= 0.10: # 15/10% chance for moon dust vape juice
                                    item = items_static.item_map.get(ewcfg.item_id_moon_dust_pod)
                                    item_props = item_utils.gen_item_props(item)
                                    # create vape pod
                                    bknd_item.item_create(
                                        item_type=item.item_type,
                                        id_user=player,
                                        id_server=id_server,
                                        item_props=item_props,
                                    )
                                    response = "*{}*: A mysterious pod appears in your pocket.".format(player_name)
                                    resp_cont_poi_event.add_channel_response(district_object.channel, response)                                    
                                

                    # If the event is a japestorm
                    elif event_data.event_type == ewcfg.event_type_jape_storm:
                        district = event_data.event_props.get('poi')
                        district_data = EwDistrict(district=district, id_server=id_server)
                        district_object = poi_static.id_to_poi.get(district)
                        players = district_data.get_players_in_district(life_states=[ewcfg.life_state_enlisted, ewcfg.life_state_juvenile]) # Ghosts are immune to comedy

                        # If there are players in the district, pick one to get PRANK'D
                        if len(players) >= 1 and random.random() > 0.85:
                            player = random.choice(players)
                            user_data = EwUser(id_user=player, id_server=id_server)
                            player_data = EwPlayer(id_user=user_data.id_user, id_server=id_server)

                            mutations = user_data.get_mutations()

                            # User will get better prank items if they have the lucky mutation
                            if ewcfg.mutation_id_lucky in mutations:
                                item = random.choice(items_static.prank_items_forbidden)
                            else:
                                item = random.choice(items_static.prank_items_heinous + items_static.prank_items_scandalous)

                            item_props = item_utils.gen_item_props(item)
                            id_user = district

                            # Make channel response
                            response = "A {} is thrown at {}, clobbering their face. Thank god it wasn't lethal!".format(item_props['item_name'], player_data.display_name)
                        # Spawn a primed prank item
                        elif random.random() > 0.985: 
                            # Generate a trap to put on the ground
                            item = random.choice(items_static.prank_items_trap)
                            item_props = item_utils.gen_item_props(item)
                            item_props["trap_stored_credence"] = 0
                            item_props["trap_user_id"] = str(431446476112134144) # ENDLESS WAR's user ID

                            # Make the trap itemed primed
                            id_user = district + '_trap'

                            # Make channel response
                            response = "A primed {} appears on the ground.".format(item_props['item_name'])
                        # Cancel before going on if neither of the previous conditions were true
                        else: 
                            continue

                        # Create item on the ground
                        bknd_item.item_create(
                            item_type=item.item_type,
                            id_user=id_user,
                            id_server=id_server,
                            item_props=item_props,
                        )
                        # Create channel response
                        resp_cont_poi_event.add_channel_response(district_object.channel, response)
                            
            await resp_cont_poi_event.post()
            
        except:
            ewutils.logMsg("Error occurred in weather tick for server {}".format(id_server))

async def weather_cycle(id_server = None):
    market_data = EwMarket(id_server)
    
    # Potentially change the weather
    if random.randrange(3) == 0:
            pattern_count = len(weather_static.weather_list)

            if pattern_count > 1:
                weather_old = market_data.weather

                # if random.random() < 0.4:
                # 	market_data.weather = ewcfg.weather_bicarbonaterain

                # Randomly select a new weather pattern. Try again if we get the same one we currently have.
                while market_data.weather == weather_old:
                    pick = random.randrange(len(weather_static.weather_list))
                    market_data.weather = weather_static.weather_list[pick].name
                    market_data.persist()
            # Log message for statistics tracking.
            ewutils.logMsg("The weather changed. It's now {}.".format(market_data.weather))


async def create_poi_event(id_server, pre_chosen_event=None, pre_chosen_poi=None, no_buffer=False): # Events are natural disasters, pop-up events, etc.
    event_props = {}
    # Get a random event type from poi_events
    if pre_chosen_event != None:
        event_type = pre_chosen_event
    else:
        event_type = random.choice(ewcfg.poi_events)

    # Get the time right now
    time_now = int(time.time())    

    # Set the event's poi.
    event_def = poi_static.event_type_to_def.get(event_type)

    if pre_chosen_poi != None:
        event_props['poi'] = pre_chosen_poi
    elif event_def.pois != []:
        event_props['poi'] = random.choice(event_def.pois)
    else:
        for gup in range(100):
            district = random.choice(poi_static.capturable_districts)

            if district not in [ewcfg.poi_id_downtown, ewcfg.poi_id_greenlightdistrict]: # These two POIs shouldn't have dangerous natural disasters so EW -> JR is always 100% possible
                event_props['poi'] = district
                break

    # Set the activation time and expiration time
    if no_buffer:
        activation_time = time_now + 6 # The extra 6 seconds is for the event tick loop to see it as activated
    else:
        activation_time = time_now + (event_def.buffer * 60 * 15) + 6 # buffer x 15 minutes
    expiration_time = activation_time + (event_def.length * 60 * 15) # length x 15 minutes

    # Set whether or not there will be a specific alert for the poi event.
    alert = ""
    if random.random() > 0.5:
        alert = "gangbase"
    event_props['alert'] = alert

    # Does configuration for dimensional rifts - creates the second rift, as well as making the 2 POIs neighbors.
    if event_type == ewcfg.event_type_dimensional_rift:
        # Rift 1 is the original location
        rift1_poi = poi_static.id_to_poi.get(event_props['poi'])
        # Rift 2 is the sister location
        rift2_poi_id = poi_static.landlocked_destinations.get(rift1_poi.id_poi)
        rift2_poi = poi_static.id_to_poi.get(rift2_poi_id)
        
        # Set both locations as neighbors
        rift1_poi.neighbors[rift2_poi_id] = ewcfg.travel_time_district
        rift2_poi.neighbors[rift1_poi.id_poi] = ewcfg.travel_time_district

        # Create the world event for 1st rift.
        event_props['sisterlocation'] = rift2_poi_id
        bknd_worldevent.create_world_event(
            id_server=id_server,
            event_type=event_type,
            time_activate=activation_time,
            time_expir=expiration_time,
            event_props=event_props
        )        

        # Set up props for the sister world event's creation
        event_props['poi'] = rift2_poi_id
        event_props['sisterlocation'] = rift1_poi.id_poi

    # Create world event
    bknd_worldevent.create_world_event(
        id_server=id_server,
        event_type=event_type,
        time_activate=activation_time,
        time_expir=expiration_time,
        event_props=event_props
    )  

    # Send gangbase forecast
    gangbase_resp_cont = EwResponseContainer(client=ewutils.get_client(), id_server=id_server)

    if alert == "gangbase":
        poi = poi_static.id_to_poi.get(event_props['poi'])

        gangbase_forecast = "It seems {} will begin in {} in {} hours NLACakaNMian time.".format(event_def.str_name, poi.str_name, event_def.buffer)
    else:
        gangbase_forecast = "It seems something is forming in NLACakaNM..."

    for channel in ewcfg.hideout_channels:
        gangbase_resp_cont.add_channel_response(channel, gangbase_forecast)

    await gangbase_resp_cont.post()