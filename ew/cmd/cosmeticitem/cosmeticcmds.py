import asyncio
import time
import random

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.static import cfg as ewcfg
from ew.static import cosmetics
from ew.static import hue as hue_static
from ew.static import items as static_items
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwUser
try:
    from ew.static.rstatic import debugsmoke
    from ew.cmd.debugr import debug22
except:
    from ew.static.rstatic_dummy import debugsmoke

async def smoke(cmd):
    usermodel = EwUser(member=cmd.message.author)
    # item_sought = bknd_item.find_item(item_search="cigarette", id_user=cmd.message.author.id, id_server=usermodel.id_server)
    item_sought = None
    space_adorned = 0

    item_seek = ewutils.flattenTokenListToString(cmd.tokens[1:])
    item = bknd_item.find_item(item_search=item_seek, id_user=cmd.message.author.id, id_server=cmd.guild.id)
    if item:
        if item.get('name') == debugsmoke:
            return await debug22(cmd=cmd)

    item_stash = bknd_item.inventory(id_user=cmd.message.author.id, id_server=usermodel.id_server)
    for item_piece in item_stash:
        item = EwItem(id_item=item_piece.get('id_item'))
        if item.item_props.get('adorned') == 'true':
            space_adorned += int(item.item_props.get('size'))

        if item_piece.get('item_type') == ewcfg.it_cosmetic and (item.item_props.get('id_cosmetic') == "cigarette" or item.item_props.get('id_cosmetic') == "cigar") and "lit" not in item.item_props.get('cosmetic_desc'):
            item_sought = item_piece

    if item_sought:
        item = EwItem(id_item=item_sought.get('id_item'))
        if item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigarette":
            if int(item.item_props.get('size')) > 0:
                space_adorned += int(item.item_props.get('size'))

            usermodel.change_crime(n=ewcfg.cr_underage_smoking_points)
            response = "You light a cig and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
            item.item_props['cosmetic_desc'] = "A single lit cigarette sticking out of your mouth. You huff these things down in seconds but you’re never seen without one. Everyone thinks you’re really, really cool."
            if space_adorned < ewutils.max_adornspace_bylevel(usermodel.slimelevel):
                item.item_props['adorned'] = "true"
            item.persist()
            usermodel.persist()

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            await asyncio.sleep(60)
            item = EwItem(id_item=item_sought.get('id_item'))

            response = "The cigarette fizzled out."

            item.item_props['cosmetic_desc'] = "It's a cigarette butt. What kind of hoarder holds on to these?"
            item.item_props['adorned'] = "false"
            item.item_props['id_cosmetic'] = "cigarettebutt"
            item.item_props['cosmetic_name'] = "cigarette butt"
            item.persist()



        elif item_sought.get('item_type') == ewcfg.it_cosmetic and item.item_props.get('id_cosmetic') == "cigar":
            if int(item.item_props['size']) > 0:
                space_adorned += int(item.item_props['size'])

            usermodel.change_crime(n=ewcfg.cr_underage_smoking_points)
            response = "You light up your stogie and bring it to your mouth. So relaxing. So *cool*. All those naysayers and PSAs in Health class can go fuck themselves."
            item.item_props['cosmetic_desc'] = "A single lit cigar sticking out of your mouth. These thing take their time to kick in, but it's all worth it to look like a supreme gentleman."
            if space_adorned < ewutils.max_adornspace_bylevel(usermodel.slimelevel):
                item.item_props['adorned'] = "true"

            item.persist()

            usermodel.persist()

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            await asyncio.sleep(300)
            item = EwItem(id_item=item_sought.get('id_item'))

            response = "The cigar fizzled out."

            item.item_props['cosmetic_desc'] = "It's a cigar stump. It's seen better days."
            item.item_props['adorned'] = "false"
            item.item_props['id_cosmetic'] = "cigarstump"
            item.item_props['cosmetic_name'] = "cigar stump"
            item.persist()


        else:
            response = "You can't smoke that."
    else:   
        response = "There aren't any usable cigarettes or cigars in your inventory."
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def vape(cmd):
    user_data = EwUser(member=cmd.message.author)
    vape_sought = None
    pod_sought = None

    # If the player specified a pod type, get that pod
    search = ewutils.flattenTokenListToString(cmd.tokens[1:])
    pod_seek = bknd_item.find_item(item_search=search, id_user=cmd.message.author.id, id_server=cmd.guild.id)
    if pod_seek:
        item = EwItem(id_item=pod_seek.get('id_item'))
        if item.item_props.get('context') == "vapepod":
            pod_sought = item

    # Find a vape and a pod
    inventory = bknd_item.inventory(id_user=cmd.message.author.id, id_server=user_data.id_server)
    for inv_item in inventory:
        # If there's no vape found, check if the item is a vape.
        if inv_item.get('item_type') == ewcfg.it_cosmetic and vape_sought == None:
            item = EwItem(id_item=inv_item.get('id_item'))
            if item.item_props.get('id_cosmetic') == "vape":
                vape_sought = item

        # If there's no pod found, check if the item is a pod.
        elif inv_item.get('item_type') == ewcfg.it_item and pod_sought == None:
            item = EwItem(id_item=inv_item.get('id_item'))
            if item.item_props.get('context') == "vapepod":
                pod_sought = item

    # If there was a vape
    if vape_sought:
        # If there was a pod
        if pod_sought:
            # Give the user some crime and a response
            user_data.change_crime(n=ewcfg.cr_underage_smoking_points)
            response = "You flick out your vape and bring it to your mouth. The {} feels so relaxing. So *hip* (and with the times). All those adults who told you to stop smoking clearly don't know how fun vaping is.".format(pod_sought.item_props.get('item_name'))
            user_data.persist()
        
            # Delete vape pod
            bknd_item.item_delete(pod_sought.id_item)
    
            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
            await asyncio.sleep(9)

            # Have them vaaaaaaaaaaaaape
            vapes = 0
            while vapes < 11:
                if random.randint(1, 10) == 1:
                    response = "You do a slick trick with an epic vape cloud. Sheeeeeeeesh..."
                else:
                    response = "You take a puff of the vape."

                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
                await asyncio.sleep(28)
                vapes += random.randint(1, 5)

            # Create a spent vape pod
            bknd_item.item_create(
            item_type=ewcfg.it_item,
            id_user=user_data.id_user,
            id_server=cmd.guild.id,
            item_props={
                'id_item': ewcfg.item_id_spent_pod,
                'item_name': 'Spent Vape Pod',
                'item_desc': 'A spent vape pod. Junk.',
                'context': 'spentpod',
            })
            
            # Final message
            response = "Your vape ran out of juice. Better get a new pod."

        else:
            response = "You don't have any usable pods in your inventory."
    else:
        response = "You don't have a vape in your inventory, dink."
    # Send message
    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def adorn(cmd):
    user_data = EwUser(member=cmd.message.author)
    market_data = EwMarket(id_server=user_data.id_server)

    # Check to see if you even have the item you want to repair
    item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

    try:
        item_id_int = int(item_id)
    except:
        item_id_int = None

    if item_id is not None and len(item_id) > 0:
        response = "You don't have one."

        cosmetic_items = bknd_item.inventory(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type_filter=ewcfg.it_cosmetic
        )
        item_sought = None
        item_from_slimeoid = None
        already_adorned = False
        space_adorned = 0

        for item in cosmetic_items:
            i = EwItem(item.get('id_item'))
            # Get space used adorned cosmetics
            if i.item_props['adorned'] == 'true':
                space_adorned += int(i.item_props['size'])

        # Check all cosmetics found
        for item in cosmetic_items:
            i = EwItem(item.get('id_item'))

            # Search for desired cosmetic
            if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):

                if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
                    item_from_slimeoid = i
                    continue
                if i.item_props.get("adorned") == 'true':
                    already_adorned = True
                elif i.item_props.get("context") == 'costume' and not ewcfg.dh_active:
                    if not ewcfg.dh_active and ewutils.check_moon_phase(market_data) != ewcfg.moon_full:
                        response = "You can't adorn your costume right now."
                else:
                    item_sought = i
                    break

        if item_sought == None:
            item_sought = item_from_slimeoid

        # If the cosmetic you want to adorn is found
        if item_sought != None:

            # Calculate how much space you'll have after adorning...
            if int(item_sought.item_props['size']) > 0:
                space_adorned += int(item_sought.item_props['size'])

            # If you don't have enough space, abort
            if space_adorned > ewutils.max_adornspace_bylevel(user_data.slimelevel):
                response = "Oh yeah? And, pray tell, just how do you expect to do that? You’re out of space, you can’t adorn any more garments!"

            # If you have enough space, adorn
            else:
                item_sought.item_props['adorned'] = 'true'
                ability = item_sought.item_props['ability']

                # Take the hat from your slimeoid if necessary
                if item_sought.item_props.get('slimeoid') == 'true':
                    item_sought.item_props['slimeoid'] = 'false'
                    response = "You take your {} from your slimeoid and successfully adorn it.".format(item_sought.item_props.get('cosmetic_name'))
                else:
                    onadorn_response = item_sought.item_props['str_onadorn']
                    response = onadorn_response.format(item_sought.item_props['cosmetic_name'])

                # Cosmetics with these abilities will turn you into a furry
                if ability in ['nmsmascot', 'furry', 'moonlighter']:
                    user_data.race = ewcfg.race_furry
                    time_now = int(time.time())
                    user_data.time_racialability = time_now + ewcfg.cd_change_race
                    # Only certain will get extra flavor text
                    if ability in ['moonlighter', 'furry']:
                        response += " ...You feel yourself becoming... furpilled?"

                item_sought.persist()
                user_data.persist()

        elif already_adorned:
            response = "You already have that garment adorned!"

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))


async def dedorn(cmd):
    user_data = EwUser(member=cmd.message.author)
    # ewutils.moves_active[cmd.message.author.id] = 0

    # Check to see if you even have the item you want to repair
    item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

    try:
        item_id_int = int(item_id)
    except:
        item_id_int = None

    if item_id is not None and len(item_id) > 0:
        response = "You don't have one."

        cosmetic_items = bknd_item.inventory(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
            item_type_filter=ewcfg.it_cosmetic
        )

        item_sought = None
        already_adorned = False

        # Check all cosmetics found
        for item in cosmetic_items:
            i = EwItem(item.get('id_item'))

            # Search for desired cosmetic
            if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
                if i.item_props.get("adorned") == 'true':
                    already_adorned = True
                    item_sought = i
                    break

        # If the cosmetic you want to adorn is found
        if item_sought != None:

            # Unadorn the cosmetic
            if already_adorned:
                item_sought.item_props['adorned'] = 'false'

                unadorn_response = str(item_sought.item_props['str_unadorn'])

                response = unadorn_response.format(item_sought.item_props['cosmetic_name'])

                item_sought.persist()
                user_data.persist()

            # That garment has not be adorned..
            else:
                response = "You haven't adorned that garment in the first place! How can you dedorn something you haven't adorned? You disgust me."

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))


async def sew(cmd):
    user_data = EwUser(member=cmd.message.author)

    # Player must be at the Bodega
    if user_data.poi == ewcfg.poi_id_bodega:
        item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_id)
        except:
            item_id_int = None

        # Check to see if you even have the item you want to repair
        if item_id != None and len(item_id) > 0:
            response = "You don't have one."

            cosmetic_items = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            item_from_slimeoid = None

            for item in cosmetic_items:
                if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
                    i = EwItem(item.get('id_item'))

                    if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
                        item_from_slimeoid = i
                        continue
                    else:
                        item_sought = i
                        break

            if item_sought == None:
                item_sought = item_from_slimeoid

            # If the cosmetic you want to have repaired is found
            if item_sought != None:
                # Can't repair items without durability limits, since they couldn't have been damaged in the first place
                if item_sought.item_props['durability'] is None:
                    response = "I'm sorry, but I can't repair that piece of clothing!"

                else:
                    if item_sought.item_props['id_cosmetic'] == 'soul':
                        original_durability = ewcfg.soul_durability

                    elif item_sought.item_props['id_cosmetic'] == 'scalp':
                        if 'original_durability' not in item_sought.item_props.keys():  # If it's a scalp created before this update
                            original_durability = ewcfg.generic_scalp_durability
                        else:
                            original_durability = int(float(item_sought.item_props['original_durability']))  # If it's a scalp created after

                    else:  # Find the mold of the item in cosmetics.cosmetic_items_list
                        if item_sought.item_props.get('rarity') == ewcfg.rarity_princeps:
                            original_durability = ewcfg.base_durability * 100
                            original_item = None  # Princeps do not have existing templates
                        else:
                            try:
                                original_item = cosmetics.cosmetic_map.get(item_sought.item_props['id_cosmetic'])
                                original_durability = original_item.durability
                            except:
                                original_durability = ewcfg.base_durability

                    current_durability = int(float(item_sought.item_props['durability']))

                    # If the cosmetic is actually damaged at all
                    if current_durability < original_durability:
                        difference = abs(current_durability - original_durability)

                        # cost_ofrepair = difference * 4 # NO ONE SAID IT WOULD BE EASY
                        cost_ofrepair = 10000  # I did...

                        if cost_ofrepair > user_data.slimes:
                            response = 'The hipster behind the counter narrows his gaze, his thick-rimmed glasses magnify his hatred of your ignoble ancestry.\n"Sir… it would cost {:,} to sew this garment back together. That’s more slime than you or your clan could ever accrue. Good day, sir. I SAID GOOD DAY. Come back when you’re a little, mmmmhh, *richer*."'.format(cost_ofrepair)
                        else:
                            response = '"Let’s see, all told… including tax… plus gratuity… and a hefty tip, of course… your total comes out to {}, sir."'.format(cost_ofrepair)
                            response += "\n**!accept** or **!refuse** the deal."

                            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                            # Wait for an answer
                            accepted = False

                            try:
                                message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                                 message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                                if message != None:
                                    if message.content.lower() == ewcfg.cmd_accept:
                                        accepted = True
                                    if message.content.lower() == ewcfg.cmd_refuse:
                                        accepted = False
                            except:
                                accepted = False

                            # Cancel deal if the hat is no longer in user's inventory
                            if item_sought.id_owner != str(user_data.id_user):
                                accepted = False

                            # Cancel deal if the user has left Krak Bay
                            if user_data.poi != ewcfg.poi_id_bodega:
                                accepted = False

                            # Candel deal if the user doesn't have enough slime anymore
                            if cost_ofrepair > user_data.slimes:
                                accepted = False

                            if accepted == True:
                                user_data.change_slimes(n=-cost_ofrepair, source=ewcfg.source_spending)
                                user_data.persist()

                                item_sought.item_props['durability'] = original_durability
                                item_sought.persist()

                                response = '"Excellent. Just a moment… one more stitch and-- there, perfect! Your {}, sir. It’s good as new, no? Well, no refunds in any case."'.format(item_sought.item_props['cosmetic_name'])

                            else:
                                response = '"Oh, yes, of course. I understand, sir. No, really that’s okay. I get it. I totally get it. That’s your decision. Really, it’s okay. No problem here. Yep. Yup. Uh-huh, uh-huh. Yep. It’s fine, sir. That’s completely fine. For real. Seriously. I understand, sir. It’s okay. I totally get it. Yep. Uh-huh. Yes, sir. Really, it’s okay. Some people just don’t care how they look. I understand, sir."'
                    else:
                        response = 'The hipster behind the counter looks over your {} with the thoroughness that a true man would only spend making sure all the blood really was wrung from his most recent hunt’s neck or all the cum was ejactulated from his partner’s throbbing cock…\n"Sir," he begins to say, turning back to you before almost vomiting at the sight. After he regains his composure, he continues, "I understand you are an, shall we say, uneducated peasant, to put it delicately, but even still you should be able to tell that your {} is in mint condition. Please, do not bother me with such wastes of my boss’ time again. I do enough of that on my own."'.format(
                            item_sought.item_props['cosmetic_name'], item_sought.item_props['cosmetic_name'])
        else:
            response = "Sew which cosmetic? Check your **!inventory**."
    else:
        response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally fucking lame, everyone knows that! Even people who sew know that! You’re gonna have to find some nerd to do it for you."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def retrofit(cmd):
    user_data = EwUser(member=cmd.message.author)

    # Player must be at the Bodega
    if user_data.poi == ewcfg.poi_id_bodega:
        item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

        try:
            item_id_int = int(item_id)
        except:
            item_id_int = None

        # Check to see if you even have the item you want to retrofit
        if item_id != None and len(item_id) > 0:
            response = "You don't have one."

            cosmetic_items = bknd_item.inventory(
                id_user=cmd.message.author.id,
                id_server=cmd.guild.id,
                item_type_filter=ewcfg.it_cosmetic
            )

            item_sought = None
            item_from_slimeoid = None

            for item in cosmetic_items:
                if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
                    i = EwItem(item.get('id_item'))

                    if item_from_slimeoid == None and i.item_props.get("slimeoid") == 'true':
                        item_from_slimeoid = i
                        continue
                    else:
                        item_sought = i
                        break

            if item_sought == None:
                item_sought = item_from_slimeoid

            # If the cosmetic you want to have repaired is found
            if item_sought != None:
                if item_sought.item_props.get('id_cosmetic') == 'soul' or item_sought.item_props.get('id_cosmetic') == 'scalp':
                    response = 'The hipster behind the counter is taken aback by your total lack of self awareness. "By Doctor Who!" He exclaims. "This is a place where fine clothing is sold, sir. Not a common circus freak show for ill-bred worms to feed upon the suffering of others, where surely someone of your morally bankrupt description must surely have originated! That or the whore house, oh my Rainbow Dash..." He begins to tear up. "Just… go. Take your {} and go. Do come back if you want it sewn back together, though."'.format(
                        item_sought.item_props['cosmetic_name'])
                else:
                    current_item_stats = {}
                    # Get the current stats of your cosmetic
                    for stat in ewcfg.playerstats_list:
                        if stat in item_sought.item_props.keys():
                            if abs(int(item_sought.item_props[stat])) > 0:
                                current_item_stats[stat] = int(item_sought.item_props[stat])

                    if 'ability' in item_sought.item_props.keys():
                        current_item_stats['ability'] = item_sought.item_props['ability']

                    # Get the stats retrofitting would give you from the item model in cosmetics.cosmetic_items_list
                    desired_item = cosmetics.cosmetic_map.get(item_sought.item_props['id_cosmetic'])

                    if desired_item == None:
                        response = "The hipster behind the counter doesn't really know what to do with that cosmetic, it's simply too outdated and worn out. He thinks you should just take it home and stuff it inside a box as a souvenir."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    desired_item_stats = {}

                    for stat in ewcfg.playerstats_list:
                        if stat in desired_item.stats.keys():
                            if abs(int(desired_item.stats[stat])) > 0:
                                desired_item_stats[stat] = desired_item.stats[stat]

                    if desired_item.ability is not None:
                        desired_item_stats['ability'] = desired_item.ability

                    # Check to see if the cosmetic is actually outdated
                    if current_item_stats != desired_item_stats:
                        cost_ofretrofit = 100  # This is a completely random number that I arbitrarily pulled out of my ass

                        if cost_ofretrofit > user_data.slimes:
                            response = 'The hipster behind the counter narrows his gaze, his thick-rimmed glasses magnify his hatred of your ignoble ancestry.\n"Sir… it would cost {:,} to retrofit this garment with updated combat abilities. That’s more slime than you or your clan could ever accrue. Good day, sir. I SAID GOOD DAY. Come back when you’re a little, mmmmhh, *richer*."'.format(
                                cost_ofretrofit)
                        else:
                            response = '"Let’s see, all told… including tax… plus gratuity… and a hefty tip, of course… your total comes out to {}, sir."'.format(cost_ofretrofit)
                            response += "\n**!accept** or **!refuse** the deal."

                            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                            # Wait for an answer
                            accepted = False

                            try:
                                message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                                 message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                                if message != None:
                                    if message.content.lower() == ewcfg.cmd_accept:
                                        accepted = True
                                    if message.content.lower() == ewcfg.cmd_refuse:
                                        accepted = False
                            except:
                                accepted = False

                            # Cancel deal if the hat is no longer in user's inventory
                            if item_sought.id_owner != str(user_data.id_user):
                                accepted = False

                            # Cancel deal if the user has left Krak Bay
                            if user_data.poi != ewcfg.poi_id_bodega:
                                accepted = False

                            # Candel deal if the user doesn't have enough slime anymore
                            if cost_ofretrofit > user_data.slimes:
                                accepted = False

                            if accepted == True:
                                for stat in ewcfg.playerstats_list:
                                    if stat in desired_item_stats.keys():
                                        item_sought.item_props[stat] = desired_item_stats[stat]

                                item_sought.persist()

                                user_data.slimes -= cost_ofretrofit

                                user_data.persist()

                                response = '"Excellent. Just a moment… one more iron press and-- there, perfect! Your {}, sir. It’s like you just smelted it, no? Well, no refunds in any case."'.format(item_sought.item_props['cosmetic_name'])

                            else:
                                response = '"Oh, yes, of course. I understand, sir. No, really that’s okay. I get it. I totally get it. That’s your decision. Really, it’s okay. No problem here. Yep. Yup. Uh-huh, uh-huh. Yep. It’s fine, sir. That’s completely fine. For real. Seriously. I understand, sir. It’s okay. I totally get it. Yep. Uh-huh. Yes, sir. Really, it’s okay. Some people just don’t care how they look. I understand, sir."'
                    else:
                        response = 'The hipster behind the counter looks over your {} with the thoroughness that a true man would only spend making sure all the blood really was wrung from his most recent hunt’s neck or all the cum was ejactulated from his partner’s throbbing cock…\n"Sir," he begins to say, turning back to you before almost vomiting at the sight. After he regains his composure, he continues, "I understand you are an, shall we say, uneducated peasant, to put it delicately, but even still you should be able to tell that your {} is already completely up-to-date. Please, do not bother me with such wastes of my boss’ time again. I do enough of that on my own."'.format(
                            item_sought.item_props['cosmetic_name'], item_sought.item_props['cosmetic_name'])
        else:
            response = "Sew which cosmetic? Check your **!inventory**."
    else:
        response = "Heh, yeah right. What kind of self-respecting juvenile delinquent knows how to sew? Sewing totally lame, everyone knows that! Even people who sew know that! Looks like you’re gonna have to find some nerd to do it for you."

    return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def dye(cmd):
    hat_id = ewutils.flattenTokenListToString(cmd.tokens[1:2])
    dye_id = ewutils.flattenTokenListToString(cmd.tokens[2:])

    try:
        hat_id_int = int(hat_id)
    except:
        hat_id_int = None

    try:
        dye_id_int = int(dye_id)
    except:
        dye_id_int = None

    if hat_id != None and len(hat_id) > 0 and dye_id != None and len(dye_id) > 0:
        response = "You don't have one."

        items = bknd_item.inventory(
            id_user=cmd.message.author.id,
            id_server=cmd.guild.id,
        )

        cosmetic = None
        dye = None
        for item in items:

            if int(item.get('id_item')) == hat_id_int or hat_id in ewutils.flattenTokenListToString(item.get('name')):
                if item.get('item_type') == ewcfg.it_cosmetic and cosmetic is None:
                    cosmetic = item

            if int(item.get('id_item')) == dye_id_int or dye_id in ewutils.flattenTokenListToString(item.get('name')):
                if item.get('item_type') == ewcfg.it_item and item.get('name') in static_items.dye_map and dye is None:
                    dye = item

            if cosmetic != None and dye != None:
                break

        if cosmetic != None:
            if dye != None:
                cosmetic_item = EwItem(id_item=cosmetic.get("id_item"))
                dye_item = EwItem(id_item=dye.get("id_item"))

                hue = hue_static.hue_map.get(dye_item.item_props.get('id_item'))

                response = "You dye your {} in {} paint!".format(cosmetic_item.item_props.get('cosmetic_name'), hue.str_name)
                cosmetic_item.item_props['hue'] = hue.id_hue

                cosmetic_item.persist()
                bknd_item.item_delete(id_item=dye.get('id_item'))
            else:
                response = 'Use which dye? Check your **!inventory**.'
        else:
            response = 'Dye which cosmetic? Check your **!inventory**.'

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
    else:
        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, 'You need to specify which cosmetic you want to paint and which dye you want to use! Check your **!inventory**.'))


"""
	Load new values into these and reboot to balance cosmetics.
"""


async def balance_cosmetics(cmd):
    author = cmd.message.author

    if not author.guild_permissions.administrator:
        return

    if cmd.tokens_count == 2:
        id_cosmetic = cmd.tokens[1]

        try:
            # Pull info from the cache if items are being cached
            item_cache = bknd_core.get_cache(obj_type = "EwItem")
            if item_cache is not False:
                # find all cosmetics for the target server
                server_cosmetic_data = item_cache.find_entries(criteria={"id_server": cmd.guild.id, "item_type": ewcfg.it_cosmetic})

                # format the results the same way the sql query would
                data = list(map(lambda dat: [
                    dat.get("id_item"),
                    dat.get("item_type"),
                    dat.get("soulbound"),
                    dat.get("stack_max"),
                    dat.get("stack_size")
                ], server_cosmetic_data))
                if len(data) == 0:
                    data = None

            else:
                data = bknd_core.execute_sql_query(
                    "SELECT {id_item}, {item_type}, {col_soulbound}, {col_stack_max}, {col_stack_size} FROM items WHERE {id_server} = {server_id} AND {item_type} = '{type_item}'".format(
                        id_item=ewcfg.col_id_item,
                        item_type=ewcfg.col_item_type,
                        col_soulbound=ewcfg.col_soulbound,
                        col_stack_max=ewcfg.col_stack_max,
                        col_stack_size=ewcfg.col_stack_size,
                        id_server=ewcfg.col_id_server,

                        server_id=cmd.guild.id,
                        type_item=ewcfg.it_cosmetic
                    ))

            if data != None:
                for row in data:
                    id_item = row[0]

                    item_data = EwItem(id_item=id_item)
                    item_type = ewcfg.it_cosmetic
                    item_data.item_type = item_type
                    if id_cosmetic == "soul":
                        if item_data.item_props['id_cosmetic'] == 'soul':
                            item_data.item_props = {
                                'id_cosmetic': item_data.item_props['id_cosmetic'],
                                'cosmetic_name': item_data.item_props['cosmetic_name'],
                                'cosmetic_desc': item_data.item_props['cosmetic_desc'],
                                'str_onadorn': ewcfg.str_soul_onadorn,
                                'str_unadorn': ewcfg.str_soul_unadorn,
                                'str_onbreak': ewcfg.str_soul_onbreak,
                                'rarity': ewcfg.rarity_patrician,
                                'attack': 6,
                                'defense': 6,
                                'speed': 6,
                                'ability': None,
                                'durability': ewcfg.soul_durability,
                                'size': 1,
                                'fashion_style': ewcfg.style_cool,
                                'freshness': 10,
                                'adorned': 'false',
                                'user_id': item_data.item_props['user_id']
                            }
                    elif id_cosmetic == "scalp":
                        if item_data.item_props['id_cosmetic'] == 'scalp':
                            item_data.item_props = {
                                'id_cosmetic': item_data.item_props['id_cosmetic'],
                                'cosmetic_name': item_data.item_props['cosmetic_name'],
                                'cosmetic_desc': item_data.item_props['cosmetic_desc'],
                                'str_onadorn': ewcfg.str_generic_onadorn,
                                'str_unadorn': ewcfg.str_generic_unadorn,
                                'str_onbreak': ewcfg.str_generic_onbreak,
                                'rarity': ewcfg.rarity_plebeian,
                                'attack': 0,
                                'defense': 0,
                                'speed': 0,
                                'ability': None,
                                'durability': ewcfg.generic_scalp_durability,
                                'size': 16,
                                'fashion_style': ewcfg.style_cool,
                                'freshness': 0,
                                'adorned': 'false',
                            }
                    elif id_cosmetic == "costume":
                        if item_data.item_props.get('context') == 'costume':
                            item_data.item_props = {
                                'id_cosmetic': 'dhcostume',
                                'cosmetic_name': item_data.item_props['cosmetic_name'],
                                'cosmetic_desc': item_data.item_props['cosmetic_desc'],
                                'str_onadorn': ewcfg.str_generic_onadorn,
                                'str_unadorn': ewcfg.str_generic_unadorn,
                                'str_onbreak': ewcfg.str_generic_onbreak,
                                'rarity': ewcfg.rarity_plebeian,
                                'attack': 1,
                                'defense': 1,
                                'speed': 1,
                                'ability': None,
                                'durability': ewcfg.base_durability * 100,
                                'size': 1,
                                'fashion_style': ewcfg.style_cute,
                                'freshness': 0,
                                'adorned': 'false',
                            }
                    elif id_cosmetic == 'cigarettebutt':
                        if item_data.item_props.get('id_cosmetic') == 'cigarettebutt':
                            item_data.item_props = {
                                'id_cosmetic': 'cigarettebutt',
                                'cosmetic_name': item_data.item_props['cosmetic_name'],
                                'cosmetic_desc': item_data.item_props['cosmetic_desc'],
                                'str_onadorn': ewcfg.str_generic_onadorn,
                                'str_unadorn': ewcfg.str_generic_unadorn,
                                'str_onbreak': ewcfg.str_generic_onbreak,
                                'rarity': ewcfg.rarity_plebeian,
                                'attack': 2,
                                'defense': 0,
                                'speed': 0,
                                'ability': None,
                                'durability': ewcfg.base_durability / 2,
                                'size': 1,
                                'fashion_style': ewcfg.style_cool,
                                'freshness': 5,
                                'adorned': 'false',
                            }
                    else:
                        if item_data.item_props.get('id_cosmetic') == id_cosmetic:
                            item = cosmetics.cosmetic_map.get(item_data.item_props['id_cosmetic'])
                            item_data.item_props = {
                                'id_cosmetic': item.id_cosmetic,
                                'cosmetic_name': item.str_name,
                                'cosmetic_desc': item.str_desc,
                                'str_onadorn': item.str_onadorn if item.str_onadorn else ewcfg.str_generic_onadorn,
                                'str_unadorn': item.str_unadorn if item.str_unadorn else ewcfg.str_generic_unadorn,
                                'str_onbreak': item.str_onbreak if item.str_onbreak else ewcfg.str_generic_onbreak,
                                'rarity': item.rarity if item.rarity else ewcfg.rarity_plebeian,
                                'attack': item.stats[ewcfg.stat_attack] if ewcfg.stat_attack in item.stats.keys() else 0,
                                'defense': item.stats[ewcfg.stat_defense] if ewcfg.stat_defense in item.stats.keys() else 0,
                                'speed': item.stats[ewcfg.stat_speed] if ewcfg.stat_speed in item.stats.keys() else 0,
                                'ability': item.ability if item.ability else None,
                                'durability': item.durability if item.durability else ewcfg.base_durability,
                                'size': item.size if item.size else 1,
                                'fashion_style': item.style if item.style else ewcfg.style_cool,
                                'freshness': item.freshness if item.freshness else 0,
                                'adorned': 'false',
                            }

                    item_data.persist()

                    ewutils.logMsg('Balanced cosmetic: {}'.format(id_item))

        except KeyError as k:
            ewutils.logMsg("Key error: " + str(k))
            return await fe_utils.send_response("Failure.", cmd)

        except Exception as e:
            ewutils.logMsg(e)
            return await fe_utils.send_response("Failure.", cmd)

    return await fe_utils.send_response("Success!", cmd)
