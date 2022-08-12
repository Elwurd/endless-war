from ew.backend.dungeons import EwGamestate
from ew.static.poi import id_to_poi


debug3 = 'gatekeep'
debug4 = {
    'id_relic':'gaslight',
    'relic_name':'Girl Boss',
    'relic_desc':'I lost touch with these slippery ass memes ages ago. Not funny in the least.',
    'acquisition':'testing'
}
debug5 = "guh?"

auction_relic_date_map = {}

def canCreateRelic(item, id_server, createstate = 0):
    state = EwGamestate(id_server=id_server, id_state=item)

    if state.bit is not None:
        return None
    else:
        state.bit = 0
        state.value = ""
        if createstate == 1:
            state.persist()
        return 1



def debug16(one, two, three):
    pass

def debug17(one):
    return " "

def movement_checker(user_data, poi_from, poi_to, cmd):
    return

def poi_is_pvp(poi_name = None):
    poi = id_to_poi.get(poi_name)

    if poi != None:
        return poi.pvp

    return False

def eg_check1(t, user_data):
    return False

def eg_check2(t, shootee_data):
    return True if poi_is_pvp(shootee_data.poi) == False else False

def eg_check3(t, shootee_data, user_data):
    poi = id_to_poi.get(user_data.poi)

    return True if not poi.pvp and not (shootee_data.life_state == 3 or shootee_data.get_inhabitee() == user_data.id_user) else False
