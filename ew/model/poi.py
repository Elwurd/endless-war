"""
    Point of Interest (POI) data model
"""


class EwPoi:
    # The typable single-word ID of this location.
    id_poi = ""

    # Acceptable alternative typable single-word names for this place.
    alias = []

    # The nice name for this place.
    str_name = ""

    # You find yourself $str_in $str_name
    str_in = "in"

    # You $str_enter $str_name
    str_enter = "enter"

    # A description provided when !look-ing here.
    str_desc = ""

    # (X, Y) location on the map (left, top) zero-based origin.
    coord = None
    coord_alias = []

    # Channel name associated with this POI
    channel = ""

    # Discord role associated with this zone (control channel visibility).
    role = None

    # Discord permissions associated with this zone (control channel visibility) - 5/28/20
    permissions = None

    # Zone allows PvP combat and interactions.
    pvp = True

    # Factions allowed in this zone.
    factions = []

    # Life states allowed in this zone.
    life_states = []

    # If true, the zone is inaccessible.
    closed = False

    # Message shown before entering the zone fails when it's closed.
    str_closed = None

    # Vendor names available at this POI.
    vendors = []

    # The value of the district
    property_class = ""

    # If the zone is a district
    is_district = False

    # If the zone is a gang base (Juvie's Row included)
    is_gangbase = False

    # If true, the zone is a district that can be controlled/captured
    is_capturable = False

    # If it's a subzone
    is_subzone = False

    # If it's an apartment
    is_apartment = False

    # if this zone is a street within a district
    is_street = False

    # What District/street each subzone is in. Subzones could potentially have multiple mother districts if they are between streets/districts.
    mother_districts = []

    # What District each street is attatched to
    father_district = ""

    # If it's a mobile zone
    is_transport = False

    # which type of transport
    transport_type = ""

    # default line to follow, if it's a transport
    default_line = ""

    # default station to start at, if it's a transport
    default_stop = ""

    # If a transport line stops here
    is_transport_stop = True

    # which transport lines stop here
    transport_lines = set()

    # if this zone belongs to the outskirts
    is_outskirts = False

    # id for the zone's community chest, if it has one
    community_chest = None

    # if you can fish in the zone
    is_pier = False

    # if the pier is in fresh slime or salt slime
    pier_type = None

    # if the poi is part of the tutorial
    is_tutorial = False

    # whether to show ads here
    has_ads = False

    # if you can write zines here
    write_manuscript = False

    # dict EwPoi -> int, that defines travel times into adjacent pois
    neighbors = None

    # The topic associated with that poi's channel
    topic = ""

    # The wiki page associated with that poi
    wikipage = ""

    #check to split POI
    isSplit = ""

    #if !jump will take you anywhere
    jump_dest = ""

    def __init__(
            self,
            id_poi = "unknown",
            alias = [],
            str_name = "Unknown",
            str_desc = "...",
            str_in = "in",
            str_enter = "enter",
            coord = None,
            coord_alias = [],
            channel = "",
            role = None,
            permissions = None,
            pvp = True,
            factions = [],
            life_states = [],
            closed = False,
            str_closed = None,
            vendors = [],
            property_class = "",
            is_district = False,
            is_gangbase = False,
            is_capturable = False,
            is_subzone = False,
            is_apartment = False,
            is_street = False,
            mother_districts = [],
            father_district = "",
            is_transport = False,
            transport_type = "",
            default_line = "",
            default_stop = "",
            is_transport_stop = False,
            is_outskirts = False,
            community_chest = None,
            is_pier = False,
            pier_type = None,
            is_tutorial = False,
            has_ads = False,
            write_manuscript = False,
            neighbors = None,
            topic = "",
            wikipage = "",
            isSplit = "",
            jump_dest = ""
    ):
        self.id_poi = id_poi
        self.alias = alias
        self.str_name = str_name
        self.str_desc = str_desc
        self.str_in = str_in
        self.str_enter = str_enter
        self.coord = coord
        self.coord_alias = coord_alias
        self.channel = channel
        self.role = role
        self.permissions = permissions
        self.pvp = pvp
        self.factions = factions
        self.life_states = life_states
        self.closed = closed
        self.str_closed = str_closed
        self.vendors = vendors
        self.property_class = property_class
        self.is_district = is_district
        self.is_gangbase = is_gangbase
        self.is_capturable = is_capturable
        self.is_subzone = is_subzone
        self.is_apartment = is_apartment
        self.is_street = is_street
        self.mother_districts = mother_districts
        self.father_district = father_district
        self.is_transport = is_transport
        self.transport_type = transport_type
        self.default_line = default_line
        self.default_stop = default_stop
        self.is_transport_stop = is_transport_stop
        self.transport_lines = set()
        self.is_outskirts = is_outskirts
        self.community_chest = community_chest
        self.is_pier = is_pier
        self.pier_type = pier_type
        self.is_tutorial = is_tutorial
        self.has_ads = has_ads
        self.write_manuscript = write_manuscript
        self.topic = topic
        self.wikipage = wikipage
        self.isSplit = isSplit
        self.jump_dest = jump_dest

        self.neighbors = neighbors
        if self.neighbors == None:
            self.neighbors = {}


""" Object that defines a public transportation line """


class EwTransportLine:
    # name of the transport line
    id_line = ""

    # alternative names
    alias = []

    # Nice name for output
    str_name = ""

    # which stop the line starts at
    first_stop = ""

    # which stop the line ends at
    last_stop = ""

    # which line transports switch to after the last stop
    next_line = ""

    # how long to stay at each stop, and which stop follows
    schedule = {}

    def __init__(self,
                 id_line = "",
                 alias = [],
                 str_name = "",
                 first_stop = "",
                 last_stop = "",
                 next_line = "",
                 schedule = {}
                 ):
        self.id_line = id_line
        self.alias = alias
        self.str_name = str_name
        self.first_stop = first_stop
        self.last_stop = last_stop
        self.next_line = next_line
        self.schedule = schedule


class EwEventDef:
    event_type = ""

    str_name = ""
    pois = []

    length = 0
    buffer = 0

    str_event_start = ""
    str_event_ongoing = ""
    str_event_end = ""
    str_check_text = ""

    def __init__(
            self,
            event_type = "",
            str_name = "",
            pois = [],
            length = 0,
            buffer = 0,
            str_event_start = "",
            str_event_ongoing = "",
            str_event_end = "",
            str_check_text = "",
    ):
        self.event_type = event_type
        self.str_name = str_name
        self.pois = pois
        self.length = length
        self.buffer = buffer
        self.str_event_start = str_event_start
        self.str_event_ongoing = str_event_ongoing
        self.str_event_end = str_event_end
        self.str_check_text = str_check_text


class EwDungeonScene:
    # The text sent when a scene starts
    text = ""

    # Whether or not the dungeon is active
    dungeon_state = True

    # Where the scene is taking place
    poi = None

    # life state to assign for this scene
    life_state = None

    # Commands that can be used in a scene, and what scene ID that leads to
    options = {}

    def __init__(
            self,
            text = "",
            dungeon_state = True,
            options = {},
            poi = None,
            life_state = None,
    ):
        self.text = text
        self.dungeon_state = dungeon_state
        self.options = options
        self.poi = poi
        self.life_state = life_state
