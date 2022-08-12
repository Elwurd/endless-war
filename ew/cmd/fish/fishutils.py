import random
import asyncio
import time

from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.dungeons import EwGamestate
from ew.static import cfg as ewcfg
from ew.static import fish as static_fish
from ew.static import status as se_static
from ew.static import vendors
from ew.static import poi as poi_static
from ew.static import weapons as static_weapons
from ew.static import weather as weather_static
from ew.utils import item as itm_utils
from ew.utils import poi as poi_utils
from ew.utils import core as ewutils
from ew.cmd.move.moveutils import one_eye_dm
from ew.utils import frontend as ewfrontend
from ew.utils.district import EwDistrict
from ew.utils.rolemgr import updateRoles
from ew.utils.combat import EwUser

try:    
    from ew.utils import rutils 
except:
    from ew.utils import rutils_dummy as rutils


class EwFisher:
    fishing = False
    bite = False
    current_fish = ""
    current_size = ""
    pier = ""
    bait = False
    bait_id = 0
    high = False
    fishing_id = 0
    inhabitant_id = None
    fleshling_reeled = False
    ghost_reeled = False
    length = 0
    cast_poi = ""

    def stop(self):
        self.fishing = False
        self.bite = False
        self.current_fish = ""
        self.current_size = ""
        self.pier = ""
        if self.bait == True and self.bait_id != 0:
            bknd_item.item_delete(self.bait_id)
        self.bait = False
        self.bait_id = 0
        self.high = False
        self.fishing_id = 0
        self.inhabitant_id = None
        self.fleshling_reeled = False
        self.ghost_reeled = False
        self.length = 0
        self.cast_poi = ""


fishers = {}
fishing_counter = 0


# Randomly generates a fish.
def gen_fish(market_data, fisher, has_fishingrod = False,  mutations = [], rarity = None, secret_unlocked = False):
    fish_pool = []

    rarity_number = random.randint(0, 100)

    # TODO: reimplement chance to get items in black pond using negapoudrin
    # fragments when any of that shit has any use beyond making staves.
    # just ctrl+f the variable below and remove anything to do with it
    voidfishing = fisher.pier.pier_type == ewcfg.fish_slime_void
    if rarity is None:
        if has_fishingrod:
            if rarity_number >= 0 and rarity_number < 21 and not voidfishing:  # 20%
                rarity = "item"

            elif rarity_number >= 21 and rarity_number < 31:  # 10%
                rarity = "common"

            elif rarity_number >= 31 and rarity_number < 71:  # 40%
                rarity = "uncommon"

            elif rarity_number >= 71 and rarity_number < 91:  # 20%
                rarity = "rare"

            else:  # 10%
                rarity = "promo"

        # If player doesn't have a fishing rod but does have OMJ, increase junk item chance.
        elif ewcfg.mutation_id_onemansjunk in mutations:
            if rarity_number >= 0 and rarity_number < 31 and not voidfishing:  # 30%
                rarity = "item"

            elif rarity_number >= 31 and rarity_number < 71:  # 40%
                rarity = "common"

            elif rarity_number >= 71 and rarity_number < 91:  # 20%
                rarity = "uncommon"

            elif rarity_number >= 91 and rarity_number < 100:  # 9%
                rarity = "rare"

            else:  # 1%
                rarity = "promo"

        else:
            if rarity_number >= 0 and rarity_number < 11 and not voidfishing:  # 10%
                rarity = "item"

            elif rarity_number >= 11 and rarity_number < 61:  # 50%
                rarity = "common"

            elif rarity_number >= 61 and rarity_number < 91:  # 30%
                rarity = "uncommon"

            elif rarity_number >= 91 and rarity_number < 100:  # 9%
                rarity = "rare"

            else:  # 1%
                rarity = "promo"
    
    if rarity == "item":
        fish = "item"
        return fish
    else:
        fish_pool.extend(static_fish.rarity_to_list[rarity])

    # Weather exclusive fish
    if market_data.weather != "rainy":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.rainy_fish]
    if market_data.weather != "sunny":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.sunny_fish]
    if market_data.weather != "foggy":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.foggy_fish]
    if market_data.weather != "snow":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.snow_fish]

    # Time exclusive fish
    if 5 < market_data.clock < 20:
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.night_fish]
    elif market_data.clock < 8 or market_data.clock > 17:
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.day_fish]
        if ewutils.check_moon_phase(market_data) != ewcfg.moon_special:
            fish_pool = [fish for fish in fish_pool if fish not in static_fish.moon_phase_special_fish]
    else:
        for fish in fish_pool:
            if static_fish.fish_map[fish].catch_time != None:
                fish_pool.remove(fish)

    # Pier type exclusive fish
    if fisher.pier.pier_type == "freshwater":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.salt_fish and fish not in static_fish.void_fish and fish not in static_fish.event_fish and fish not in static_fish.moon_fish]
    elif fisher.pier.pier_type == "saltwater":
        fish_pool = [fish for fish in fish_pool if fish not in static_fish.fresh_fish and fish not in static_fish.void_fish and fish not in static_fish.event_fish and fish not in static_fish.moon_fish]
    elif fisher.pier.pier_type == "void":
        fish_pool = [fish for fish in fish_pool if fish in static_fish.void_fish]
    elif fisher.pier.pier_type == "event":
        fish_pool = [fish for fish in fish_pool if fish in static_fish.event_fish]
    elif fisher.pier.pier_type == "moon":
        fish_pool = [fish for fish in fish_pool if fish in static_fish.moon_fish]


    fish = random.choice(fish_pool)

    # Get fucked
    if fisher.pier.id_poi == ewcfg.poi_id_juviesrow_pier:
        fish = 'plebefish'

    #TODO you can unlock the secret fish by catching all the other ones
    # secret fish
    if secret_unlocked and random.randint(0, 1000) == 69:
        fish = 'mermaid'

    return fish


# Determines the size of the fish
def gen_fish_size(mastery_bonus = 0, fish_size = None):

    iterator = 0 #
    choice = 0 #decides whether the fish is large or small, is useless for colossal variations
    size_multiplier = 1 + mastery_bonus/30

    fish_category = "average"

    if random.randint(0, 1) == 1: #this loop could theoretically go on forever
        while(iterator < 10000):
            iterator = iterator + 1
            limit = random.randint(1, 10)

            if limit <= 3: # 3/10
                choice = 1
                break
            elif limit <= 6: # 3/10
                choice = 2
                break
            # 4/10 chance of repeating

    if fish_size is None:
        if iterator == 0:                   # 50%
            fish_category = ewcfg.fish_size_average 
        elif iterator == 1 and choice == 1: # 15%
            fish_category = ewcfg.fish_size_big
        elif iterator == 1 and choice == 2: # 15%
            fish_category = ewcfg.fish_size_small
        elif iterator == 2 and choice == 1: # 6%
            fish_category = ewcfg.fish_size_miniscule
        elif iterator == 2 and choice == 2: # 6%
            fish_category = ewcfg.fish_size_huge
        elif iterator > 2:                  # 8%
            fish_category = ewcfg.fish_size_colossal
    else:
        fish_category = fish_size

    size_minimum = ewcfg.fish_size_range.get(fish_category)[0]

    size_maximum = ewcfg.fish_size_range.get(fish_category)[1]

    if iterator > 2:
        size_minimum += (iterator - 3) * 12
        size_maximum += (iterator - 3) * 12

    size_maximum *= size_multiplier

    return round(random.uniform(size_minimum, size_maximum), 2)


    """size_number = random.randint(min(mastery_bonus * 5, 100), 100)

    if size_number >= 0 and size_number < 6:  # 5%
        size = ewcfg.fish_size_miniscule
    elif size_number >= 6 and size_number < 21:  # 15%
        size = ewcfg.fish_size_small
    elif size_number >= 21 and size_number < 71:  # 50%
        size = ewcfg.fish_size_average
    elif size_number >= 71 and size_number < 86:  # 15%
        size = ewcfg.fish_size_big
    elif size_number >= 86 and size_number < 100:  # 4
        size = ewcfg.fish_size_huge
    else:  # 1%
        size = ewcfg.fish_size_colossal

    return size"""

def length_to_size(size_number):

    for size in ewcfg.fish_size_range.keys():
        if ewcfg.fish_size_range.get(size)[0] < size_number < ewcfg.fish_size_range.get(size)[1]:
            return size

    return ewcfg.fish_size_colossal



# Determines bite text
def gen_bite_text(size):
    if size == "item":
        text = "You feel a distinctly inanimate tug at your fishing pole!"

    elif size == ewcfg.fish_size_miniscule:
        text = "You feel a wimpy tug at your fishing pole!"
    elif size == ewcfg.fish_size_small:
        text = "You feel a mediocre tug at your fishing pole!"
    elif size == ewcfg.fish_size_average:
        text = "You feel a modest tug at your fishing pole!"
    elif size == ewcfg.fish_size_big:
        text = "You feel a mildly threatening tug at your fishing pole!"
    elif size == ewcfg.fish_size_huge:
        text = "You feel a startlingly strong tug at your fishing pole!"
    elif size == ewcfg.fish_size_colossal:
        text = "You feel a tug at your fishing pole so intense that you nearly get swept off your feet!"
    else:
        text = "You feel a tug at your fishing pole!" # Just in case flavor text fix

    text += " **!REEL NOW!!!!!**"
    return text


async def award_fish(fisher, cmd, user_data):
    response = ""

    actual_fisherman = None
    actual_fisherman_data = user_data

    if fisher.inhabitant_id:
        actual_fisherman = user_data.get_possession()[1]
        actual_fisherman_data = EwUser(id_user=actual_fisherman, id_server=cmd.guild.id)

    if fisher.current_fish in ["item", "seaitem"]:
        slimesea_inventory = bknd_item.inventory(id_server=cmd.guild.id, id_user=ewcfg.poi_id_slimesea)

        if fisher.pier.pier_type == ewcfg.fish_slime_moon and fisher.current_fish == "item":
            district = EwDistrict(id_server=cmd.guild.id, district=fisher.cast_poi.id_poi)
            players_in_district = district.get_players_in_district()
            
            moonfishing = EwGamestate(id_state='moonfishing', id_server=cmd.guild.id)

            if moonfishing.bit == 1 and len(players_in_district) >= 1:
                player_id = random.choice(players_in_district)

                target_data = EwUser(id_user=player_id, id_server=cmd.guild.id)
                target = cmd.guild.get_member(player_id)

                mutations = target_data.get_mutations()

                # No Big Bones
                if ewcfg.mutation_id_bigbones in mutations:
                    response = "You reel onto someone, but they're too fat! Your line breaks."
                else:
                    ewutils.moves_active[target_data.id_user] = 0
                    await rutils.movement_checker(target_data, poi_static.id_to_poi.get(target_data.poi), fisher.cast_poi, cmd=cmd)

                    # Send a bit of a wait message
                    response = "***HRRRRKK-!!!***"
                    await ewfrontend.send_message(cmd.client, cmd.message.channel, ewfrontend.formatMessage(cmd.message.author, response))
                    await asyncio.sleep(3)

                    # Send 'em to the moon!
                    await updateRoles(client=cmd.client, member=target, new_poi='crestofthecrescentmoon')
                    target_data.poi = 'crestofthecrescentmoon'
                    target_data.time_lastenter = int(time.time())
                    target_data.persist()

                    # Move ghosts and make possible oeo dms.
                    await one_eye_dm(id_user=target_data.id_user, id_server=target_data.id_server, poi='crestofthecrescentmoon')
                    await target_data.move_inhabitants(id_poi='crestofthecrescentmoon')
                    response = "Oh? Looks like you've reeled up a {}!".format(target.display_name)

            # If there AREN'T players
            else:
                items_in_poi = bknd_item.inventory(id_user=fisher.cast_poi.id_poi, id_server=user_data.id_server)
                
                if len(items_in_poi) > 0:
                    item_caught = random.choice(items_in_poi)

                    response = "You reel in a {}!".format(item_caught.get('name'))

                    if bknd_item.check_inv_capacity(user_data=user_data, item_type=item_caught.get('item_type')):
                        bknd_item.give_item(id_user=user_data.id_user, id_server=user_data.id_server, id_item=item_caught.get("id_item"))
                    else:
                        response += " But you couldn't carry any more {}s, so it falls on the floor.".format(item_caught.get('item_type'))
                        bknd_item.give_item(id_user=user_data.poi, id_server=user_data.id_server, id_item=item_caught.get("id_item"))
                else:
                    response = "You reeled... nothing!"

        elif (fisher.pier.pier_type != ewcfg.fish_slime_saltwater or len(slimesea_inventory) == 0 or random.random() < 0.2) and fisher.current_fish == "item":

            # Choose a random item from the possible mining results - currently just poudrins
            item = random.choice(vendors.mine_results)


            unearthed_item_amount = (random.randrange(5) + 8)  # anywhere from 8-12 drops

            item_props = itm_utils.gen_item_props(item)

            # Ensure item limits are enforced, including food since this isn't the fish section
            if bknd_item.check_inv_capacity(user_data=actual_fisherman_data, item_type=item.item_type):
                for creation in range(unearthed_item_amount):
                    bknd_item.item_create(
                        item_type=item.item_type,
                        id_user=actual_fisherman or cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props=item_props
                    )

                response = "You reel in {} {}s! ".format(unearthed_item_amount, item.str_name)
            else:
                response = "You woulda reeled in some {}s, but your back gave out under the weight of the rest of your {}s.".format(item.str_name, item.item_type)
        
        # If "seaitem" is specified, get a sea item.
        else:
            item = random.choice(slimesea_inventory)

            if bknd_item.give_item(id_item=item.get('id_item'), member=cmd.message.author):
                response = "You reel in a {}!".format(item.get('name'))
            else:
                response = "You woulda reeled in a {}, but your back gave out under the weight of the rest of your {}s.".format(item.str_name, item.item_type)

        fisher.stop()
        user_data.persist()

    else:
        user_initial_level = user_data.slimelevel

        gang_bonus = False

        has_fishingrod = False

        # Check if the user has a fishing rod equipped
        if user_data.weapon >= 0:
            weapon_item = EwItem(id_item=user_data.weapon)
            weapon = static_weapons.weapon_map.get(weapon_item.item_props.get("weapon_type"))
            if weapon.id_weapon == "fishingrod":
                has_fishingrod = True
                
        # The fish's value, for bartering.
        value = 0

        # Rewards from the fish's size
        slime_gain = ewcfg.fish_gain * static_fish.size_to_reward[fisher.current_size]
        value += 10 * static_fish.size_to_reward[fisher.current_size]

        # Rewards from the fish's rarity
        value += 10 * static_fish.rarity_to_reward[static_fish.fish_map[fisher.current_fish].rarity]

        # Give the user a bonus if they catch a day fish as a rowdy or a night fish as a killer. 
        if user_data.life_state == 2:
            if fisher.current_fish in static_fish.day_fish and user_data.faction == ewcfg.faction_rowdys:
                gang_bonus = True
                slime_gain = slime_gain * 1.5
                value += 20

            if fisher.current_fish in static_fish.night_fish and user_data.faction == ewcfg.faction_killers:
                gang_bonus = True
                slime_gain = slime_gain * 1.5
                value += 20

        # Disabled while I try out the new mastery fishing
        #if has_fishingrod == True:
        #    slime_gain = slime_gain * 2

        # Fish are more valuable at the void.
        if fisher.pier.pier_type == ewcfg.fish_slime_void or fisher.pier.pier_type == ewcfg.fish_slime_moon:
            slime_gain = slime_gain * 1.5
            value += 30

        if fisher.current_fish == "plebefish":
            slime_gain = ewcfg.fish_gain * .5
            value = 10

        controlling_faction = poi_utils.get_subzone_controlling_faction(user_data.poi, user_data.id_server)

        if controlling_faction != "" and controlling_faction == user_data.faction:
            slime_gain *= 2

        if user_data.poi == ewcfg.poi_id_juviesrow_pier:
            slime_gain = int(slime_gain / 4)

        # Makes sure slime gain can never go below 0.
        slime_gain = max(0, round(slime_gain))

        bknd_item.item_create(
            id_user=actual_fisherman or cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type=ewcfg.it_food,
            item_props={
                'id_food': static_fish.fish_map[fisher.current_fish].id_fish,
                'food_name': static_fish.fish_map[fisher.current_fish].str_name,
                'food_desc': "{}\nIt's {} inches long.".format(static_fish.fish_map[fisher.current_fish].str_desc, fisher.length),
                'recover_hunger': 20,
                'str_eat': ewcfg.str_eat_raw_material.format(static_fish.fish_map[fisher.current_fish].str_name),
                'rarity': static_fish.fish_map[fisher.current_fish].rarity,
                'size': fisher.current_size,
                'time_expir': time.time() + ewcfg.std_food_expir,
                'time_fridged': 0,
                'acquisition': ewcfg.acquisition_fishing,
                'value': value,
                'noslime': 'false',
                'length': fisher.length
            }
        )

        if fisher.inhabitant_id:
            server = cmd.guild
            inhabitant_member = server.get_member(fisher.inhabitant_id)
            inhabitant_name = inhabitant_member.display_name
            inhabitant_data = EwUser(id_user=fisher.inhabitant_id, id_server=user_data.id_server)
            inhabitee_name = server.get_member(actual_fisherman).display_name

            # Take 1/4 of the slime the player would have gained, to inverse and give to the ghost.
            slime_gain = int(0.25 * slime_gain)        
            response = "The two of you together manage to reel in a {fish}! {flavor} It's {length} inches long! {ghost} haunts {slime:,} slime away from the fish before placing it on {fleshling}'s hands." \
                .format(
                fish=static_fish.fish_map[fisher.current_fish].str_name,
                flavor=static_fish.fish_map[fisher.current_fish].str_desc,
                ghost=inhabitant_name,
                fleshling=inhabitee_name,
                slime=slime_gain,
                length=fisher.length,
            )

            inhabitant_data.change_slimes(n=-slime_gain)
            inhabitant_data.persist()
            fisher.stop()
        else:
            response = "You reel in a {fish}! {flavor} It's {length} inches long! You grab hold and wring {slime:,} slime from it. " \
                .format(fish=static_fish.fish_map[fisher.current_fish].str_name, length=fisher.length, flavor=static_fish.fish_map[fisher.current_fish].str_desc, slime=slime_gain)
            
            # Add to the response if the user gets a gang bonus.
            if gang_bonus == True:
                if user_data.faction == ewcfg.faction_rowdys:
                    response += "The Rowdy-pride this fish is showing gave you more slime than usual. "
                elif user_data.faction == ewcfg.faction_killers:
                    response += "The Killer-pride this fish is showing gave you more slime than usual. "

            levelup_response = user_data.change_slimes(n=slime_gain, source=ewcfg.source_fishing)
            was_levelup = True if user_initial_level < user_data.slimelevel else False
            # Tell the player their slime level increased.
            if was_levelup:
                response += levelup_response

        fisher.stop()

        user_data.persist()
    return response


def cancel_rod_possession(fisher, user_data):
    response = ''
    if fisher.inhabitant_id:
        user_data.cancel_possession()
        response += '\n'
        if fisher.fleshling_reeled:
            response += "Fucking ghosts, can't rely on them for anything."
        elif fisher.ghost_reeled:
            response += "You can't trust the living even for the simplest shit, I guess."
        else:
            response += "Are you two even trying?"
        response += ' Your contract is dissolved.'
    return response
