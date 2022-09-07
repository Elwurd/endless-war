# Import cfg constants
from ew.static import cfg as ewcfg
from ew.static import slimeoid as sl_static

# Import util function
from ew.utils.frontend import send_response
from ew.cmd.slimeoid.slimeoidutils import get_slimeoid_count
from ew.utils import slimeoid as slimeoid_utils
from ew.backend import item as bknd_item
from ew.utils import core as ewutils

# Import classes
from ew.utils.combat import EwUser
from ew.utils.slimeoid import EwSlimeoid
from ew.backend.item import EwItem

# Print lab instructions
async def instructions(cmd):

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "There's no instructions to read here."
        return await send_response(response, cmd)  

    elif cmd.message.channel.name == ewcfg.channel_slimeoidlab:
        response = "Welcome to NLACU's Brawlden Laboratory Facilities."

        response += "\n\nThis facility specializes in the emerging technology of Slimeoids, or slime-based artificial lifeforms. Research into the properties of Slimeoids is ongoing, but already great advancements in the field have been made and we are proud to continue providing public access to Slimeoid creation."

        # Explain incubation
        response += "\n\nThis laboratory is equipped with everything required for the creation of a Slimeoid from scratch. To create a Slimeoid, you will need to supply one (1) Slime Poudrin, which will serve as the locus around which your Slimeoid will be based. You will also need to supply some Slime. You may supply as much or as little slime as you like, but greater Slime contribution will lead to superior Slimeoid genesis. To begin the Slimeoid creation process, use **!incubateslimeoid** followed by the amount of slime you wish to use."


        # Explain grow body commands
        response += "\n\nAfter beginning incubation, you will need to use the console to adjust your Slimeoid's features while it is still forming. Use **!growbody**, **!growhead**, **!growlegs**, **!growweapon**, **!growarmor**, **!growspecial**, or **!growbrain** followed by a letter (A - G) to choose the appearance, abilities, and temperament of your Slimeoid. You will also need to give youe Slimeoid a name. Use **!nameslimeoid** followed by your desired name. These traits may be changed at any time before the incubation is completed."

        # Explain add stat commands
        response += "\n\nIn addition to physical features, you will need to allocate your Slimeoid's attributes. Your Slimeoid will have a different amount of potential depending on how much slime you invested in its creation. You must distribute this potential across the three Slimeoid attributes, Moxie, Grit, and Chutzpah. Use **!raisemoxie**, **!lowermoxie**, **!raisegrit**, **!lowergrit**, **!raisechutzpah**, and **!lowerchutzpah** to adjust your Slimeoid's attributes to your liking."
        
        # Send half of instructions here becasuse this is a lot of text
        await send_response(response, cmd)
        

        # Spawn slimeoid and explain one active slimeoid limit 
        response = "\n\nWhen all of your Slimeoid's traits are confirmed, use **!spawnslimeoid** to end the incubation and eject your Slimeoid from the gestation vat. Be aware that once spawned, the Slimeoid's traits are not easy to change, so be sure you are happy with your Slimeoid's construction before spawning. Additionally, be aware that you may only have Slimeoid roaming free at a time, meaning should you ever want to make a new Slimeoid, you will need to **!bottleslimeoid** or euthanise your old one with **!dissolveslimeoid**."

        # Commands that can be done with your slimeoid
        response += "\n\nYou can read a full description of your or someone else's Slimeoid with the **!slimeoid** command. It will react to your actions, including when you kill an opponent, when you are killed, when you return from the dead, and when you !howl. If you want to give your Slimeoid some identifying information, get a dog tag and **!tagslimeoid**. Alternatively, **!untagslimeoid** to re-obscure its identity. In addition, you can also perform activities with your Slimeoid. Try **!observeslimeoid**, **!petslimeoid**, **!walkslimeoid**, and **!playfetch** and see what happens."

        # Pls report bugs
        response += "\n\nSlimeoid research is ongoing, and the effects of a Slimeoid's physical makeup, brain structure, and attribute allocation on its abilities are a rapidly advancing field. Please report any unusual findings or behaviors to a NLACU lab technician."

        # Send the response to the player.
        return await send_response(response, cmd, format_name = False)

    else:
        # Shoutouts to Hasbro
        response = "There's a scribbled-over sheet of paper on the table next to the suspiciously-placed Ouija® Board."

        # Introduce sheet of paper idea.
        response += "\n\n**The Ouija® Board**\nThe Ouija® Board (pronounced WEE-JA) has always been mysterious and mystifying. Ask it a question and it will respond by spelling out your answer in the window of the Message Indicator (Planchette)."

        # Explain Conjuration
        response += "\n\n**Assembly**\nRemove the 3 glide feet from the runner. Discard ~~the▬r~~▓**▓1 NEGAPOUDRIN. !CONJURENEGASLIMEOID AND GIVE NEGASLIME.**"


        # Explain grow body commands
        response += "\n\n**How Do I Make It Work?**\nAt night, leave the Board and the Planchet~~te▬si~~▓**▓SPELL** ***!GROWBODY/HEAD/LEGS/WEAPON/ARMOR/SPECIAL/BRAIN*** **AND A/B/C/D/E/F/G.** ***!NAMENEGASLIMEOID*** **TOO.**"

        # Explain add stat commands
        response += "\n\n**Set-Up**\nIf desired, set the mood by dimm~~ing▬~~▓**▓SPELL** ***!RAISEMOXIE/GRIT/CHUTZPAH*** **OR** ***!LOWERMOXIE/GRIT/CHUTZPAH*** **FOR STATS.**"
        
        # Send half of instructions here because this is a lot of text
        await send_response(response, cmd)
        

        # Spawn negaslimeoid and explain that reviving will kill it 
        response = "\n\n**Set-Up** (cont.)\nSet the Ouija® Board either on the players' la~~ps▬or▬~~▓**▓TO FINISH** ***!SPAWNNEGASLIMEOID.*** **REVIVAL WILL KILL.**"

        # Explains to do !destroyslimeoid if you have a living slimeoid.
        response += "\n\n**What Do I Do Now?**\nPlayers take turns asking questions and all s~~houl~~▓**▓IF THE ANCIENT ONES ARE DISPLEASED** ***!DESTROYSLIMEOID.*** **DEFEAT SLIMEOIDS. WIN.**"

        # Ouija Board catchphrase
        response += "\n\n*Look Into The Future. Have Fun! And Remember. The Ouija® Board is just a game...                      or is it?*"

        # Send the response to the player.
        return await send_response(response, cmd, format_name = False)


"""
    Initialize incubation process
"""
async def incubate_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    if cmd.message.channel.name != ewcfg.channel_slimeoidlab:
        response = "You must go to the NLACU Laboratories in Brawlden to create a Slimeoid."
        # Go to final response

    elif user_data.life_state == ewcfg.life_state_corpse:
        response = "Ghosts cannot interact with the NLACU Lab apparati."
        # Go to final response

    #TODO: change this because player can have more than one slimeoid now
    # this is fucking brutal. poor slimeoid
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_active:
        response = "You have already created a Slimeoid. Bottle or dissolve your current slimeoid before incubating a new one."
        # Go to final response

    elif slimeoid_data.life_state == ewcfg.slimeoid_state_forming:
        response = "You are already in the process of incubating a Slimeoid."
        # Go to final response


    else:
        
        #Check if player has too many slimeoids
        slimeoid_count = get_slimeoid_count(user_id=cmd.message.author.id, server_id=cmd.guild.id)
        
        if slimeoid_count >= 3:
            response = "You have too many slimeoids."
            # Go to final response


        else:
            #Check if player has a poudrin
            poudrin = bknd_item.find_item(item_search=ewcfg.item_id_slimepoudrin, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)
            if poudrin is None:
                response = "You need a slime poudrin."
                # Go to final response
    

            else:
                # Get arguement for how big the slimeoid should be made
                injected_slime = None
                if cmd.tokens_count > 1:
                    injected_slime = ewutils.getIntToken(tokens=cmd.tokens, allow_all=True)
                    # -1 from getIntToken() means use all slime
                    if injected_slime == -1:
                        injected_slime = user_data.slimes

                if injected_slime == None:
                    response = "You must contribute some of your own slime to create a Slimeoid. Specify how much slime you will sacrifice."
                    # Go to final response

                elif injected_slime > user_data.slimes:
                    response = "You do not have that much slime to sacrifice."
                    # Go to final response

                else:
                    # delete a slime poudrin from the player's inventory
                    bknd_item.item_delete(id_item=poudrin.get('id_item'))

                    # Remove slime
                    user_data.change_slimes(n=-injected_slime)

                    # Setup gestating slimeoid
                    level = len(str(injected_slime))
                    slimeoid_data.life_state = ewcfg.slimeoid_state_forming
                    slimeoid_data.level = level
                    slimeoid_data.id_user = str(user_data.id_user)
                    slimeoid_data.id_server = user_data.id_server

                    # Save changes
                    slimeoid_data.persist()
                    user_data.persist()

                    response = "You place a poudrin into a small opening on the console. As you do, a needle shoots up and pricks your finger, intravenously extracting {injected_slime:,} slime from your body. The poudrin is then dropped into the gestation tank. Looking through the observation window, you see what was once your slime begin to seep into the tank and accrete around the poudrin. The incubation of a new Slimeoid has begun! {slime_emote}".format(
                        injected_slime = injected_slime, 
                        slime_emote = ewcfg.emote_slime2
                    )
                    # Go to final response



    # Final response
    await send_response(response, cmd)

# Just use a different command for incubating Negaslimeoids
async def incubate_negaslimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    # Check for if the player is a corpse
    if user_data.life_state != ewcfg.life_state_corpse:
        if cmd.message.channel.name == ewcfg.channel_wafflehouse:
            response = "You feel as though there is some ancient power here, but the slime coursing through your veins prevents you from using it."
        else:
            response = "Huh? What'd you say?"

    # Check for if the player is at Waffle House
    elif cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "You can't exactly summon anything in {}. Go to Waffle House first.".format(cmd.message.channel.name)

    # Check if the player already has a Slimeoid or a Negaslimeoid.
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_active:
        if slimeoid_data.sltype == ewcfg.sltype_nega:
            response = "You already have a Negaslimeoid by your side. Destroy your current Negaslimeoid before you commune with the Ancient Ones yet again."
        else:
            response = "You wish to summon a Negaslimeoid, yet you have a Slimeoid that still calls you its master. !destroyslimeoid if you wish to commune with the Ancient Ones properly."

    # Check if the player is already incubating a Slimeoid or Negaslimeoid
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_forming:
        if slimeoid_data.sltype == ewcfg.sltype_nega:
            response = "You are already in the process of conjuring a Negaslimeoid."
        else:
            response = "You wish to summon a Negaslimeoid, yet you have a Slimeoid that is still yet to call you its master. !destroyslimeoid if you wish to commune with the Ancient Ones properly."


    else:
        
        #Check if player has too many slimeoids
        slimeoid_count = get_slimeoid_count(user_id=cmd.message.author.id, server_id=cmd.guild.id)
        
        if slimeoid_count >= 3:
            response = "You have too many slimeoids."
            # Go to final response


        else:
            #Check if player has a negapoudrin
            negapoudrin = bknd_item.find_item(item_search=ewcfg.item_id_negapoudrin, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)
            if negapoudrin is None:
                response = "You need a negapoudrin to bind a Negaslimeoid to your command."
                # Go to final response
    

            else:
                # Get argument for how big the negaslimeoid should be made
                sacrificed_negaslime = None
                if cmd.tokens_count > 1:
                    # -1 from getIntToken() could possibly be gotten from player input, so do a check here.
                    if cmd.tokens[1] == "all":
                        if user_data.slimes < 0:
                            sacrificed_negaslime = -user_data.slimes
                        
                    else:
                        sacrificed_negaslime = ewutils.getIntToken(tokens=cmd.tokens) 
                        if sacrificed_negaslime < 0:
                                sacrificed_negaslime = -sacrificed_negaslime

                # Check if player sacrificed any negaslime or if they have enough to sacrifice.
                if sacrificed_negaslime == None:
                    response = "You must sacrifice your own negaslime to conjure a Negaslimeoid. Specify how much negaslime you will sacrifice."
                    # Go to final response

                elif -sacrificed_negaslime < user_data.slimes:
                    response = "You do not have that much negaslime to sacrifice."
                    # Go to final response

                else:
                    # delete a negapoudrin from the player's inventory
                    bknd_item.item_delete(id_item=negapoudrin.get('id_item'))

                    # Remove negaslime
                    user_data.change_slimes(n=+sacrificed_negaslime)

                    # Establish these stats for conjuring the negaslimeoid
                    level = len(str(sacrificed_negaslime))
                    slimeoid_data.life_state = ewcfg.slimeoid_state_forming
                    slimeoid_data.level = level
                    slimeoid_data.sltype = ewcfg.sltype_nega
                    slimeoid_data.hue = ewcfg.hue_id_negative
                    slimeoid_data.id_user = str(user_data.id_user)
                    slimeoid_data.id_server = user_data.id_server
                    
                    # Save changes
                    slimeoid_data.persist()
                    user_data.persist()

                    response = "Floating in front of the Ouija® Board, you place both of your ghastly appendages on the planchette. {sacrificed_negaslime:,} negaslime rises from your body, flowing towards your negapoudrin. The negapoudrin appears to lift into the air, held up by a pool of rising negaslime. Whispers awake around you, indiscernible and unknowable. It feels as though the planchette beneath your ghastly fingers has more than one set of hands on it. \n\nThe conjuration of a Negaslimeoid has begun! {negaslime_emote}".format(
                        sacrificed_negaslime = sacrificed_negaslime, 
                        negaslime_emote = ewcfg.emote_negaslime
                    )
                    # Go to final response



    # Final response
    await send_response(response, cmd)

"""
    Handle all part changes of slimeoid during incubation process
"""
async def change_body_part(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    # Checks whether slimeoid is a Negaslimeoid or not. For flavor text.
    if slimeoid_data.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"    

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if response is None: # Slimeoid is incubating

        button_pressed = None

        # If player does not provide an argument for the button they pressed# Interperate which part player is trying to grow by command name

        cmd_to_change_type = {
            ewcfg.cmd_growbody: ("body", sl_static.body_map),
            ewcfg.cmd_growhead: ("head", sl_static.head_map),
            ewcfg.cmd_growlegs: ("leg", sl_static.mobility_map),
            ewcfg.cmd_growweapon: ("weapon", sl_static.offense_map),
            ewcfg.cmd_growarmor: ("armor", sl_static.defense_map),
            ewcfg.cmd_growspecial: ("special", sl_static.special_map),
            ewcfg.cmd_growbrain: ("brain", sl_static.brain_map),
        }

        # Gets part_map based on command used
        desired_change, part_map = cmd_to_change_type.get(cmd.tokens[0].lower())

        if cmd.tokens_count == 1:
            if slimeoidtype == "Slimeoid":
                response = f"You must specify a {desired_change} type. Choose an option from the buttons on the body console labelled A through G."
            else:
                response = f"You must specify a {desired_change} type. Choose an option with your planchette, from A through G."
            # Go to final response

        else:
            
            
            pressed_button = cmd.tokens[1].lower()

            # If it's a negaslimeoid and the desired part is a brain, change letter to the corresponding Negaslimeoid brain.
            if  desired_change == "brain" and slimeoidtype == "Negaslimeoid":
                    
                # This is done to keep abcdefg parity with between !growbrain and the other grow commands with negaslimeoids.
                cmd_abcdefg_to_hijklmn = {
                    "a": ("h"),
                    "b": ("i"),
                    "c": ("j"),
                    "d": ("k"),
                    "e": ("l"),
                    "f": ("m"),
                    "g": ("n"),
                }

                pressed_button = cmd_abcdefg_to_hijklmn.get(pressed_button)

            # Check if desired part is in part map 
            part = part_map.get(pressed_button)

            # If no part is found
            if part == None:
                if slimeoidtype == "Slimeoid":
                    response = "Choose an option from the buttons on the body console labelled A through G."
                else:
                    response = "Choose an option with your planchette, from A through G."
                # Go to final response

            
            else: 

                #TODO: this could be simplified if slimeoid part id variables to one name
                # e.g. EwSlimeoidBody.id_body and EwSlimeoidBody.id_head were called EwSlimeoidBody.part_id and EwSlimeoidBody.part_id instead
                if desired_change == "body":
                    slimeoid_data.body = part.id_body

                elif desired_change == "head":
                    slimeoid_data.head = part.id_head

                elif desired_change == "leg":
                    slimeoid_data.legs = part.id_mobility

                elif desired_change == "weapon":
                    slimeoid_data.weapon = part.id_offense

                elif desired_change == "armor":
                    slimeoid_data.armor = part.id_defense

                elif desired_change == "special":
                    slimeoid_data.special = part.id_special

                elif desired_change == "brain":
                    slimeoid_data.ai = part.id_brain

                else:
                    response = f"Some thing when wrong with {cmd.tokens[0]} command. Please report bug." # something when wrong in cmd_to_change_type
                    return await send_response(response, cmd)
                    # Break out of command early because of error

                
                slimeoid_data.persist()
                response = "{}".format(part.str_create_nega if (user_data.life_state == ewcfg.life_state_corpse and desired_change != "brain") else part.str_create)
                # Go to final response


    # Final response
    await send_response(response, cmd)
                

"""
    Handle all raise and lower stat commands during slimeoid incubation
"""
async def change_stat(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    # Check for slimeoid's type, for flavor text purposes.
    if slimeoid_data.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"
    
    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if response is None: # Slimeoid is incubating

        # Interperate which stat player is trying to change by command name

        cmd_to_change_type = {
            ewcfg.cmd_raisemoxie: "+ moxie",
            ewcfg.cmd_raisegrit: "+ grit",
            ewcfg.cmd_raisechutzpah: "+ chutzpah",
            ewcfg.cmd_lowermoxie: "- moxie",
            ewcfg.cmd_lowergrit: "- grit",
            ewcfg.cmd_lowerchutzpah: "- chutzpah",
        }
        desired_change = cmd_to_change_type.get(cmd.tokens[0].lower())

        moxie_mod = 0
        grit_mod = 0
        chutzpah_mod = 0
        
        # Plus one stat
        if desired_change == "+ moxie":
            moxie_mod = 1
            changed_stat = "moxie"

        elif desired_change == "+ grit":
            grit_mod = 1
            changed_stat = "grit"

        elif desired_change == "+ chutzpah":
            chutzpah_mod = 1
            changed_stat = "chutzpah"

        # Minus one stat
        elif desired_change == "- moxie":
            moxie_mod = -1
            changed_stat = "moxie"

        elif desired_change == "- grit":
            grit_mod = -1
            changed_stat = "grit"

        elif desired_change == "- chutzpah":
            chutzpah_mod = -1
            changed_stat = "chutzpah"

        else:
            response = f"Some thing when wrong with {cmd.tokens[0]} command. Please report bug." # something when wrong in cmd_to_change_type
            return await send_response(response, cmd)
            # Break out of command early because of error


        # Now that we no what stat is trying to be changed do the final checks


        available_points = slimeoid_data.level - (slimeoid_data.atk + moxie_mod) - (slimeoid_data.defense + grit_mod) - (slimeoid_data.intel + chutzpah_mod)

        # Check if stat points are available
        if (available_points < 0):
            response = f"You have allocated all of your {slimeoidtype}'s potential. Try !lowering some of its attributes first."
            response += stat_breakdown_str(slimeoid_data.atk, slimeoid_data.defense, slimeoid_data.intel, available_points + 1)
            # Go to final response

        # Check if player is trying to lower a stat below zero
        elif ((slimeoid_data.atk + moxie_mod < 0) or (slimeoid_data.defense + grit_mod < 0) or (slimeoid_data.intel + chutzpah_mod < 0)):
            response = f"You cannot reduce your {slimeoidtype}'s {changed_stat} any further."
            response += stat_breakdown_str(slimeoid_data.atk, slimeoid_data.defense, slimeoid_data.intel, available_points - 1)
            
        elif (available_points >= slimeoid_data.level):
            response = f"You cannot reduce your {slimeoidtype}'s {changed_stat} any further."
            response += stat_breakdown_str(slimeoid_data.atk, slimeoid_data.defense, slimeoid_data.intel, available_points - 1)
            # Go to final response


        # Command successful
        else:
            
            # Change slimeoid stats
            slimeoid_data.atk += moxie_mod 
            slimeoid_data.defense += grit_mod 
            slimeoid_data.intel += chutzpah_mod
            # Save changes
            slimeoid_data.persist()

            # Generate response
            if (moxie_mod + grit_mod + chutzpah_mod > 0):
                response = f"Your gestating {slimeoidtype} gains more {changed_stat}."
            else:
                response = f"Your gestating {slimeoidtype} loses some {changed_stat}."
            response += stat_breakdown_str(slimeoid_data.atk, slimeoid_data.defense, slimeoid_data.intel, available_points)
            # Go to final response



    # Final response
    await send_response(response, cmd)


"""
    Name slimeoid during incubation process
"""
async def name_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)
    command_used = ""

    # Check if player is in the labs and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response

    # Lifestate check for flavor text
    if slimeoid_data.sltype == ewcfg.sltype_nega:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"

    if response is None: # Slimeoid is incubating

        # Check if player has specified a name
        if cmd.tokens_count < 2:
            response = "You must specify a name."
            # Go to final response

        else:

            # Turn entire message minus "!nameslimeoid" in to name variable
            command_used = ewutils.flattenTokenListToString(cmd.tokens[0])
            name = cmd.message.content[(len(command_used) + len(ewcfg.cmd_prefix)):].strip()

            # Limit name length to 32 characters
            if len(name) > 32:
                response = "That name is too long. ({:,}/32)".format(len(name))
                # Go to final response

            else:
                # Save slimeoid name
                slimeoid_data.name = str(name)

                user_data.persist()
                slimeoid_data.persist()

                if slimeoidtype == "Slimeoid":
                    response = "You enter the name {} into the console.".format(str(name))
                else:
                    response = "You move the planchette between letters, spelling out the name {}.".format(str(name))
                # Go to final response


    # Final response
    await send_response(response, cmd)


"""
    Check if all parts have been added and complete the incubation processs
"""
async def spawn_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    # Check if player is in the appropriate POI and has a slimeoid incubating
    response = basic_slimeoid_incubation_checks(channel_name = cmd.message.channel.name, user_data = user_data, slimeoid_data = slimeoid_data)
    # If response returns None go to final response


    if response is None: # Slimeoid is incubating

            incomplete = False
            required_parts_explanation = ""

            # Check for flavor text purposes
            if slimeoid_data.sltype == ewcfg.sltype_nega:
                slimeoidtype = "Negaslimeoid"
            else:
                slimeoidtype = "Slimeoid"

            # Check if parts are missing 
            # Bold missing part names for visual clarity
            if (slimeoid_data.body == ""):
                incomplete = True
                required_parts_explanation += "\nIts **BODY** has not yet been given a distinct form."

            if (slimeoid_data.head == ""):
                incomplete = True
                required_parts_explanation += "\nIt does not yet have a **HEAD**."

            if (slimeoid_data.legs == ""):
                incomplete = True
                required_parts_explanation += "\nIt has no **LEGS** or means of locomotion."

            if (slimeoid_data.weapon == ""):
                incomplete = True
                required_parts_explanation += "\nIt lacks a means of **WEAPON**."

            if (slimeoid_data.armor == ""):
                incomplete = True
                required_parts_explanation += "\nIt lacks any form of **ARMOR**."

            if (slimeoid_data.special == ""):
                incomplete = True
                required_parts_explanation += "\nIt lacks a **SPECIAL** ability."

            if (slimeoid_data.ai == ""):
                incomplete = True
                required_parts_explanation += "\nIt does not yet have a **BRAIN**."

            if ((slimeoid_data.atk + slimeoid_data.defense + slimeoid_data.intel) < (slimeoid_data.level)):
                incomplete = True
                required_parts_explanation += "\nIt still has potential that must be distributed between **MOXIE**, **GRIT** and **CHUTZPAH**."

            if (slimeoid_data.name == ""):
                incomplete = True
                required_parts_explanation += "\nIt needs a **NAME**."

            if incomplete:
                # Add explanation of which parts need to be added
                if slimeoidtype == "Slimeoid":
                    response = f"Your Slimeoid is not yet ready to be spawned from the gestation vat. {required_parts_explanation}"
                else:
                    response = f"Your Negaslimeoid is not yet fully conjured by the Ancient Ones. {required_parts_explanation}"
                # Go to final response

            
            else: 
                # Set slimeoid as active
                slimeoid_data.life_state = ewcfg.slimeoid_state_active
                # Save slimeoid
                slimeoid_data.persist()

                # Generate spawning flavor text
                if slimeoidtype == "Slimeoid":
                    response = "You press the big red button labelled 'SPAWN'. The console lights up and there is a rush of mechanical noise as the fluid drains rapidly out of the gestation tube. The newly born Slimeoid within writhes in confusion before being sucked down an ejection chute and spat out messily onto the laboratory floor at your feet. Happy birthday, {slimeoid_name} the Slimeoid!! {slime_heart_emote}".format(
                        slimeoid_name = slimeoid_data.name, 
                        slime_heart_emote = ewcfg.emote_slimeheart
                    )
                else:
                    response = "You move the Ouija® planchette to 'GOOD BYE'. The whispering around you explodes into a roaring chorus, nearly deafening your ghost ears. The pile of negaslime in front of you, now resembling a Negaslimeoid, ambles towards you. With a blood-curdling screech, the chorus around you dies. Your unholy abomination {slimeoid_name} the Negaslimeoid has been conjured!! {negaslime_emote}".format(
                        slimeoid_name = slimeoid_data.name, 
                        negaslime_emote = ewcfg.emote_negaslime
                    )


                # Add slimeoid description
                response += "\n\n{} is a {}-foot-tall {}.".format(slimeoid_data.name, str(slimeoid_data.level), slimeoidtype)
                response += slimeoid_utils.slimeoid_describe(slimeoid_data)


                # Add slimeoid's reaction based on brain type
                brain = sl_static.brain_map.get(slimeoid_data.ai)
                response += "\n\n" + brain.str_spawn.format(
                    slimeoid_name=slimeoid_data.name
                )
                # Go to final response


    # Final response
    await send_response(response, cmd)

async def destroy_slimeoid(cmd):
    user_data = EwUser(member=cmd.message.author)
    slimeoid_data = EwSlimeoid(member=cmd.message.author)

    # Check of the player is alive
    if user_data.life_state != ewcfg.life_state_corpse:
        response = "You... want to destroy your Slimeoid? That's, like, sorta illegal."

    # Check if the player isn't at Waffle House as a ghost
    elif user_data.life_state == ewcfg.life_state_corpse and cmd.message.channel.name != ewcfg.channel_wafflehouse:
        response = "Slimeoids don't fuck with ghosts."

    # Check if the player has a slimeoid
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_none:
        response = "Good news! You don't have a Slimeoid. So no need to destroy one."

    # If all of those don't work
    else:
        # Creates each type-specific heart. Also turns the slimeoid's type into a string, for flavor text purposes.
        if slimeoid_data.sltype == ewcfg.sltype_lab:
            # Creates string "Slimeoid"
            slimeoid_type = "Slimeoid"

            # Forming slimeoids DON'T drop hearts
            if slimeoid_data.life_state != ewcfg.slimeoid_state_forming:
                # Creates the item props for the slimeoid heart
                item_props = {
                'context': ewcfg.context_slimeoidheart,
                'subcontext': slimeoid_data.id_slimeoid,
                'item_name': "Heart of {}".format(slimeoid_data.name),
                'item_desc': "A poudrin-like crystal. If you listen carefully you can hear something that sounds like a faint heartbeat."
                }
                # Creates the item in downtown
                bknd_item.item_create(
                id_user=ewcfg.channel_downtown,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
                )
        else:
            # Creates string "Negaslimeoid"
            slimeoid_type = "Negaslimeoid"

            # Forming negaslimeoids DON'T drop cores
            if slimeoid_data.life_state != ewcfg.slimeoid_state_forming:
                # Creates the item props for the negaslimeoid core
                item_props = {
                'context': ewcfg.context_negaslimeoidheart,
                'subcontext': slimeoid_data.id_slimeoid,
                'item_name': "Core of {}".format(slimeoid_data.name),
                'item_desc': "A smooth, inert rock. If you listen carefully you can hear otherworldly whispering."
                }
                # Creates the item at Waffle House
                bknd_item.item_create(
                id_user=ewcfg.channel_wafflehouse,
                id_server=cmd.guild.id,
                item_type=ewcfg.it_item,
                item_props=item_props
                )
        
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
        
        # Craft the response
        response = "You think upon your past and spiritually connect with {} the {}. With the Ouija® Board in front of you, you spell out the forbidden words: \n\n\"lol\" \"lmao\" \n\nYour former companion is rended across space and time. All that remains is their {}, though unobtainable by you. {}".format(slimeoid_data.name, slimeoid_type, "heart" if slimeoid_type == "Slimeoid" else "core", ewcfg.emote_slimeskull)
        
        # Kill the slimeoid and persist
        slimeoid_data.die()
        slimeoid_data.persist()
        user_data.active_slimeoid = -1

        # Take some of the player's negaslime for destroying a slimeoid.
        if user_data.slimes < 0:
            user_data.slimes -= user_data.slimes / 10
            user_data.persist()
        
        # Go to final response

    # Final response
    await send_response(response, cmd)

###
# Utilities
###

""" 
    Does some of the basic checks all slimeoid growing commands do
    Returns response string if there is a reason the player can't do the command
"""
def basic_slimeoid_incubation_checks(channel_name, user_data, slimeoid_data):

    # Establish if the desired slimeoid is a Negaslimeoid or not. Use life_state instead of slimeoid_data as the player could possibly have no slimeoid.
    if user_data.life_state == ewcfg.life_state_corpse:
        slimeoidtype = "Negaslimeoid"
    else:
        slimeoidtype = "Slimeoid"

    # Check for if player is in the Slimeoid Labs or Waffle House
    if channel_name != ewcfg.channel_slimeoidlab and channel_name != ewcfg.channel_wafflehouse: 
        if slimeoidtype == "Slimeoid":
            return "You must go to the NLACU Laboratories in Brawlden to create a Slimeoid."
        else:
            return "You must go to Waffle House in order to conjure a Negaslimeoid."

    # checks for correct lifestate in corresponding locations
    elif channel_name == ewcfg.channel_wafflehouse and slimeoidtype == "Slimeoid":
        return "You feel as though there is some ancient power here, but the slime coursing through your veins prevents you from using it."
    elif channel_name == ewcfg.channel_slimeoidlab and slimeoidtype == "Negaslimeoid":
        return "Ghosts cannot interact with the NLACU Lab apparati."

    # Check for incubating slimeoid
    # TODO: other checks for slimeoid lifestates?
    elif slimeoid_data.life_state == ewcfg.slimeoid_state_none:
        if slimeoidtype == "Slimeoid":
            return "You must begin incubating a new Slimeoid first."
        else:
            return "You must begin conjuring a Negaslimeoid first."

    elif slimeoid_data.life_state == ewcfg.slimeoid_state_active:
        if slimeoidtype == "Slimeoid":
            return "Your Slimeoid is already fully formed."
        else:
            return "Your Negaslimeoid has already been conjured."

    else:
        return None

def stat_breakdown_str(moxie, grit, chuzpah, available_points = None):
    response = f"\nMoxie: {moxie}"
    response += f"\nGrit: {grit}"
    response += f"\nChutzpah: {chuzpah}"
    
    #optional line if you just want to print the stats alone
    if available_points != None:
        response += f"\nPoints remaining: {available_points}"

    return response
    
