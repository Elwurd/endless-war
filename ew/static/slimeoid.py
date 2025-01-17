import random

from . import cfg as ewcfg
from ..model.slimeoid import EwBody
from ..model.slimeoid import EwBrain
from ..model.slimeoid import EwDefense
from ..model.slimeoid import EwHead
from ..model.slimeoid import EwMobility
from ..model.slimeoid import EwOffense
from ..model.slimeoid import EwSpecial

# All body attributes in the game.
body_list = [
    EwBody(  # body 1
        id_body="teardrop",
        alias=[
            "tear",
            "drop",
            "oblong",
            "a"
        ],
        str_create="You press a button on the body console labelled 'A'. Through the observation port, you see the rapidly congealing proto-Slimeoid take on a roughly teardrop-shaped form.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"A\". In front of you, you see the undulating proto-Negaslimeoid take on a roughly teardrop-shaped form.",
        str_body="It is teardrop-shaped.",
        str_observe="{slimeoid_name} is bobbing its top-heavy body back and forth."
    ),
    EwBody(  # body 2
        id_body="wormlike",
        alias=[
            "long",
            "serpent",
            "serpentine",
            "b"
        ],
        str_create="You press a button on the body console labelled 'B'. Through the observation port, you see the rapidly congealing proto-Slimeoid begin to stretch into an elongated form.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"B\". In front of you, you see the undulating proto-Negaslimeoid begin to stretch into an elongated form.",
        str_body="It is long and wormlike.",
        str_observe="{slimeoid_name} is twisting itself around, practicing tying its knots."
    ),
    EwBody(  # body 3
        id_body="spherical",
        alias=[
            "sphere",
            "orb",
            "ball",
            "c"
        ],
        str_create="You press a button on the body console labelled 'C'. Through the observation port, you see the rapidly congealing proto-Slimeoid take on a roughly spherical form.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"C\". In front of you, you see the undulating proto-Negaslimeoid take on a roughly spherical form.",
        str_body="It is generally orb-shaped.",
        str_observe="{slimeoid_name} flops over onto one side of its round body."
    ),
    EwBody(  # body 4
        id_body="humanoid",
        alias=[
            "biped",
            "human",
            "d"
        ],
        str_create="You press a button on the body console labelled 'D'. Through the observation port, you see the rapidly congealing proto-Slimeoid curl into a foetal, vaguely humanoid form.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"D\". In front of you, you see the undulating proto-Negaslimeoid curl into a foetal, vaguely humanoid form.",
        str_body="It is vaguely humanoid.",
        str_observe="{slimeoid_name} is scraping at something on the ground with its arms."
    ),
    EwBody(  # body 5
        id_body="tentacled",
        alias=[
            "squid",
            "squidlike",
            "tentacle",
            "tentacles",
            "e"
        ],
        str_create="You press a button on the body console labelled 'E'. Through the observation port, you see the rapidly congealing proto-Slimeoid begin to sprout long tendrils from its nucleus.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"E\". In front of you, you see the undulating proto-Negaslimeoid begin to sprout long tendrils from its nucleus.",
        str_body="It is a mass of tendrils.",
        str_observe="{slimeoid_name} is moving its tentacles around, running them over one another."
    ),
    EwBody(  # body 6
        id_body="amorphous",
        alias=[
            "none",
            "formless",
            "f"
        ],
        str_create="You press a button on the body console labelled 'F'. Through the observation port, you see the rapidly congealing proto-Slimeoid accreting itself together with no distinct shape to speak of.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"F\". In front of you, you see the undulating proto-Negaslimeoid accreting itself together with no distinct shape to speak of",
        str_body="It has no defined shape.",
        str_observe="{slimeoid_name}'s body is spread out on the floor like a kind of living puddle."
    ),
    EwBody(  # body 7
        id_body="quadruped",
        alias=[
            "animal",
            "g"
        ],
        str_create="You press a button on the body console labelled 'G'. Through the observation port, you see the rapidly congealing proto-Slimeoid beginning to grow bones and vertebrae as it starts to resemble some kind of quadruped.",
        str_create_nega="You move the planchette to spell \"BODY\", then move the planchette to \"G\". In front of you, you see the undulating proto-Negaslimeoid beginning to grow bones and vertebrae as it starts to resemble some kind of quadruped.",
        str_body="It has a body shape vaguely reminiscent of a quadruped.",
        str_observe="{slimeoid_name} has its hindquarters lowered in a sort of sitting position."
    )
]

# A map of id_body to EwBody objects.
body_map = {}

# A list of body names
body_names = []

# Populate body map, including all aliases.
for body in body_list:
    body_map[body.id_body] = body
    body_names.append(body.id_body)

    for alias in body.alias:
        body_map[alias] = body

# All head attributes in the game.
head_list = [
    EwHead(  # head 1
        id_head="eye",
        alias=[
            "cyclops",
            "a"
        ],
        str_create="You press a button on the head console labelled 'A'. Through the observation port, you see a dark cluster within the proto-Slimeoid begin to form into what looks like a large eye.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"A\". In front of you, you see a bright cluster within the proto-Negaslimeoid begin to form into what looks like a large eye.",
        str_head="Its face is a single huge eye.",
        str_feed="{slimeoid_name} swallows the {food_name} whole.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name}'s huge eye follows the ball's arc, and it makes a leap to catch it!!\n\n...only to get socked right in the eye, sending it to the floor in pain. Depth perception... it's truly a gift."
    ),
    EwHead(  # head 2
        id_head="maw",
        alias=[
            "mouth",
            "b"
        ],
        str_create="You press a button on the head console labelled 'B'. Through the observation port, you see an opening form in what you think is the proto-Slimeoid's face, which begins to sprout large pointed teeth.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"B\". In front of you, you see an opening form in what you think is the proto-Negaslimeoid's face, which begins to sprout large pointed teeth.",
        str_head="Its face is a huge toothy mouth.",
        str_feed="{slimeoid_name} crunches the {food_name} to paste with its huge teeth.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} slavers and drools as it awaits the throw, and when it sees the ball start to fly, it lunges to grab it out of the air in its huge toothy maw, slicing it to shreds with its teeth in seconds."
    ),
    EwHead(  # head 3
        id_head="void",
        alias=[
            "hole",
            "c"
        ],
        str_create="You press a button on the head console labelled 'C'. Through the observation port, you see what you thought was the proto-Slimeoid's face suddenly sucked down into its body, as though by a black hole.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"C\". In front of you, you see what you thought was the proto-Negaslimeoid's face suddenly sucked down into its body, as though by a black hole.",
        str_head="Its face is an empty black void.",
        str_feed="The {food_name} disappears into the unknowable depths of {slimeoid_name}'s face hole.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} positions itself to catch the ball in it's... face? The ball falls into the empty void of {slimeoid_name}'s face, then just keeps falling, falling, falling, down into the depths, falling so far it disappears forever."
    ),
    EwHead(  # head 4
        id_head="beast",
        alias=[
            "animal",
            "dragon",
            "d"
        ],
        str_create="You press a button on the head console labelled 'D'. Through the observation port, you see the beginnings of an animal-like face forming on your proto-Slimeoid, with what might be eyes, a nose, teeth... maybe.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"D\". In front of you, you see the beginnings of an animal-like face forming on your proto-Negaslimeoid with what might be eyes, a nose, teeth... maybe.",
        str_head="Its face is that of a vicious beast.",
        str_feed="{slimeoid_name} gobbles up the {food_name} greedily.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} focuses its eyes and bares its teeth, then makes a flying leap, snapping the ball clean out of the air in its jaws! It comes back to you and drops the ball at your feet. Good boy!"
    ),
    EwHead(  # head 5
        id_head="insect",
        alias=[
            "bug",
            "insectoid",
            "e"
        ],
        str_create="You press a button on the head console labelled 'E'. Through the observation port, you see the proto-Slimeoid suddenly bulge with a series of hard orbs which congeal into what appear to be large compound eyes.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"E\". In front of you, you see the proto-Negaslimeoid suddenly bulge with a series of hard orbs which congeal into what appear to be large compound eyes.",
        str_head="It has bulging insectoid eyes and mandibles.",
        str_feed="{slimeoid_name} cuts the {food_name} into pieces with its mandibles.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} stands motionless, presumably watching the ball with its large compound eyes, before darting toward it as it sails through the air, snapping its mandibles around the ball and slicing it cleanly in two."
    ),
    EwHead(  # head 6
        id_head="skull",
        alias=[
            "skeleton",
            "f"
        ],
        str_create="You press a button on the head console labelled 'F'. Through the observation port, you see the proto-Slimeoid's frontal features twist into a ghastly death's-head.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"F\". In front of you, you see the proto-Negaslimeoid's frontal features twist into a ghastly death's-head.",
        str_head="Its face resembles a skull.",
        str_feed="{slimeoid_name} spills half the {food_name} on the floor trying to chew it with its exposed teeth.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} moves as quickly as it can to make the catch, making it just before the ball lands! With a thunk, the ball lodges itself in {slimeoid_name}'s open eye socket. {slimeoid_name} yanks it out and tosses the ball back to you. Euughh."
    ),
    EwHead(  # head 7
        id_head="none",
        alias=[
            "g"
        ],
        str_create="You press a button on the head console labelled 'G'. Through the observation port, you see the proto-Slimeoid's front end melt into an indistinct mass.",
        str_create_nega="You move the planchette to spell \"HEAD\", then move the planchette to \"G\". In front of you, you see the proto-Negaslimeoid's front end melt into an indistinct mass.",
        str_head="It has no discernable head.",
        str_feed="{slimeoid_name} just sort of... absorbs the {food_name} into its body.",
        str_fetch="You toss a ball for {slimeoid_name} to fetch. {slimeoid_name} moves under the ball as it flies through the air, but makes no attempt to catch it in its mouth on account of having none. The ball lands next to {slimeoid_name}, who merely looks on. Actually, you can't tell where it's looking."
    )
]

# A map of id_head to EwBody objects.
head_map = {}

# A list of head names
head_names = []

# Populate head map, including all aliases.
for head in head_list:
    head_map[head.id_head] = head
    head_names.append(head.id_head)

    for alias in head.alias:
        head_map[alias] = head

# All mobility attributes in the game.
mobility_list = [
    EwMobility(  # mobility 1
        id_mobility="legs",
        alias=[
            "animal",
            "quadruped",
            "biped",
            "jointed",
            "limbs",
            "a"
        ],
        str_advance="{active} barrels toward {inactive}!",
        str_retreat="{active} leaps away from {inactive}!",
        str_advance_weak="{active} limps toward {inactive}!",
        str_retreat_weak="{active} limps away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'A'. Through the observation port, you see jointed limbs begin to sprout from the proto-Slimeoid's underside.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"A\". In front of you, you see jointed limbs begin to sprout from the proto-Negaslimeoid's underside.",
        str_mobility="It walks on legs.",
        str_defeat="{slimeoid_name}'s knees buckle under it as it collapses to the ground, defeated!",
        str_walk="{slimeoid_name} walks along beside you."
    ),
    EwMobility(  # mobility 2
        id_mobility="rolling",
        alias=[
            "roll",
            "b"
        ],
        str_advance="{active} rolls itself toward {inactive}!",
        str_retreat="{active} rolls away from {inactive}!",
        str_advance_weak="{active} rolls itself unsteadily towards {inactive}!",
        str_retreat_weak="{active} rolls unsteadily away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'B'. Through the observation port, you see the proto-Slimeoid becoming smoother and rounder.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"B\". In front of you, you see the proto-Negaslimeoid becoming smoother and rounder.",
        str_mobility="It moves by rolling its body around.",
        str_defeat="{slimeoid_name} rolls itself over before collapsing on the ground, defeated!",
        str_walk="{slimeoid_name} rolls itself along the ground behind you."
    ),
    EwMobility(  # mobility 3
        id_mobility="flagella",
        alias=[
            "flagella",
            "tendrils",
            "tentacles",
            "c"
        ],
        str_advance="{active} slithers toward {inactive}!",
        str_retreat="{active} slithers away from {inactive}!",
        str_advance_weak="{active} drags itself toward {inactive}!",
        str_retreat_weak="{active} drags itself away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'C'. Through the observation port, you see masses of writhing flagella begin to protrude from the proto-Slimeoid's extremities.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"C\". In front of you, you see masses of writhing flagella begin to protrude from the proto-Negaslimeoid's extremities.",
        str_mobility="It moves by pulling itself around with its flagella.",
        str_defeat="{slimeoid_name}'s flagella go limp as it collapses to the ground, defeated!",
        str_walk="{slimeoid_name} writhes its way along the ground on its flagella next to you."
    ),
    EwMobility(  # mobility 4
        id_mobility="jets",
        alias=[
            "fluid",
            "jet",
            "d"
        ],
        str_advance="{active} propels itself toward {inactive}!",
        str_retreat="{active} propels itself away from {inactive}!",
        str_advance_weak="{active} sputters towards {inactive}!",
        str_retreat_weak="{active} sputters away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'D'. Through the observation port, you see openings forming in the proto-Slimeoid's body, which begin to vent fluid.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"D\". In front of you, you see openings forming in the proto-Negaslimeoid's body, which begin to vent fluid.",
        str_mobility="It moves via jet-propulsion by squirting fluids.",
        str_defeat="{slimeoid_name} fires its fluid jets wildly in a panic until it completely deflates and collapses, defeated!",
        str_walk="{slimeoid_name} tries to keep pace with you, spurting jets of fluid to propel itself along behind you."
    ),
    EwMobility(  # mobility 5
        id_mobility="slug",
        alias=[
            "undulate",
            "e"
        ],
        str_advance="{active} undulates its way toward {inactive}!",
        str_retreat="{active} undulates itself away from {inactive}!",
        str_advance_weak="{active} heaves itself slowly toward {inactive}!",
        str_retreat_weak="{active} heaves itself slowly away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'E'. Through the observation port, you see the base of the proto-Slimeoid's body widen and flatten out.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"E\". In front of you, you see the base of the proto-Negaslimeoid's body widen and flatten out.",
        str_mobility="It moves like a slug, undulating its underside along the ground.",
        str_defeat="{slimeoid_name} stops moving entirely and collapses to the ground, defeated!",
        str_walk="{slimeoid_name} glacially drags its way along behind you in its slug-like way. Your walk ends up taking fucking forever."
    ),
    EwMobility(  # mobility 5
        id_mobility="float",
        alias=[
            "gas",
            "f"
        ],
        str_advance="{active} floats toward {inactive}!",
        str_retreat="{active} floats away from {inactive}!",
        str_advance_weak="{active} bobs unsteadily through the air towards {inactive}!",
        str_retreat_weak="{active} bobs unsteadily away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'F'. Through the observation port, you see the bottom of the proto-Slimeoid's body start to inflate itself.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"F\". In front of you, you see the bottom of the proto-Negaslimeoid's body start to inflate itself.",
        str_mobility="It floats in the air with the use of super-low-density gas bladders.",
        str_defeat="{slimeoid_name} spins wildly in the air before careening to the ground, defeated!",
        str_walk="{slimeoid_name} bobs along next to you on its leash like a balloon."
    ),
    EwMobility(  # mobility 5
        id_mobility="wings",
        alias=[
            "fly",
            "g"
        ],
        str_advance="{active} darts through the air toward {inactive}!",
        str_retreat="{active} flaps away from {inactive}!",
        str_advance_weak="{active} flaps its way doggedly towards {inactive}!",
        str_retreat_weak="{active} flaps doggedly away from {inactive}!",
        str_create="You press a button on the mobility console labelled 'G'. Through the observation port, you see the proto-Slimeoid start to sprout wide, flat, thin appendages.",
        str_create_nega="You move the planchette to spell \"LEGS\", then move the planchette to \"G\". In front of you, you see the proto-Negaslimeoid start to sprout wide, flat, thin appendages.",
        str_mobility="It moves by making short flights through the air with its wings.",
        str_defeat="{slimeoid_name} flaps helplessly as it spins out and crashes into the ground, defeated!",
        str_walk="{slimeoid_name} flaps along through the air next to you, occasionally perching in trees or windowsills along the route."
    )
]

# A map of id_mobility to EwBody objects.
mobility_map = {}

# A list of mobility names
mobility_names = []

# Populate mobility map, including all aliases.
for mobility in mobility_list:
    mobility_map[mobility.id_mobility] = mobility
    mobility_names.append(mobility.id_mobility)

    for alias in mobility.alias:
        mobility_map[alias] = mobility

# All offense attributes in the game.
offense_list = [
    EwOffense(  # offense 1
        id_offense=ewcfg.slimeoid_weapon_blades,
        alias=[
            "edged",
            "edges",
            "edgy",
            "bladed",
            "blade",
            "a"
        ],
        str_attack="{active} slashes {inactive} with its blades!",
        str_attack_weak="{active} desperately swipes at {inactive} with its blades!",
        str_attack_coup="{active} slices deep into {inactive}! Green goo splatters onto the ground from the wound!!",
        str_create="You press a button on the weapon console labelled 'A'. Through the observation port, you see long, sharp protrusions begin to form on the proto-Slimeoid's extremities.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"A\". In front of you, you see long, sharp protrusions begin to form on the proto-Negaslimeoid's extremities.",
        str_offense="It slices foes with retractible blades.",
        str_observe="{slimeoid_name} is sharpening its retractible blades on a stone nearby."
    ),
    EwOffense(  # offense 2
        id_offense=ewcfg.slimeoid_weapon_teeth,
        alias=[
            "bite",
            "biting",
            "crunch",
            "crunching",
            "b"
        ],
        str_attack="{active} sinks its teeth into {inactive}!",
        str_attack_weak="{active} gnashes its teeth, biting {inactive} wherever it can!",
        str_attack_coup="{active} bites hard into {inactive}, tearing off a piece and chewing it hungrily!",
        str_create="You press a button on the weapon console labelled 'B'. Through the observation port, you see large bony structures resembling teeth forming in the proto-Slimeoid's... mouth?",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"B\". In front of you, you see large bony structures resembling teeth forming in the proto-Negaslimeoid's... mouth?",
        str_offense="It can bite foes with deadly fangs.",
        str_observe="{slimeoid_name} is idly picking its sharp teeth."
    ),
    EwOffense(  # offense 3
        id_offense=ewcfg.slimeoid_weapon_grip,
        alias=[
            "squeeze",
            "grab",
            "squeezing",
            "grabbing",
            "gripping",
            "constrict",
            "constriction",
            "c"
        ],
        str_attack="{active} grabs {inactive} and squeezes hard!",
        str_attack_weak="{active} grabs at {inactive}, trying to fend it off!",
        str_attack_coup="{active} grips {inactive} like a vice, squeezing until you hear a sickening pop!",
        str_create="You press a button on the weapon console labelled 'C'. Through the observation port, you see the proto-Slimeoid's limbs becoming thicker and stronger, beginning to twist and writhe, seeking something to grip onto.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"C\". In front of you, you see the proto-Negaslimeoid's limbs becoming thicker and stronger, beginning to twist and writhe, seeking something to grip onto.",
        str_offense="It can grab and crush its foes with its limbs.",
        str_observe="{slimeoid_name} picks up a rock off the ground and squeezes it like a stress ball."
    ),
    EwOffense(  # offense 4
        id_offense=ewcfg.slimeoid_weapon_bludgeon,
        alias=[
            "strike",
            "striking",
            "smash",
            "smashing",
            "bash",
            "bashing",
            "crush",
            "crushing",
            "d"
        ],
        str_attack="{active} bashes {inactive} with its limbs!",
        str_attack_weak="{active} flails its limbs to strike back at {inactive}!",
        str_attack_coup="{active} winds back and smashes {inactive}, dealing a knockout blow!",
        str_create="You press a button on the weapon console labelled 'D'. Through the observation port, you see the ends of the proto-Slimeoid's limbs becoming harder and heavier.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"D\". In front of you, you see the ends of the proto-Negaslimeoid's, limbs becoming harder and heavier.",
        str_offense="It can smash foes with one or more of its limbs.",
        str_observe="{slimeoid_name} spots an insect on the ground nearby and smashes it."
    ),
    EwOffense(  # offense 5
        id_offense=ewcfg.slimeoid_weapon_spikes,
        alias=[
            "puncture",
            "spear",
            "e"
        ],
        str_attack="{active} skewers {inactive} with its spikes!",
        str_attack_weak="{active} tries to defend itself from {inactive} with its spikes!",
        str_attack_coup="{active} punctures {inactive} with its spikes, opening a hole that oozes green fluid all over the ground!",
        str_create="You press a button on the weapon console labelled 'E'. Through the observation port, you see hard spikes forming out of the congealing slime biomatter.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"E\". In front of you, you see hard spikes forming out of the congealing negaslime biomatter.",
        str_offense="It can puncture its enemies with the spikes on its body.",
        str_observe="{slimeoid_name} carefully adjusts its position so as not to prick itself with its own spikes."
    ),
    EwOffense(  # offense 6
        id_offense=ewcfg.slimeoid_weapon_electricity,
        alias=[
            "strike",
            "f"
        ],
        str_attack="{active} unleashes a pent-up electrical discharge into {inactive}!",
        str_attack_weak="{active} sparks and flickers with electricity, shocking {inactive}!",
        str_attack_coup="{active} charges up and sends a bolt of electricity through {inactive}, making it sizzle!",
        str_create="You press a button on the weapon console labelled 'F'. Through the observation port, you see the proto-Slimeoid begin to spark with small electrical discharges.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"F\". In front of you, you see the proto-Negaslimeoid begin to spark with small electrical discharges.",
        str_offense="It crackles with stored electrical energy.",
        str_observe="A fly flies a little too near {slimeoid_name} and is zapped with a tiny bolt of electricity, killing it instantly."
    ),
    EwOffense(  # offense 7
        id_offense=ewcfg.slimeoid_weapon_slam,
        alias=[
            "bodyslam",
            "g"
        ],
        str_attack="{active} slams its entire body into {inactive}!",
        str_attack_weak="{active} flails itself back against {inactive}'s onslaught!",
        str_attack_coup="{active} hurls its whole weight into {inactive}, crushing it to the ground!",
        str_create="You press a button on the weapon console labelled 'G'. Through the observation port, you see the ends of the proto-Slimeoid's congealing body condense, becoming heavier and more robust.",
        str_create_nega="You move the planchette to spell \"WEAPON\", then move the planchette to \"G\". In front of you, you see the ends of the proto-Negaslime's congealing body condense, becoming heavier and more robust.",
        str_offense="It can slam its body into its foes with tremendous force.",
        str_observe="{slimeoid_name} shifts its weight back and forth before settling down in a kind of sumo-squat position."
    )
]

# A map of id_offense to EwBody objects.
offense_map = {}

# A list of offense names
offense_names = []

# Populate offense map, including all aliases.
for offense in offense_list:
    offense_map[offense.id_offense] = offense
    offense_names.append(offense.id_offense)

    for alias in offense.alias:
        offense_map[alias] = offense

# All defense attributes in the game.
defense_list = [
    EwDefense(  # defense 1
        id_defense=ewcfg.slimeoid_armor_scales,
        alias=[
            "scale",
            "scaled",
            "scaly",
            "a"
        ],
        str_defense="",
        str_pet="You carefully run your hand over {slimeoid_name}'s hide, making sure to go with the grain so as not to slice your fingers open on its sharp scales.",
        str_abuse="You pick up {slimeoid_name} by the hind legs, swinging them over your head and repeatedly slamming them to the ground.",
        str_create="You press a button on the armor console labelled 'A'. Through the observation port, you see the proto-Slimeoid's skin begin to glint as it sprouts roughly-edged scales.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"A\". In front of you, you see the proto-Negaslimeoid's skin begin to glint as it sprouts roughly-edged scales.",
        str_armor="It is covered in scales.",
        id_resistance=ewcfg.slimeoid_weapon_electricity,
        id_weakness=ewcfg.slimeoid_special_TK,
        str_resistance=" {}'s scales conduct the electricity away from its vitals!",
        str_weakness=" {}'s scales refract and amplify the disrupting brainwaves inside its skull!",
    ),
    EwDefense(  # defense 2
        id_defense=ewcfg.slimeoid_armor_boneplates,
        alias=[
            "bone",
            "bony",
            "bones",
            "plate",
            "plates",
            "armor",
            "plating",
            "b"
        ],
        str_defense="",
        str_pet="You pat one of the hard, bony plates covering {slimeoid_name}'s skin.",
        str_abuse="You take a stick and hit {slimeoid_name}'s face with it.",
        str_create="You press a button on the armor console labelled 'B'. Through the observation port, you see hard bony plates begin to congeal on the proto-Slimeoid's surface.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"B\". In front of you, you see hard bony plates begin to congeal on the proto-Negaslimeoid's surface.",
        str_armor="It is covered in bony plates.",
        id_resistance=ewcfg.slimeoid_weapon_blades,
        id_weakness=ewcfg.slimeoid_special_spines,
        str_resistance=" {}'s bone plates block the worst of the damage!",
        str_weakness=" {}'s bone plates only drive the quills deeper into its body as it moves!",

    ),
    EwDefense(  # defense 3
        id_defense=ewcfg.slimeoid_armor_quantumfield,
        alias=[
            "quantum",
            "field",
            "energy",
            "c"
        ],
        str_defense="",
        str_pet="You pat {slimeoid_name}, and your hand tingles as it passes through the quantum field that surrounds its body.",
        str_abuse="You grab hold of {slimeoid_name} and shake them aggressively, until their quantum static is splayed out and they look nauseous.",
        str_create="You press a button on the armor console labelled 'C'. Through the observation port, start to notice the proto-Slimeoid begin to flicker, and you hear a strange humming sound.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"C\". In front of you, you start to notice the proto-Negaslimeoid begin to flicker, and you hear a strange humming sound.",
        str_armor="It is enveloped in a field of quantum uncertainty.",
        id_resistance=ewcfg.slimeoid_weapon_slam,
        id_weakness=ewcfg.slimeoid_special_laser,
        str_resistance=" {}'s quantum superposition makes it difficult to hit head-on!",
        str_weakness=" {}'s quantum particles are excited by the high-frequency radiation, destabilizing its structure!",

    ),
    EwDefense(  # defense 4
        id_defense=ewcfg.slimeoid_armor_formless,
        alias=[
            "amorphous",
            "shapeless",
            "squishy",
            "d"
        ],
        str_defense="",
        str_pet="You pat {slimeoid_name}, its fluid, shapeless body squishing and deforming in response to even slight pressure.",
        str_abuse="You stick your fist into {slimeoid_name}'s squishy body and jostle its vital organs.",
        str_create="You press a button on the armor console labelled 'D'. Through the observation port, you see the proto-Slimeoid suddenly begin to twist itself, stretching and contracting as its shape rapidly shifts.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"D\". In front of you, you see the proto-Negaslimeoid suddenly begin to twist itself, stretching and contracting as its shape rapidly shifts.",
        str_armor="It is malleable and can absorb blows with ease.",
        id_resistance=ewcfg.slimeoid_weapon_bludgeon,
        id_weakness=ewcfg.slimeoid_special_webs,
        str_resistance=" {}'s squishy body easily absorbs the blows!",
        str_weakness=" {}'s squishy body easily adheres to and becomes entangled by the webs!",

    ),
    EwDefense(  # defense 5
        id_defense=ewcfg.slimeoid_armor_regeneration,
        alias=[
            "healing",
            "regen",
            "e"
        ],
        str_defense="",
        str_pet="You pat {slimeoid_name}. Its skin is hot, and you can feel it pulsing rhythmically.",
        str_abuse="You take a blowtorch to {slimeoid_name}'s pulsating skin and watch as it wears itself out trying to regenerate the rapidly burning tissue.",
        str_create="You press a button on the armor console labelled 'E'. Through the observation port, you see the proto-Slimeoid begin to pulse, almost like a beating heart.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"E\". In front of you, you see the proto-Negaslimeoid begin to pulse, almost like a beating heart.",
        str_armor="It can regenerate damage to its body rapidly.",
        id_resistance=ewcfg.slimeoid_weapon_spikes,
        id_weakness=ewcfg.slimeoid_special_spit,
        str_resistance=" {} quickly begins regenerating the small puncture wounds inflicted by the spikes!",
        str_weakness=" {}'s regeneration is impeded by the corrosive chemicals!",

    ),
    EwDefense(  # defense 6
        id_defense=ewcfg.slimeoid_armor_stench,
        alias=[
            "stink",
            "smell",
            "f"
        ],
        str_defense="",
        str_pet="You pat {slimeoid_name}, taking care not to inhale through your nose, as one whiff of its odor has been known to make people lose their lunch.",
        str_abuse="You try to humiliate {slimeoid_name} by plugging your nose and kicking it around.",
        str_create="You press a button on the armor console labelled 'F'. Through the observation port, you see the proto-Slimeoid give off bubbles of foul-colored gas.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"F\". In front of you, you see the proto-Negaslimeoid give off bubbles of foul-colored gas.",
        str_armor="It exudes a horrible stench.",
        id_resistance=ewcfg.slimeoid_weapon_teeth,
        id_weakness=ewcfg.slimeoid_special_throw,
        str_resistance=" {}'s noxious fumes make its opponent hesitant to put its mouth anywhere near it!",
        str_weakness=" {}'s foul odor gives away its position, making it easy to target with thrown projectiles!",

    ),
    EwDefense(  # defense 7
        id_defense=ewcfg.slimeoid_armor_oil,
        alias=[
            "slick",
            "g"
        ],
        str_defense="",
        str_pet="You pat {slimeoid_name}'s slick wet skin, and your hand comes away coated in a viscous, slippery oil.",
        str_abuse="You turn {slimeoid_name} upside down and push their oily body, sending them slipping down the sidewalk.",
        str_create="You press a button on the armor console labelled 'G'. Through the observation port, you see the surface of the proto-Slimeoid become shiny with some kind of oily fluid.",
        str_create_nega="You move the planchette to spell \"ARMOR\", then move the planchette to \"G\". In front of you, you see the surface of the proto-Negaslimeoid become shiny with some kind of oily fluid.",
        str_armor="It is covered in a coating of slippery oil.",
        id_resistance=ewcfg.slimeoid_weapon_grip,
        id_weakness=ewcfg.slimeoid_special_fire,
        str_resistance=" {}'s slippery coating makes it extremely difficult to grab on to!",
        str_weakness=" {}'s oily coating is flammable, igniting as it contacts the flame!",

    )
]

# A map of id_defense to EwBody objects.
defense_map = {}

# A list of defense names
defense_names = []

# Populate defense map, including all aliases.
for defense in defense_list:
    defense_map[defense.id_defense] = defense
    defense_names.append(defense.id_defense)

    for alias in defense.alias:
        defense_map[alias] = defense

# All special attributes in the game.
special_list = [
    EwSpecial(  # special 1
        id_special=ewcfg.slimeoid_special_spit,
        alias=[
            "spitting",
            "spray",
            "squirt",
            "spraying",
            "squirting",
            "liquid",
            "fluid",
            "acid",
            "acidic",
            "toxic",
            "poison",
            "a"
        ],
        str_special_attack="{active} spits acidic ooze onto {inactive}!",
        str_special_attack_weak="{active} coughs and spurts up a sputtering spray of acid at {inactive}!",
        str_special_attack_coup="{active} vomits a torrent of acid onto {inactive}, deteriorating it to the point that it can no longer fight!",
        str_create="You press a button on the special attack console labelled 'A'. Through the observation port, you see the proto-Slimeoid's body begin to excrete a foul, toxic ooze.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"A\". In front of you, you see the proto-Negaslimeoid's body begin to excrete a foul, toxic ooze.",
        str_special="It can spit acidic ooze.",
        str_observe="A bit of acidic fluid drips from {slimeoid_name} onto the ground, where it smokes and sizzles."
    ),
    EwSpecial(  # special 2
        id_special=ewcfg.slimeoid_special_laser,
        alias=[
            "beam",
            "energy",
            "radiation",
            "b"
        ],
        str_special_attack="{active} sears {inactive} with a blast of radiation!",
        str_special_attack_weak="{active} starts to flicker before firing an unsteady beam of light at {inactive}!",
        str_special_attack_coup="{active} blasts {inactive} with a beam of green energy, searing it all over its body!",
        str_create="You press a button on the special attack console labelled 'B'. Through the observation port, you see the proto-Slimeoid's body begin to glow with energy as the gestation vat's built-in Geiger Counter begins to click frantically.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"B\". In front of you, you see the proto-Negaslimeoid's body begin to glow with energy as the  Ouija® Board's built-in Geiger Counter begins to click frantically.",
        str_special="It can fire beams of radiation.",
        str_observe="{slimeoid_name} suddenly glows with radioactive energy. Best not to look directly at it until it settles down..."
    ),
    EwSpecial(  # special 3
        id_special=ewcfg.slimeoid_special_spines,
        alias=[
            "spikes",
            "spiky",
            "spiny",
            "quills",
            "c"
        ],
        str_special_attack="{active} fires a volley of quills into {inactive}!",
        str_special_attack_weak="{active} desperately fires a few of its last quills into {inactive}!",
        str_special_attack_coup="{active} fires a rapid burst of sharp quills into {inactive}, filling it like a pincushion!",
        str_create="You press a button on the special attack console labelled 'C'. Through the observation port, you see the proto-Slimeoid's congealing body suddenly protruding with long, pointed spines, which quickly retract back into it.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"C\". In front of you, you see the proto-Negaslimeoid's congealing body suddenly protruding with long, pointed spines, which quickly retract back into it.",
        str_special="It can fire sharp quills.",
        str_observe="{slimeoid_name} shudders and ejects a few old quills onto the ground. You can see new ones already growing in to replace them."
    ),
    EwSpecial(  # special 4
        id_special=ewcfg.slimeoid_special_throw,
        alias=[
            "throwing",
            "hurling",
            "hurl",
            "d"
        ],
        str_special_attack="{active} picks up a nearby {object} and hurls it into {inactive}!",
        str_special_attack_weak="{active} unsteadily hefts a nearby {object} before throwing it into {inactive}!",
        str_special_attack_coup="{active} hurls a {object}, which smashes square into {inactive}, knocking it to the ground! A direct hit!",
        str_create="You press a button on the special attack console labelled 'D'. Through the observation port, you see the proto-Slimeoid's limbs become more articulate.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"D\". In front of you, you see the proto-Negaslimeoid's limbs become more articulate.",
        str_special="It can hurl objects at foes.",
        str_observe="{slimeoid_name} is idly picking up stones and seeing how far it can toss them."
    ),
    EwSpecial(  # special 5
        id_special=ewcfg.slimeoid_special_TK,
        alias=[
            "telekinesis",
            "psychic",
            "e"
        ],
        str_special_attack="{active} focuses on {inactive}... {inactive} convulses in pain!",
        str_special_attack_weak="{active}'s cranium bulges and throbs! {inactive} convulses!",
        str_special_attack_coup="{active} emanates a strange static sound as {inactive} is inexplicably rendered completely unconscious!",
        str_create="You press a button on the special attack console labelled 'E'. You momentarily experience an uncomfortable sensation, sort of like the feeling you get when you know there's a TV on in the room even though you can't see it.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"E\". You momentarily experience an uncomfortable sensation, sort of like the feeling you get when you know there's a TV on in the room even though you can't see it.",
        str_special="It can generate harmful frequencies with its brainwaves.",
        str_observe="You momentarily black out. When you come to, your nose is bleeding. {slimeoid_name} tries to look innocent."
    ),
    EwSpecial(  # special 6
        id_special=ewcfg.slimeoid_special_fire,
        alias=[
            "chemical",
            "breath",
            "breathe",
            "f"
        ],
        str_special_attack="{active} ejects a stream of fluid which ignites in the air, burning {inactive}!",
        str_special_attack_weak="{active} fires an unsteady, sputtering stream of fluid that ignites and singes {inactive}!",
        str_special_attack_coup="{active} empties its fluid bladders in a final burst of liquid! {inactive} is completely engulfed in the conflagration!",
        str_create="You press a button on the special attack console labelled 'F'. Through the observation port, you see fluid bladders forming deep under the still-forming proto-Slimeoid's translucent skin.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"F\". In front of you, you see fluid bladders forming deep under the still-forming proto-Negaslimeoid's translucent skin.",
        str_special="It can fire a stream of pyrophoric fluid at its foes.",
        str_observe="A bit of fluid drips from {slimeoid_name} onto the floor and ignites, but you manage to smother the small flame quickly before it spreads."
    ),
    EwSpecial(  # special 7
        id_special=ewcfg.slimeoid_special_webs,
        alias=[
            "webbing",
            "web",
            "g"
        ],
        str_special_attack="{active} fires a stream of sticky webbing onto {inactive}!",
        str_special_attack_weak="{active} is running out of webbing! It shoots as much as it can onto {inactive}!",
        str_special_attack_coup="{active} gathers itself up before spurting a blast of webbing that coats {inactive}'s body, completely ensnaring it!",
        str_create="You press a button on the special attack console labelled 'G'. Through the observation port, you see large glands forming near the surface of the still-forming proto-Slimeoid's translucent skin.",
        str_create_nega="You move the planchette to spell \"SPECIAL\", then move the planchette to \"G\". In front of you, you see large glands forming near the surface of the still-forming proto-Negaslimeoid's translucent skin.",
        str_special="It can spin webs and shoot webbing fluid to capture prey.",
        str_observe="{slimeoid_name} is over in the corner, building itself a web to catch prey in."
    )
]

# A map of id_special to EwBody objects.
special_map = {}

# A list of special names
special_names = []

# Populate special map, including all aliases.
for special in special_list:
    special_map[special.id_special] = special
    special_names.append(special.id_special)

    for alias in special.alias:
        special_map[alias] = special


def get_strat_a(combat_data, in_range, first_turn, active):
    base_attack = 30
    base_evade = 10
    base_block = 10

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 3
            weight_block *= 2
        else:
            weight_block *= 3

    else:
        if active:
            weight_evade *= 2
        else:
            weight_evade *= 5

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.8))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_b(combat_data, in_range, first_turn, active):
    base_attack = 20
    base_evade = 10
    base_block = 10

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 3
            weight_block *= 2
        else:
            weight_block *= 2
            weight_evade *= 3

    else:
        if active:
            weight_attack *= 3
            weight_evade *= 3
        else:
            weight_evade *= 4
            weight_block *= 2

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.65))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_c(combat_data, in_range, first_turn, active):
    base_attack = 30
    base_evade = 10
    base_block = 10

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 3
        else:
            weight_block *= 2
            weight_evade *= 2

    else:
        if active:
            weight_attack *= 3
        else:
            weight_evade *= 2
            weight_block *= 2

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.8))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_d(combat_data, in_range, first_turn, active):
    base_attack = 20
    base_evade = 5
    base_block = 15

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 3
        else:
            weight_attack /= 2
            weight_block *= 2

    else:
        if active:
            weight_attack *= 3
        else:
            weight_attack /= 2
            weight_block *= 2

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.35))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_e(combat_data, in_range, first_turn, active):
    base_attack = 20
    base_evade = 10
    base_block = 10

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 2
            weight_evade *= 2
        else:
            weight_evade *= 4

    else:
        if active:
            weight_attack *= 4
            weight_block *= 2
        else:
            weight_block *= 3

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.65))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_f(combat_data, in_range, first_turn, active):
    base_attack = 20
    base_evade = 20
    base_block = 10

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 3
            weight_evade *= 2
        else:
            weight_evade *= 3
            weight_block *= 2

    else:
        if active:
            weight_attack *= 4
            weight_block *= 2
        else:
            weight_block *= 3
            weight_evade *= 2

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.35))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


def get_strat_g(combat_data, in_range, first_turn, active):
    base_attack = 10
    base_evade = 15
    base_block = 5

    weight_attack = base_attack
    weight_evade = base_evade
    weight_block = base_block

    if in_range:
        if active:
            weight_attack *= 4
        else:
            weight_evade *= 2

    else:
        if active:
            weight_attack *= 4
        else:
            weight_evade *= 2

    strat = random.randrange(weight_attack + weight_evade + weight_block)
    if strat < weight_attack:
        strat_used = ewcfg.slimeoid_strat_attack
    elif strat < weight_attack + weight_evade:
        strat_used = ewcfg.slimeoid_strat_evade
    else:
        strat_used = ewcfg.slimeoid_strat_block

    if first_turn:
        sap_spend = int(random.triangular(0, combat_data.sap, int(combat_data.sap * 0.2))) + 1

    else:
        sap_spend = combat_data.sap

    sap_spend = min(sap_spend, combat_data.sap)

    return strat_used, sap_spend


# All brain attributes in the game. 1-7 are for slimeoids, 8-14 for negaslimeoids
brain_list = [
    # Slimeoid brains

    EwBrain(  # brain 1
        id_brain="a",
        alias=[
            "typea",
            "type a"
        ],
        str_create="You press a button on the brain console labelled 'A'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to move, thrashing about as if in frustration.",
        str_brain="It is extremely irritable.",
        str_observe="{slimeoid_name} is snarling. You're not sure if it's angry at you, or at the world in general.",
        str_pet="{slimeoid_name} hisses at you.",
        str_walk="You wrestle {slimeoid_name} down and force a leash onto it, as it angrily snarls and hisses at you in protest.",
        str_feed="{slimeoid_name} almost bites your hand off as you offer the {food_name} to it! It growls at you before eating, as if to secure its prey.",
        str_kill="{slimeoid_name} howls with savage delight at the bloodshed!!",
        str_death="{slimeoid_name} howls in fury at its master's death! It tears away in a blind rage!",
        str_victory="{slimeoid_name} roars in triumph!!",
        str_battlecry="{slimeoid_name} roars with bloodlust!! ",
        str_battlecry_weak="{slimeoid_name} is too breathless to roar, but is still filled with bloodlust!! ",
        str_movecry="{slimeoid_name} snarls at its prey! ",
        str_movecry_weak="{slimeoid_name}  hisses with frustrated rage! ",
        str_revive="{slimeoid_name} howls at your return, annoyed to have been kept waiting.",
        str_spawn="{slimeoid_name} shakes itself off to get rid of some excess gestation fluid, then starts to hiss at you. Seems like a real firecracker, this one.",
        str_dissolve="{slimeoid_name} hisses and spits with fury as you hold it over the N.L.A.C.U Dissolution Vats. Come on, get in there...\n{slimeoid_name} claws at you, clutching at the edge of the vat, screeching with rage even as you hold its head under the surface and wait for the chemical soup to do its work. At last, it stops fighting.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_a,
        str_abuse="{slimeoid_name} lashes out, trying to fight back."

    ),
    EwBrain(  # brain 2
        id_brain="b",
        alias=[
            "typeb",
            "type b"
        ],
        str_create="You press a button on the brain console labelled 'B'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to move about its gestation tank, exploring its surroundings.",
        str_brain="It is enthusiastic about almost everything.",
        str_observe="{slimeoid_name} notices you looking at it and seems delighted!",
        str_pet="{slimeoid_name} purrs happily.",
        str_walk="{slimeoid_name} is so excited for its walk, it can barely hold still enough to let you put the leash on it!",
        str_feed="{slimeoid_name} starts running circles around you and drooling uncontrollably in anticipation as soon as you reach for the {food_name}.",
        str_kill="{slimeoid_name} gives a bestial woop of excitement for your victory!",
        str_death="{slimeoid_name} gives a wail of grief at its master's death, streaking away from the scene.",
        str_victory="{slimeoid_name} woops with delight at its victory!",
        str_battlecry="{slimeoid_name} lets out a loud war woop! ",
        str_battlecry_weak="{slimeoid_name} is determined not to lose! ",
        str_movecry="{slimeoid_name} is thrilled by the battle! ",
        str_movecry_weak="{slimeoid_name} seems a little less thrilled now... ",
        str_revive="{slimeoid_name} is waiting patiently downtown when you return from your time as a corpse. It knew you'd be back!",
        str_spawn="{slimeoid_name} gets up off the ground slowly at first, but then it notices you and leaps into your arms. It sure seems glad to see you!",
        str_dissolve="You order {slimeoid_name} into the Dissolution Vats. It's initially confused, but realization of what you're asking slowly crawks across its features.\nIt doesn't want to go, but after enough stern commanding, it finally pitches itself into the toxic sludge, seemingly too heartbroken to fear death.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_b,
        str_abuse="{slimeoid_name} yelps in pain. It's beside itself and doesn't know what to do..."
    ),
    EwBrain(  # brain 3
        id_brain="c",
        alias=[
            "typec",
            "type c"
        ],
        str_create="You press a button on the brain console labelled 'C'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid draws its congealing body together, as if trying to gather its strength.",
        str_brain="It is quiet and withdrawn.",
        str_observe="{slimeoid_name} seems to be resting, possibly deep in thought.",
        str_pet="{slimeoid_name} doesn't react.",
        str_walk="{slimeoid_name} holds still as you place the leash on it. It regards the leash, seemingly pontificating.",
        str_feed="{slimeoid_name} shows neither happiness nor reluctance as you offer the {food_name}. It accepts the treat as though it were a mere formality.",
        str_kill="{slimeoid_name} regards the corpse of your former adversary with an unknowable expression.",
        str_death="{slimeoid_name} stares at the killer, memorizing their face before fleeing the scene.",
        str_victory="{slimeoid_name} silently turns away from its defeated opponent.",
        str_battlecry="{slimeoid_name} carefully regards its opponent. ",
        str_battlecry_weak="{slimeoid_name} tries to steady itself. ",
        str_movecry="{slimeoid_name} seems to be getting impatient. ",
        str_movecry_weak="{slimeoid_name} is losing its composure just a little! ",
        str_revive="{slimeoid_name} is downtown when you return from the sewers. You find it staring silently up at ENDLESS WAR.",
        str_spawn="{slimeoid_name} regards you silently from the floor. You can't tell if it likes you or not, but it starts to follow you regardless.",
        str_dissolve="You pick up {slimeoid_name} and hurl it into the N.L.A.C.U. Dissolution Vats before it starts to suspect anything. It slowly sinks into the chemical soup, kind of like Arnold at the end of Terminator 2, only instead of giving you a thumbs-up, it stares at you with an unreadable expression. Betrayal? Confusion? Hatred? Yeah, probably.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_c,
        str_abuse="You can feel {slimeoid_name} trembling, but it just takes your abuse."
    ),
    EwBrain(  # brain 4
        id_brain="d",
        alias=[
            "typed",
            "type d"
        ],
        str_create="You press a button on the brain console labelled 'D'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid lazily turns over in its gestation vat, floating and doing little else.",
        str_brain="It is usually staring off into space.",
        str_observe="{slimeoid_name} stares off into the distance. Who knows if it's actually looking at anything in particular.",
        str_pet="{slimeoid_name} is startled out of a stupor by your touch.",
        str_walk="{slimeoid_name} hardly seems to notice you fastening it with a leash.",
        str_feed="You have to literally shove the {food_name} into {slimeoid_name}'s face to get its attention. It takes a moment to recover its orientation before accepting the treat.",
        str_kill="{slimeoid_name} wasn't paying attention and missed the action.",
        str_death="{slimeoid_name} is startled to realize its master has died. It blinks in confusion before fleeing.",
        str_victory="{slimeoid_name} keeps attacking for a moment before realizing it's already won.",
        str_battlecry="{slimeoid_name} is weighing its options! ",
        str_battlecry_weak="{slimeoid_name} is desperately trying to come up with a plan! ",
        str_movecry="{slimeoid_name} isn't really feeling this. ",
        str_movecry_weak="{slimeoid_name} tries to buy itself some time to think! ",
        str_revive="{slimeoid_name} is exactly where you left it when you died.",
        str_spawn="{slimeoid_name} flops over on the floor and stares up at you. Its gaze wanders around the room for a while before it finally picks itself up to follow you.",
        str_dissolve="You lead {slimeoid_name} up to the edge of the Dissolution Vats and give a quick 'Hey, look, a distraction!'. {slimeoid_name} is immediately distracted and you shove it over the edge. Landing in the vat with a sickening *gloop* sound, it sinks quickly under the fluid surface, flailing madly in confusion and desperation.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_d,
        str_abuse="You have a hard time with it, {slimeoid_name} is panicked and keeps trying to run."
    ),
    EwBrain(  # brain 5
        id_brain="e",
        alias=[
            "typee",
            "type e"
        ],
        str_create="You press a button on the brain console labelled 'E'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid starts to sporadically twitch and shiver.",
        str_brain="It is extremely skittish and jumpy.",
        str_observe="{slimeoid_name} is glancing around furtively, seemingly scanning for threats.",
        str_pet="{slimeoid_name} flinches nervously at your touch.",
        str_walk="{slimeoid_name} shivers in place as you're fastening the leash, then starts to pull and tug at it, seemingly perturbed.",
        str_feed="{slimeoid_name} backs up anxiously as you reach out with the {food_name} in your hand. You sigh and take a bite of the treat yourself to convince {slimeoid_name} that its not poisoned. It reluctantly accepts the {food_name} and starts nibbling at it.",
        str_kill="{slimeoid_name} peers out from behind its master, hoping the violence is over.",
        str_death="{slimeoid_name} is overcome with terror, skittering away from the killer in a mad panic!",
        str_victory="{slimeoid_name} is deeply relieved that the battle is over.",
        str_battlecry="{slimeoid_name} chitters fearfully! ",
        str_battlecry_weak="{slimeoid_name} squeals in abject terror! ",
        str_movecry="{slimeoid_name} makes a break for it! ",
        str_movecry_weak="{slimeoid_name} is in a full-blown panic! ",
        str_revive="{slimeoid_name} peeks out from behind some trash cans before rejoining you. It seems relieved to have you back.",
        str_spawn="{slimeoid_name}'s eyes dart frantically around the room. Seeing you, it darts behind you, as if for cover from an unknown threat.",
        str_dissolve="{slimeoid_name} is looking around the lab nervously, obviously unnerved by the Slimeoid technology. Its preoccupation makes it all too easy to lead it to the Dissolution Vats and kick its legs out from under it, knocking it in. As it falls and hits the solvent chemicals, it wails and screeches in shock and terror, but the noise eventually quiets as it dissolves into a soft lump, then disintegrates altogether.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_e,
        str_abuse="{slimeoid_name} is squealing in horror. It will remember this..."
    ),
    EwBrain(  # brain 6
        id_brain="f",
        alias=[
            "typef",
            "type f"
        ],
        str_create="You press a button on the brain console labelled 'F'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid darts to the opposite side of the gestation vat. You're not sure, but you feel like it's watching you.",
        str_brain="It acts secretive, as though it's up to something.",
        str_observe="{slimeoid_name} is moving around, apparently searching for... something.",
        str_pet="{slimeoid_name} seems nonplussed, but doesn't object.",
        str_walk="{slimeoid_name} exasperatedly lets you fit it with a leash for a walk.",
        str_feed="{slimeoid_name} only seems to halfway pay attention as you offer the {food_name}. It pockets the treat for later and eats it when it thinks you aren't looking.",
        str_kill="{slimeoid_name} rifles through your victim's pockets for food.",
        str_death="{slimeoid_name} rifles through its dead master's pockets for whatever it can find before slinking away.",
        str_victory="{slimeoid_name} shakes itself off after the battle.",
        str_battlecry="{slimeoid_name} makes its move! ",
        str_battlecry_weak="{slimeoid_name}, backed into a corner, tries to counterattack! ",
        str_movecry="{slimeoid_name} decides on a tactical repositioning. ",
        str_movecry_weak="{slimeoid_name} thinks it'd better try something else, and fast! ",
        str_revive="{slimeoid_name} starts following you around again not long after you have returned from the dead.",
        str_spawn="{slimeoid_name} picks itself up off the floor and regards you coolly. It seems as if it's gauging your usefulness.",
        str_dissolve="{slimeoid_name} eyes you suspiciously as you approach the Dissolution Vats. It's on to you. Before it has a chance to bolt, you grab it, hoist it up over your head, and hurl it into the chemical soup. {slimeoid_name} screeches in protest, sputtering and hissing as it thrashes around in the vat, but the chemicals work quickly and it soon dissolves into nothing.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_f,
        str_abuse="{slimeoid_name}'s fear grows as it desperately looks for an escape."
    ),
    EwBrain(  # brain 7
        id_brain="g",
        alias=[
            "typeg",
            "type g"
        ],
        str_create="You press a button on the brain console labelled 'G'.\nA cluster of neurons coagulates within your newly-forming Slimeoid. The proto-Slimeoid begins to flit around the gestation vat, seemingly unsure where to go.",
        str_brain="It seems to have no idea what it's doing.",
        str_observe="{slimeoid_name} seems unsure of whether it wants to wander around or just stay put.",
        str_pet="{slimeoid_name} seems confused about how to react.",
        str_walk="{slimeoid_name} lets you put its leash on it, but immediately starts to trip over it and get tangled in it.",
        str_feed="{slimeoid_name} stares at the {food_name} like it's unfamiliar with the concept of food. You make a chewing motion with your mouth to demonstrate. It still seems confused. You lose your patience and force-feed the treat to your slimeoid.",
        str_kill="{slimeoid_name} seems unsure of whether to celebrate the victory or to mourn the decline of your civilization into rampant youth violence.",
        str_death="{slimeoid_name} starts to approach its master's body, then changes its mind and starts to run away. It trips over itself and falls on its way out.",
        str_victory="{slimeoid_name} looks around, apparently shocked that it somehow won.",
        str_battlecry="{slimeoid_name} decides to actually do something for once! ",
        str_battlecry_weak="{slimeoid_name} decides to actually do something for once, now that it's probably too late.",
        str_movecry="{slimeoid_name} is moving around aimlessly! ",
        str_movecry_weak="{slimeoid_name} is limping around aimlessly! ",
        str_revive="{slimeoid_name} wanders by, seemingly by accident, but thinks it probably ought to start following you again.",
        str_spawn="{slimeoid_name} starts to pick itself up off the floor, then changes its mind and lies back down. Then it gets up again. Lies down again. Up. Down. Up. Ok, this time it stays up.",
        str_dissolve="{slimeoid_name} is perplexed by the laboratory machinery. Taking advantage of its confusion, you point it towards the Dissolution Vats, and it gormlessly meanders up the ramp and over the edge. You hear a gloopy SPLOOSH sound, then nothing. You approach the vats and peer over the edge, but see no trace of your former companion.\n\n{slimeoid_name} is no more.",
        get_strat=get_strat_g,
        str_abuse="{slimeoid_name} still hasn't caught up to all this chaos, and is lost and confused."
    ),

    # Negaslimeoid Brains
     
    EwBrain(  # brain 8
        id_brain="h",
        alias=[
            "typeh",
            "type h"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"A\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. The proto-Negaslimeoid stares at you maliciously.", 
        str_brain="It exudes malevolence.",
        str_observe="{slimeoid_name} is quietly shaking. Poor guy, probably has a fever!",
        str_pet="{slimeoid_name} bites your arm! Shit!",
        str_walk="You carefully put a leash around {slimeoid_name}, sure to keep your distance.",
        str_feed="{slimeoid_name} takes the {food_name} from you calmly! It tosses it on the street, catching the attention of another nearby slimeoid. As the slimeoid eats the {food_name}, {slimeoid_name} dives in.",
        str_kill="unused",
        str_death="unused",
        str_victory="{slimeoid_name} is content standing above their prey.",
        str_battlecry="{slimeoid_name} takes control of the situation. ",
        str_battlecry_weak="{slimeoid_name} tries to take control of the situation. ",
        str_movecry="{slimeoid_name} stares daggers at its prey. ",
        str_movecry_weak="{slimeoid_name} shakes violently in anger. ",
        str_revive="unused",
        str_spawn="{slimeoid_name} picks itself up off the floor, then stares at you with an empty expression. You should probably keep a careful eye on this one.",
        str_dissolve="unused",
        get_strat=get_strat_a,
        str_abuse="{slimeoid_name} takes the blow before charging at you. You barely avoid its gnashing!"
    ),
    EwBrain(  # brain 9
        id_brain="i",
        alias=[
            "typei",
            "type i"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"B\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. The proto-Negaslimeoid begins muttering self-affirmations.",
        str_brain="It's admiring itself.",
        str_observe="{slimeoid_name} notices you looking at it and starts showing off.",
        str_pet="{slimeoid_name} loves the attention.",
        str_walk="{slimeoid_name} makes sure to look its best before being leashed.",
        str_feed="{slimeoid_name} grabs the {food_name} quickly, before carefully eating it in a photogenic way. It makes sure to snap a few photos for its Instagrime.",
        str_kill="unused",
        str_death="unused",
        str_victory="{slimeoid_name} boasts about its victory loudly.",
        str_battlecry="{slimeoid_name} throws an insult at the opponent! ",
        str_battlecry_weak="{slimeoid_name} throws slurs at the opponent! Yikes! ",
        str_movecry="{slimeoid_name} prattles on about their strength! ",
        str_movecry_weak="{slimeoid_name} prattles on about their superiority! ",
        str_revive="unused",
        str_spawn="{slimeoid_name} rolls off the floor. From seemingly nowhere, {slimeoid_name} pulls out a gellphone and sets up a Slime Twitter. It begins to move about the Waffle House, seeking drama.",
        str_dissolve="unused",
        get_strat=get_strat_b,
        str_abuse="{slimeoid_name} screams in terror! Expect a 5-part docuseries on this interaction shortly."
    ),
    EwBrain(  # brain 10
        id_brain="j",
        alias=[
            "typej",
            "type j"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"C\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. The proto-Negaslimeoid starts to roll around on the floor, looking for a dark space.",
        str_brain="It is raucous and withdrawn.",
        str_observe="{slimeoid_name} jeers at passerbys, hissing at couples, women, and attractive men.",
        str_pet="{slimeoid_name} is wayyyyyyyyy too into this.",
        str_walk="{slimeoid_name} sniffles as you rope a leash around it. It preens itself, preparing for a trick encounter.",
        str_feed="{slimeoid_name} absolutely tears through the {food_name}. Not even crumbs remain.",
        str_kill="unusued",
        str_death="unused",
        str_victory="{slimeoid_name} can't bask in the victory.",
        str_battlecry="{slimeoid_name} starts sending hate mail! ",
        str_battlecry_weak="{slimeoid_name} starts sending death threats. ",
        str_movecry="{slimeoid_name} posts on SlimeChan about how loose their enemy is. ",
        str_movecry_weak="{slimeoid_name} cries in agony! ",
        str_revive="unused",
        str_spawn="{slimeoid_name} gets up, walks to the counter, and orders a Wet Waffle. Sitting down, they begin harassing women online while eating the absolutely nasty waffle. It completely ignores your existence.",
        str_dissolve="unused",
        get_strat=get_strat_c,
        str_abuse="{slimeoid_name} gets smacked across the street. Just, like, absolutely launched."
    ),
    EwBrain(  # brain 11
        id_brain="k",
        alias=[
            "typek",
            "type k"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"D\". \nA cluster of antineurons begins coagulating, but is ripped apart by the proto-Negaslimeoid's developing body. Oh shit, dude! You're pretty sure there's now no brain at all within the proto-Negaslimeoid.",
        str_brain="Its only actions are autonomous body processes.",
        str_observe="{slimeoid_name} stands unmoving",
        str_pet="{slimeoid_name} is unreactive to your touch.",
        str_walk="{slimeoid_name} stands as you leash it. You pull it along.",
        str_feed="You have to shove the {food_name} into {slimeoid_name}'s mouth for it to begin chewing. It makes no noise as it swallows.",
        str_kill="unused",
        str_death="unused",
        str_victory="{slimeoid_name} stands unmoving.",
        str_battlecry="{slimeoid_name} stands unmoving. ",
        str_battlecry_weak="{slimeoid_name} slouches unmoving. ",
        str_movecry="{slimeoid_name} moves autonomously. ",
        str_movecry_weak="{slimeoid_name} crawls autonomously ",
        str_revive="unused",
        str_spawn="{slimeoid_name} stands up. It exists in the Waffle House, but within its shell is nothing. It follows your every command. ",
        str_dissolve="unused",
        get_strat=get_strat_d,
        str_abuse="{slimeoid_name} is hit, but has no reaction."
    ),
    EwBrain(  # brain 12
        id_brain="l",
        alias=[
            "typel",
            "type l"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"E\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. But a Waffle House worker notices your conjuration, and tosses a burnt waffle at the proto-Negaslimeoid! It painfully smacks the side of the undulating proto-Negaslimeoid, and the entire anticreature recoils.",
        str_brain="It's terrified of others.",
        str_observe="{slimeoid_name} is hiding from everyone around it.",
        str_pet="{slimeoid_name} recoils from your touch.",
        str_walk="{slimeoid_name} runs from your leash, before dejectedly being backed into a corner. It soullessly follows along during the walk.",
        str_feed="{slimeoid_name} backs up anxiously as you reach out with the {food_name} in your hand. You just toss the {food_name} at {slimeoid_name}, slamming it into its side. It cries in pain, before eating the food.",
        str_kill="unused",
        str_death="unused",
        str_victory="{slimeoid_name} stands still, unhappy.",
        str_battlecry="{slimeoid_name} screams incredibly loudly. ",
        str_battlecry_weak="{slimeoid_name} screaches incredibly loudly. ",
        str_movecry="{slimeoid_name} skitters away! ",
        str_movecry_weak="{slimeoid_name} skitters away quietly. ",
        str_revive="unused",
        str_spawn="{slimeoid_name}'s eyes dart frantically around the room. It sees you and carefully approaches, before the Waffle House worker comes back! She smacks the shit out of {slimeoid_name} with a spatula, before running to the back to grab some fryer grease. It'd probably be best if you got out of here.",
        str_dissolve="unused",
        get_strat=get_strat_e,
        str_abuse="{slimeoid_name} takes the hit, crying."
    ),
    EwBrain(  # brain 13
        id_brain="m",
        alias=[
            "typem",
            "type m"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"F\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. The proto-Negaslimeoid looks up towards you from the floor, watching your every move.",
        str_brain="It's silently observing all those around it.",
        str_observe="You go to look at {slimeoid_name}, but it was already staring at you. Unblinking.",
        str_pet="{slimeoid_name} looks at your hand. You're a bit too unsettled to actually pet it.",
        str_walk="{slimeoid_name} gets put on a leash, and moves along with you, staring at its surroundings.",
        str_feed="{slimeoid_name} only looks at the {food_name}. You mimic eating the food, and eventually {slimeoid_name} begins to slowly peck at it.",
        str_kill="unused",
        str_death="unused",
        str_victory="{slimeoid_name} looks at the remains of its opponent, unmoving.",
        str_battlecry="{slimeoid_name} lets out a quiet coo. ",
        str_battlecry_weak="{slimeoid_name} sheds single tear. ",
        str_movecry="{slimeoid_name} tactically stays within range!. ",
        str_movecry_weak="{slimeoid_name} tries to tactically stay within range. ",
        str_revive="unused",
        str_spawn="{slimeoid_name} carefully picks itself up, then looks at you. It looks out the blackened windows of Waffle House, chittering at its reflection. It doesn't seem to like this place.",
        str_dissolve="unused",
        get_strat=get_strat_f,
        str_abuse="{slimeoid_name} saw your abuse coming, but isn't fast enough to get beat up."
    ),
    EwBrain(  # brain 14
        id_brain="n",
        alias=[
            "typen",
            "type n"
        ],
        str_create="You move the planchette to spell \"BRAIN\", then move the planchette to \"G\". \nA cluster of antineurons coagulates within your newly-forming Negaslimeoid. The proto-Negaslimeoid begins muttering incomprehensibly.",
        str_brain="It's muttering  ̷̢̧̛̞̮͕̫͂̀͐̅̀̏̓̏̽̅͋̈́̌̃̽͘͘̚͝͠͝▐̷̨̢̲͙̦̤̮̞͈̠̬͖̀̈̂̅͗̑̓͝▄̸̡̧̧̛̱͓̜͍͎̹̟̣̰̞̤̹̝̹̼̘̺̳̈́̔́͑͐̑͋͛̆̄̅̍͘͝█̷̧̨̛͉͚̟͍̙͓̻͖̝̗̅́͊͜ ̶̡̗̺̦͉̲̝̼͗͗█̶̠̗͔͙͖̺̣̑̃͌̆̑̒͂͗̾̒̋̔͛̚̕ ̴̢̨̰̝͇̘͒́̔̀̉͆̇͝▮̸̧̛̛̜̱͇̰͙͉̩̭̘̠̞̹̜̳̤͖̯͚̳̇̃̄̇̏̐̈́͒͂͋̑͊̎͆͠⯊̶̡̛̘͕͈̀͆̅̍͂͌͠  to itself.",
        str_observe="{slimeoid_name} is seeking children to torment, trying to incur upon them nightmares.",
        str_pet="In exchange for the pets, {slimeoid_name} mutters ░̸̢̡̡̢̻̯̱̗̤͔͈̯̮̞͙̱̹͔̹͍̱̜͖̱̭̰̖͇̦̝̣̝̓̒̓̈́͒̈́̍̿́͂̊́̏̏̂͋̑̍͒̓̋̐̌̀̃̇̾͊͘͜͝▄̵̧̨̛͚̟͉̬͚̩̹̝̪̜͉͕͙͔̭͇̻̘̰͎̠̳̦̫̥̤̘̆͋̀̌̾͑̓̉̓̆͗̀̔̆́͌̐͘̕͜͜͠͝▀̵̨̗̟̩̺͗͒͑̂͂̍͑͌̄͐̿̀͐̽̋̒̊̎̂͌̂̓̚͠͝▄̵̧̡̢͕̱͎̝̭̹̖͙̺͍̤͎̮͈͖̟͎̤̞͔̖͇͔͙̐̀͆̈́̓̽̋͑͊̂͐̎͛̅̏́̏̃͒͗̂͐͊͒͒́̓̋͛̀̃͂̓̾̓̐͑̅̀̅̐͆̒̆͘͝ͅ░̴̨̢̢̡̛̘̘̜͚̩͚̠̦͔̜̘̙͍̻̥͖̱͓̞͓̫̩͚̥̰̫̪̩̰̙̟͔̰͚͍̆̏͐̆̋̐̇͒͊̌͂̈́͂̓͊̽́̌̅͋͗̍̒̀͋̍͆̈́̋̃̏̂́͂̒̐̈̓̓̿͋̕͘͜͝͝▀̶̧̢̧̡͚̲̳͓̥̱̤̝̱͓̼͇̟͓͓̬̮̮̼̱͕͙̖̙͍͉̲͔̘͔̉̐͊̇̿̌̂̋̀̾̇́̿̔͛̓͛͐͗́̈́̓̕̚̕͜͜͝͝͝ͅ█̶̡̨̧̟̹̮̭̪͈͙̣̙̖͉͍̱̭͙̭̪̣͇̱͎̺͆̌̏̎̆̽́͒̇́̽̉̊͂̿̈́̔͆̚͝░̴̢̨̛͉̖̯͇͓̭̘͈̮̹̳̼͔̦̟̻̦̥̼̬̯͚̜̭̯͉̠̤̦̩̫̿̓̚͝ͅͅͅͅ█̴̬̬̘͙̪̽̎̂̓̋̓̈́́̈́̈́̏̄̑̄̆̈́̑́̾̕̚͝͠͠͠▀̶̧̢̢̢̠̟̣̖̼̲̞̙̫͔̫̯̪͈͖̙͔͕̈́͒͌͋͛̓̔̒̈̾̈̐̍̀̋̓̋̃̿̈̀̏̀̀̐͗͑̑͑̊̎̇͌̈́͋̕͘͝͝ͅ▄̵̧̧̢̢̧̨̧̡̜͔̱̙̞̱̙̠͚̱͙͈̹͓̰̥͎̗̲̹̪͎̳̯̜̯̣̟̜̖̳̤̙̤̽̅̽̀̓̕̕͜ͅ░̴̡̢̢̡̡̛̲͙͖͍͈̭̣̬̰͙̩͋̏̃̑̎̉͊̊̎̌̍̈́̂͐́͛́͆̿̇͊̏͌͋͛̋̕͘͜͜͠͝͝█̵̢̢̢̡͎̲̟͔͓̥̘̙̠̠͖̝̭͇̮̟̙̗̳̳̞̗̜͐͑́̃͂͂̒̋͑̕͘̚͜͠͝ͅͅ  in your ear. It's strangely comforting.",
        str_walk="Once leashed, {slimeoid_name} follows alongside you slowly. You feel like you're walking mor̶e than just it.",
        str_feed="{slimeoid_name} begins eating the {food_name} without much instruction. With each bite, it sputters out ඞ̵̨̧̥̫͕̰͉͖̥̈̏̀̽̆░̸͖͉̮̼͎̜̦̻͖̓̍̐̿̒̄̃͜ͅ░̵̵̧̢̯̲͇͕̤̩͇̺̳̲̫̺̺̽̓̈́̃̏̏͜͝▒̸̡̡̢͔̲̤̖̮̺̖̘̄̓̀͠░̴̺̥̥͉̩̞͊̀͜ . Kinda spooky.",
        str_kill="ǘ̴͔͉̋n̸̝̈́̊u̷̧̱̎s̸̹̎e̴̮͝d̴̠̬̎",
        str_death="ǘ̴͔͉̋n̸̝̈́̊u̷̧̱̎s̸̹̎e̴̮͝d̴̠̬̎",
        str_victory="{slimeoid_name} steals the losing slimeoid's soul. Not like it's worth anything, though.",
        str_battlecry="{slimeoid_name} screams ·̵̳̄̈͊͝▄̴̼͙̯͚̓̽̚͝▄̷̢̱͈̳̠̩͉͌͜▄̸̛͙̣̙͕̇͌̐͒̚▄̴̥̘̗̺̍̅̍̓̌̕ ̴̢̛̲̣̻́̊̽̔ ̸̡̡̰̘̮̿̉̅̃͠͠▪̷̨̺̲̞̳̳͗̇̓̊̄̕͝ ̷͇̫͉̉̎ ̶̰̏̕▄̴̹̺͕̱̠͒̓̋ͅ▄̸͔̾̅̔̂̌͘̕▄̵̮̣̩̫̓͆̏̈͌̿ ̷͔̯̏̓̈́̓͐̋̿͌.̵̷͙̻͇̣̩̼̟͐̿́̎̿͋͆̎█̶͎̜͇͓͗͆͐█̴͈̖̰̟̦̻̈́͗̄̓͂͗̊͜ͅ▪̸͓̹̭̖̰͚̎̑̏̌̎͝ ̶̜̰̲̹̰͆̈̍̈́ͅ!!",
        str_battlecry_weak="{slimeoid_name} roars  ̴̨̘̻̳͙͖̼͇̺̜̘͖̠̅̓̃̂̓̉̋̀͗̋̌̕͘̚͝͝|̷͉̖̬̠̱̣̳̣̗̗̗̎̾̌̑̃̊̈́͋̏͗̈́͗͗͑́̈́͌̓̃̉͝͝ͅͅ ̸̛͕̭͒́͛̇́́́̋̾̂͑̾̓̈́̂̈̑̂̿̏͊̄͌̆̉̾̓̽̄̋͜͝/̷̧̨̛̭̳̥̰̥͇͙͇̗̠̗̱̥̫̱̫̙͔̥̦͎͓̩̬̯̻̥͈͈͔̟̮͙͉́̍̂̊̀̌͋̀̈̈͆̂̇͒͆́̆̋̈́̕͠ͅͅ ̴̧̡̧̛̛̼̣̹̳̫̺̘̳͕͎̤̱͈͓̬̮̟͓͎̟̭̭̹͚̱̪̣̞̜͂́̄́̏̓̒́͊͌̍̿́́̌̈́͆͊̉̋͘͝ͅͅ_̴̡̨̧̡̡̡̛͓̜̙̞̻̗̼̦̦͔̱̪͈̼͖̭͕̗̗̘̱̗͕͈̰͔̑̃̂̈́͒̍͊̒̾͊̃̒͐́͑̑̄̓̏̆̏͗̏̑̑̏͒͐̒̂̀̂̽̈́͊̚͜͝͝͠͝░̷̛̩̹͈̪͉̹̂̔̽̀̑̇̽͌̅̒̌̍͂͂̏͆̎͆̾͐͑̊̃̾͘̕̚͝͝͠▒̵̡̧̨̡̡̜͚̟̗̯̹̙͔̻̖̥̳͓͔̰̲̥̱̥̳̖͈̻͔̭̟͙̙̺̙̙͙͆̀̇̒̄̒͐̊̎̀̀̌̈́͌̔̋̽͘͠͠▓̵̨̧͓͕̮̤̩̥̞͎͚͚̲͙͗͒̎̓́͑̑̓̓͆̽̔͂̔̿̒̏̂́̾̀́̐̽͐̇͂̄̄͂̈́̈́̀́̇̈́͋̃̚͠͝░̴̧̡̢̟͎͓͇͉̜̰̳͇̮͈͍̟͓̩̗͔̪̜̊͆̀̈́̐̒̊̎̄̈́͂̌̇̆̾́̂̊͌̄̒̈̓̉̽̒̎̉͋́̂͘͜͜͠͠͝▒̸̢̞͔̳͕͙̪̫̬̣̙͔͓̩̟̭̩̯͇͇̖̱̗̬͉̲͗͐̓̾̽͛́͗̄̃̕͠ !",
        str_movecry="{slimeoid_name} communes before making a move. ",
        str_movecry_weak="{slimeoid_name} calls for ̴̹̫̤́͑͑▐̶̣́͂▅̴̛͈͓̲̄̈́▚̶̗̬̫͂▾̶̻̱͝ ̵̦̑̂̔ ̷̹̬̝̑̾͛▅̷̡̯̫̌̉▀̷͉̪̜͊͘  by name, but gets no response! ",
        str_revive="ǘ̴͔͉̋n̸̝̈́̊u̷̧̱̎s̸̹̎e̴̮͝d̴̠̬̎",
        str_spawn="{slimeoid_name} momentarily levitates off the floor. The whispers around you seemed to really like this one, and it continues to mutter as it looks at you.",
        str_dissolve="ǘ̴͔͉̋n̸̝̈́̊u̷̧̱̎s̸̹̎e̴̮͝d̴̠̬̎",
        get_strat=get_strat_g,
        str_abuse="{slimeoid_name} takes the hit. It takes note of this, for later."
    ),
]

# A map of id_brain to EwBrain objects.
brain_map = {}

# A list of brain names
brain_names = []

# Populate brain map, including all aliases.
for brain in brain_list:
    brain_map[brain.id_brain] = brain
    brain_names.append(brain.id_brain)

    for alias in brain.alias:
        brain_map[alias] = brain
