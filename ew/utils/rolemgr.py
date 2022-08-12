import time

import discord

from . import core as ewutils
from . import frontend as fe_utils
from ..backend.user import EwUserBase as EwUser
from ew.backend.dungeons import EwGamestate
from ..static import cfg as ewcfg
from ..static import poi as poi_static

"""
	Find relevant roles and save them to the database.
"""

roles_map = {}
id_to_roles_map = {}


def setupRoles(client=None, id_server=-1):
    global roles_map
    global id_to_roles_map
    roles_map[id_server] = ewutils.getRoleMap(client.get_guild(id_server).roles)
    id_to_roles_map[id_server] = ewutils.getRoleIdMap(client.get_guild(id_server).roles)



async def updateRoles(client, member, server_default=None, refresh_perms=True, new_poi=None):
    """	Fix the Discord roles assigned to this member. """
    time_now = int(time.time())

    roles_add = set()
    replacement_roles = set()

    if server_default is not None:
        user_data = EwUser(id_user=member.id, id_server=server_default)
    else:
        user_data = EwUser(member=member)

    id_server = user_data.id_server


    roles_map_user = ewutils.getRoleMap(member.roles)


    user_poi = poi_static.id_to_poi.get(user_data.poi)
    if new_poi is not None:
        user_poi = poi_static.id_to_poi.get(new_poi)

    mother_poi = None
    if len(user_poi.mother_districts) != 0:
        mother_poi = poi_static.id_to_poi.get(user_poi.mother_districts[0])

    if user_data.life_state != ewcfg.life_state_kingpin and ewcfg.role_kingpin in roles_map_user:
        # Fix the life_state of kingpins, if somehow it wasn't set.
        user_data.life_state = ewcfg.life_state_kingpin
        user_data.persist()

    elif user_data.life_state != ewcfg.life_state_grandfoe and ewcfg.role_grandfoe in roles_map_user:
        # Fix the life_state of a grand foe.
        user_data.life_state = ewcfg.life_state_grandfoe
        user_data.persist()

    elif user_data.life_state == ewcfg.life_state_kingpin and ewcfg.role_kingpin not in roles_map_user:
        # Fix the life_state for low-life gangstars
        if user_data.faction:
            user_data.life_state = ewcfg.life_state_enlisted
        else:
            user_data.life_state = ewcfg.life_state_juvenile
        user_data.persist()

    # Manage faction roles.
    faction_role = ewutils.get_faction(user_data=user_data)

    if ewcfg.dh_stage == 4 and ewcfg.dh_active:
        faction_role = ewcfg.role_juvenile

    roles_add.add(faction_role)

    lastwarp = ewutils.last_warps.get(user_data.id_user)
    lastwarp = 0 if lastwarp is None else lastwarp + 19  # add 19 secs to the last time someone started a teleport to check pvp flagging
    #  If faction has an associated PVP role
    if faction_role in ewcfg.role_to_pvp_role:

        # If the POI the user is in is PVP or not
        if user_poi.pvp or not (user_poi.is_apartment or not (mother_poi and mother_poi.pvp)) or lastwarp > time_now:
            pvp_role = ewcfg.role_to_pvp_role.get(faction_role)
            roles_add.add(pvp_role)


    if user_poi.id_poi in poi_static.tutorial_pois:
        roles_add.add(ewcfg.role_tutorial)

    if user_data.has_gellphone():
        roles_add.add(ewcfg.role_gellphone)

    currentkingpin = EwGamestate(id_server=id_server, id_state='slimernaliakingpin').value
    if currentkingpin == str(user_data.id_user):

        roles_add.add(ewcfg.role_slimernalia)

    roles_remove = set()
    roles_remove.update(ewcfg.faction_roles)
    roles_remove.update(ewcfg.misc_roles)
    roles_remove = roles_remove - roles_add

    # Refunds non-critical roles
    for role_id in roles_map_user:
        role_data = roles_map[id_server].get(role_id)
        if role_data and role_id not in roles_remove and role_id not in roles_add:
            replacement_roles.add(role_data)

    # Adds critical roles
    for role in roles_add:
        role_data = roles_map[id_server].get(role)
        if role_data:
            replacement_roles.add(role_data)
        else:
            ewutils.logMsg("Failed to find role for {role}.".format(role = role))

    try:
        await member.edit(roles=replacement_roles)
    except Exception as e:
        ewutils.logMsg('error: failed to replace roles for {}:{}'.format(member.display_name, str(e)))

    if refresh_perms:

        await refresh_user_perms(client, id_server, member, new_poi=new_poi)


# Removes and updates user permissions. It's got a fair amount of debuggers, sorry about the mess!
async def refresh_user_perms(client, id_server, used_member, new_poi=None):
    server = client.get_guild(id_server)

    user_data = EwUser(member=used_member)
    if new_poi is not None:
        user_poi_obj = poi_static.id_to_poi.get(new_poi)
    else:
        user_poi_obj = poi_static.id_to_poi.get(user_data.poi)

    if not user_poi_obj:
        user_poi_obj = poi_static.id_to_poi.get(ewcfg.poi_id_downtown)


    # Part 1: Remove overrides the user shouldn't have
    for poi in poi_static.poi_list:
        channel = fe_utils.get_channel(server, poi.channel)
        if channel is None:
            continue

        if used_member in channel.overwrites and user_poi_obj.id_poi != poi.id_poi:
            # Incorrect overwrite found for user

            try:
                for chname in poi.permissions:
                    ch = fe_utils.get_channel(server, chname)
                    if ch:
                        await ch.set_permissions(used_member, overwrite=None)
            except Exception as e:
                ewutils.logMsg("Failed to remove permissions for {} in channel {}: {}.".format(used_member.display_name, channel.name, e))

    # Part 2: Add overrides for the POI the user should be in
    channel = fe_utils.get_channel(server, user_poi_obj.channel)
    if channel:
        for chname in user_poi_obj.permissions:
            perms_dict = user_poi_obj.permissions[chname]
            overwrite = discord.PermissionOverwrite()
            overwrite.read_messages = True if ewcfg.permission_read_messages in perms_dict else False
            overwrite.send_messages = True if ewcfg.permission_send_messages in perms_dict else False
            overwrite.connect = True if ewcfg.permission_connect_to_voice in perms_dict else False
            ch = fe_utils.get_channel(server, chname)
            if ch:
                await ch.set_permissions(used_member, overwrite=overwrite)
    else:
        ewutils.logMsg(f"Couldn't apply overwrites for user {user_data.id_user}, channel {user_poi_obj.channel} doesn't exist.")


# Remove all user overwrites in the server's POI channels
async def remove_user_overwrites(cmd):
    if not cmd.message.author.guild_permissions.administrator:
        return

    server = cmd.guild
    client = ewutils.get_client()

    for poi in poi_static.poi_list:

        searched_channel = poi.channel

        channel = fe_utils.get_channel(server, searched_channel)

        if channel == None:
            # Second try
            channel = fe_utils.get_channel(server, searched_channel)
            if channel == None:
                continue

        # print('{} overwrites: {}'.format(poi.id_poi, channel.overwrites))
        for tuple in channel.overwrites:
            # print('tuplevar: {}'.format(tuple) + '\n\n')
            if tuple not in server.roles:
                member = tuple

                print('removed overwrite in {} for {}'.format(channel, member))

                for i in range(ewcfg.permissions_tries):
                    await channel.set_permissions(member, overwrite=None)

    response = "DEBUG: ALL USER OVERWRITES DELETED."
    return await fe_utils.send_message(client, cmd.message.channel,
                                       fe_utils.formatMessage(cmd.message.author, response))



def check_clearance(member=None) -> int:

    """
    Returns an int showing the clearance of the user depending on the roles they have attached to their discord member.
    The lower the number, the greater the clearance.
    - 10 is a regular user
    - 4 & 3 is moderators
    - 1 & 2 is admins and kingpins
    """

    if member is None:
        return -1

    roles_map_user = ewutils.getRoleMap(member.roles)

    if (ewcfg.role_bpadmin in roles_map_user) or (ewcfg.role_rowdyfucker in roles_map_user) or (
            ewcfg.role_copkiller in roles_map_user):
        return 1  # currently in admin
    elif ewcfg.role_brimstoneprog in roles_map_user:
        return 2  # casual admin
    elif ewcfg.role_bdadmin in roles_map_user:
        return 3  # mod admin
    elif ewcfg.role_brimstonedesperados in roles_map_user:
        return 4  # casual mod admin
    else:
        return 10
