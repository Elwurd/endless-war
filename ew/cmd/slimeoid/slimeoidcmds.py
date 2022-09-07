import random
import time
import asyncio

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend import hunting as bknd_hunting
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.backend.quadrants import EwQuadrant
from ew.static import cfg as ewcfg
from ew.static import hue as hue_static
from ew.static import poi as poi_static
from ew.static import slimeoid as sl_static
from ew.utils import casino as casino_utils
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils import item as item_utils
from ew.utils import slimeoid as slimeoid_utils
from ew.utils import combat as cmbt_utils
from ew.utils.combat import EwUser
from ew.utils.combat import EwEnemy
from ew.utils.district import EwDistrict
from ew.utils.slimeoid import EwSlimeoid
from .slimeoidutils import battle_slimeoids
from .slimeoidutils import can_slimeoid_battle
from .slimeoidutils import get_slimeoid_count


# Destroy a slimeoid
async def dissolveslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)

    slimeoid = EwSlimeoid(member=cmd.message.author)
    # roles_map_user = ewutils.getRoleMap(message.author.roles)

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "You must go to the SlimeCorp Laboratories in Brawlden to dissolve a Slimeoid."

    elif user_data.life_state == ewcfg.life_state_corpse and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "Ghosts cannot interact with the SlimeCorp Lab apparati."

    elif user_data.life_state != ewcfg.life_state_corpse and cmd.message.channel.name == ewcfg.channel_wafflehouse:
        response = "You feel as though there is some ancient power here, but the slime coursing through your veins prevents you from using it."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You have no slimeoid to dissolve."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:

        poi = poi_static.id_to_poi.get(user_data.poi)
        district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

        #see if the player is a ghost or not, and correspond this to dissolving a slimeoid or negaslimeoid
        if slimeoid.sltype == ewcfg.sltype_nega:
            slimeoidtype = "Negaslimeoid"
        else:
            slimeoidtype = "Slimeoid"

        if slimeoid.life_state != ewcfg.slimeoid_state_forming:
            # If the user isn't a ghost
            if user_data.life_state != ewcfg.life_state_corpse:
                brain = sl_static.brain_map.get(slimeoid.ai)
                response = brain.str_dissolve.format(
                    slimeoid_name=slimeoid.name
                )
                response += "{}".format(ewcfg.emote_slimeskull)

            else:
                # If the user is a ghost and has fully-formed Negaslimeoid, make them !destroyslimeoid instead.
                response = "The Ancient Ones would be very displeased if you attempted to dissolve your Negaslimeoid. Use your latent ghostly powers instead and !destroyslimeoid."
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        else:
            if slimeoidtype == "Slimeoid":
                response = "You hit a large red button with a white X on it. Immediately a buzzer goes off and the half-formed body of what would have been your new Slimeoid is flushed out of the gestation tank and down a drainage tube, along with your poudrin and slime. What a waste."                
            else:
                response = "The planchette lands upon \"NO\" and you hear ghastly screeches from ahead. The Negaslimeoid you were conjuring is torn apart into space, sending negaslime across the ether. The planchette moves to \"GOOD BYE\". It seems your communion with the Ancient Ones has come to an end."


        cosmetics = bknd_item.inventory(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type_filter=ewcfg.it_cosmetic
        )

        # get the cosmetics worn by the slimeoid
        for item in cosmetics:
            cos = EwItem(id_item=item.get('id_item'))
            if cos.item_props.get('slimeoid') == 'true':
                cos.item_props['slimeoid'] = 'false'
                cos.id_owner = user_data.id_user
                cos.persist()

        bknd_core.execute_sql_query(
            "DELETE FROM slimeoids WHERE {id_user} = %s AND {id_server} = %s".format(
                id_user=ewcfg.col_id_user,
                id_server=ewcfg.col_id_server,
            ), (
                slimeoid.id_user,
                slimeoid.id_server,
            ))

        user_data.active_slimeoid = -1
        user_data.persist()

    # Send the response to the player.

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# Show a player's slimeoid data.
async def slimeoid(cmd):
    member = None
    selfcheck = True
    response = ""

    if cmd.mentions_count == 0:
        selfcheck = True
        user_data = EwUser(member=cmd.message.author)
        slimeoid = EwSlimeoid(member=cmd.message.author)
    else:
        selfcheck = False
        member = cmd.mentions[0]
        user_data = EwUser(member=member)
        slimeoid = EwSlimeoid(member=member)

        # Set the slimeoid's type to Negaslimeoid if they're that
    if slimeoid.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid" 
    else:
        slimeoidtype = "Slimeoid" # slimeoidtype is a string so that some flavor text can just use slimeoidtype

    # If the user is a ghost and has a living slimeoid, this will prevent them from interacting with that slimeoid.
    if user_data.life_state == ewcfg.life_state_corpse and slimeoidtype != "Negaslimeoid":    
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        if selfcheck == True:
            response = "You have not yet created a slimeoid."
        else:
            response = "{} has not yet created a slimeoid.".format(member.display_name)

    else:
        if slimeoid.life_state == ewcfg.slimeoid_state_forming:
            if selfcheck == True:
                if slimeoidtype == "Negaslimeoid":
                    response = "Your Negaslimeoid is still emerging from the spawning glob. It is about {} feet from end to end.".format(str(slimeoid.level))
                else:
                    response = "Your Slimeoid is still forming in the gestation vat. It is about {} feet from end to end.".format(str(slimeoid.level))
            else:
                if slimeoidtype == "Negaslimeoid":
                    response = "{}'s Negaslimeoid is still emerging from the spawning glob. It is about {} feet from end to end.".format(member.display_name, str(slimeoid.level))
                else:                
                    response = "{}'s Slimeoid is still forming in the gestation vat. It is about {} feet from end to end.".format(member.display_name, str(slimeoid.level))
        elif slimeoid.life_state == ewcfg.slimeoid_state_active:
            if selfcheck == True:
                response = "You are accompanied by {}, a {}-foot-tall {}.".format(slimeoid.name, str(slimeoid.level), slimeoidtype)
            else:
                response = "{} is accompanied by {}, a {}-foot-tall {}.".format(member.display_name, slimeoid.name, str(slimeoid.level), slimeoidtype)

        response += slimeoid_utils.slimeoid_describe(slimeoid)

        cosmetics = bknd_item.inventory(
            id_user=slimeoid.id_slimeoid,
            id_server=cmd.guild.id,
            item_type_filter=ewcfg.it_cosmetic
        )

        # get the cosmetics worn by the slimeoid
        adorned_cosmetics = []

        for item in cosmetics:
            cos = EwItem(id_item=item.get('id_item'))
            if cos.item_props.get('slimeoid') == 'true':
                hue = hue_static.hue_map.get(cos.item_props.get('hue'))
                adorned_cosmetics.append((hue.str_name + " colored " if hue != None else "") + cos.item_props.get('cosmetic_name'))

        # List the cosmetics the slimeoid has adorned
        if len(adorned_cosmetics) > 0:
            response += "\n\nIt has a {} adorned.".format(ewutils.formatNiceList(adorned_cosmetics, "and"))
    
            # If it has more than 2, give it a freshness rating
            if len(adorned_cosmetics) >= 2:
                outfit_map = item_utils.get_outfit_info(id_user=slimeoid.id_slimeoid, id_server=cmd.guild.id, slimeoid = True)

                if outfit_map is not None:
                    response += " Its total freshness rating is a {} {}.".format(outfit_map['dominant_style'], outfit_map['total_freshness'])

        # If the user is wearing clout goggles, show the slimeoid's clout as a number.
        cosmetic_abilities = item_utils.get_cosmetic_abilities(id_user=cmd.message.author.id, id_server=cmd.guild.id)
        if ewcfg.cosmeticAbility_id_clout in cosmetic_abilities:
            if slimeoid.clout == 0:
                response += "\n\nUsing your *soul-searing clout goggles*, you can see the **CLOUTLETS** radiating off of {}. But... it doesn't have any clout! What a LOSER!!!".format(slimeoid.name)
            else:
                response += "\n\nUsing your *soul-searing clout goggles*, you can see the **CLOUTLETS** radiating off of {}. You determine that {} has approximately **{} clout**! Holy cow!".format(slimeoid.name, slimeoid.name, slimeoid.clout)

        # Show the slimeoid's description.
        if slimeoid.dogtag != "":
            response += "\n\nThere's a dog tag embedded in it: {}".format(slimeoid.dogtag)


    # Send the response to the player.
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


# play with your slimeoid
async def playfetch(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    # Ghosts with living slimeoids can't play fetch.
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    # Users with souls can't play fetch.
    elif user_data.has_soul == 0:
        response = "You reel back to throw the stick, but your motivation wears thin halfway through. You drop it on the ground with a sigh."

    # Slimeoids that aren't active or have been recently defeated can play fetch.
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to play fetch with."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} is too beat up from its last battle to play fetch right now.".format(slimeoid.name)

    # Get the flavor text corresponding to the slimeoid's head.
    else:
        head = sl_static.head_map.get(slimeoid.head)
        response = head.str_fetch.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def petslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    target = None
    target_data = None
    list_ids = None

    # mentions[0]
    # If a player is @'d in the command, pet their slimeoid if you're in the same POI, are both sharing quadrants, and pass lifestate checks.
    if cmd.mentions_count > 0:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)

        list_ids = []

        for quadrant in ewcfg.quadrant_ids:
            quadrant_data = EwQuadrant(id_server=cmd.guild.id, id_user=cmd.message.author.id, quadrant=quadrant)
            if quadrant_data.id_target != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target)
            if quadrant_data.id_target2 != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target2)

        if target_data.poi != user_data.poi:
            response = "You can't pet them because they aren't here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.id_user not in list_ids:
            response = "You try to pet {}'s slimeoid, but you're not close enough for them to trust you. Better whip out those quadrants...".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
            response = "Slimeoids don't fuck with ghosts.".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            slimeoid = EwSlimeoid(member=target)

    # Living players in a ghost's quadrants can't pet negaslimeoids.
    if slimeoid.sltype == ewcfg.sltype_nega and user_data.life_state != ewcfg.life_state_corpse:
        response = "You go to pet the Negaslimeoid, but then you realize you're a fucking idiot. If you lay one finger on that unholy abomination your hand will evaporate."

    # Ghosts can't fuck with slimeoids.
    elif user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    elif cmd.mentions_count > 1:
        response = "Getting a bit too touchy-feely with these slimeoids, eh? You can only pet one at a time."

    elif user_data.has_soul == 0:
        response = "The idea doesn't even occur to you because your soul is missing."

    # Slimeoids that aren't active or have been recently defeated can play fetch.
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to pet."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} whimpers. It's still recovering from being beaten up.".format(slimeoid.name)

    # Get the flavor text corresponding to the slimeoid's defense and brain.
    else:

        armor = sl_static.defense_map.get(slimeoid.armor)
        response = armor.str_pet.format(
            slimeoid_name=slimeoid.name
        )
        response += " "
        brain = sl_static.brain_map.get(slimeoid.ai)
        response += brain.str_pet.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def abuseslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    target = None
    target_data = None
    list_ids = None

    # mentions[0]
    # If a player is @'d in the command, pet their slimeoid if you're in the same POI, are both sharing quadrants, and pass lifestate checks.
    if cmd.mentions_count > 0:
        target = cmd.mentions[0]
        target_data = EwUser(member=target)

        list_ids = []

        for quadrant in ewcfg.quadrant_ids:
            quadrant_data = EwQuadrant(id_server=cmd.guild.id, id_user=cmd.message.author.id, quadrant=quadrant)
            if quadrant_data.id_target != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target)
            if quadrant_data.id_target2 != -1 and quadrant_data.check_if_onesided() is False:
                list_ids.append(quadrant_data.id_target2)

        if target_data.poi != user_data.poi:
            response = "You can't beat them up them because they aren't here."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.id_user not in list_ids:
            response = "You try to lynch {}'s slimeoid, but you're not close enough for them to trust you. Better whip out those quadrants...".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        elif target_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
            response = "Slimeoids don't fuck with ghosts.".format(target.display_name)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            slimeoid = EwSlimeoid(member=target)

    # Living players in a ghost's quadrants can't pet negaslimeoids.
    if slimeoid.sltype == ewcfg.sltype_nega and user_data.life_state != ewcfg.life_state_corpse:
        response = "Why don't you !slimeoidbattle? No point in abusing something you could just kill."

    # Ghosts can't fuck with slimeoids.
    elif slimeoid.sltype != ewcfg.sltype_nega and user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif cmd.mentions_count > 1:
        response = "Control your anger! Everybody knows it's more efficient to inflict trauma on one slimeoid at a time."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to hurt."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    # elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
    #		response = "{} whimpers. It's still recovering from being beaten up.".format(slimeoid.name)

    # Get the flavor text corresponding to the slimeoid's defense and brain.
    else:

        armor = sl_static.defense_map.get(slimeoid.armor)
        response = armor.str_abuse.format(
            slimeoid_name=slimeoid.name
        )
        response += " "
        brain = sl_static.brain_map.get(slimeoid.ai)
        response += brain.str_abuse.format(
            slimeoid_name=slimeoid.name
        )
        slimeoid.time_defeated = time_now
        slimeoid.persist()
    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def walkslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    # Ghosts with living slimeoids can't walk their slimeoid.
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    elif user_data.has_soul == 0:
        response = "Why take it on a walk? It's not like it understands your needs."

    # Check for slimeoid life state and whether it has been defeated recently
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to take for a walk."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} can barely move. It's still recovering from its injuries.".format(slimeoid.name)

    # Get the flavor text corresponding to the slimeoid's brain and legs.
    else:
        brain = sl_static.brain_map.get(slimeoid.ai)
        response = brain.str_walk.format(
            slimeoid_name=slimeoid.name
        )
        poi = poi_static.id_to_poi.get(user_data.poi)
        response += " With that done, you go for a leisurely stroll around {}, while ".format(poi.str_name)
        legs = sl_static.mobility_map.get(slimeoid.legs)
        response += legs.str_walk.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def observeslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())

    if user_data.life_state != ewcfg.life_state_corpse:
        slimeoidtype = "Slimeoid"
    else:
        slimeoidtype = "Negaslimeoid"

    # Ghosts with living slimeoids can't observe them.
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "{}s don't fuck with ghosts.".format(slimeoidtype)

    # Checks for slimeoid lifestate and whether it was defeated recently.
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a {} to observe.".format(slimeoidtype)

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your {} is not yet ready. Use !spawnslimeoid to complete incubation.".format(slimeoidtype)

    elif (time_now - slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
        response = "{} lies totally inert, recuperating from being recently pulverized.".format(slimeoid.name)

    # Choose a random response between the slimeoid's body, weapon, special, and brain.
    else:
        options = [
            'body',
            'weapon',
            'special',
            'brain',
        ]

        roll = random.randrange(len(options))
        result = options[roll]

        if result == 'body':
            part = sl_static.body_map.get(slimeoid.body)

        if result == 'weapon':
            part = sl_static.offense_map.get(slimeoid.weapon)

        if result == 'special':
            part = sl_static.special_map.get(slimeoid.special)

        if result == 'brain':
            part = sl_static.brain_map.get(slimeoid.ai)

        response = part.str_observe.format(
            slimeoid_name=slimeoid.name
        )

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def slimeoidbattle(cmd):
    # if cmd.message.channel.name != ewcfg.channel_arena:
    # Only at the arena
    #	response = "You can only have Slimeoid Battles at the Battle Arena."
    #	return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    pvp_battle = False
    fatal = False
    size_limit = False
    bet = None
    response = ""
    user_name = "" # get it, like a username!
    target_name = ""
    duel = False
    if cmd.tokens[0] == "!slimeoidduel":
        duel = True

    if ewutils.channel_name_is_poi(str(cmd.message.channel)) is False:
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, "You must {} in a zone's channel.".format(cmd.tokens[0])))

    if cmd.mentions_count > 1:
        response = "Slow down there, bucko! You can only challenge one person to a slimeoid battle at a time."
        return await fe_utils.send_response(response, cmd)
    elif cmd.mentions_count == 1:
        pvp_battle = True
    
    author = cmd.message.author
    user_name = author.display_name
    challenger = EwUser(member=author)
    challenger_slimeoid = EwSlimeoid(member=author)
    
    if pvp_battle:
        member = cmd.mentions[0]
        target_name = member.display_name

        if author.id == member.id:
            response = "You can't challenge yourself, dumbass."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

        # Gets the data of the player and slimeoid being challenged
        challengee = EwUser(member=member)
        challengee_slimeoid = EwSlimeoid(member=member)

        # Sets the bet to 0 if no bet is specified or if not at the arena.
        if "bet" in cmd.tokens:
            location = cmd.tokens.index("bet")+1
            if len(cmd.tokens) > location:
                bet = ewutils.getIntToken(tokens=[0,cmd.tokens[location]], allow_all=True)
        

        if bet == None or challenger.poi != ewcfg.poi_id_arena:
            bet = 0
        
        if bet == -1:
            bet = challenger.slimes

        # Make the slimeoid battle fatal if "todeath" is anywhere in the command
        if "death" in ewutils.flattenTokenListToString(cmd.tokens):
            fatal = True
        if "size" in cmd.tokens:
            if challenger.poi == ewcfg.poi_id_arena:
                location = cmd.tokens.index("size")+1
                if len(cmd.tokens) > location:
                    size_limit = ewutils.getIntToken(tokens=[0,cmd.tokens[location]])
                if(size_limit == None):
                    size_limit = False
            else:
                response = "Theres nobody to officiate the match, don't bother making it fair. Go to the arena for that."
                return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
        if fatal and size_limit:
            response = "You're dumber than you look if you think a slimeoid will hold back in a deathmatch."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    else:
        
        # Try to find an enemy by the name / indicator given
        targetenemy = " ".join(cmd.tokens[1:]).lower()
        challengee = cmbt_utils.find_enemy(targetenemy, challenger)
        
        if challengee is None:
            response = "Huh? Who do you want to challenge? You don't use an @ on npcs, try using their letter from {}".format(ewcfg.cmd_survey)
            return await fe_utils.send_response(response, cmd)
        
        target_name = challengee.display_name
        challengee_slimeoid = EwSlimeoid(id_user=challengee.id_enemy, id_server=cmd.message.guild.id)
        
        bet = 0

    # Check if you can throw down
    response = can_slimeoid_battle(challenger, challengee, challenger_slimeoid, challengee_slimeoid, bet)
    if response != "":
        return await fe_utils.send_response(response, cmd)

    # Assign a challenger so partipants can't be challenged again
    challenger_slimeoid_id = challenger_slimeoid.id_slimeoid
    challengee_slimeoid_id = challengee_slimeoid.id_slimeoid
    ewutils.active_slimeoidbattles[challenger_slimeoid_id] = True
    ewutils.active_slimeoidbattles[challengee_slimeoid_id] = True

    if pvp_battle:
        ewutils.active_target_map[challengee.id_user] = challenger.id_user
        response = "You have been challenged by {} to a Slimeoid Battle{}. Do you !accept or !refuse?".format(user_name, " **TO THE DEATH**" if fatal else "").replace("@", "\{at\}")
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(member, response))

        # Wait for an answer
        accepted = 0
        try:
            msg = await cmd.client.wait_for('message', timeout=30, check=lambda message: message.author == member and message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

            if msg != None:
                if msg.content == ewcfg.cmd_accept:
                    accepted = 1
        except:
            accepted = 0
        
        if accepted == 1:
            if duel:
                response = "**THREE**"
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
                await asyncio.sleep(1)
                response = "**TWO**"
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
                await asyncio.sleep(1)
                response = "**ONE**"
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
                await asyncio.sleep(1)

            # Load information again in case it changed while we were awaiting the challenge
            challengee = EwUser(member=member)
            challengee_slimeoid = EwSlimeoid(member=member)
            challenger = EwUser(member=author)
            challengee_slimeoid = EwSlimeoid(member=member)

            ewutils.active_target_map[challengee.id_user] = ""
            ewutils.active_target_map[challenger.id_user] = ""

            # Double check to make sure nothing has happened in the mean time

            if challenger_slimeoid.life_state != ewcfg.slimeoid_state_active:
                ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
                ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False
                response = "You do not have a Slimeoid ready to battle with!"
                return await fe_utils.send_response(response, cmd)

            if challengee_slimeoid.life_state != ewcfg.slimeoid_state_active:
                ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
                ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False
                response = "{} does not have a Slimeoid ready to battle with!".format(target_name)
                return await fe_utils.send_response(response, cmd)

            if duel:
                response = "***GO!***"
                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))
    else:
        accepted = 1

    # Start game
    if accepted == 1:
        # Don't change slimes unless we realllllyyyyyy have to
        # Winnings needs to be established in order for this to work.
        winnings = 0
        if bet != 0:
            challengee.change_slimes(n=-bet, source=ewcfg.source_slimeoid_betting)
            challenger.change_slimes(n=-bet, source=ewcfg.source_slimeoid_betting)

            challengee.persist()
            challenger.persist()

            winnings = bet * 2

        if not pvp_battle:
            winnings = 1000000 * challengee_slimeoid.level

        # The actual battle goes here
        result = await battle_slimeoids(
            id_s1=challengee_slimeoid.id_slimeoid,
            id_s2=challenger_slimeoid.id_slimeoid,
            channel=cmd.message.channel,
            battle_type=ewcfg.battle_type_arena,
            challengee_name=target_name,
            challenger_name=user_name,
            pvp_battle=pvp_battle,
            size_limit=size_limit
        )

        # Challenger won
        if result ==  1:
            winner = challenger
            winner_slimeoid_name = challenger_slimeoid.name
            winner_trainer_name = user_name
        else:
            winner = challengee
            winner_slimeoid_name = challengee_slimeoid.name
            winner_trainer_name = target_name

        response = "\n**{slimeoid_name} has won the Slimeoid battle!! The crowd erupts into cheers for {slimeoid_name} and {trainer_name}!!** :tada:".format(
            slimeoid_name = winner_slimeoid_name,
            trainer_name = winner_trainer_name
            )
        
        # The player is given their bounty if it exists and is rewarded slimecoin for killing a slimeoid trainer.
        if winnings != 0 and isinstance(winner, EwUser):
            if pvp_battle:
                response += "\nThey recieve {:,} slime!".format(winnings)
            if not pvp_battle:
                response += "\nThey recieve {:,} slimecoin!".format(winnings)

        # Coating is removed from each slimeoid
        if challengee_slimeoid.coating != '' and pvp_battle:
            response += "\n{}'s coating has been tarnished by battle.".format(challengee_slimeoid.name, challengee_slimeoid.coating)
            challengee_slimeoid.coating = ''
            challengee_slimeoid.persist()
        
        if challenger_slimeoid.coating != '' and pvp_battle:
            response += "\n{}'s coating has been tarnished by battle.".format(challenger_slimeoid.name, challenger_slimeoid.coating)
            challenger_slimeoid.coating = ''
            challenger_slimeoid.persist()
        
        # Kills losing slimeoid if battle is fatal
        if fatal:
            # Figures out the slimeoid to kill
            if winner == challenger:
                dead_slimeoid = challengee_slimeoid
                loser = challengee 
            else:
                dead_slimeoid = challenger_slimeoid
                loser = challenger

            # Dedorn all items
            cosmetics = bknd_item.inventory(
                id_user=loser.id_user,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            # get the cosmetics worn by the slimeoid
            for item in cosmetics:
                cos = EwItem(id_item=item.get('id_item'))
                if cos.item_props.get('slimeoid') == 'true':
                    cos.item_props['slimeoid'] = 'false'
                    cos.id_owner = loser.id_user
                    cos.persist()

            # Turn slimeoid and negaslimeoids into their corresponding type of items
            if dead_slimeoid.sltype == ewcfg.sltype_lab:
                item_props = {
                    'context': ewcfg.context_slimeoidheart,
                    'subcontext': dead_slimeoid.id_slimeoid,
                    'item_name': "Heart of {}".format(dead_slimeoid.name),
                    'item_desc': "A poudrin-like crystal. If you listen carefully you can hear something that sounds like a faint heartbeat."
                }
            else:
                item_props = {
                    'context': ewcfg.context_negaslimeoidheart,
                    'subcontext': dead_slimeoid.id_slimeoid,
                    'item_name': "Core of {}".format(dead_slimeoid.name),
                    'item_desc': "A smooth, inert rock. If you listen carefully you can hear otherworldly whispering."
                }

            bknd_item.item_create(
                id_user=loser.id_user,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
            )

            # RIP :,(             
            dead_slimeoid.die()
            dead_slimeoid.persist()
            loser.active_slimeoid = -1
            loser.persist()

            # RIP flavor text
            response = "\n{} feasts on {}. All that remains is a small chunk of crystallized slime.".format(winner_slimeoid_name, dead_slimeoid.name)
            response += "\n{} is no more. {}".format(dead_slimeoid.name, ewcfg.emote_slimeskull)

        # Sends message!
        await fe_utils.send_message(cmd.client, cmd.message.channel, response)

        # Putting this here because something broke, and... idk!!!! Geez!!!!
        ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
        ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False

        if pvp_battle or not isinstance(winner, EwEnemy):
            # Update the winner's state one last time, then give 'em their winnings!
            challenger = EwUser(member=author)
            if winner.life_state != ewcfg.life_state_corpse and pvp_battle:
                winner.change_slimes(n=winnings)
                winner.persist()
            if winner.life_state != ewcfg.life_state_corpse and not pvp_battle:
                challenger.change_slimecoin(n=winnings, coinsource=ewcfg.coinsource_bounty)
                challenger.persist()

        
        if not pvp_battle and not isinstance(winner, EwEnemy):
            # Fucking delete 'em if they lose!
            response = "{name} is out of useable Slimeoids! {name} blacked out!".format(name=challengee.display_name)
            await fe_utils.send_message(cmd.client, cmd.message.channel, response)
            
            bknd_hunting.delete_enemy(challengee)

    else:
        response = "{} was too cowardly to accept your challenge.".format(member.display_name).replace("@", "\{at\}")

        # Send the response to the player.
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(author, response))

    ewutils.active_slimeoidbattles[challenger_slimeoid_id] = False
    ewutils.active_slimeoidbattles[challengee_slimeoid_id] = False


async def saturateslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)

    if slimeoid.sltype == ewcfg.sltype_nega:
        response = "As much as you may want to, you can't saturate Negaslime."

    elif user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "Wow, great idea! Too bad you don’t even have a slimeoid with which to saturate! You’d think you’d remember really obvious stuff like that, but no. What a dumbass."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif item_sought:
        value = item_search
        hue = hue_static.hue_map.get(value)

        if hue != None:
            if hue.id_hue in [ewcfg.hue_id_copper, ewcfg.hue_id_chrome, ewcfg.hue_id_gold]:
                response = "You saturate your {} with the {} paint! {}".format(slimeoid.name, hue.str_name, hue.str_saturate)
                slimeoid.hue = hue.id_hue
                slimeoid.coating = hue.id_hue
                slimeoid.persist()

                paint_bucket_item = EwItem(id_item=item_sought.get('id_item'))
                if int(paint_bucket_item.item_props.get('durability')) <= 1:
                    bknd_item.item_delete(id_item=item_sought.get('id_item'))
                    response += "\nThe paint bucket is consumed in the process."
                else:
                    await item_utils.lower_durability(item_sought)
                user_data.persist()
            else:
                response = "You saturate your {} with the {} dye! {}".format(slimeoid.name, hue.str_name, hue.str_saturate)
                slimeoid.hue = hue.id_hue
                slimeoid.persist()

                bknd_item.item_delete(id_item=item_sought.get('id_item'))
                user_data.persist()

        else:
            response = "You can only saturate your slimeoid with dyes and paints."

    else:
        if item_search:  # if they didn't forget to specify an item and it just wasn't found
            response = "You can only saturate your slimeoid with dyes and paints."
        else:
            response = "Saturate your slimeoid with what, exactly? (check **!inventory**)"

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def restoreslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)

    slimeoid = EwSlimeoid(member=cmd.message.author)
    item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item_sought = bknd_item.find_item(item_search=item_search, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

    # Check for if you're in the the correct location
    if cmd.message.channel.name != ewcfg.channel_slimeoidlab and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        if user_data.life_state == ewcfg.life_state_corpse:
            response = "You must go to Waffle House to restore a Negaslimeoid."
        else:
            response = "You must go to the NLACU Laboratories in Brawlden to restore a Slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    poi = poi_static.id_to_poi.get(user_data.poi)
    district_data = EwDistrict(district=poi.id_poi, id_server=user_data.id_server)

    # Corresponding lifestate checks for locations - ghosts waffle house, everyone else slimeoidlab. Player is already in one of those two locations, because of the above check
    if user_data.life_state == ewcfg.life_state_corpse and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "Ghosts cannot interact with the NLACU Lab apparati."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif user_data.life_state != ewcfg.life_state_corpse and cmd.message.channel.name != ewcfg.channel_slimeoidlab:
        response = "You feel as though there is some ancient power here, but the slime coursing through your veins prevents you from using it."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # What type the slimeoid is in a string, for flavor text
    if user_data.life_state == ewcfg.life_state_corpse:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"

    # You need a slimeoid
    if slimeoid.life_state != ewcfg.slimeoid_state_none:
        response = "You already have an active slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # If you didn't specify an item
    if item_sought is None:
        if item_search:
            response = "You need a {}'s heart to restore it to life.".format(slimeoidtype)
        else:
            response = "Restore which {}?".format(slimeoidtype)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    item_data = EwItem(id_item=item_sought.get('id_item'))

    # If the item isn't a slimeoid heart or negaslimeoid core
    if item_data.item_props.get('context') != ewcfg.context_slimeoidheart and item_data.item_props.get('context') != ewcfg.context_negaslimeoidheart:
        response = "You need a {} to restore it to life.".format("Slimeoid's heart" if slimeoidtype == "Slimeoid" else "Negaslimeoid's core")
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Ghosts can't revive slimeoids, and alive players can't revive negaslimeoids
    if item_data.item_props.get('context') == ewcfg.context_slimeoidheart and user_data.life_state == ewcfg.life_state_corpse:
        response = "You can't restore Slimeoids to live with the power of the Ancient Ones."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    elif item_data.item_props.get('context') == ewcfg.context_negaslimeoidheart and user_data.life_state != ewcfg.life_state_corpse:
        response = "You can't use the NLACU Lab apparati in order to revive Negaslimeoids."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Get the slimeoid & how much the slimeoid will cost
    slimeoid = EwSlimeoid(id_slimeoid=item_data.item_props.get('subcontext'))
    slimes_to_restore = 2 * 10 ** (slimeoid.level - 2)  # 1/5 of the original cost

    # Check if the player has enough slime/antislime to restore the slimeoid.
    if slimeoidtype == "Slimeoid":
        if user_data.slimes < slimes_to_restore:
            response = "You need at least {} slime to restore this Slimeoid.".format(slimes_to_restore)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        if -user_data.slimes < slimes_to_restore:
            response = "You need at least {} negaslime to restore this Negaslimeoid".format(slimes_to_restore)
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid.life_state = ewcfg.slimeoid_state_active
    slimeoid.id_user = str(user_data.id_user)
    slimeoid.persist()

    bknd_item.item_delete(id_item=item_data.id_item)

    # Change player's slime and give corresponding response
    if user_data.life_state == ewcfg.life_state_corpse:
        response = "You place the core of your beloved {} in front of the Ouija® Board. You place your ghastly appendages on the board. Then, just like when it was first conjured, whispers awake around you and negaslime flows from your body. It coalesces around the inert core and, bit by bit, the formless mass starts to assume a familiar shape.\n\n{} has been restored to its former glory!".format(
        slimeoid.name, slimeoid.name)
        user_data.change_slimes(n=slimes_to_restore, source=ewcfg.source_spending)
    else:
        response = "You insert the heart of your beloved {} into one of the restoration tanks. A series of clattering sensors analyze the crystalline core. Then, just like when it was first incubated, the needle pricks you and extracts slime from your body, which coalesces around the poudrin-like heart. Bit by bit the formless mass starts to assume a familiar shape.\n\n{} has been restored to its former glory!".format(
        slimeoid.name, slimeoid.name)    
        user_data.change_slimes(n=-slimes_to_restore, source=ewcfg.source_spending)

    user_data.persist()

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def bottleslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    if slimeoid.sltype == ewcfg.sltype_nega:
        response = "You don't have hands to bottle your Negaslimeoid, dumbass."

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to bottle."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:
        items = bknd_item.inventory(id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

        bottles = []
        for item in items:
            item_data = EwItem(id_item=item.get('id_item'))
            if item_data.item_props.get('context') == ewcfg.context_slimeoidbottle:
                bottles.append(item_data)

        if len(bottles) >= 2:
            response = "You can't carry any more slimeoid bottles."

        else:
            slimeoid.life_state = ewcfg.slimeoid_state_stored
            slimeoid.id_user = ""

            user_data.active_slimeoid = -1

            slimeoid.persist()
            user_data.persist()

            item_props = {
                'context': ewcfg.context_slimeoidbottle,
                'subcontext': slimeoid.id_slimeoid,
                'item_name': "Bottle containing {}".format(slimeoid.name),
                'item_desc': "A slimeoid bottle."
            }
            bknd_item.item_create(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
            )

            response = "You shove {} into a random bottle. It's a tight squeeze, but in the end you manage to make it fit.".format(slimeoid.name)

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def unbottleslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    response = ""

    if user_data.life_state == ewcfg.life_state_corpse:
        response = "Slimeoids don't fuck with ghosts."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    if cmd.tokens_count < 2:
        response = "Specify which Slimeoid you want to unbottle."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    slimeoid_search = cmd.message.content[len(cmd.tokens[0]):].lower().strip()

    items = bknd_item.inventory(id_user=user_data.id_user, id_server=user_data.id_server, item_type_filter=ewcfg.it_item)

    bottles = []
    for item in items:
        item_data = EwItem(id_item=item.get('id_item'))
        if item_data.item_props.get('context') == ewcfg.context_slimeoidbottle:
            bottles.append(item_data)

    slimeoid = None
    bottle_data = None
    for bottle in bottles:
        slimeoid_data = EwSlimeoid(id_slimeoid=bottle.item_props.get('subcontext'))
        name = slimeoid_data.name.lower()
        if slimeoid_search in name or bottle.id_item == slimeoid_search:
            slimeoid = slimeoid_data
            bottle_data = bottle
            break

    if slimeoid is None:
        response = "You aren't carrying a bottle containing that Slimeoid."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    active_slimeoid = EwSlimeoid(member=cmd.message.author)

    if active_slimeoid.life_state == ewcfg.slimeoid_state_active:

        if ewutils.active_slimeoidbattles.get(active_slimeoid.id_slimeoid):
            response = "You can't do that right now."
            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

        active_slimeoid.life_state = ewcfg.slimeoid_state_stored
        active_slimeoid.id_user = ""

        user_data.active_slimeoid = -1

        active_slimeoid.persist()
        user_data.persist()

        item_props = {
            'context': ewcfg.context_slimeoidbottle,
            'subcontext': active_slimeoid.id_slimeoid,
            'item_name': "Bottle containing {}".format(active_slimeoid.name),
            'item_desc': "A slimeoid bottle."
        }
        bknd_item.item_create(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type=ewcfg.it_item,
            item_props=item_props
        )
        response += "You shove {} into a random bottle. It's a tight squeeze, but in the end you manage to make it fit.\n\n".format(active_slimeoid.name)

    slimeoid.life_state = ewcfg.slimeoid_state_active
    slimeoid.id_user = str(user_data.id_user)

    slimeoid.persist()

    user_data.active_slimeoid = slimeoid.id_slimeoid
    user_data.persist()

    bknd_item.item_delete(id_item=bottle_data.id_item)

    response += "You crack open a fresh bottle of Slimeoid. After a bit of shaking {} sits beside you again, fully formed.".format(slimeoid.name)
    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def feedslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    time_now = int(time.time())
    response = ""

    # Ghosts can't feed slimeoids or negaslimeoids
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    # Slimeoid has to be alive
    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You do not have a Slimeoid to feed."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    # Have to specify 1 item
    elif cmd.tokens_count < 2:
        response = "Specify which item you want to feed to your slimeoid."

    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        item_sought = bknd_item.find_item(item_search=item_search, id_user=user_data.id_user, id_server=user_data.id_server)

        if item_sought:
            item_data = EwItem(id_item=item_sought.get('id_item'))
            # If the item has the context "slimeoidfood", then try to feed the slimeoid.
            if item_data.item_type == ewcfg.it_item and item_data.item_props.get('context') == ewcfg.context_slimeoidfood:
                # "eat", which changes stats. If stats can't be changed, it returns False.
                feed_success = slimeoid.eat(item_data)

                # If eating worked and returned True
                if feed_success:
                    # Persist the stat changes from slimeoid.eat
                    slimeoid.persist()

                    # Delete the candy
                    bknd_item.item_delete(id_item=item_data.id_item)

                    # Flavor text. Unique for each brain and head type.
                    response = "{slimeoid_name} eats the {food_name}."
                    slimeoid_brain = sl_static.brain_map.get(slimeoid.ai)
                    slimeoid_head = sl_static.head_map.get(slimeoid.head)
                    if slimeoid_brain != None and slimeoid_head != None:
                        response = "{} {}".format(slimeoid_brain.str_feed, slimeoid_head.str_feed)

                # If the slimeoid's stats can't be changed.
                else:
                    response = "{slimeoid_name} refuses to eat the {food_name}."

                # Format the response - change "slimeoid_name" and "food_name" to the actual names
                response = response.format(slimeoid_name=slimeoid.name, food_name=item_sought.get('name'))

            # If the item is a food item
            elif item_data.item_type == ewcfg.it_food:

                # Delete the food
                bknd_item.item_delete(id_item=item_data.id_item)

                # Make the slimeoid able to battle again
                slimeoid.time_defeated = slimeoid.time_defeated - 300

                # Flavor text. Unique for each brain and head type.
                response = "{slimeoid_name} eats the {food_name}."
                slimeoid_brain = sl_static.brain_map.get(slimeoid.ai)
                slimeoid_head = sl_static.head_map.get(slimeoid.head)
                if slimeoid_brain != None and slimeoid_head != None:
                    response = "{} {}".format(slimeoid_brain.str_feed, slimeoid_head.str_feed)
                
                # Clout trouts make some gooooooggles kiddo
                if item_data.item_props.get('id_food') == "clouttrout":
                    
                    # Give the player some Clout Goggles
                    bknd_item.item_create(
                        item_type=ewcfg.it_cosmetic,
                        id_user=cmd.message.author.id,
                        id_server=cmd.guild.id,
                        item_props={
                            'id_cosmetic': 'cloutgoggles',
                            'cosmetic_name': 'Clout Goggles',
                            'cosmetic_desc': 'A pair of bulbous ovular sunglasses. They\'re way too tinted, but hot DAMN do these radiate sick shit energy. They maybe even radiate... cloutlets? You can see the hidden Clout in the world with these on!',
                            'str_onadorn': 'You put on the Clout Goggles and feel... lamer. Other than cloutlets, you can\'t see anything with these on!',
                            'str_unadorn': 'You take off the Clout Goggles. You lose 10,000 Instagrime followers nigh-instantaneously. The horror!',
                            'str_onbreak': 'Whaaaa-? Your Clout Goggles **SHATTER!** Cloutlets scatter across the floor, splitting from your naked eyes.',
                            'rarity': ewcfg.rarity_patrician,
                            'attack': 3,
                            'defense': 1,
                            'speed': 1,
                            'ability': 'clout',
                            'durability': 2500000,
                            'size': 2,
                            'fashion_style': ewcfg.style_cool,
                            'freshness': min(slimeoid.clout // 5, 10), # 1/5 of the slimeoid's clout, capped at 10 freshness.
                            'adorned': 'false',
                                    }
                    )

                    # Add on to previous flavor text
                    response += "\nThe clout trout is *soooooooo coooooool*, {slimeoid_name} can't fully digest it! The trout breaks down into Clout Fragments, recombobulates into Clout Scrap, and reforms into Clout Goggles. {slimeoid_name} spits the Clout Goggles out onto the ground in front of you. You just gained some **sick swag sauce!!!**"

                # Persist the time_defeated.
                slimeoid.persist()

                # Format the response - change "slimeoid_name" and "food_name" to the actual names
                response = response.format(slimeoid_name=slimeoid.name, food_name=item_sought.get('name'))

            # If the item is a negapoudrin
            elif item_data.item_props.get("id_item") == ewcfg.item_id_negapoudrin and slimeoid.sltype == ewcfg.sltype_lab:

                # Delete the negapoudrin from the player's inventory
                bknd_item.item_delete(id_item=item_data.id_item)
    
                # Flavor text. Unique for each brain and head type.
                response = "{slimeoid_name} eats the {food_name}."
                slimeoid_brain = sl_static.brain_map.get(slimeoid.ai)
                slimeoid_head = sl_static.head_map.get(slimeoid.head)
                if slimeoid_brain != None and slimeoid_head != None:
                    response = "{} {} \n{slimeoid_name} nigh-instantaneously implodes in on itself, disappearing into nothingness. No heart, no slime, no trace of its existence is left behind. RIP {slimeskull}".format(slimeoid_brain.str_feed, slimeoid_head.str_feed, slimeskull = ewcfg.emote_slimeskull, slimeoid_name=slimeoid.name)
                    # Double formatting so the formatting within the formatting works. Probably a better way to do this :/
                    response = response.format(slimeoid_name=slimeoid.name, food_name=item_sought.get('name'))
                    
                # Erase the slimeoid
                slimeoid.delete()
                user_data.active_slimeoid = -1
                user_data.persist()

            elif item_data.item_props.get("id_item") == ewcfg.item_id_slimepoudrin and slimeoid.sltype == ewcfg.sltype_nega:

                # Delete the poudrin from the player's inventory
                bknd_item.item_delete(id_item=item_data.id_item)
    
                # Flavor text. Unique for each brain and head type.
                response = "{slimeoid_name} eats the {food_name}."
                slimeoid_brain = sl_static.brain_map.get(slimeoid.ai)
                slimeoid_head = sl_static.head_map.get(slimeoid.head)
                if slimeoid_brain != None and slimeoid_head != None:
                    response = "{} {} \n{slimeoid_name} nigh-instantaneously implodes in on itself, disappearing into nothingness. No core, no negaslime, no trace of its existence is left behind. The Ancient Ones are displeased. RIP {slimeskull}".format(slimeoid_brain.str_feed, slimeoid_head.str_feed, slimeskull = ewcfg.emote_slimeskull, slimeoid_name=slimeoid.name)
                    # Double formatting so the formatting within the formatting works. Probably a better way to do this :/
                    response = response.format(slimeoid_name=slimeoid.name, food_name=item_sought.get('name'))
                    
                # Erase the negaslimeoid
                slimeoid.delete()
                user_data.active_slimeoid = -1
                user_data.persist()

            # Not a candy, food item, or negapoudrin/poudrin for slimeoid/negaslimeoid
            else:
                response = "That item is not suitable for slimeoid consumption."

        # No item found
        else:
            response = "You don't have an item like that."

    # Send the response to the player.
    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def dress_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    market_data = EwMarket(id_server=user_data.id_server)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    if slimeoid.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"

    # Ghosts can't dress their living slimeoids
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You'll have to create a Slimeoid if you want to play dress up."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif slimeoid.life_state != ewcfg.slimeoid_state_active:
        response = "You don't have a Slimeoid with you."

    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:

            cosmetics = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            already_adorned = False
            item_from_user = None
            for item in cosmetics:
                if item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name')):
                    cos = EwItem(item.get('id_item'))
                    if item_from_user == None and cos.item_props.get('adorned') == 'true':
                        item_from_user = cos
                        continue

                    if cos.item_props.get('slimeoid') == 'true':
                        already_adorned = True
                    elif cos.item_props.get("context") == 'costume':
                        if ewutils.check_moon_phase(market_data) != ewcfg.moon_full and not ewcfg.dh_active:
                            response = "You can't dress your slimeoid with your costume right now."
                            return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                        else:
                            item_sought = cos
                            break
                    else:
                        item_sought = cos
                        break

            if item_sought == None:
                item_sought = item_from_user

            if item_sought != None:
                # get the cosmetics worn by the slimeoid
                adorned_cosmetics = []
                for item in cosmetics:
                    cos = EwItem(id_item=item.get('id_item'))
                    if cos.item_props.get('slimeoid') == 'true':
                        adorned_cosmetics.append(cos)

                if len(adorned_cosmetics) < slimeoid.level:
                    # Remove hat from player if adorned
                    if item_sought.item_props.get('adorned') == 'true':
                        item_sought.item_props['adorned'] = 'false'

                        response = "You take off your {} and give it to {}.".format(item_sought.item_props.get('cosmetic_name'), slimeoid.name)
                    else:
                        response = "You give {} a {}.".format(slimeoid.name, item_sought.item_props.get('cosmetic_name'))

                    item_sought.item_props['slimeoid'] = 'true'
                    item_sought.id_owner = slimeoid.id_slimeoid
                    item_sought.persist()
                    user_data.persist()
                else:
                    response = 'Your {} is too small to wear any more clothes.'.format(slimeoidtype)
            elif already_adorned:
                response = "Your {} is already wearing it.".format(slimeoidtype)
            else:
                response = 'You don\'t have one.'
        else:
            response = 'Adorn which cosmetic? Check your **!inventory**.'

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def undress_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Ghosts can't undress their living slimeoids.
    if user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype != ewcfg.sltype_nega:
        response = "Slimeoids don't fuck with ghosts."

    elif slimeoid.life_state == ewcfg.slimeoid_state_none:
        response = "You'll have to create a Slimeoid if you want to play dress up."

    elif slimeoid.life_state == ewcfg.slimeoid_state_forming:
        response = "Your Slimeoid is not yet ready. Use !spawnslimeoid to complete incubation."

    elif slimeoid.life_state != ewcfg.slimeoid_state_active:
        response = "You don't have a Slimeoid with you."

    elif ewutils.active_slimeoidbattles.get(slimeoid.id_slimeoid):
        response = "You can't do that right now."

    else:
        item_search = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_search)
        except:
            item_id_int = None

        if item_search != None and len(item_search) > 0:

            cosmetics = bknd_item.inventory(
                id_user=slimeoid.id_slimeoid,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            for item in cosmetics:
                if item.get('id_item') == item_id_int or item_search in ewutils.flattenTokenListToString(item.get('name')):
                    cos = EwItem(item.get('id_item'))
                    if cos.item_props.get('slimeoid') == 'true':
                        item_sought = cos
                        break

            if item_sought != None:

                response = "You take the {} back from {}".format(item_sought.item_props.get('cosmetic_name'), slimeoid.name)
                item_sought.item_props['slimeoid'] = 'false'
                item_sought.id_owner = user_data.id_user

                item_sought.persist()
            else:
                response = 'They don\'t have one.'
        else:
            response = 'Dedorn which cosmetic? Check your **!slimeoidinventory**.'

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def tagslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)
    outofspace = False
    
    # Lifestate check as well as establishing slimeoidtype
    if user_data.life_state != ewcfg.life_state_corpse:
        slimeoidtype = "Slimeoid"
    elif user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        response = "Slimeoids don't fuck with ghosts."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # Gotta have a response
    if cmd.tokens_count == 1:
        response = "Hmm? Tag your {}? Uh, spraying your slimeoid with paint sounds like abuse, and that's a different command. Specify something to put on your dog tag.".format(slimeoidtype)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    # If the player doesn't have a dog tag, they can't tag their slimeoid.
    dogtag = bknd_item.find_item(item_search='dogtag', id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_cosmetic)
    if dogtag is None:
        response = "You can't tag your {} without a dog tag. Idiot.".format(slimeoidtype)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))        

    # If the player somehow is trying to tag with a different item, they can't tag their slimeoid.
    dogtagitem = EwItem(id_item=dogtag.get('id_item'))
    if dogtagitem.item_props.get('id_cosmetic') != "dogtag":
        response = "You can't tag your {} with... whatever this is. Idiot.".format(slimeoidtype)
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))        

    # Turn the rest of the message into the dog tag message.
    message_text = ' '.join(word for word in cmd.tokens[1:])

    if len(message_text) > 1000:
        outofspace = True
        message_text = message_text[:1000]

    # Delete dog tag
    bknd_item.item_delete(id_item=dogtag.get('id_item'))
    
    # Give the slimeoid the tag
    slimeoid.dogtag = message_text
    slimeoid.persist()

    response = "You attach the dog tag to {} the {}. The tag slowly sinks into its gelatinous body.\n\n{}".format(slimeoid.name, slimeoidtype, message_text)
    if outofspace is True:
        response += "\nYou run out of space on the dog tag. You really went ham on that little tag, huh?"

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def untagslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid = EwSlimeoid(member=cmd.message.author)

    # Lifestate check as well as establishing slimeoidtype
    if user_data.life_state != ewcfg.life_state_corpse:
        slimeoidtype = "Slimeoid"
    elif user_data.life_state == ewcfg.life_state_corpse and slimeoid.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        response = "Slimeoids don't fuck with ghosts."
        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    
    # Slimeoid has to have a tag
    if slimeoid.dogtag == "":
        response = "Your {} is already free of any tags.".format(slimeoidtype)
    else:
        # Erase the tag
        slimeoid.dogtag = ""
        slimeoid.persist()
        response = "You reach into your {} and rip out the dog tag within it.".format(slimeoidtype)

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
