from . import core as ewutils
from ..backend import core as bknd_core
from ..backend.district import EwDistrictBase as EwDistrict
from ..backend.dungeons import EwGamestate
from ..static import cfg as ewcfg
from ..static import poi as poi_static


def get_subzone_controlling_faction(subzone_id, id_server):
    subzone = poi_static.id_to_poi.get(subzone_id)

    if subzone == None:
        return
    else:
        if not subzone.is_subzone:
            return

    mother_pois = subzone.mother_districts

    # Get all the mother pois of a subzone in order to find the father poi, which is either one of the mother pois or the father poi of the mother poi
    # Subzones such as the food court will have both a district poi and a street poi as one of their mother pois
    district_data = None

    for mother_poi in mother_pois:

        mother_poi_data = poi_static.id_to_poi.get(mother_poi)

        if mother_poi_data.is_district:
            # One of the mother pois was a district, get its controlling faction
            district_data = EwDistrict(district=mother_poi, id_server=id_server)
            break
        else:
            # One of the mother pois was a street, get the father district of that street and its controlling faction
            father_poi = mother_poi_data.father_district
            district_data = EwDistrict(district=father_poi, id_server=id_server)
            break

    if district_data != None:
        faction = district_data.controlling_faction
        return faction


def get_street_list(str_poi):
    poi = poi_static.id_to_poi.get(str_poi)
    neighbor_list = poi.neighbors
    poi_list = []
    if poi.is_district == False:
        return poi_list
    else:
        for neighbor in neighbor_list.keys():
            neighbor_poi = poi_static.id_to_poi.get(neighbor)
            if neighbor_poi.is_street == True:
                poi_list.append(neighbor)
        return poi_list


def inaccessible(user_data = None, poi = None):
    if poi == None or user_data == None:
        return True

    if user_data.life_state == ewcfg.life_state_observer:
        return False

    elevatorstop = EwGamestate(id_server=user_data.id_server, id_state='elevator')
    for lock in ewcfg.lock_states:
        if poi in ewcfg.lock_states.get(lock) and user_data.poi in ewcfg.lock_states.get(lock):
            # print(lock)
            gamestate = EwGamestate(id_server=user_data.id_server, id_state=lock)
            if gamestate.bit == 0 or elevatorstop.value not in ewcfg.lock_states.get(lock):
                return True



    bans = user_data.get_bans()
    vouchers = user_data.get_vouchers()

    locked_districts_list = retrieve_locked_districts(user_data.id_server)

    if (
            len(poi.factions) > 0 and
            (set(vouchers).isdisjoint(set(poi.factions)) or user_data.faction != "") and
            user_data.faction not in poi.factions
    ) or (
            len(poi.life_states) > 0 and
            user_data.life_state not in poi.life_states
    ):
        return True
    elif (
            len(poi.factions) > 0 and
            len(bans) > 0 and
            set(poi.factions).issubset(set(bans))
    ):
        return True
    elif poi.id_poi in locked_districts_list and user_data.life_state not in [ewcfg.life_state_executive, ewcfg.life_state_lucky]:
        return True
    else:
        return False

def retrieve_locked_districts(id_server):
    locked_districts_list = []

    locked_districts = bknd_core.execute_sql_query(
        "SELECT {district} FROM global_locks WHERE id_server = %s AND {locked_status} = %s".format(
            district=ewcfg.col_district,
            locked_status=ewcfg.col_locked_status
        ), (
            id_server,
            'true'
        ))
    for district in locked_districts:
        locked_districts_list.append(district[0])

    return locked_districts_list
