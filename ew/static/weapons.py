import random

from . import cfg as ewcfg
from ..model.weapon import EwWeapon
from ..utils import core as ewutils


def get_weapon_type_stats(weapon_type):
    types = {
        "normal": {
            "damage_multiplier": 1.1,
            "cost_multiplier": 1,
            "crit_chance": 0.2,
            "crit_multiplier": 1.8,
            "hit_chance": 0.9,
        },
        "precision": {
            "damage_multiplier": 1.3,
            "cost_multiplier": 1.3,
            "crit_chance": 0,
            "crit_multiplier": 2,
            "hit_chance": -1,
        },
        "small_game": {
            "damage_multiplier": 0.5,
            "cost_multiplier": 0.25,
            "crit_chance": 0.1,
            "crit_multiplier": 2,
            "hit_chance": 0.95,
        },
        "variable_damage": {
            "damage_multiplier": 0.75,
            "variable_damage_multiplier": 1.5,
            "cost_multiplier": 1,
            "crit_chance": 0.1,
            "crit_multiplier": 1.5,
            "hit_chance": 0.9,
        },
        "heavy": {
            "damage_multiplier": 1.7,
            "cost_multiplier": 2.75,
            "crit_chance": 0.1,
            "crit_multiplier": 1.5,
            "hit_chance": 0.8,
        },
        "defensive": {
            "damage_multiplier": 0.75,
            "cost_multiplier": 1.5,
            "crit_chance": 0.1,
            "crit_multiplier": 1.5,
            "hit_chance": 0.85,
        },
        "burst_fire": {
            "damage_multiplier": 0.4,
            "cost_multiplier": 0.8,
            "crit_chance": 0.2,
            "crit_multiplier": 1.5,
            "hit_chance": 0.85,
            "shots": 3
        },
        "minigun": {
            "damage_multiplier": 0.35,
            "cost_multiplier": 2.5,
            "crit_chance": 0.1,
            "crit_multiplier": 2,
            "hit_chance": 0.5,
            "shots": 10
        },
        "incendiary": {
            "damage_multiplier": 0.75,
            "bystander_damage": 0.5,
            "cost_multiplier": 1.5,
            "crit_chance": 0.1,
            "crit_multiplier": 2,
            "hit_chance": 0.9,
            "mass_apply_status": ewcfg.status_burning_id
        },
        "explosive": {
            "damage_multiplier": 0.5,
            "bystander_damage": 0.5,
            "cost_multiplier": 1,
            "crit_chance": 0.1,
            "crit_multiplier": 2,
            "hit_chance": 0.9,
        },
        "tool": {
            "damage_multiplier": 0.5,
            "cost_multiplier": 1,
            "crit_chance": 0.2,
            "crit_multiplier": 1.8,
            "hit_chance": 0.9,
        },
        "ultraheavy": {
            "damage_multiplier": 3,
            "cost_multiplier": 1.6,
            "crit_chance": 0,
            "crit_multiplier": 1,
            "hit_chance": 1,
        },
        "unarmed": {
            "damage_multiplier": 0.25,
            "cost_multiplier": 1,
            "crit_chance": 0,
            "crit_multiplier": 1,
            "hit_chance": 0.9
        }
    }

    return types[weapon_type]


def get_normal_attack(weapon_type = "normal", cost_multiplier = None, damage_multiplier = None, crit_chance = None, crit_multiplier = None, hit_chance = None, apply_status = None, mass_apply_status = None):
    weapon_stats = get_weapon_type_stats(weapon_type)
    if cost_multiplier:
        weapon_stats["cost_multiplier"] = cost_multiplier
    if damage_multiplier:
        weapon_stats["damage_multiplier"] = damage_multiplier
    if crit_chance:
        weapon_stats["crit_chance"] = crit_chance
    if crit_multiplier:
        weapon_stats["crit_multiplier"] = crit_multiplier
    if hit_chance:
        weapon_stats["hit_chance"] = hit_chance
    if apply_status:
        weapon_stats["apply_status"] = apply_status
    if mass_apply_status:
        weapon_stats["mass_apply_status"] = mass_apply_status

    def get_hit_damage(ctn):
        hit_damage = 0
        base_damage = ctn.slimes_damage

        player_has_sharptoother = (ewcfg.mutation_id_sharptoother in ctn.user_data.get_mutations())
        hit_roll = min(random.random(), random.random()) if player_has_sharptoother else random.random()
        guarantee_crit = (weapon_type == "precision" and ctn.user_data.sidearm == -1)

        ignore_hitchance = weapon_stats["hit_chance"] == -1

        # Adds the base chance to hit and the chance from modifiers. Hits if the roll is lower
        if (hit_roll < (weapon_stats["hit_chance"] + ctn.hit_chance_mod)) or ignore_hitchance:
            # Sets multiplier to the default, then adds a random 0 < x < 1 multiple of the variable damage mod
            effective_multiplier = weapon_stats["damage_multiplier"]
            if "variable_damage_multiplier" in weapon_stats:
                effective_multiplier += random.random() * weapon_stats["variable_damage_multiplier"]

            # Multiplies the damage by the effective multiplier
            hit_damage = base_damage * effective_multiplier
            if guarantee_crit or random.random() < (weapon_stats["crit_chance"] + ctn.crit_mod):
                hit_damage *= weapon_stats["crit_multiplier"]
                if not ("shots" in weapon_stats):
                    ctn.crit = True

            if weapon_stats.get("apply_status") is not None:
                ctn.apply_status.update(weapon_stats.get("apply_status"))
            ctn.mass_apply_status = weapon_stats.get("mass_apply_status")
            ctn.explode = True if weapon_type == "explosive" else False

        return hit_damage

    def attack(ctn):
        ctn.slimes_spent = int(ctn.slimes_spent * weapon_stats["cost_multiplier"])
        damage = 0
        if "shots" in weapon_stats:
            ctn.crit = True
            for _ in range(weapon_stats["shots"]):
                hit_damage = get_hit_damage(ctn)
                damage += hit_damage
                if hit_damage == 0:
                    ctn.crit = False
        else:
            damage = get_hit_damage(ctn)
            # TODO: Move this to if damage so that multi-shot weapons can also deal bystander effects when needed
            if "bystander_damage" in weapon_stats:
                ctn.bystander_damage = damage * weapon_stats["bystander_damage"]

        if damage:
            ctn.slimes_damage = int(damage)
            # If any weapon is given a status to apply to the target that requires a damage based value, handle it here
            for status, source in ctn.apply_status.items():
                # This is here to make sure that the weapon modified damage gets used for NS damage
                # If you add a weapon type that also applies burn to target, find a way to add it on top of this.
                # Thats not my job right now though considering no weapons like that exist yet
                # Maybe reverse as {source: type} when declaring, then update with {type: magnitude + apply_status.get(type, 0)}
                # then remove the source key from the dict
                if source == ewcfg.mutation_id_napalmsnot:
                    ctn.apply_status[status] = damage // 2
        else:
            ctn.miss = True

    return attack


# weapon effect function for "garrote"
def wef_garrote(ctn = None):
    ctn.slimes_damage *= 15
    # ctn.sap_damage = 0
    # ctn.sap_ignored = ctn.shootee_data.hardened_sap

    user_mutations = ctn.user_data.get_mutations()
    aim = (random.randrange(100) + 1)
    if aim <= int(100 * ctn.hit_chance_mod):
        if ewcfg.mutation_id_sharptoother in user_mutations:
            if random.random() < 0.5:
                ctn.miss = True
        else:
            ctn.miss = True

    elif aim <= (1 - int(100 * ctn.crit_mod)):
        ctn.slimes_damage *= 10
        ctn.crit = True

    if ctn.miss == False:
        # Stop movement
        ewutils.moves_active[ctn.user_data.id_user] = 0
        # Stun player for 5 seconds
        ctn.user_data.applyStatus(id_status=ewcfg.status_stunned_id, value=(int(ctn.time_now) + 5))
        # Start strangling target
        ctn.shootee_data.applyStatus(id_status=ewcfg.status_strangled_id, source=ctn.user_data.id_user)


# weapon effect function for "Eldritch Staff"
def wef_staff(ctn = None):
    market_data = ctn.market_data
    conditions_met = 0
    conditions = {
        lambda _: 3 <= market_data.clock < 4,  # witching hour
        lambda _: market_data.weather == ewcfg.weather_foggy,
        lambda _: ewutils.check_moon_phase(market_data) == ewcfg.moon_new,  # moonless night
        lambda ctn: not ctn.user_data.has_soul,
        lambda ctn: ctn.user_data.get_possession('weapon'),
        lambda ctn: ctn.user_data.poi == ewcfg.poi_id_thevoid,
        lambda ctn: ctn.shootee_data.slimes > ctn.user_data.slimes,
        lambda ctn: (ctn.user_data.poi_death == ctn.user_data.poi) or (ctn.shootee_data.poi_death == ctn.shootee_data.poi),
        lambda ctn: (ctn.user_data.id_killer == ctn.shootee_data.id_user) or (ctn.user_data.id_user == ctn.shootee_data.id_killer),
        lambda ctn: (ctn.shootee_data.life_state == ewcfg.life_state_juvenile) or (ctn.shootee_data.life_state == ewcfg.life_state_enlisted and ctn.shootee_data.faction == ctn.user_data.faction),
        lambda ctn: (ctn.shootee_data.gender == ctn.user_data.gender), # SGAB, or Same Gender Attack Bonus
    }
    for condition in conditions:
        try:
            if condition(ctn):
                conditions_met += 1
        except:
            pass

    ctn.slimes_spent = int(ctn.slimes_spent * 2)
    ctn.slimes_damage = int(ctn.slimes_damage * (0.3 + conditions_met * 0.6))
    if conditions_met >= (random.randrange(15) + 1):  # 6.66% per condition met
        ctn.crit = True
        ctn.slimes_damage = int(ctn.slimes_damage * 1.8)


def wef_paintgun(ctn = None):
    ctn.slimes_damage = int(ctn.slimes_damage * .7)
    ctn.slimes_spent = int(ctn.slimes_spent * .75)
    aim = (random.randrange(10) + 1)
    # ctn.sap_ignored = 10
    # ctn.sap_damage = 2

    if aim >= (9 - int(10 * ctn.crit_mod)):
        ctn.crit = True
        ctn.slimes_damage *= 2


def wef_paintroller(ctn = None):
    ctn.slimes_damage = int(ctn.slimes_damage * 1.75)
    ctn.slimes_spent = int(ctn.slimes_spent * 4)

    aim = (random.randrange(10) + 1)
    user_mutations = ctn.user_data.get_mutations()

    if aim <= (1 + int(10 * ctn.hit_chance_mod)):
        if ewcfg.mutation_id_sharptoother in user_mutations:
            if random.random() < 0.5:
                ctn.miss = True
        else:
            ctn.miss = True

    elif aim >= (10 - int(10 * ctn.crit_mod)):
        ctn.crit = True
        ctn.slimes_damage *= 2


# ctn.sap_damage *= 2

def wef_watercolors(ctn = None):
    ctn.slimes_damage = 4000
    aim = (random.randrange(250) + 1)
    user_mutations = ctn.user_data.get_mutations()
    # ctn.sap_damage = 0

    if aim <= (1 + int(250 * ctn.hit_chance_mod)):
        if ewcfg.mutation_id_sharptoother in user_mutations:
            if random.random() < 0.5:
                ctn.miss = True
        else:
            ctn.miss = True

    elif aim == 1000:
        ctn.crit = True
        ctn.slimes_damage *= 1


def wef_harpoon(ctn = None):
    aim = 100
    # GNNNNRHRRRHHRHRHRHRHH I NEED BOTH ME HANDS TO WIELD THIS SUNUVABITCH!
    if ctn.user_data.sidearm != -1:
        aim = (random.randrange(11) + 1)
    ctn.slimes_damage = int(ctn.slimes_damage * 3)
    aim *= ctn.hit_chance_mod
    if aim >= 10:
        ctn.miss = False
    else:
        ctn.miss = True


# All weapons in the game.
weapon_list = [
    EwWeapon(  # 1
        id_weapon=ewcfg.weapon_id_revolver,
        alias=[
            "pistol",
            "handgun",
            "bigiron"
        ],
        str_crit="**Critical Hit!** You have fataly wounded {name_target} with a lethal shot!",
        str_miss="**You missed!** Your shot whizzed past {name_target}'s head!",
        str_equip="You equip the revolver.",
        str_name="revolver",
        str_weapon="a revolver",
        str_weaponmaster_self="You are a rank {rank} {title} of the revolver.",
        str_weaponmaster="They are a rank {rank} {title} of the revolver.",
        # str_trauma_self = "You have scarring on both temples, which occasionally bleeds.",
        # str_trauma = "They have scarring on both temples, which occasionally bleeds.",
        str_kill="{name_player} puts their revolver to {name_target}'s head. **BANG**. Execution-style. Blood splatters across the hot asphalt. {emote_skull}",
        str_killdescriptor="gunned down",
        str_damage="{name_target} takes a bullet to the {hitzone}!!",
        str_duel="**BANG BANG**. {name_player} and {name_target} practice their quick-draw, bullets whizzing past one another's heads.",
        str_description="It's a revolver.",
        str_reload="You swing out the revolver’s chamber, knocking the used shells out onto the floor before hastily slamming fresh bullets back into it.",
        str_reload_warning="**BANG--** *tk tk...* **SHIT!!** {name_player} just spent the last of the ammo in their revolver’s chamber; it’s out of bullets!!",
        str_scalp=" It has a bullet hole in it.",
        fn_effect=get_normal_attack(cost_multiplier=0.8),
        price=10000,
        clip_size=6,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_revolver_kills,
        str_brandish="{name} spins {weapon} around on their finger, blowing smoke off the barrel like a Texas gunman."
    ),
    EwWeapon(  # 2
        id_weapon=ewcfg.weapon_id_dualpistols,
        alias=[
            "dual",
            "pistols",
            "berettas",
            "dualies"
        ],
        str_crit="**Critical Hit!** {name_player} has lodged several bullets into {name_target}'s vital arteries!",
        str_miss="**You missed!** Your numerous, haphazard shots hit everything but {name_target}!",
        str_equip="You equip the dual pistols.",
        str_name="dual pistols",
        str_weapon="dual pistols",
        str_weaponmaster_self="You are a rank {rank} {title} of the dual pistols.",
        str_weaponmaster="They are a rank {rank} {title} of the dual pistols.",
        # str_trauma_self = "You have several stitches embroidered into your chest over your numerous bullet wounds.",
        # str_trauma = "They have several stitches embroidered into your chest over your numerous bullet wounds.",
        str_kill="{name_player} dramatically pulls both triggers on their dual pistols midair, sending two bullets straight into {name_target}'s lungs'. {emote_skull}",
        str_killdescriptor="double gunned down",
        str_damage="{name_target} takes a flurry of bullets to the {hitzone}!!",
        str_duel="**tk tk tk tk tk tk tk tk tk tk**. {name_player} and {name_target} hone their twitch aim and trigger fingers, unloading clip after clip of airsoft BBs into one another with the eagerness of small children.",
        str_description="They're dual pistols.",
        str_reload="You swing out the handles on both of your pistols, knocking the used magazines out onto the floor before hastily slamming fresh mags back into them.",
        str_reload_warning="**tk tk tk tk--** *tk...* **SHIT!!** {name_player} just spent the last of the ammo in their dual pistol’s mags; they’re out of bullets!!",
        str_scalp=" It has a couple bullet holes in it.",
        fn_effect=get_normal_attack(),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_dual_pistols_kills,
        str_brandish="{name} cocks {weapon} back, aiming them at the nearest passersby. *Bang.*"
    ),
    EwWeapon(  # 3
        id_weapon=ewcfg.weapon_id_shotgun,
        alias=[
            "remington",
            "scattergun",
            "r870",
            "pumpaction"
        ],
        str_crit="**Critical Hit!** {name_player} has landed a thick, meaty shot into {name_target}'s chest!",
        str_miss="**You missed!** Your pellets inexplicably dodge {name_target}. Fucking random bullet spread, this game will never be competitive.",
        str_equip="You equip the shotgun.",
        str_name="shotgun",
        str_weapon="a shotgun",
        str_weaponmaster_self="You are a rank {rank} {title} of the shotgun.",
        str_weaponmaster="They are a rank {rank} {title} of the shotgun.",
        # str_trauma_self = "You have a few large, gaping holes in your abdomen. Someone could stick their arm through the biggest one.",
        # str_trauma = "They have a few large, gaping holes in your abdomen. Someone could stick their arm through the biggest one.",
        str_kill="{name_player} blasts their shotgun into {name_target}'s chest at point-blank range, causing guts to explode from their back and coat the surrounding street. **chk chk** Who's next? {emote_skull}",
        str_killdescriptor="pumped full of lead",
        str_damage="{name_target} takes a shotgun blast to the {hitzone}!!",
        str_duel="**BOOM.** {name_player} and {name_target} stand about five feet away from a wall, pumping it full of lead over and over to study it's bullet spread.",
        str_description="It's a shotgun.",
        str_reload="You tilt your shotgun and perform a double quad load into the shell tube.",
        str_reload_warning="**chk--** *...* **SHIT!!** {name_player}’s shotgun has ejected the last shell in its chamber, it’s out of ammo!!",
        str_scalp=" It has a gaping hole in the center.",
        fn_effect=get_normal_attack(cost_multiplier=2.5, weapon_type='heavy'),
        clip_size=8,
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_shotgun_kills,
        str_brandish="**ChkCHK.** {name} takes {weapon} and pumps back a couple rounds, listening to the shells clink onto the ground."
    ),
    EwWeapon(  # 4
        id_weapon=ewcfg.weapon_id_rifle,
        alias=[
            "assaultrifle",
            "machinegun",
            "mg"
        ],
        str_crit="**Critical hit!!** You unload an entire magazine into the target!!",
        str_miss="**You missed!** Not one of your bullets connected!!",
        str_equip="You equip the assault rifle.",
        str_name="assault rifle",
        str_weapon="an assault rifle",
        str_weaponmaster_self="You are a rank {rank} {title} of the assault rifle.",
        str_weaponmaster="They are a rank {rank} {title} of the assault rifle.",
        # str_trauma_self = "Your torso is riddled with scarred-over bulletholes.",
        # str_trauma = "Their torso is riddled with scarred-over bulletholes.",
        str_kill="**RAT-TAT-TAT-TAT-TAT!!** {name_player} rains a hail of bullets directly into {name_target}!! They're officially toast! {emote_skull}",
        str_killdescriptor="gunned down",
        str_damage="Bullets rake over {name_target}'s {hitzone}!!",
        str_duel="**RAT-TAT-TAT-TAT-TAT!!** {name_player} and {name_target} practice shooting at distant targets with quick, controlled bursts.",
        str_description="It's a rifle.",
        str_reload="You hastily rip the spent magazine out of your assault rifle, before slamming a fresh one back into it.",
        str_reload_warning="**RAT-TAT-TAT--** *ttrrr...* **SHIT!!** {name_player}’s rifle just chewed up the last of its magazine; it’s out of bullets!!",
        str_scalp=" It has a shit-load of holes in it.",
        fn_effect=get_normal_attack(cost_multiplier=0.7, weapon_type='burst_fire'),
        clip_size=10,
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_rifle_kills,
        str_brandish="**BAM BAM!** {name} takes {weapon} and fires some warning rounds into the air."
    ),
    EwWeapon(  # 5
        id_weapon=ewcfg.weapon_id_smg,
        alias=[
            "submachinegun",
            "machinegun"
        ],
        str_crit="**Critical hit!!** {name_target}’s vital arteries are ruptured by miraculously accurate bullets that actually hit their intended target!!",
        str_miss="**You missed!!** {name_player}'s reckless aiming sends their barrage of bullets in every direction but into {name_target}’s body!",
        str_equip="You equip the SMG.",
        str_name="SMG",
        str_weapon="an SMG",
        str_weaponmaster_self="You are a rank {rank} {title} of the SMG.",
        str_weaponmaster="They are a rank {rank} {title} of the SMG.",
        # str_trauma_self = "Your copious amount of bullet holes trigger onlookers’ Trypophobia.",
        # str_trauma = "Their copious amount of bullet holes trigger onlookers’ Trypophobia.",
        str_kill="**RATTA TATTA TAT!!** {name_player}’s bullets rip through what little was left of {name_target} after the initial barrage. All that remains is a few shreds of clothing and splatterings of slime. {emote_skull}",
        str_killdescriptor="riddled with bullets",
        str_damage="A reckless barrage of bullets pummel {name_target}’s {hitzone}!!",
        str_duel="**RATTA TATTA TAT!!** {name_player} and {name_target} spray bullets across the floor and walls of the Dojo, having a great time.",
        str_description="It's a submachine gun.",
        # str_jammed = "Your SMG jams again, goddamn piece of shit gun...",
        str_reload="You hastily rip the spent magazine out of your SMG, before slamming a fresh one back into it.",
        str_reload_warning="**RATTA TATTA--** *tk tk tk tk…* **SHIT!!** {name_player}’s SMG just chewed up the last of its magazine; it’s out of bullets!!",
        # str_unjam = "{name_player} successfully whacks their SMG hard enough to dislodge whatever hunk of gunk was blocking it’s internal processes.",
        str_scalp=" It has a bunch of holes strewn throughout it.",
        fn_effect=get_normal_attack(cost_multiplier=0.7, weapon_type='burst_fire'),
        clip_size=10,
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_smg_kills,
        str_brandish="**RATTATTATTAT!** {name} takes {weapon} and fires a line of bullets along the ground. *You're next.*"
    ),
    EwWeapon(  # 6
        id_weapon=ewcfg.weapon_id_minigun,
        alias=[
            "mini",
            "gatlinggun"
        ],
        str_crit="**Critical hit!!** Round after round of bullets fly through {name_target}, inflicting irreparable damage!!",
        str_miss="**You missed!!** Despite the growing heap of used ammunition shells {name_player} has accrued, none of their bullets actually hit {name_target}!",
        str_equip="You equip the minigun.",
        str_name="minigun",
        str_weapon="a minigun",
        str_weaponmaster_self="You are a rank {rank} {title} of the minigun.",
        str_weaponmaster="They are a rank {rank} {title} of the minigun.",
        # str_trauma_self = "What little is left of your body has large holes punched through it, resembling a slice of swiss cheese.",
        # str_trauma = "What little is left of their body has large holes punched through it, resembling a slice of swiss cheese.",
        str_kill="**TKTKTKTKTKTKTKTKTK!!** {name_player} pushes their minigun barrel right up to {name_target}’s chest, unloading a full round of ammunition and knocking their lifeless corpse back a few yards from the sheer force of the bullets. They failed to outsmart bullet. {emote_skull}",
        str_killdescriptor="obliterated",
        str_damage="Cascades of bullets easily puncture and rupture {name_target}’s {hitzone}!!",
        str_duel="**...** {name_player} and {name_target} crouch close to the ground, throwing sandwiches unto the floor next to each other and repeating memetic voice lines ad nauseam.",
        str_description="It's a minigun.",
        # str_reload = "You curse under your breath, before pulling a fresh belt of bullets from hammerspace and jamming it into your minigun’s hungry feed.",
        # str_reload_warning = "**TKTKTKTKTKTK--** *wrrrrrr…* **SHIT!!** {name_player}’s minigun just inhaled the last of its belt; it’s out of bullets!!",
        str_scalp=" It looks more like a thick slice of swiss cheese than a scalp.",
        fn_effect=get_normal_attack(weapon_type='minigun'),
        price=1000000,
        vendors=[ewcfg.vendor_bazaar],
        classes=[ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_minigun_kills,
        captcha_length=6,
        str_brandish="{name} laughs to themselves as they spin {weapon}'s barrel. These suckers won't know what hit 'em."
    ),
    EwWeapon(  # 7
        id_weapon=ewcfg.weapon_id_bat,
        alias=[
            "club",
            "batwithnails",
            "nailbat",
        ],
        str_crit="**Critical hit!!** {name_player} has bashed {name_target} up real bad!",
        str_miss="**MISS!!** {name_player} swung wide and didn't even come close!",
        str_equip="You equip the bat with nails in it.",
        str_name="bat",
        str_weaponmaster_self="You are a rank {rank} {title} of the nailbat.",
        str_weaponmaster="They are a rank {rank} {title} of the nailbat.",
        str_weapon="a bat full of nails",
        # str_trauma_self = "Your head appears to be slightly concave on one side.",
        # str_trauma = "Their head appears to be slightly concave on one side.",
        str_kill="{name_player} pulls back for a brutal swing! **CRUNCCHHH.** {name_target}'s brains splatter over the sidewalk. {emote_skull}",
        str_killdescriptor="nail bat battered",
        str_damage="{name_target} is struck with a hard blow to the {hitzone}!!",
        # str_backfire = "{name_player} recklessly budgens themselves with a particularly overzealous swing! Man, how the hell could they fuck up so badly?",
        str_duel="**SMASHH! CRAASH!!** {name_player} and {name_target} run through the neighborhood, breaking windshields, crushing street signs, and generally having a hell of a time.",
        str_description="It's a nailbat.",
        str_scalp=" It has a couple nails in it.",
        fn_effect=get_normal_attack(weapon_type='variable_damage'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_bat_kills,
        str_brandish="{name} winds up a swing with {weapon}. Time to knock some heads."
    ),
    EwWeapon(  # 8
        id_weapon=ewcfg.weapon_id_brassknuckles,
        alias=[
            "knuckles",
            "knuckledusters",
            "dusters"
        ],
        str_crit="***SKY UPPERCUT!!*** {name_player} executes an artificially difficult combo, rocketing their fist into the bottom of {name_target}’s jaw so hard that {name_target}’s colliding teeth brutally sever an inch off their own tongue!!",
        str_miss="**MISS!** {name_player} couldn't land a single blow!!",
        str_equip="You equip the brass knuckles.",
        str_name="brass knuckles",
        str_weapon="brass knuckles",
        str_weaponmaster_self="You are a rank {rank} {title} pugilist.",
        str_weaponmaster="They are a rank {rank} {title} pugilist.",
        # str_trauma_self = "You've got two black eyes, missing teeth, and a profoundly crooked nose.",
        # str_trauma = "They've got two black eyes, missing teeth, and a profoundly crooked nose.",
        str_kill="{name_player} slugs {name_target} right between the eyes! *POW! THWACK!!* **CRUNCH.** Shit. May have gotten carried away there. Oh, well. {emote_skull}",
        str_killdescriptor="pummeled to death",
        str_damage="{name_target} is socked in the {hitzone}!!",
        str_duel="**POW! BIFF!!** {name_player} and {name_target} take turns punching each other in the abs. It hurts so good.",
        str_description="They're brass knuckles.",
        str_scalp=" It has bone fragments in it.",
        fn_effect=get_normal_attack(weapon_type='variable_damage'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_brassknuckles_kills,
        str_brandish="{name} takes off {weapon} and flips the bird. Get fucked."
    ),
    EwWeapon(  # 9
        id_weapon=ewcfg.weapon_id_katana,
        alias=[
            "weebsword",
            "ninjasword",
            "samuraisword",
            "blade"
        ],
        str_crit="**Critical hit!!** {name_target} is cut deep!!",
        str_miss="",
        str_equip="You equip the katana.",
        str_name="katana",
        str_weapon="a katana",
        str_weaponmaster_self="You are a rank {rank} {title} of the blade.",
        str_weaponmaster="They are a rank {rank} {title} of the blade.",
        # str_trauma_self = "A single clean scar runs across the entire length of your body.",
        # str_trauma = "A single clean scar runs across the entire length of their body.",
        str_kill="Faster than the eye can follow, {name_player}'s blade glints in the greenish light. {name_target} falls over, now in two pieces. {emote_skull}",
        str_killdescriptor="bisected",
        str_damage="{name_target} is slashed across the {hitzone}!!",
        str_duel="**CRACK!! THWACK!! CRACK!!** {name_player} and {name_target} duel with bamboo swords, viciously striking at head, wrist and belly.",
        str_description="It's a katana.",
        str_scalp=" It seems to have been removed with some precision.",
        fn_effect=get_normal_attack(weapon_type='precision'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_katana_kills,
        captcha_length=4,
        str_brandish="{name} pulls {weapon} halfway out of its scabbard. It shines menacingly..."
    ),
    EwWeapon(  # 10
        id_weapon=ewcfg.weapon_id_broadsword,
        alias=[
            "sword",
            "highlander",
            "arawheapofiron",
            "eyelander"
        ],
        str_crit="Critical hit!! {name_player} screams at the top of their lungs and unleashes a devastating overhead swing that maims {name_target}.",
        str_miss="You missed! You grunt as your failed overhead swing sends ripples through the air.",
        # str_backfire = "You feel the bones in your wrists snap as you botch your swing with the heavy blade!! Fucking ouch dawg!",
        str_equip="You equip the broadsword.",
        str_name="broadsword",
        str_weapon="a broadsword",
        str_weaponmaster_self="You are a rank {rank} {title} berserker.",
        str_weaponmaster="They are a rank {rank} {title} berserker.",
        # str_trauma_self = "A large dent resembling that of a half-chopped down tree appears on the top of your head.",
        # str_trauma = "A dent resembling that of a half-chopped down tree appears on the top of their head.",
        str_kill="{name_player} skewers {name_target} through the back to the hilt of their broadsword, before kicking their lifeless corpse onto the street corner in gruesome fashion. {name_player} screams at the top of their lungs. {emote_skull}",
        str_killdescriptor="slayed",
        str_damage="{name_target}'s {hitzone} is separated from their body!!",
        str_duel="SCHWNG SCHWNG! {name_player} and {name_target} scream at the top of their lungs to rehearse their battle cries.",
        str_description="It's a broadsword.",
        str_reload="You summon strength and muster might from every muscle on your body to hoist your broadsword up for another swing.",
        str_reload_warning="**THUD...** {name_player}’s broadsword is too heavy; its blade has fallen to the ground!!",
        str_scalp=" It was sloppily lopped off.",
        clip_size=1,
        price=10000,
        fn_effect=get_normal_attack(weapon_type='heavy'),
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_broadsword_kills,
        str_brandish = "{name} raises {weapon} and lets out a hearty battlecry! **AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA**"
    ),
    EwWeapon(  # 11
        id_weapon=ewcfg.weapon_id_nunchucks,
        alias=[
            "nanchacku",
            "nunchaku",
            "chucks",
            "numchucks",
            "nunchucks"
        ],
        str_crit="**COMBO!** {name_player} strikes {name_target} with a flurry of 5 vicious blows!",
        # str_backfire = "**Whack!!** {name_player} fucks up their kung-fu routine and whacks themselves in the head with their own nun-chucks!!",
        str_miss="**WOOSH** {name_player} whiffs every strike!",
        str_equip="You equip the nun-chucks.",
        str_name="nun-chucks",
        str_weapon="nun-chucks",
        str_weaponmaster_self="You are a rank {rank} kung-fu {title}.",
        str_weaponmaster="They are a rank {rank} kung-fu {title}.",
        # str_trauma_self = "You are covered in deep bruises. You hate martial arts of all kinds.",
        # str_trauma = "They are covered in deep bruises. They hate martial arts of all kinds.",
        str_kill="**HIIII-YAA!!** With expert timing, {name_player} brutally batters {name_target} to death, then strikes a sweet kung-fu pose. {emote_skull}",
        str_killdescriptor="fatally bludgeoned",
        str_damage="{name_target} takes a bunch of nun-chuck whacks directly in the {hitzone}!!",
        str_duel="**HII-YA! HOOOAAAAAHHHH!!** {name_player} and {name_target} twirl wildly around one another, lashing out with kung-fu precision.",
        str_description="They're nunchucks.",
        str_scalp=" It looks very bruised.",
        fn_effect=get_normal_attack(weapon_type='burst_fire'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_nunchucks_kills,
        str_brandish="**WA-TWAAAAH!** {name} swings {weapon} so fast that it becomes a blur in their hands!"
    ),
    EwWeapon(  # 12
        id_weapon=ewcfg.weapon_id_scythe,
        alias=[
            "sickle"
        ],
        str_crit="**Critical hit!!** {name_target} is carved by the wicked curved blade!",
        str_miss="**MISS!!** {name_player}'s swings wide of the target!",
        str_equip="You equip the scythe.",
        str_name="scythe",
        str_weapon="a scythe",
        str_weaponmaster_self="You are a rank {rank} {title} of the scythe.",
        str_weaponmaster="They are a rank {rank} {title} of the scythe.",
        # str_trauma_self = "You are wrapped tightly in bandages that hold your two halves together.",
        # str_trauma = "They are wrapped tightly in bandages that hold their two halves together.",
        str_kill="**SLASHH!!** {name_player}'s scythe cleaves the air, and {name_target} staggers. A moment later, {name_target}'s torso topples off their waist. {emote_skull}",
        str_killdescriptor="sliced in twain",
        str_damage="{name_target} is cleaved through the {hitzone}!!",
        str_duel="**WHOOSH, WHOOSH** {name_player} and {name_target} swing their blades in wide arcs, dodging one another's deadly slashes.",
        str_description="It's a scythe.",
        str_scalp=" It's cut in two pieces.",
        price=10000,
        fn_effect=get_normal_attack(weapon_type='heavy'),
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_scythe_kills,
        str_brandish="{name} takes a couple swings with {weapon}. Bell tolls for thee, motherfucker."
    ),
    EwWeapon(  # 13
        id_weapon=ewcfg.weapon_id_yoyo,
        alias=[
            "yo-yos",
            "yoyo",
            "yoyos"
        ],
        str_crit="SMAAAASH!! {name_player} pulls off a modified Magic Drop, landing a critical hit on {name_target} just after the rejection!",
        str_miss="You missed! {name_player} misjudges their yo-yo's trajectory and botches an easy trick.",
        str_equip="You equip the yo-yo.",
        str_name="yo-yo",
        str_weaponmaster_self="You are a rank {rank} {title} of the yo-yo.",
        str_weaponmaster="They are a rank {rank} {title} of the yo-yo.",
        str_weapon="a yo-yo",
        # str_trauma_self = "Simple yo-yo tricks caught even in your peripheral vision triggers intense PTSD flashbacks.",
        # str_trauma = "Simple yo-yo tricks caught even in their peripheral vision triggers intense PTSD flashbacks.",
        str_kill="{name_player} performs a modified Kwyjibo, effortlessly nailing each step before killing their opponent just ahead of the dismount.",
        str_killdescriptor="amazed",
        str_damage="{name_player} used {name_target}'s {hitzone} as a counterweight!!",
        str_duel="**whhzzzzzz** {name_player} and {name_target} practice trying to Walk the Dog for hours. It never clicks.",
        str_description="It's a yo-yo.",
        str_scalp=" It has a ball bearing hidden inside it. You can spin it like a fidget spinner.",
        fn_effect=get_normal_attack(),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_yoyo_kills,
        str_brandish="Oh shit! {name} has {weapon}! Son of a bitch, they're doing a Houdini Mount! This is terrifying!!"
    ),
    EwWeapon(  # 14
        id_weapon=ewcfg.weapon_id_knives,
        alias=[
            "knife",
            "dagger",
            "daggers",
            "throwingknives",
            "throwingknife"
        ],
        str_crit="**Critical hit!!** {name_player}'s knife strikes a vital point!",
        str_miss="**MISS!!** {name_player}'s knife missed its target!",
        str_equip="You equip the throwing knives.",
        str_name="throwing knives",
        str_weapon="throwing knives",
        str_weaponmaster_self="You are a rank {rank} {title} of the throwing knife.",
        str_weaponmaster="They are a rank {rank} {title} of the throwing knife.",
        # str_trauma_self = "You are covered in scarred-over lacerations and puncture wounds.",
        # str_trauma = "They are covered in scarred-over lacerations and puncture wounds.",
        str_kill="A blade flashes through the air!! **THUNK.** {name_target} is a goner, but {name_player} slits their throat before fleeing the scene, just to be safe. {emote_skull}",
        str_killdescriptor="knifed",
        str_damage="{name_target} is stuck by a knife in the {hitzone}!!",
        str_duel="**TING! TING!!** {name_player} and {name_target} take turns hitting one another's knives out of the air.",
        str_description="They're throwing knives.",
        str_scalp=" It has about a half dozen stab holes in it.",
        fn_effect=get_normal_attack(weapon_type='small_game'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_knives_kills,
        str_brandish="{name} stares down the world, licking the blade of {weapon} like some kind of sick freak!"
    ),
    EwWeapon(  # 15
        id_weapon=ewcfg.weapon_id_molotov,
        alias=[
            "firebomb",
            "molotovcocktail",
            "bomb",
            "bombs",
            "moly"
        ],
        # str_backfire = "**Oh, the humanity!!** The bottle bursts in {name_player}'s hand, burning them terribly!!",
        str_miss="**A dud!!** the rag failed to ignite the molotov!",
        str_crit="{name_player}’s cocktail shatters at the feet of {name_target}, sending a shower of shattered shards of glass into them!!",
        str_equip="You equip the molotov cocktail.",
        str_name="molotov cocktail",
        str_weapon="molotov cocktails",
        str_weaponmaster_self="You are a rank {rank} {title} arsonist.",
        str_weaponmaster="They are a rank {rank} {title} arsonist.",
        # str_trauma_self = "You're wrapped in bandages. What skin is showing appears burn-scarred.",
        # str_trauma = "They're wrapped in bandages. What skin is showing appears burn-scarred.",
        str_kill="**SMASH!** {name_target}'s front window shatters and suddenly flames are everywhere!! The next morning, police report that {name_player} is suspected of arson. {emote_skull}",
        str_killdescriptor="exploded",
        str_damage="{name_target} dodges a bottle, but is singed on the {hitzone} by the blast!!",
        str_duel="{name_player} and {name_target} compare notes on frontier chemistry, seeking the optimal combination of combustibility and fuel efficiency.",
        str_description="These are glass bottles filled with some good ol' fashioned pyrotechnics.",
        str_scalp=" It's burnt to a crisp!",
        fn_effect=get_normal_attack(weapon_type='incendiary'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_burning, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_molotov_kills,
        captcha_length=4,
        str_brandish="{name} lights {weapon}'s fuse for just a second. Heheh, just you wait."
    ),
    EwWeapon(  # 16
        id_weapon=ewcfg.weapon_id_grenades,
        alias=[
            "nades",
            "grenade"
        ],
        str_crit="**Critical hit!!** {name_target} is blown off their feet by the initial explosion, and lacerated by innumerable shards of shrapnel scattering themselves through their body!!",
        str_miss="**You missed!!** {name_player}’s poor aim sends their grenade into a nearby alleyway, its explosion eliciting a Wilhelm scream and the assumed death of an innocent passerby. LOL!!",
        str_equip="You equip the grenades.",
        str_name="grenades",
        str_weapon="grenades",
        str_weaponmaster_self="You are a rank {rank} {title} of the grenades.",
        str_weaponmaster="They are a rank {rank} f {title} of the grenades.",
        # str_trauma_self = "Blast scars and burned skin are spread unevenly across your body.",
        # str_trauma = "Blast scars and burned skin are spread unevenly across their body.",
        str_kill="**KA-BOOM!!** {name_player} pulls the safety pin and holds their grenade just long enough to cause it to explode mid air, right in front of {name_target}’s face, blowing it to smithereens. {emote_skull}",
        str_killdescriptor="exploded",
        str_damage="{name_player}’s grenade explodes, sending {name_target}’s {hitzone} flying off their body!!",
        str_duel="**KA-BOOM!!** {name_player} and {name_target} pull the pin out of their grenades and hold it in their hands to get a feel for how long it takes for them to explode. They lose a few body parts in the process.",
        str_description="A stack of grenades.",
        str_scalp=" It's covered in metallic shrapnel.",
        fn_effect=get_normal_attack(weapon_type='explosive'),
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        classes=[ewcfg.weapon_class_exploding, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_grenade_kills,
        captcha_length=4,
        str_brandish="{name} spins {weapon} on their finger like an anarchist Harlem Globetrotter."
    ),
    EwWeapon(  # 17
        id_weapon=ewcfg.weapon_id_garrote,
        alias=[
            "wire",
            "garrotewire",
            "garrottewire"
        ],
        str_crit="**CRITICAL HIT!!** {name_player} got lucky and caught {name_target} completely unaware!!",
        str_miss="**MISS!** {name_player}'s target got away in time!",
        str_equip="You equip the garrotte wire.",
        str_name="garrote wire",
        str_weapon="a garrotte wire",
        str_weaponmaster_self="You are a rank {rank} {title} of the garrotte.",
        str_weaponmaster="They are a rank {rank} {title} of the garrotte.",
        # str_trauma_self = "There is noticeable bruising and scarring around your neck.",
        # str_trauma = "There is noticeable bruising and scarring around their neck.",
        str_kill="{name_player} quietly moves behind {name_target} and... **!!!** After a brief struggle, only a cold body remains. {emote_skull}",
        str_killdescriptor="garrote wired",
        str_damage="{name_target} is ensnared by {name_player}'s wire!!",
        str_duel="{name_player} and {name_target} compare their dexterity by playing Cat's Cradle with deadly wire.",
        str_description="It's a garrote wire.",
        str_scalp=" It's a deep shade of blue.",
        fn_effect=wef_garrote,
        price=10000,
        vendors=[ewcfg.vendor_dojo, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_garrote_kills,
        str_brandish="{name} wraps {weapon} around their own neck and feigns getting decapitated. Eh, who are they kidding, that thing never kills anybody."
    ),
    EwWeapon(  # 18
        id_weapon=ewcfg.weapon_id_pickaxe,
        alias=[
            "pick",
            "poudrinpickaxe",
            "poudrinpick"
        ],
        str_crit="**Critical hit!!** By sheer dumb luck, {name_player} manages to get a good hit off on {name_target}’s {hitzone}.",
        str_miss="**MISS!!** {name_player} is too weak to lift their pickaxe!",
        str_equip="You equip the pickaxe.",
        str_name="pickaxe",
        str_weapon="a pickaxe",
        str_weaponmaster_self="You are a rank {rank} {title} coward of the pickaxe.",
        str_weaponmaster="They are a rank {rank} {title} coward of the pickaxe.",
        # str_trauma_self = "There is a deep, precise indent in the crown of your skull. How embarrassing!",
        # str_trauma = "There is a deep, precise indent in the crown of their skull. How embarrassing!",
        str_kill="**THWACK!!** {name_player} summons what little courage they possess to lift the pickaxe above their head and !mine {name_target} to death. How embarrassing! {emote_skull}",
        str_killdescriptor="!mined",
        str_damage="{name_target} is lightly tapped on the {hitzone}!!",
        str_duel="**THWACK, THWACK** {name_player} and {name_target} spend some quality time together, catching up and discussing movies they recently watched or food they recently ate.",
        str_scalp=" It reeks of dirt and poudrins. How embarrassing!",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="It's a pickaxe.",
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_pickaxe_kills,
        is_tool=1,
        str_brandish="{name} starts ramming {weapon} into the ground, whistling a little tune as they work!"
    ),
    EwWeapon(  # 19
        id_weapon=ewcfg.weapon_id_fishingrod,
        alias=[
            "fish",
            "fishing",
            "rod",
            "super",
            "superrod",
            "superfishingrod"
        ],
        str_crit="**Critical hit!!** By sheer dumb luck, {name_player} manages to get a good hit off on {name_target}’s {hitzone}.",
        str_miss="**MISS!!** {name_player} is too weak to cast their fishing rod!",
        str_equip="You equip the super fishing rod.",
        str_name="super fishing rod",
        str_weapon="a super fishing rod",
        str_weaponmaster_self="You are a rank {rank} {title} fisherman.",
        str_weaponmaster="They are a rank {rank} {title} fisherman.",
        # str_trauma_self = "There is a piercing on the side of your mouth. How embarrassing!",
        # str_trauma = "There is a piercing on the side of their mouth. How embarrassing!",
        str_kill="*whsssh* {name_player} summons what little courage they possess to reel in {name_target} and wring all the slime out of them. How embarrassing! {emote_skull}",
        str_killdescriptor="!reeled",
        str_damage="{name_target} is lightly pierced on the {hitzone}!!",
        str_duel="**whsssh, whsssh** {name_player} and {name_target} spend some quality time together, discussing fishing strategy and preferred types of bait.",
        str_scalp=" It has a fishing hook stuck in it. How embarrassing!",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="It's a super fishing rod.",
        acquisition=ewcfg.acquisition_smelting,
        classes=[ewcfg.weapon_class_juvie],
        stat=ewcfg.stat_fishingrod_kills,
        is_tool=1,
        str_brandish="{name} recklessly swings {weapon} around, and starts exaggerating about the largest fish they ever caught! Nobody believes them, though."
    ),
    EwWeapon(  # 20
        id_weapon=ewcfg.weapon_id_bass,
        alias=[
            "bass",
        ],
        str_crit="**Critical hit!!** Through skilled swipes {name_player} manages to sharply strike {name_target}’s {hitzone}.",
        str_miss="**MISS!!** {name_player} swings and misses like a dumbass!",
        str_equip="You equip the bass guitar, and a highly distorted and reverbed riff of unknown origin plays as you place the strap over your neck.",
        str_name="bass guitar",
        str_weapon="a bass guitar",
        str_weaponmaster_self="You are a rank {rank} {title} of the bass guitar.",
        str_weaponmaster="They are a rank {rank} {title} of the bass guitar.",
        # str_trauma_self = "There is a large concave dome in the side of your head.",
        # str_trauma = "There is a large concave dome in the side of their head.",
        str_kill="*CRASSHHH.* {name_player} brings down the bass on {name_target} with righteous fury. Discordant notes play harshly as the bass tries its hardest to keep itself together. {emote_skull}",
        str_killdescriptor="smashed to pieces",
        str_damage="{name_target} is whacked across the {hitzone}!!",
        str_duel="**SMASHHH.** {name_player} and {name_target} smash their bass together before admiring eachothers skillful basslines.",
        str_scalp=" If you listen closely, you can still hear the echoes of a sick bassline from yesteryear.",
        fn_effect=get_normal_attack(weapon_type='variable_damage'),
        str_description="It's a bass guitar. All of its strings are completely out of tune and rusted.",
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_bass_kills,
        str_brandish="{name} takes {weapon} out and belts out an insane bassline!"
    ),
    EwWeapon(  # 21
        id_weapon=ewcfg.weapon_id_umbrella,
        alias=[
            "umbrella",
            "slimebrella",
            "slimecorpumbrella"
        ],
        str_crit="**Critical hit!!** {name_player} briefly stuns {name_target} by opening their umbrella in their face, using the opportunity to score a devastating blow to their {hitzone}.",
        str_miss="**MISS!!** {name_player} fiddles with their umbrella, failing to open it!",
        str_equip="You equip the umbrella.",
        str_name="umbrella",
        str_weapon="an umbrella",
        str_weaponmaster_self="You are a rank {rank} {title} of the umbrella.",
        str_weaponmaster="They are a rank {rank} {title} of the umbrella.",
        # str_trauma_self = "You have a large hole in your chest.",
        # str_trauma = "They have a large hole in their chest.",
        str_kill="*SPLAT.* {name_player} pierces {name_target} through the chest, hoists them over their head, and opens their umbrella, causing them to explode in a rain of blood and slime. {emote_skull}",
        str_killdescriptor="umbrella'd",
        str_damage="{name_target} is struck in the {hitzone}!!",
        str_duel="**THWACK THWACK.** {name_player} and {name_target} practice their fencing technique, before comparing their favorite umbrella patterns.",
        str_scalp=" At least it didn't get wet.",
        fn_effect=get_normal_attack(weapon_type='defensive'),
        str_description="It's an umbrella, both stylish and deadly.",
        price=100000,
        vendors=[ewcfg.vendor_bazaar],
        classes=[ewcfg.weapon_class_defensive, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_umbrella_kills,
        captcha_length=4,
        str_brandish="{name} takes {weapon} and daintily drapes it over their shoulder, batting their eyes for good measure."
    ),
    EwWeapon(  # 22
        id_weapon=ewcfg.weapon_id_bow,
        alias=[
            "bow",
        ],
        str_crit="**Critical hit!!** Through measured shots {name_player} manages to stick a pixelated arrow in {name_target}’s {hitzone}.",
        str_miss="**MISS!!** {name_player} completely misses, a pixelated arrow embeds itself into the ground!",
        str_equip="You equip the minecraft bow, c418 music plays in the background.",
        str_name="minecraft bow",
        str_weapon="a minecraft bow",
        str_weaponmaster_self="You are a rank {rank} minecraft bow {title}.",
        str_weaponmaster="They are a rank {rank} minecraft bow {title}.",
        # str_trauma_self = "There is a pixelated arrow in the side of your head.",
        # str_trauma = "There is a pixelated arrow in the side of their head.",
        str_kill="*Pew Pew Pew.* {name_player} spams the bow as {name_target}'s life fades, riddling their body with arrows. {emote_skull}",
        str_killdescriptor="shot to death",
        str_damage="{name_target} is shot in the {hitzone}!!",
        str_duel="{name_player} and {name_target} shoot distant targets, {name_player} is clearly the superior bowman.",
        str_scalp=" The scalp has pixels covering it.",
        fn_effect=get_normal_attack(weapon_type='small_game'),
        str_description="It's a newly crafted minecraft bow, complete with a set of minecraft arrows",
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_bow_kills,
        str_brandish="{name} mashes shift, crouching rapidly and pointing {weapon} to the heavens!"
    ),
    EwWeapon(  # 23
        id_weapon=ewcfg.weapon_id_dclaw,
        alias=[
            "dragon claw",
        ],
        str_crit="{name_player} runs like a madman towards {name_target}, {name_target} swings but is deftly parried by {name_player}, {name_player} hoists their dragon claw into the air and ripostes {name_target} for massive damage ***!!!Critical Hit!!!***",
        str_miss="{name_player} swings but {name_target} is in the middle of a dodge roll and is protected by iframes. **!!Miss!!**",
        str_equip="You place the core of the dragon claw on your hand and it unfolds around it, conforming to the contour of your hands. Claws protude out the end of your fingers as your hand completes its transformation into the *dragon claw*.",
        str_name="dragon claw",
        str_weapon="a dragon claw",
        str_weaponmaster_self="You are a rank {rank} {title} of the dragon claw.",
        str_weaponmaster="They are a rank {rank} {title} of the dragon claw.",
        # str_trauma_self = "Three smoldering claw marks are burned into your flesh, the flames `won't seem to extinguish.",
        # str_trauma = "Three smoldering claw marks are burned into their flesh, the flames won't seem to extinguish.",
        str_kill="***Thwip.*** {name_player}'s dragon claw cuts the air followed by a trail of flame and blood, the camera pans out and {name_target} is shown, cut in twain. {emote_skull}",
        str_killdescriptor="cut to pieces",
        str_damage=random.choice(["{name_target} is slashed across the {hitzone}!!", "{name_player} furiously slashes {name_target} across the {hitzone}!!", "{name_player} flicks their fingers and a jet of flame ignites from the dragon claw, burning {name_target} in the {hitzone}!!"]),
        str_duel="**SLICE!! SWIPE!! SLASH!!** {name_player} and {name_target} cut the fuck out of eachother, a fire extinguisher is never more than a meter away.",
        str_scalp="The scalp is burning and doesn't look like it's gonna stop.",
        fn_effect=get_normal_attack(weapon_type='incendiary'),
        str_description="It's the core of a Dragon Claw, it will morph around whatever hand it is held by granting them the power of the elusive GREEN EYES SLIME DRAGON. If you listen closely you can hear whines of the dragon soul as it remains perpetually trapped in the weapon.",
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_dclaw_kills,
        classes=[ewcfg.weapon_class_burning, ewcfg.weapon_class_captcha],
        captcha_length=4,
        str_brandish="{name} does a Praise the Sun, {weapon} in hand!"
    ),

    EwWeapon(  # 24
        id_weapon=ewcfg.weapon_id_spraycan,
        alias=[
            "spray can",
            "spray"
        ],
        str_crit="**Critical hit!!** {name_player} flicks the nozzle off their spray can and lights it like a fuse! {name_target} gets nasty burns and a fresh coat of paint! **WHOOSH!!!**",
        str_miss="**MISS!!** {name_player} attempts a spray attack, but the wind blows it back in their face!",
        str_equip="You hold the spray can tightly, hoping to god somebody confuses it for a gun.",
        str_name="spray can",
        str_weapon="a spray can",
        str_weaponmaster_self="You are a rank {rank} {title} vandal of the spray can.",
        str_weaponmaster="They are a rank {rank} {title} vandal of the spray can.",
        # str_trauma_self = "You're having trouble breathing, and the inside of your mouth is off-color.",
        # str_trauma = "They're weirdly short of breath, and their mouth and tongue are off-color.",
        str_kill="***PPPPPPSSSSSSSSSHHHHHhhhhhfff.*** {name_player} forcibly opens {name_target}'s mouth and sprays everything they have into their lungs. Their eyes roll back into their head and, trembling, they slowly asphyxiate in your arms. {emote_skull}",
        str_killdescriptor="suffocated",
        str_damage=random.choice(["{name_target} is whacked across the {hitzone}!!",
                                  "{name_player} sprays {name_target} with paint, making them a gaudy color in the {hitzone}!!",
                                  "{name_player} humiliates {name_target} by bringing a spray can to a gunfight, mentally damaging them in the {hitzone}!!"]),
        str_duel="**PSSS PSSS PSSSSSHH!** {name_player} and {name_target} spray the dojo walls until they get dizzy from the smell.",
        str_scalp="The scalp is a nice shade of mauve.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="It's a Based Hardware brand spray can, in your gang's color. The blurb on the backside preaches about the merits of street art and murals, but you're pretty sure that's just to cover their ass.",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_spraycan_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        # sap_cost=2,
        captcha_length=3,
        is_tool=1,
        # str_backfire = "As {name_player} shakes the can to fire another shot, the thing suddenly explodes on them!",
        tool_props={
            'reg_spray': "You run down the streets, tagging buildings, street signs, and old ladies with spray paint in the image of the {gang}!",
            'miss_spray': "**Miss!** Your can seems to be low on spray. You fill it up and give it a good shake. Good as new!",
            'crit_spray': "**Critical hit!** You dual wield spray cans, painting an urban masterpiece in one hand and shooting toxic chemicals into a cop's mouth with the other!",
            'equip_spray': "You get your trusty spray paint at the ready."},
        str_brandish="**PSSSSSSHHHHHT!** {name} takes out {weapon} and sprays down a nearby wall!\n{tag}"
    ),
    EwWeapon(  # 25
        id_weapon=ewcfg.weapon_id_paintgun,
        alias=[
            "paint gun",
            "splatoon"
        ],
        str_crit="**Critical hit!!** {name_player} aims down the sights with the precision of a video game real life sniper, shooting {name_target} in the eyes from 30 yards! **SPLAAAAAT!!!**",
        str_miss="**MISS!!** {name_player} fires off a volley of paint, but {name_target} jumps behind cover!",
        str_equip="Now listen here. You just equipped a paint gun. Keep in mind this is the weapon that boomer families shoot each other with to have fun. Enjoy trying to kill with it.",
        str_name="paint gun",
        str_weapon="a paint gun",
        str_weaponmaster_self="You are a rank {rank} {title} vandal of the paint gun.",
        str_weaponmaster="They are a rank {rank} {title} vandal of the paint gun.",
        # str_trauma_self = "You have a splitting headache.",
        # str_trauma = "They look hungover, almost like their entire body exploded.",
        str_kill="***SPLAAAAART!!!!*** {name_player} fatally strikes {name_target}, and they explode from the inside out! There's a lot more gore than when you see it happen in Splatoon, though.{emote_skull}",
        str_killdescriptor="imploded",
        str_damage=random.choice(["{name_target} is splatted in the {hitzone}!!",
                                  "{name_player} shoots {name_target} with paint, making them a gaudy color in the {hitzone}!!",
                                  "{name_player} attacks {name_target} with harmless paint!!"]),
        str_duel="**SPLAT TAT TAT!!** {name_player} and {name_target} harass everyone in the dojo with their paint guns.",
        str_scalp="The scalp is colorful, from both blood and paint.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="It's an industrial strength two handed paint gun with a sniper scope attached. What do they use this for in industry, anyway?",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_paintgun_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_ammo, ewcfg.weapon_class_captcha],
        clip_size=15,
        price=5000,
        # sap_cost=2,
        captcha_length=4,
        is_tool=1,
        str_reload="*Click.* You grab a paint cylinder from god knows where and load it into your gun, chucking the leftover one behind an alleyway.",
        # str_backfire = "Whoops, looks like somebody didn't fasten the paint cylinder hard enough! {name_player} gets a thorough spray to the face!",
        tool_props={
            'reg_spray': "You find a patch of wall several yards away that hasn't been vandalized yet. Time to take aim and...BAM! Nice shot!",
            'miss_spray': "**Miss!** Your aim was as sharp as ever, but a fucking pigeon took the hit! Christ, what are the odds?",
            'crit_spray': "**Critical hit!** The paint bullet skids a wall, spreading your paint across the whole thing!",
            'equip_spray': "You load a clip of paint into the gun and throw it onto your back, kinda like Rambo if he were an art major."
        },
    str_brandish="**SPLAAART!** {name} takes out {weapon} and inks the fuck out of a nearby splat zone!\n{tag}"
    ),
    EwWeapon(  # 26
        id_weapon=ewcfg.weapon_id_paintroller,
        alias=[
            "paint roller",
            "roller"
        ],
        str_crit="**Critical hit!!** {name_player}  knocks {name_target} to the ground and does a golf swing to their vulnerable little head, sending them spinning. **FWAP!!!**",
        str_miss="**MISS!!** {name_player} does cringey bo staff jujitsu moves with the roller and forgets to actually attack {name_target}!",
        str_equip="You hold the paint roller in your hand. The light plastic broom handle and spongy brush are sure to deal at least 10 damage.",
        str_name="paint roller",
        str_weapon="a paint roller",
        str_weaponmaster_self="You are a rank {rank} {title} vandal of the paint roller.",
        str_weaponmaster="They are a rank {rank} {title} vandal of the paint roller.",
        # str_trauma_self = "There's a gaudy colored dent in your skull.",
        # str_trauma = "There is a gaudy colored dent in their skull.",
        str_kill="***CA-CRACK!*** {name_player} opens {name_target}'s skull like an egg using the dull metal edge of the roller. It appears to be hollow, after all, {name_target} was stupid enough to get killed with a fucking paint roller.{emote_skull}",
        str_killdescriptor="cracked open",
        str_damage=random.choice(["{name_target} is swatted in the {hitzone}!!",
                                  "{name_player} slaps {name_target} with paint, making them a gaudy color in the {hitzone}!!",
                                  "{name_player} rolls paint all over {name_target}'s {hitzone}!!"]),
        str_duel="{name_player} and {name_target} quietly pass the time rolling paint over the windows of nearby houses You both have learned tranquility.",
        str_scalp="The scalp is split in half, with a big hole right in the middle.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=4500,
        str_description="It's a long, broom-like plastic paint roller with a spongy brush and metal axle. The modern man's bo staff.",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_paintroller_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        # sap_cost=2,
        captcha_length=4,
        is_tool=1,
        # str_backfire = "{name_player} waves the paint roller around like it's a plastic toy, spreading paint nowhere but giving themselves a thorough welt in the head from the 2 square inches of it that could actually do any damage. How'd they manage that?",
        tool_props={
            'reg_spray': "You roll paint over as much surface area as your puny little Juvie legs can take you to.",
            'miss_spray': "**Miss!** The sponge on your roller snaps off and it takes too long for you to notice. What a waste!",
            'crit_spray': "**Critical hit!** Your mind goes blank in a painting-induced rage. When you wake up, all your surroundings are {color}. You should do that more often!",
            'equip_spray': "You grab your paint roller and strap it on your back."},
        str_brandish="{name} takes out {weapon} and paints up the town!\n{tag}"
    ),
    EwWeapon(  # 27
        id_weapon=ewcfg.weapon_id_paintbrush,
        alias=[
            "paint brushes",
            "brush"
        ],
        str_crit="**Critical hit!!** {name_player} stabs {name_target} with one brush and paints over their eyes with another!  **HOT DOG!!!**",
        str_miss="**MISS!!** {name_player} throws the brushes at {name_target}, but they get hit with the soft bristles instead of the pointy bit!",
        str_equip="If only you had a whittling knife that could sharpen paintbrush handles. That way you could equip the knife as a weapon instead of this.",
        str_name="paintbrushes",
        str_weapon="paintbrushes",
        str_weaponmaster_self="You are a rank {rank} {title} vandal of the paintbrush.",
        str_weaponmaster="They are a rank {rank} {title} vandal of the paintbrush.",
        # str_trauma_self = "You have bruises all over your body and you can't get the paint out of your clothes.",
        # str_trauma = "They have bruises all over their body, and they can't get the paint out of their clothes.",
        str_kill="***MASTERPIECE!*** {name_target} takes a mortal brush to the forehead, courtesy of {name_player}'s talent as a painter. {emote_skull}",
        str_killdescriptor="paintbrushed to death",
        str_damage=random.choice(["{name_target} is handlestabbed in the {hitzone}!!",
                                  "{name_player} flecks {name_target} with paint, making them a gaudy color in the {hitzone}!!",
                                  "{name_player} grazes {name_target}'s {hitzone} with coarse bristles!!"]),
        str_duel="{name_player} and {name_target} paint random text commands on the walls outside the Dojo. {name_target} paints some furry art when nobody's looking.",
        str_scalp="The scalp has a bunch of welts, and has a faint smell of lead.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="A stack of large, coarse-bristled paintbrushes, linked together on a burlap string.",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_paintbrush_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        # sap_cost=2,
        price=100,
        captcha_length=3,
        is_tool=1,
        # str_backfire = "In an attempt to paint faster, {name_player} sticks one of the handles in their mouth and try to use it to cover more ground. Instead, they broke your teeth and scraped their cheek on a hard brick surface. Better not try that again...",
        tool_props={
            'reg_spray': "You paint vulgar {gang} symbols on as many buildings as you can.",
            'miss_spray': "**Miss!** You finish with a paint can and have to switch! You waste too much time getting the can open.",
            'crit_spray': "**Critical hit!**  You hold the paint can in your mouth and start crab walking, throwing paint along the wall as you do it! Somehow, this is more efficient!",
            'equip_spray': "You get your brushes at the ready."},
        str_brandish="{name} grips {weapon} tightly, pensive look on their face.\n{tag}"
    ),
    EwWeapon(  # 28
        id_weapon=ewcfg.weapon_id_watercolors,
        alias=[
            "paint brushes",
            "brush"
        ],
        str_crit="```css\n\"oooOOOOOOOH LA LA! {name_target} is exposed to {name_player}'s watercolor pornography! They won't be able to recover from that!\"\n```",
        str_miss="```css\n[{name_player} paints a picture for {name_target}. It does no damage, as expected.]\n```",
        str_equip="```ini\n[You get a nice mug to dip your little paintbrush in, and open your 12 set of watercolors. Look out world, here comes you!]\n```",
        str_name="watercolors",
        str_weapon="a set of watercolors",
        str_weaponmaster_self="You are a rank {rank} {title} flaming homosexual of watercolors.",
        str_weaponmaster="They are a rank {rank} {title} flaming homosexual of watercolors.",
        # str_trauma_self = "You are eternally humiliated after being murdered by a gangster wielding watercolor paints.",
        # str_trauma = "They are eternally humiliated after being murdered by a gangster wielding watercolor paints.",
        str_kill="```bash\n\"HUUUUUUH?? {name_target} goes and kills themselves after having an existential crisis! {name_player} seems to have done this with only their own retardation!\"\n```",
        str_killdescriptor="driven to suicide",
        str_damage="```ini\n[{name_player} paints a picture of {name_target}. Their self esteem takes a hit!]\n```",
        str_duel="```json\n\"{name_player} and {name_target} practice art using Dojo-owned easels and canvases. Eventually, the training session breaks down and, you just throw paint water at each other and giggle like schoolgirls.\"\n```",
        str_scalp="The scalp is perfectly intact.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="A 12 pack of watercolors, the kind you used when you were a 5 years old boy.",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_watercolor_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        # sap_cost=2,
        price=1300,
        captcha_length=3,
        is_tool=1,
        # str_backfire = "{name_player} has the idea of trying to paint their parents fucking, thinking it will be really funny and everyone will love them. Pretty soon we're going to have to ban watercolors because people like you are using them to molest yourself.",
        tool_props={
            'reg_spray': "Nice drawing, {curse}! ",
            'miss_spray': "**Miss!** Your painting sucks. God, you're stupid. ",
            'crit_spray': "After the thousandth failed watercolor gesamtkunstwerk you decide enough is enough. Fuck this. Fuck the gangs, fuck the violence, fuck the perpetually rotting lets player that compels you to rigor mortis yourself more frequently than you eat breakfast. The spite is so concentrated that it compels you to turn your life around. You get a fake ID, join the PTA, and rope them into cleaning every last inch of this district until the homeless population smell like citrus and give out free, non-tainted lollipops. However, your newfound peaceful life is interrupted by the night terrors ENDLESS WAR now gives you on a daily basis, and you decide to go back to being a gangster. You suppose some things never change.",
            'equip_spray': "You get out your 12 pack of watercolors. Can't believe you have to use one of these."
        },
        str_brandish="{name} prances around and sings a gay little song! **\"I'M A GIRL, I HAVE TITS, I HAVE PUSSY AND A CLIT, I'M A GIRL, I HAVE TITS, I HAVE PUSSY AND A CLIT!\"**"
    ),
    EwWeapon(  # 29
        id_weapon=ewcfg.weapon_id_thinnerbomb,
        alias=[
            "thinner",
            "thinnerbombs"
        ],
        str_crit="**Critical hit!!** {name_player} slams {name_target} with a bottle of paint thinner, showering their face with broken glass and getting some of the thinner down their gullet. They fall back, dazed and bleeding.",
        str_miss="**MISS!!** {name_player} is too dazed by their own chemicals to make a move! They drop the bottle on accident, throwing vapors all over the place.",
        str_equip="You pull out the thinner bombs and hold their bottlenecks between your fingers. Never has a not-weapon ever felt so cool.",
        str_name="thinner bombs",
        str_weapon="thinner bombs",
        str_weaponmaster_self="You are a rank {rank} {title} vandal of the thinner bomb.",
        str_weaponmaster="They are a rank {rank} {title} vandal of the thinner bomb.",
        # str_trauma_self = "You have the hangover from hell.",
        # str_trauma = "They have the hangover from hell.",
        str_kill="***WHAT A SIZZLER!*** {name_target}, dazed from the concentrated toxic chemicals in the air, falls to the ground, giving {name_player} the chance to stab them through the neck with the broken bottle. Inhalants. Not even once. {emote_skull}",
        str_killdescriptor="drugged",
        str_damage=random.choice(["{name_target} gets a thinnerbomb to the {hitzone}!!",
                                  "{name_player} slashes {name_target} with a broken thinnerbomb! Ooh, right in the {hitzone}!!"]),
        str_duel="{name_player} and {name_target} build a resistance to the noxious chemicals they're using by drinking paint thinner together. Cheers.",
        str_scalp="The scalp smells awful, you can hardly hold it.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="A pack of brittle glass bottles filled with paint thinner. This stuff vaporizes like nobody's business, and could strip the osmotic membrane off a slimeoid.",
        vendors=[ewcfg.vendor_basedhardware, ewcfg.vendor_breakroom],
        stat=ewcfg.stat_thinnerbomb_kills,
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        # sap_cost=2,
        price=15000,
        captcha_length=4,
        is_tool=1,
        # str_backfire = "You haven't had a good buzz in awhile, so you take a whiff of one of your thinner bombs. Great trip and all, but you rough yourself up convulsing on the ground while it happens.",
        tool_props={
            'reg_spray': "You find a vandalized wall and toss a thinner bomb on it! You hear a faint sizzling as paint begins to strip off the walls. Sick!",
            'miss_spray': "**Miss!** You make a mistake on the throw's distance and it bursts uselessly on the ground. You got to do some littering, so at least there's that.",
            'crit_spray': "**Critical hit!** You take out a paint bomb and throw it at a particularly fragile looking building. The chemicals you used were so caustic that they burned a hole through the whole wall, preventing anyone from painting it for all of time!",
            'equip_spray': "You get your glass thinner bombs out you you can throw them in a moment's notice."
        },
        str_brandish="{name} takes a huge whiff from {weapon}! They let out a confused battlecry and start tripping around!"
    ),
    EwWeapon(  # 30
        id_weapon=ewcfg.weapon_id_staff,
        alias=[
            "eldritchstaff",
            "spookystaff",
            "reprehensiblerod",
            "wickedwand",
            "frighteningfaggot"
        ],
        str_miss="Your mind goes blank as you feel slime disappear from your body in preparation for a deadly attack.",
        str_damage="{name_player} finalizes their invocation. " + random.choice([
            "Gravity violently increases in the space around {name_target}, slamming them into the ground.",
            "A blinding white light shines from {name_target}'s {hitzone} as it burns hotter than the surface of the sun.",
            "Spectral hands caress {name_target}'s body, leaving gaping wounds in their path.",
            "An unseen force suddenly yoinks {name_target} by their {hitzone}, sending them flying into the air.",
            "A pitch black horror forms around {name_target}'s {hitzone} and tears into it."
        ]),
        str_crit="{name_player} notices {name_target} still recoiling from the damage, and takes the chance to bonk the everliving shit out of them with their staff. **Critical hit!!**",
        str_kill="A mass of tiny hands erupts from the ground below {name_target}, grabbing on to their body. Their screams echo across the streets as they're dragged through the ground and into the sewers.",
        str_equip="You equip the eldritch staff.",
        str_name="eldritch staff",
        str_weapon="an eldritch staff",
        str_weaponmaster_self="You are a rank {rank} {title}-conduit of the ones below.",
        str_weaponmaster="They are a rank {rank} {title}-conduit of the ones below.",
        str_killdescriptor="cast down",
        str_duel="{name_player} and {name_target} compare notes on their understanding of the eldritch fuckery they've each experienced.",
        str_description="An intricate wooden staff with a cloudy crystal on its handle. It looks fucking class, but it also gives you the creeps.",
        str_scalp="It's covered in symbols written with a strange black substance.",
        fn_effect=wef_staff,
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_staff_kills,
        # sap_cost = 2,
        captcha_length=10,
        str_brandish="{name} lifts {weapon} and begins to chant unholy incantations! Small rocks slowly rise from the ground around them... \n\nWhoops, they forgot the last bit. The spell collapses."
    ),
    EwWeapon(  # 31
        id_weapon=ewcfg.weapon_id_hoe,
        str_miss="**MISS!!** {name_player}'s hoe strikes the earth with a loud THUD.",
        str_damage="{name_player} scrapes their hoe across {name_target}'s {hitzone}.",
        str_crit="**CRITICAL HIT!!** {name_player} gets their hoe deep into {name_target}'s body, cutting up their vitals!",
        str_kill="{name_player} pushes {name_target} to the ground. After an intense windup, they slam their hoe down on {name_target}'s neck, decapitating them in the process.",
        str_equip="You ready your hoe.",
        str_name="hoe",
        str_weapon="a hoe",
        str_weaponmaster_self="You are a rank {rank} {title} farmer of the hoe.",
        str_weaponmaster="They are a rank {rank} {title} farmer of the hoe.",
        str_killdescriptor="!reaped",
        str_duel="{name_player} and {name_target} discuss their latest harvest and exchange farming tips.",
        str_description="It's a farming hoe.",
        str_scalp="It's covered in dirt.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=100000,
        vendors=[ewcfg.vendor_atomicforest],
        classes=[ewcfg.weapon_class_farming, ewcfg.weapon_class_juvie],
        stat=ewcfg.stat_hoe_kills,
        # sap_cost = 2,
        captcha_length=2,
        is_tool=1,
        str_brandish="{name} takes the piece of hay out of their mouth and spits chewing tobacco onto the ground! Varmints round here get {weapon} to the face."
    ),
    EwWeapon(  # 32
        id_weapon=ewcfg.weapon_id_pitchfork,
        str_miss="**MISS!!** {name_player}'s pitchfork is planted firmly into the ground.",
        str_damage="{name_player} stabs {name_target}'s {hitzone} with their pitchfork!",
        str_crit="**CRITICAL HIT!!** {name_player} pokes several holes in {name_target}!",
        str_kill="{name_player} plants their pitchfork firmly into {name_target} and lifts them high into the air. After {name_target} loses consciousness, {name_player} throws them to the ground and stabs them again for good measure.",
        str_equip="You pick up your pitchfork and give the ground a light tap with the handle's end.",
        str_name="pitchfork",
        str_weapon="a pitchfork",
        str_weaponmaster_self="You are a rank {rank} {title} farmer of the pitchfork.",
        str_weaponmaster="They are a rank {rank} {title} farmer of the pitchfork.",
        str_killdescriptor="!reaped",
        str_duel="{name_player} and {name_target} joust with their pithforks. Thankfully, no one gets hurt in the process.",
        str_description="It's a farming pitchfork.",
        str_scalp="It's got three holes in it.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=100000,
        vendors=[ewcfg.vendor_atomicforest],
        classes=[ewcfg.weapon_class_farming, ewcfg.weapon_class_juvie],
        stat=ewcfg.stat_pitchfork_kills,
        # sap_cost = 2,
        captcha_length=2,
        is_tool=1,
        str_brandish="{name} raises {weapon} into the air. Kill them! Kill them all!"
    ),
    EwWeapon(  # 33
        id_weapon=ewcfg.weapon_id_shovel,
        str_miss="**MISS!!** {name_player}'s shovel is planted firmly into the ground.",
        str_damage="{name_player} swings their shovel at {name_target}'s {hitzone}!",
        str_crit="**CRITICAL HIT!** The flat end of {name_player}'s shovel impacts {name_target}'s chest! They start coughing up blood!",
        str_kill="*BONK!* {name_player}'s shovel lands right on top of {name_target}'s head. Their skull and brain is completely crushed by the impact. {name_player} buries them in a shallow grave.",
        str_equip="You grip your shovel tightly in both hands.",
        str_name="shovel",
        str_weapon="a shovel",
        str_weaponmaster_self="You are a rank {rank} {title} farmer of the shovel.",
        str_weaponmaster="They are a rank {rank} {title} farmer of the shovel.",
        str_killdescriptor="!digged",
        str_duel="{name_player} and {name_target} perform a high-shovel. The moment could not be more perfect.",
        str_description="It's a shovel.",
        str_scalp="It's flattened.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=100000,
        vendors=[ewcfg.vendor_atomicforest],
        classes=[ewcfg.weapon_class_juvie],
        stat=ewcfg.stat_shovel_kills,
        # sap_cost = 2,
        captcha_length=2,
        is_tool=1,
        str_brandish="{name} rams {weapon} into the ground. Time to strike the earth!"
    ),
    EwWeapon(  # 34
        id_weapon=ewcfg.weapon_id_slimeringcan,
        str_miss="**MISS!!** Spouts of slime from {name_player}'s Slimering Can fly everywhere!",
        str_damage="{name_player} pours slime onto {name_target}'s {hitzone}. What the fuck is that going to accomplish?",
        str_crit="**CRITIAL HIT!!** {name_player} pours slime onto {name_target}'s eyes! How unsanitary!",
        str_kill="{name_player} rams their Slimering Can down {name_target}'s throat. {name_target} chokes to death on slime.",
        str_equip="You pick up your Slimering Can.",
        str_name="slimering can",
        str_weapon="a slimering can",
        str_weaponmaster_self="You are a rank {rank} {title} green thumbed coward.",
        str_weaponmaster="They are a rank {rank} {title} green thumbed coward.",
        str_killdescriptor="drowned",
        str_duel="{name_player} and {name_target} water flowers together. Sometimes it's nice to be a fucking weak willed coward, y'know?",
        str_description="It's a slimering can.",
        str_scalp="It's soaking wet.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=100000,
        vendors=[ewcfg.vendor_atomicforest],
        classes=[ewcfg.weapon_class_juvie],
        stat=ewcfg.stat_slimeringcan_kills,
        # sap_cost = 2,
        captcha_length=2,
        is_tool=1,
        str_brandish="OK, {name}. I get that you're trying to be scary with {weapon} and all. It's a fucking watering can. Get real, garden boy."
    ),
    EwWeapon(  # 35
        id_weapon=ewcfg.weapon_id_fingernails,
        alias=[
            "fingernails",
            "nails"
        ],
        str_crit="**Critical hit!!** {name_target} is cut deep!!",
        str_miss="",
        str_equip="",
        str_name="fingernails",
        str_weapon="their fingernails",
        str_weaponmaster_self="",
        str_weaponmaster="",
        # str_trauma_self = "A single clean scar runs across the entire length of your body.",
        # str_trauma = "A single clean scar runs across the entire length of their body.",
        str_kill="{name_player} lunges at {name_target} with fingernails bared! They're mercilessly rips them to pieces, tufts of skin flying every which way! **BRRRRRRRAP!!!** When the dust settles, {name_target} is unrecognizable, and more importantly, dead as fuck. {emote_skull}",
        str_killdescriptor="torn apart",
        str_damage="{name_target} is slashed across the {hitzone}!!",
        str_duel="",
        str_description="",
        str_scalp=" Multiple slash marks run across it.",
        fn_effect=get_normal_attack(weapon_type="normal", hit_chance=-1),
        price=0,
        stat=ewcfg.stat_fingernails_kills,
        # sap_cost = 3,
        captcha_length=8,
        str_brandish=""
    ),
    EwWeapon(  # 35
        id_weapon=ewcfg.weapon_id_roomba,
        alias=[
            "roomba",
            "vaccuum"
        ],
        str_crit="**Critical hit!!** {name_target} gets a concussion via roomba to the face!!",
        str_miss="**MISS!** The roomba forgets where it is and begins tripping around!",
        str_equip="You turn on your Roomba and place it on the ground.",
        str_name="roomba",
        str_weapon="a roomba",
        str_weaponmaster_self="You are a rank {rank} roomba {title}.",
        str_weaponmaster="They are a rank {rank} roomba {title}.",
        # str_trauma_self = "A single clean scar runs across the entire length of your body.",
        # str_trauma = "A single clean scar runs across the entire length of their body.",
        str_kill="{name_player} jumps at {name_target} using the roomba as a springboard! Screaming bloody murder, they beat {name_target} to within an inch of their life. The roomba follows, sucking whatever morsel of slime was left. Job finished. {emote_skull}",
        str_killdescriptor="sucked dry",
        str_damage="{name_player}'s roomba sucks gobs of slime out of {name_target}'s {hitzone}!!",
        str_duel="{name_player} and {name_target} begin engineering their portable vaccuums into high class battle bots. By the time you're done the Dojo floor is spotless and everyone nearby is dead.",
        str_description="It's a high powered portable vaccuum designed to clean up dust. You use it to spread paint around by attaching a spray can to the back.",
        str_scalp=" It looks stretched and wrinkled.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        price=40000,
        # str_backfire="You roomba turns on you! Its shitty AI thinks your feet are its prey, and it sucks away some precious slime!",
        vendors=[ewcfg.vendor_basedhardware],
        classes=[ewcfg.weapon_class_paint, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_roomba_kills,
        # sap_cost = 3,
        captcha_length=8,
        tool_props={
            'reg_spray': "The roomba continues its intrepid journey spraying paint around town.",
            'miss_spray': "**Miss!** Fuck, the thing got stuck on a pothole again.",
            'crit_spray': "**Critical hit!** A bystander walking by kicks your roomba as it's moving, which inadvertently overclocks its processor!! It speeds around the area with reckless abandon. Go go go!",
            'equip_spray': "You pull out your roomba and set it on the ground."
        },
        str_brandish="{name} can't find {weapon} anywhere! It's off vaccuming the sewer rats somewhere. They flip the bird instead."
    ),
    EwWeapon(  # 36
        id_weapon=ewcfg.weapon_id_laywaster,
        alias=[
            "chainsaw",
            "megachainsaw",
            "widowmaker",
            "jessica"
        ],
        str_crit="**Critical Hit!** {name_player} snaps {name_target} between two of the sawblades, ripping mercilessly into flesh and nearly vaporizing the spraying blood!",
        str_miss="**Miss!** {name_player} swings the heavy blade around and hits nothing but air.",
        str_equip="You rev up the Laywaster 9000.",
        str_name="multiblade chainsaw",
        str_weapon="a multiblade chainsaw",
        str_weaponmaster_self="You are a rank {rank} {title} of the Laywaster 9000.",
        str_weaponmaster="They are a rank {rank} {title} of the Laywaster 9000.",
        # str_trauma_self = "You have a few large, gaping holes in your abdomen. Someone could stick their arm through the biggest one.",
        # str_trauma = "They have a few large, gaping holes in your abdomen. Someone could stick their arm through the biggest one.",
        str_kill="**VRRRRRRRRRRRRRRRRRRRRRRRRRRRR!**{name_player} swings violently through {name_target}'s unconscious body, each slash making them more unrecognizable than the last. As more and more blood flecks across {name_player}'s face, their opponent turns into a pile of viscera. {emote_skull}",
        str_killdescriptor="shredded to a paste",
        str_damage="{name_target}'s {hitzone} is torn into!! Blood flies everywhere!",
        str_duel="**...** {name_player} and {name_target} clash with each other chainsaw blow for chainsaw blow like badasses.",
        str_description="It's a multi-bladed chainsaw.",
        str_scalp=" It's not really a scalp anymore, more of a paste.",
        fn_effect=get_normal_attack(weapon_type='heavy'),
        price=1000000,
        vendors=[],
        classes=[],
        stat=ewcfg.stat_megachainsaw_kills,
        str_brandish="{name} revs their Laywaster against a street sign! Sparks are flying!"
    ),
    EwWeapon(  # 37
        id_weapon=ewcfg.weapon_id_chainsaw,
        alias=[
            "ripper",
            "motoraxe"
        ],
        str_crit="**Critical hit!!** The jagged teeth of the chainsaw rest within {name_target}'s body as the slime flies!!",
        str_miss="**You missed!!** In {name_player}’s excitement and desperation neither chain nor saw hits {name_target}!",
        str_equip="You equip the chainsaw.",
        str_name="chainsaw",
        str_weapon="a chainsaw",
        str_weaponmaster_self="You are a rank {rank} {title} of the chainsaw.",
        str_weaponmaster="They are a rank {rank} {title} of the chainsaw.",
        # str_trauma_self = "Your body runs jagged with large chunks missing and patches of skin torn up.",
        # str_trauma = "Their body runs jagged with large chunks missing and patches of skin torn up.",
        str_kill="**REEERNREERN!!** {name_player} revs up their chainsaw and carves up {name_target}’s torso, cutting through the guts, bile, viscera, and slime, sending it all flying. They’ve been cut down to size. {emote_skull}",
        str_killdescriptor="chainsaw’d",
        str_damage="The numerous finely tooth blades tear at {name_target}’s {hitzone}!!",
        str_duel="**...** {name_player} and {name_target} clash with each other chainsaw blow for chainsaw blow like badasses.",
        str_description="It's a chainsaw.",
        # str_reload = "You desperately pull at the ripcord of your chainsaw trying to rev it back up to speed.",
        # str_reload_warning = "**REEERNREERN--** *shhhhh…* **FUCK!!** {name_player}’s chainsaw just ran out of it’s rev!!",
        str_scalp="It’s more like a collection of dandruff then a scalp.",
        fn_effect=get_normal_attack(weapon_type='heavy'),
        price=1000000,
        vendors=[ewcfg.vendor_basedhardware],
        classes=[],
        stat=ewcfg.stat_chainsaw_kills,
        str_brandish="{name} revs {weapon} against a street sign! Sparks are flying!"
    ),
    EwWeapon(  # 38
        id_weapon=ewcfg.weapon_id_huntingrifle,
        alias=[
            "hrifle",
            "boltaction",
            "oldrifle"
        ],
        str_crit="**Critical hit!!** {name_target}'s skull gains another hole! Good show!!",
        str_miss="**You missed!!** {name_player} misses {name_target} by a barn door and a half. Phooey!",
        str_equip="You equip the hunting rifle.",
        str_name="hunting rifle",
        str_weapon="a hunting rifle",
        str_weaponmaster_self="You are a rank {rank} {title} gentleman of the hunting rifle.",
        str_weaponmaster="They are a rank {rank} {title} gentleman of the hunting rifle.",
        str_kill="**360 NOSCOPED!!** {name_player} spins and fires! {name_target}'s head subsequently explodes! Get wr3ck3d, my good sir! {emote_skull}",
        str_killdescriptor="d3s7r0y3d",
        str_damage="{name_player} sneaks a few shots into {name_target}’s {hitzone}!!",
        str_duel="**...** {name_player} and {name_target} spin around like idiots, firing wildly and sipping tea.",
        str_description="It's a hunting rifle, lovingly repaired.",
        str_reload="You carefully dip each bullet in a cup of tea before loading them into the gun.",
        str_reload_warning="**OH, BOTHER!** {name_player}’s hunting rifle just ran out bullets!!",
        str_scalp="A single, clean hole pierces the scalp. Ahhh, the thrill of the hunt...",
        fn_effect=get_normal_attack(cost_multiplier=1.2, weapon_type='precision'),
        classes=[ewcfg.weapon_class_ammo, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_huntingrifle_kills,
        clip_size=6,
        acquisition=ewcfg.acquisition_smelting,
        captcha_length=4,
        str_brandish="{name} uses {weapon} to poach a nearby elephant! How'd they find an elephant?"
    ),
    EwWeapon(  # 39 Unused, untested afaik -K1P
        id_weapon=ewcfg.weapon_id_harpoon,
        alias=[
            "harpoon",
            "whitewhale",
            "harpoongun"
        ],
        str_crit="**Critical hit!!** {name_target}'s totally hooked!!",
        str_miss="**You missed!!** {name_player} misses {name_target}! FUCK!!",
        str_equip="You equip the harpoon gun.",
        str_name="harpoon gun",
        str_weapon="a harpoon gun",
        str_weaponmaster_self="You are a rank {rank} salty {title} of the harpoon gun.",
        str_weaponmaster="They are a rank {rank} salty {title} of the harpoon gun.",
        str_kill="**YARRR!!** {name_player} fires a harpoon right into {name_target}! {name_target} is dragged up on deck, vanquished. {emote_skull}",
        str_killdescriptor="harpooned",
        str_damage="{name_player} harpoons {name_target}’s {hitzone}!!",
        str_duel="**...** {name_player} and {name_target} dock their vessels next to one another, locked in a stern gaze. Suddenly, harpoons erupt from either vessel, smashing through timber and flesh alike.",
        str_description="It's a harpoon gun, seemingly ripped right from the deck of a whaling vessel. You're going to need both hands free to wield this thing properly, that means no sidearms, you shmuck!",
        str_reload="...aaaaand reloaded! The harpoon is ready to fire again!",
        str_reload_warning="**AVAST!** {name_player}’s harpoon is laying on the ground!!",
        str_scalp="The scalp is drenched in a salty brine.",
        fn_effect=wef_harpoon,
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_harpoon_kills,
        price=1000000000,
        # YOU EITHER KILL 'EM OR YOU DON'T, BROTHERRRR
        clip_size=1,
        str_brandish="{name} takes out {weapon} and racks their brain for a quote from Moby Dick. They can't think of a quote from Moby Dick."
    ),
    EwWeapon(  # 40
        id_weapon=ewcfg.weapon_id_model397,
        alias=[
            "anomalousrifle",
            "gatling",
            "megarifle"
        ],
        str_crit="**Critical hit!!** {name_target}'s skull gains another hole! Good show!!",
        str_miss="**You missed!!** {name_player} misses {name_target} by a barn door and a half. Phooey!",
        str_equip="You equip the model 397 hunting rifle.",
        str_name="model 397 hunting rifle",
        str_weapon="a model 397 hunting rifle",
        str_weaponmaster_self="You are a rank {rank} {title} of the model 1397 hunting rifle.",
        str_weaponmaster="They are a rank {rank} gentleman of the model 1397  hunting rifle.",
        str_kill="**360 NOSCOPED!!** {name_player} spins and fires! {name_target}'s head subsequently explodes! Get wr3ck3d, my good sir! {emote_skull}",
        str_killdescriptor="d3s7r0y3d",
        str_damage="{name_player} sneaks a few shots into {name_target}’s {hitzone}!!",
        str_duel="**...** {name_player} and {name_target} spin around like idiots, firing wildly and sipping tea.",
        str_description="It's a hunting rifle, modified to contain enough rounds to kill whole animal populations. Non-endangered ones, even!\n\nSoliss handed this to you in a back alley, you never learned quite why she fobbed it off on you. Maybe it's because no matter how much of the ammo you fire out of the clip it's heavy as two jet engines.\nhttps://imgur.com/a/O4MkWMl",
        str_reload="Oh. Fuck. You didn't think you'd even need to reload this. You detatch the two cylinders from the gun, making sure not to drop the massive weight on your toes. In goes the ammo! It's about 4x over capacity, but you somehow manage to get everything put back together in pretty good time.",
        str_reload_warning="**OH, BOTHER!** {name_player}’s hunting rifle just ran out bullets!!",
        str_scalp="A single, clean hole pierces the scalp. Ahhh, the thrill of the hunt...",
        fn_effect=get_normal_attack(weapon_type='burst_fire'),
        classes=[ewcfg.weapon_class_ammo],
        stat=ewcfg.stat_rifle_kills,
        clip_size=1000,
        str_brandish="{name} uses {weapon} to poach a nearby white elephant! How'd they find a white elephant?"
    ),
    EwWeapon(  # 41
        id_weapon=ewcfg.weapon_id_slimeoidwhistle,
        alias=[
            "slimeoidwhistle",
            "swhistle",
            "sw"
        ],
        str_crit="Your whistle makes a triumphant call!! {slimeoid_name} psyches itself up and unleashes {slimeoid_crit} upon {name_target} for a devastating and lethal blow!!",
        str_miss="Your whistle makes an awful screech! {slimeoid_name} is wandering around aimlessly before looking at you with confusion.",
        str_equip="You equip the whistle.",
        str_name="slimeoid whistle",
        str_weapon="a slimeoid whistle",
        str_weaponmaster_self="You are a rank {rank} trainer of the slimeoid whistle.",
        str_weaponmaster="They are a rank {rank} trainer of the the slimeoid whistle.",
        str_kill="{name_player}’s shrill screech overpowers {name_target}'s screams. {slimeoid_name} {slimeoid_kill} They enjoy a nice fleshy snack after the deed is done. {emote_skull}",
        str_killdescriptor="sicced on",
        str_damage="{name_target} is {slimeoid_dmg} by {slimeoid_name}!!",
        str_duel="[ ! ] {name_player} challenges {name_target} to a ‘slimeoid battle’. They summon their slimeoids and begin attacking each other.",
        str_description="It's a little whistle. It's loud as hell, and every second you blow it it adds a couple zeroes to the ol' geiger counter.",
        str_scalp="It’s drenched in slimeoid bile.",
        fn_effect=get_normal_attack(weapon_type='burst_fire'),
        classes=[],
        stat=ewcfg.stat_whistle_kills,
        acquisition=ewcfg.acquisition_smelting,
        str_brandish="{name} shakes {weapon}, but most people can't see it from this distance. It just looks like they're shaking their fist at them."
    ),
    EwWeapon(  # 42 AWP
        id_weapon=ewcfg.weapon_id_awp, #need to make
        alias=[
            "l96",
            "sniperrifle",
            "awp",
            "awm"
        ],
        str_crit="**Critical hit!!** {name_target}'s skull goes ***Kachunk!***",
        str_miss="**You missed!!** {name_player} misses {name_target}'s torso by a few inches.",
        str_equip="You equip the sniper rifle.",
        str_name="sniper rifle",
        str_weapon="a sniper rifle",
        str_weaponmaster_self="You are a rank {rank} {title} of the sniper rifle.",
        str_weaponmaster="They are a rank {rank} {title} of the sniper rifle.",
        str_kill="As soon as {name_player} rounds the corner, the damage is done. {name_target}'s lifeless body ragdolls to the floor. {emote_skull}",
        str_killdescriptor="fragged",
        str_damage="{name_player} lands a shot on {name_target}’s {hitzone}!",
        str_duel="**...** {name_player} and {name_target} begin time trials on pictures of long-dead terrorists",
        str_description="It's a sniper rifle, a well oiled machine.",
        str_reload="You carefully insert bullets into the chamber one by one until it can hold no more.",
        str_reload_warning="***Ping!*** {name_player}’s sniper rifle ran out of bullets!!",
        str_scalp="A large hole is found in what was once someones scalp",
        fn_effect=get_normal_attack(cost_multiplier=1.2, weapon_type='precision'),
        classes=[ewcfg.weapon_class_ammo, ewcfg.weapon_class_captcha],
        stat=ewcfg.stat_sniper_kills,
        clip_size=6,
        captcha_length=4,
        str_brandish="{name} realizes brandishing {weapon} is a daft idea. They're trying to take targets out from a distance, they're not supposed to know about that."
    ),
    EwWeapon(  # 43 DPick
        id_weapon=ewcfg.weapon_id_diamondpickaxe,
        alias=[
            "dpick",
            "diamondpickaxe",
            "diamondpick"
        ],
        str_crit="**Critical hit!!** X x X x X x X {name_player} jumps and lands a solid smack on {name_target}’s {hitzone}.",
        str_miss="**MISS!!** {name_player} swings their diamond pickaxe and does no damage!",
        str_equip="You equip the diamond pickaxe.",
        str_name="a Diamond Pickaxe",
        str_weapon="a diamond pickaxe",
        str_weaponmaster_self="You are a rank {rank} {title} of the diamond pickaxe.",
        str_weaponmaster="They are a rank {rank} {title} of the diamond pickaxe.",
        # str_trauma_self = "There is a deep, precise indent in the crown of your skull. How embarrassing!",
        # str_trauma = "There is a deep, precise indent in the crown of their skull. How embarrassing!",
        str_kill="**THWACK!!** {name_player} uses their block game skills to !mine {name_target} to death. How embarrassing! {emote_skull}",
        str_killdescriptor="!mined",
        str_damage="{name_target} is lightly tapped on the {hitzone}!!",
        str_duel="**THWACK, THWACK** {name_player} and {name_target} spend some quality time together, catching up on the latest minecraft manhunt episode.",
        str_scalp="It's speckled with bits of a sky blue mineral.",
        fn_effect=get_normal_attack(weapon_type='tool'),
        str_description="It's a diamond pickaxe.",
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_diamond_pickaxe_kills,
        is_tool=1,
        str_brandish="{name} starts ramming {weapon} into the ground, whistling Minecraft parodies as they work!"
    ),
    EwWeapon(  # 44
        id_weapon=ewcfg.weapon_id_monofilamentwhip,
        alias=[
            "monowhip",
            "monofilamentwhip",
            "whip"
        ],
        str_crit="**Critical hit!!** The tip of {name_player}'s whip swiftly cricles around {name_target}'s {hitzone} and removes it!",
        str_miss="**MISS!!** As {name_player}'s whip missed its target they scurry to avoid its whiplash.",
        str_equip="You equip the monowhip.",
        str_name="monofilament twhip",
        str_weapon="a monofilament whip",
        str_weaponmaster_self="You are a rank {rank} {title} of the monowhip.",
        str_weaponmaster="They are a rank {rank} {title} of the monowhip.",
        # str_trauma_self = "You are covered in scarred-over lacerations and puncture wounds.",
        # str_trauma = "They are covered in scarred-over lacerations and puncture wounds.",
        str_kill="A flash of neon hangs in the air!! {name_target}'s torso seperates from the rest of their body, as limbs fall to the floor. {name_player}'s monowhip retracts into its handle. {emote_skull}",
        str_killdescriptor="flayed",
        str_damage="{name_target} is flayed by the monowhip!!",
        str_duel="{name_player} and {name_target} avoid disaster and study Indiana Jones films.",
        str_description="It's a monofilament whip",
        str_scalp=" It feels as if it was cut off with a razorblade.",
        fn_effect=get_normal_attack(weapon_type='small_game'),
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_monowhip_kills,
        str_brandish="{name} cracks {weapon} in the air! The sparks almost burn off their eyebrow!"
    ),
    EwWeapon(  # 45
        id_weapon=ewcfg.weapon_id_fists,
        alias=[],
        str_crit="",
        str_miss="{name_target} dodges your strike.",
        str_equip="",
        str_name="fists",
        str_weapon="their fists",
        str_weaponmaster_self="",
        str_weaponmaster="",
        str_kill="{name_target} is hit!!\n\n{name_target} has died.",
        str_killdescriptor="pummeled",
        str_damage="{name_target} is hit!!",
        str_duel="",
        str_description="",
        str_scalp=" It looks like it was torn off by hand.",
        fn_effect=get_normal_attack(weapon_type='unarmed'),
        price=0,
        stat=ewcfg.stat_unarmed_kills,
        str_brandish=""
    ),
    EwWeapon(  # 46
        id_weapon=ewcfg.weapon_id_sledgehammer,
        alias=[
            "hammer",
            "sledge"
        ],
        str_crit="**Critical Hit!!** {name_player} makes {name_target} look like they just got put under a hydraulic press! Whooh-splaat!",
        str_miss="**MISS!!** {name_player} slams the sledgehammer next to {name_target} and nearly breaks their arms from misplaced confidence!",
        str_equip="You equip the unbalanced sledgehammer.",
        str_name="sledgehammer",
        str_weapon="a sledgehammer (*EUUUUUEGH???*)",
        str_weaponmaster_self="You are a rank {rank} {title} hammerkind.",
        str_weaponmaster="They are a rank {rank} {title} hammerkind.",
        str_kill="{name_player} brings their sledgehammer to {name_target}’s kneecaps, bending them backwards with a sickly crunch. As {name_target} yelps in pain, they get their skull caved in by an overhead swing. {emote_skull}",
        str_killdescriptor="slammed",
        str_damage="{name_player} swings their sledgehammer into {name_target}’s {hitzone}!",
        str_duel="**Whooosh-crik!** {name_player} spends all of their energy holding their own against {name_target}. One might say that these sledgehammer schizophrenics have become pseudo-fathers in make-believe construction work. Two fathers, eh?",
        str_description="It’s a sledgehammer, the home improver’s tool of choice. At least of the non-power tool variety, that is.",
        str_scalp=" It looks especially flat.",
        fn_effect=get_normal_attack(weapon_type='heavy'),
        price=1000000,
        vendors=[ewcfg.vendor_basedhardware],
        stat=ewcfg.stat_sledgehammer_kills,
        str_brandish="{name} finds the closest thing to destroy and hurls {weapon} into it!"
    ),
    EwWeapon(  # 47
        id_weapon=ewcfg.weapon_id_skateboard,
        alias=[
            "sk8r",
            "sk8b04rd",
            "board",
        ],
        str_crit="**Critical hit!!** {name_player} does a 360 Varial McTwist, careening into {name_target} with style!",
        str_miss="**MISS!!** {name_player} bails out, falling and eating shit on the pavement. So uncool!",
        str_equip="You get some speed before jumping onto your skateboard.",
        str_name="skateboard",
        str_weapon="a skateboard",
        str_weaponmaster_self="You are a rank {rank} {title} pro skater.",
        str_weaponmaster="They are a rank {rank} {title} pro skater.",
        str_kill="{name_player} hops off their skateboard and smacks {name_target} right in the face with it, breaking off a few teeth. As {name_target} hits the floor, {name_player} takes the opportunity to film themselves kickflipping over their body.",
        str_killdescriptor="tricked on",
        str_damage="{name_target} is smacked with a board across their {hitzone}!!",
        str_duel="{name_player} and {name_target} wheel out an old CRT, grinding out optimal trick lines on Tony Clark’s Underground for the PlaySlimestion 2.",
        str_description="It’s your trusty skateboard.",
        str_scalp=" It looks low poly.",
        fn_effect=get_normal_attack(weapon_type='variable_damage'),
        acquisition=ewcfg.acquisition_smelting,
        stat=ewcfg.stat_skateboard_kills,
        str_brandish="Try !stunt."
    ),
]





# A map of id_weapon to EwWeapon objects.
weapon_map = {}

# A list of weapon names
weapon_names = []

# Populate weapon map, including all aliases.
for weapon in weapon_list:
    weapon_map[weapon.id_weapon] = weapon
    weapon_names.append(weapon.id_weapon)

    for alias in weapon.alias:
        weapon_map[alias] = weapon

weapon_type_convert = {
    ewcfg.weapon_id_watercolors: wef_watercolors,
    ewcfg.weapon_id_spraycan: get_normal_attack(),
    ewcfg.weapon_id_paintroller: wef_paintroller,
    ewcfg.weapon_id_thinnerbomb: get_normal_attack(weapon_type='incendiary'),
    ewcfg.weapon_id_paintgun: wef_paintgun,
    ewcfg.weapon_id_paintbrush: get_normal_attack(weapon_type='small_game'),
    ewcfg.weapon_id_roomba: get_normal_attack()
}

slimeoid_weapon_type_convert = {
    -1: get_normal_attack(weapon_type='unarmed'),
    0:  get_normal_attack(weapon_type='tool'),
    1:  get_normal_attack(weapon_type='tool'),
    2:  get_normal_attack(weapon_type='small_game'),
    3:  get_normal_attack(weapon_type='small_game'),
    4:  get_normal_attack(),
    5:  get_normal_attack(),
    6:  get_normal_attack(weapon_type='variable_damage'),
    7:  get_normal_attack(weapon_type='variable_damage'),
    8:  get_normal_attack(weapon_type='heavy'),
    9:  get_normal_attack(weapon_type='heavy'),
    10: get_normal_attack(weapon_type='burst_fire'),
    11: get_normal_attack(weapon_type='burst_fire'),
    12: get_normal_attack(weapon_type='burst_fire'),
    13: get_normal_attack(weapon_type='burst_fire'),

}

slimeoid_dmg_text = {
    "blades":"slashed cleanly across the chest",
    "teeth":"impaled by numerous sharp teeth",
    "grip":"being deprived of oxygen",
    "bludgeon":"struck hard in the skull",
    "spikes":"skewered by a volley of jagged spikes",
    "electricity":"tazed by a continuous arc of electricity",
    "slam":"crushed under a massive weight"
}

slimeoid_kill_text = {
    "blades":"unleashes a flurry of strikes too fast for the eye to see. After a few heartbeats, slices slowly slide apart like fresh cut salami.",
    "teeth":"clenches their prey in its powerful jaws. Ripping and tearing the head from its body until there’s nothing left but a stump.",
    "grip":"has a tight stranglehold on their prey, squeezing until their brain bursts out of their skull like a cyst filled with grey matter.",
    "bludgeon":"swiftly bashes their prey with force of a semi truck. Their bones are flung out of their body before vaporizing against a nearby building.",
    "spikes":"slings a hail of gnarled spikes, pinning their victim against the wall like a carnival act. It eagerly picks off meat chunks of its prey to feast on like skewered BBQ.",
    "electricity":"filled with unlimited power, charges up for a massive powerful arc, unleashing a blinding lightning strike. The taste of metal fills the static-charged atmosphere before its prey is struck with 80 jigawats of power.",
    "slam":"jumps high into the air. With the force of an atomic warhead they crash down through the stratosphere and obliterate their prey below, painting the district green. "
}


slimeoid_crit_text = {
"spit":"a rain of high velocity corrosive acid",
"laser":"a searing white hot photon beam",
"spines":"a hail of massive jagged spikes",
"throw":"its unmatched strength and throws a car",
"TK":"a brain blast of psychic waves",
"fire":"a torrent of unrelenting dragon-like flames",
"webs":"a high pressure string shot of sticky webs"
}
