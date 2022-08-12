import random
import time

from . import slimeoid as slimeoid_utils
from .district import EwDistrict
from .frontend import EwResponseContainer
from ..backend.hunting import EwEnemyBase as EwEnemy
from ..backend.market import EwMarket
from ..static import cfg as ewcfg
from ..static import poi as poi_static




# Spawns an enemy in a randomized outskirt district. If a district is full, it will try again, up to 5 times.
def spawn_enemy(
        id_server,
        pre_chosen_type = None,
        pre_chosen_level = None,
        pre_chosen_slimes = None,
        pre_chosen_displayname = None,
        pre_chosen_expiration = None,
        pre_chosen_initialslimes = None,
        pre_chosen_poi = None,
        pre_chosen_identifier = None,
        pre_chosen_weather = None,
        pre_chosen_faction = None,
        pre_chosen_owner = None,
        pre_chosen_rarity = None,
        pre_chosen_props = None,
        manual_spawn = False,
):
    time_now = int(time.time())
    response = ""
    ch_name = ""
    resp_cont = EwResponseContainer(id_server=id_server)
    chosen_poi = ""
    potential_chosen_poi = ""
    threat_level = ""
    boss_choices = []
    arctic = 0

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
            threat_level = "micro"
        elif threat_level_choice <= 720:
            threat_level = "monstrous"
        elif threat_level_choice <= 900:
            threat_level = "mega"
        else:
            threat_level = "mega"
        # threat_level = "nega"

        boss_choices = ewcfg.raid_boss_tiers[threat_level]
        enemytype = random.choice(boss_choices)

    if pre_chosen_type is not None:
        enemytype = pre_chosen_type

    if not manual_spawn:

        while enemies_count >= ewcfg.max_enemies and try_count < 5:

            if pre_chosen_poi != None:
                potential_chosen_poi = pre_chosen_poi
            # Sand bags only spawn in the dojo
            elif enemytype == ewcfg.enemy_type_sandbag:
                potential_chosen_poi = ewcfg.poi_id_dojo
            # Slimeoid Trainers only spawn in the Arena
            elif enemytype == ewcfg.enemy_type_slimeoidtrainer:
                potential_chosen_poi = ewcfg.poi_id_arena
            # Underground Trainers only spawn in the Subway, Ferry, or Blimp
            elif enemytype == ewcfg.enemy_type_ug_slimeoidtrainer:
                potential_chosen_poi = random.choice(poi_static.transports)
            # Everything else spawns in the outskrits TODO: Make this code not shit
            else:
                potential_chosen_poi = random.choice(poi_static.outskirts)

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

        if enemytype == 'titanoslime':
            potential_chosen_poi = 'downtown'

        # If an enemy spawns in the Nuclear Beach, it should be remade as a 'pre-historic' enemy.
        if potential_chosen_poi in [ewcfg.poi_id_nuclear_beach_edge, ewcfg.poi_id_nuclear_beach,
                                    ewcfg.poi_id_nuclear_beach_depths]:
            enemytype = random.choice(ewcfg.pre_historic_enemies)
            # If the enemy is a raid boss, re-roll it once to make things fair
            if enemytype in ewcfg.raid_bosses:
                enemytype = random.choice(ewcfg.pre_historic_enemies)
        elif potential_chosen_poi in [ewcfg.poi_id_thesummit, ewcfg.poi_id_colloidsprings, ewcfg.poi_id_skilodges]:
            enemytype = random.choice(ewcfg.arctic_enemies)
            arctic = 1
            if enemytype in ewcfg.raid_bosses:
                enemytype = random.choice(ewcfg.arctic_enemies)
    else:
        if pre_chosen_poi == None:
            return

    if pre_chosen_poi != None:
        chosen_poi = pre_chosen_poi

    if enemytype != None:
        enemy = get_enemy_data(enemytype, arctic)

        # Assign enemy attributes that weren't assigned in get_enemy_data
        enemy.id_server = id_server
        enemy.slimes = enemy.slimes if pre_chosen_slimes is None else pre_chosen_slimes
        enemy.display_name = enemy.display_name if pre_chosen_displayname is None else pre_chosen_displayname
        enemy.level = level_byslime(enemy.slimes) if pre_chosen_level is None else pre_chosen_level
        enemy.expiration_date = time_now + ewcfg.time_despawn if pre_chosen_expiration is None else pre_chosen_expiration
        enemy.initialslimes = enemy.slimes if pre_chosen_initialslimes is None else pre_chosen_initialslimes
        enemy.poi = chosen_poi
        enemy.identifier = set_identifier(chosen_poi,
                                          id_server) if pre_chosen_identifier is None else pre_chosen_identifier
        # enemy.hardened_sap = int(enemy.level / 2) if pre_chosen_hardened_sap is None else pre_chosen_hardened_sap
        enemy.weathertype = ewcfg.enemy_weathertype_normal if pre_chosen_weather is None else pre_chosen_weather
        enemy.faction = '' if pre_chosen_faction is None else pre_chosen_faction
        enemy.owner = -1 if pre_chosen_owner is None else pre_chosen_owner
        enemy.rare_status = enemy.rare_status if pre_chosen_rarity is None else pre_chosen_rarity

        if pre_chosen_weather != ewcfg.enemy_weathertype_normal:
            if pre_chosen_weather == ewcfg.enemy_weathertype_rainresist:
                enemy.display_name = "Bicarbonate {}".format(enemy.display_name)
                enemy.slimes *= 2

        market_data = EwMarket(id_server=id_server)
        if (
                enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman or enemytype == ewcfg.enemy_type_doublehorse) and market_data.horseman_deaths >= 1:
            enemy.slimes *= 1.5

        props = None
        try:
            props = ewcfg.enemy_data_table[enemytype]["props"]
        except:
            pass

        enemy.enemy_props = props if pre_chosen_props is None else pre_chosen_props

        enemy.persist()

        # Recursively spawn enemies that belong to groups.
        if enemytype in ewcfg.enemy_group_leaders:
            sub_enemies_list = ewcfg.enemy_spawn_groups[enemytype]
            sub_enemies_list_item_max = len(sub_enemies_list)
            sub_enemy_list_item_count = 0

            while sub_enemy_list_item_count < sub_enemies_list_item_max:
                sub_enemy_type = sub_enemies_list[0]
                sub_enemy_spawning_max = sub_enemies_list[1]
                sub_enemy_spawning_count = 0

                sub_enemy_list_item_count += 1
                while sub_enemy_spawning_count < sub_enemy_spawning_max:
                    sub_enemy_spawning_count += 1

                    sub_resp_cont = spawn_enemy(id_server=id_server, pre_chosen_type=sub_enemy_type,
                                                pre_chosen_poi=chosen_poi, manual_spawn=True)

                    resp_cont.add_response_container(sub_resp_cont)

        if enemytype in ewcfg.slimeoid_trainers:
            sl_level = 1
            spawn_hue = False
            if enemy.rare_status:
                sl_level = random.randint(7, 10)
            else:
                sl_level = random.randint(1, 6)
            new_sl = slimeoid_utils.generate_slimeoid(id_owner=enemy.id_enemy, id_server=id_server, level=sl_level, persist=True)

        if enemytype not in ewcfg.raid_bosses:

            if enemytype == ewcfg.enemy_type_doubleheadlessdoublehorseman:
                response = "***BEHOLD!!!***  The {} has arrived to challenge thee! He is of {} slime, and {} in level. Happy Double Halloween, you knuckleheads!".format(
                    enemy.display_name, enemy.slimes, enemy.level)

                if market_data.horseman_deaths >= 1:
                    response += "\n***BACK SO SOON, MORTALS? I'M JUST GETTING WARMED UP, BAHAHAHAHAHAHA!!!***"

            elif enemytype == ewcfg.enemy_type_doublehorse:
                response = "***HARK!!!***  Clopping echoes throughout the cave! The {} has arrived with {} slime, and {} levels. And on top of him rides...".format(
                    enemy.display_name, enemy.slimes, enemy.level)
            
            elif enemytype == ewcfg.enemy_type_sandbag:
                    response = "A new {} just got sent in. It's level {}, and has {} slime.\n*'Don't hold back!'*, the Dojo Master cries out from afar.".format(
                        enemy.display_name, enemy.level, enemy.slimes)
            
            elif enemytype in ewcfg.slimeoid_trainers:
                response = "A {} is looking for a challenge! They are accompanied by {}, a {}-foot tall {}Slimeoid.".format(
                    enemy.display_name, new_sl.name, new_sl.level, "" if new_sl.hue == "" else new_sl.hue + " ")
            else:

                response = "**An enemy draws near!!** It's a level {} {}, and has {} slime.".format(enemy.level,
                                                                                                    enemy.display_name,
                                                                                                    enemy.slimes)
                

        ch_name = poi_static.id_to_poi.get(enemy.poi).channel

    if len(response) > 0 and len(ch_name) > 0:
        resp_cont.add_channel_response(ch_name, response)

    return resp_cont


# Determines what level an enemy is based on their slime count.
def level_byslime(slime):
    return int(abs(slime) ** 0.25)


# Assigns enemies most of their necessary attributes based on their type.
def get_enemy_data(enemy_type, arctic = 0):
    enemy = EwEnemy()

    rare_status = 0
    if random.randrange(5) == 0 and enemy_type not in ewcfg.overkill_enemies:
        rare_status = 1

    enemy.id_server = -1
    enemy.slimes = 0
    enemy.totaldamage = 0
    enemy.level = 0
    enemy.life_state = ewcfg.enemy_lifestate_alive
    enemy.enemytype = enemy_type
    enemy.bleed_storage = 0
    enemy.time_lastenter = 0
    enemy.initialslimes = 0
    enemy.id_target = -1
    enemy.raidtimer = 0
    enemy.rare_status = rare_status

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

    if arctic == 1:
        enemy.display_name = ewcfg.enemy_data_table[enemy_type]["arcticvariant"]

    if rare_status == 1:
        enemy.display_name = ewcfg.enemy_data_table[enemy_type]["raredisplayname"]
        enemy.slimes *= 2

    return enemy


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
