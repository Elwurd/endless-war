import asyncio
import random
import time

from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.item import EwItem
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
from ew.static import hue as hue_static
from ew.static import slimeoid as sl_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils.slimeoid import EwSlimeoid
from ew.utils.combat import EwUser
from ew.utils.combat import EwEnemy


# manages a slimeoid's combat stats during a slimeoid battle
class EwSlimeoidCombatData:
    # slimeoid name
    name = ""

    # slimeoid weapon object
    weapon = None

    # slimeoid armor object
    armor = None

    # slimeoid special attack object
    special = None

    # slimeoid legs object
    legs = None

    # slimeoid brain object
    brain = None

    # slimeoid hue object
    hue = None

    # slimeoid coating object
    coating = None

    # slimeoid physical attack stat
    moxie = 0

    # slimeoid physical defense stat
    grit = 0

    # slimeoid special attack stat
    chutzpah = 0

    # slimeoid maximum hp
    hpmax = 0

    # slimeoid current hp
    hp = 0

    # slimeoid maximum sap
    sapmax = 0

    # slimeoid current sap
    sap = 0

    # slimeoid current hardened sap
    hardened_sap = 0

    # slimeoid shock (reduces effective sap)
    shock = 0

    # slimeoid database object (EwSlimeoid)
    slimeoid = None

    # slimeoid owner database object (EwPlayer)
    owner = None

    # slimeoid armor weakness string
    resistance = ""

    # slimeoid armor resistance string
    weakness = ""

    # slimeoid hue physical resistance string
    analogous = ""

    # slimeoid hue physical weakness string
    splitcomplementary_physical = ""

    # slimeoid hue special weakness string
    splitcomplementary_special = ""

    def __init__(self,
                 name = "",
                 weapon = None,
                 armor = None,
                 special = None,
                 legs = None,
                 brain = None,
                 hue = None,
                 coating = None,
                 moxie = 0,
                 grit = 0,
                 chutzpah = 0,
                 hpmax = 0,
                 hp = 0,
                 sapmax = 0,
                 sap = 0,
                 slimeoid = None,
                 owner = None
                 ):
        self.name = name
        self.weapon = weapon
        self.armor = armor
        self.special = special
        self.legs = legs
        self.brain = brain
        self.hue = hue
        self.coating = coating
        self.moxie = moxie
        self.grit = grit
        self.chutzpah = chutzpah
        self.hpmax = hpmax
        self.hp = hp
        self.sapmax = sapmax
        self.sap = sap
        self.hardened_sap = 0
        self.shock = 0
        self.slimeoid = slimeoid
        self.owner = owner

    # initializes the physical resistance and special weakness strings and applies corresponding stat changes
    def apply_weapon_matchup(self, enemy_combat_data = None):
        challengee_slimeoid = self.slimeoid
        challenger_slimeoid = enemy_combat_data.slimeoid

        resistance = self.armor.get_resistance(enemy_combat_data.weapon)
        weakness = self.armor.get_weakness(enemy_combat_data.special)

        if len(resistance) > 0:
            enemy_combat_data.moxie -= 2
            enemy_combat_data.moxie = max(1, enemy_combat_data.moxie)

        if len(weakness) > 0:
            enemy_combat_data.chutzpah += 2

        self.resistance = resistance.format(self.name)
        self.weakness = weakness.format(self.name)

    # initializes the hue resistance and weakness strings and applies corresponding stat changes

    def apply_hue_matchup(self, enemy_combat_data = None):
        color_matchup = ewcfg.hue_neutral
        # get color matchups

        # If hue is None and the enemy is Negative, give the opponent a complete buff.
        if self.hue is None:
            if enemy_combat_data.slimeoid.hue == "negative":
                enemy_combat_data.grit += 2
                enemy_combat_data.moxie += 2
                enemy_combat_data.chutzpah += 2
                enemy_combat_data.analogous = "It's not very effective against {}...".format(enemy_combat_data.name)
                self.splitcomplementary_physical = "It's Super Effective against {}!".format(self.name)
                self.splitcomplementary_special = "It's Super Effective against {}!".format(self.name) 

        # If there is a hue
        if self.hue is not None:
            # If the enemy slimeoid's hue is in the hue's effectiveness. analogous returns "-1", atk_complementary returns 1, special_complementary returns 2, full_complementary returns 3
            color_matchup = self.hue.effectiveness.get(enemy_combat_data.slimeoid.hue)

        # If there's no relation between the two hues
        if color_matchup is None:
            color_matchup = ewcfg.hue_neutral

        # If the opponent's hue is in your hue's effectiveness as "analogous"
        if color_matchup < 0:
            enemy_combat_data.grit += 2
            enemy_combat_data.analogous = "It's not very effective against {}...".format(enemy_combat_data.name)

        # If the opponent's hue is in your hue's effectiveness as "complementary"
        elif color_matchup > 0:
            # If the opponent's hue is listed as "hue_atk_complementary" in your hue's effectiveness
            if color_matchup == ewcfg.hue_atk_complementary:
                self.moxie += 2
                enemy_combat_data.splitcomplementary_physical = "It's Super Effective against {}!".format(enemy_combat_data.name)
            # If the opponent's hue is listed as "hue_special_complementary" in your hue's effectiveness
            elif color_matchup == ewcfg.hue_special_complementary:
                self.chutzpah += 2
                enemy_combat_data.splitcomplementary_special = "It's Super Effective against {}!".format(enemy_combat_data.name)
            # If the opponent's hue is listed as "hue_full_complementary" in your hue's effectiveness
            elif color_matchup == ewcfg.hue_full_complementary:
                self.moxie += 2
                self.chutzpah += 2
                enemy_combat_data.splitcomplementary_physical = "It's Super Effective against {}!".format(enemy_combat_data.name)
                enemy_combat_data.splitcomplementary_special = "It's Super Effective against {}!".format(enemy_combat_data.name)

        # print(self.coating)
        if self.coating == ewcfg.hue_id_copper:
            self.moxie += 2
        elif self.coating == ewcfg.hue_id_chrome:
            self.grit += 2
        elif self.coating == ewcfg.hue_id_gold:
            self.chutzpah += 2

    # Nerfs slimeoids 11-foot and up to have 10-foot stats, as well as autobalancing slimeoids with negative stats 
    def apply_size_nerf(self, enemy_combat_data = None, size_limit = False):
        size = self.moxie + self.grit + self.chutzpah

        # If the slimeoid is bigger than size_limit feet. Comes before other matchups, so stats together should equal size. Stats are 1 at minimum in CombatData
        if(not size_limit):
            size_limit = 13
        else:
            size_limit += 3
        print(size_limit)
        if size > size_limit:
            oversize = size - size_limit

            # Take 1/3 of oversize and subtract it from grit. Tries to shave off 1/3 of oversize from each stat.
            to_subtract = oversize // 3
            oversize -= to_subtract

            while self.grit > 1 and to_subtract > 0:
                self.grit -= 1
                to_subtract -= 1
            # if grit hits 1 (0 grit), add the leftover to_subtract back to oversize
            oversize += to_subtract

            # Take half of oversize and subtract it from moxie
            to_subtract = oversize // 2
            oversize -= to_subtract
            
            while self.moxie > 1 and to_subtract > 0:
                self.moxie -= 1
                to_subtract -= 1
            # if moxie hits 1 (0 moxie), add the leftover to_subtract back to oversize
            to_subtract += oversize

            # subtract the remaining oversize from chutzpah
            while self.chutzpah > 1 and to_subtract > 0:
                self.chutzpah -= 1
                to_subtract -= 1

            # If there are any points remaining, try subtracting from grit or moxie again
            if to_subtract > 0:
                if self.grit > 1:
                    while self.grit > 1 and to_subtract > 0:
                        self.grit -= 1
                        to_subtract -= 1
                if self.moxie > 1 and to_subtract > 0:
                    while self.moxie > 1 and to_subtract > 0:
                        self.moxie -= 1
                        to_subtract -= 1
                # If all else fails, autobalance to 4/3/3
                if to_subtract > 0:
                    self.grit = 5
                    self.moxie = 4
                    self.chutpah = 4
        
        # If the slimeoid has any negative stats, autobalance to 4/3/3
        elif self.grit < 1 or self.moxie < 1 or self.chutzpah < 1:
            self.grit = 5
            self.moxie = 4
            self.chutzpah = 4

    # roll the dice on whether an action succeeds and by how many degrees of success
    def attempt_action(self, strat, sap_spend, in_range):
        # reduce sap available by shock
        self.sap -= self.shock
        self.sap = max(0, self.sap)
        self.shock = 0
        sap_spend = min(sap_spend, self.sap)

        # obtain target number based on the type of action attempted
        target_number = 0
        if strat == ewcfg.slimeoid_strat_attack:
            if in_range:
                target_number = self.moxie
            else:
                target_number = self.chutzpah

        elif strat == ewcfg.slimeoid_strat_evade:
            target_number = 6
        elif strat == ewcfg.slimeoid_strat_block:
            target_number = self.grit

        dos = 0
        dice = []
        # roll the dice
        for i in range(sap_spend):
            die_roll = random.randrange(10)
            dice.append(die_roll)
            # a result lower than the target number confers a degree of success. a result of 0 always succeeds and a result of 9 always fails.
            if (die_roll < target_number and die_roll != 9) or die_roll == 0:
                dos += 1

        # ewutils.logMsg("Rolling {} check with {} sap, target number {}: {}, {} successes".format(strat, sap_spend, target_number, dice, dos))
        # spend sap
        self.sap -= sap_spend

        # return degrees of success
        return dos

    # obtain response for attack
    def execute_attack(self, enemy_combat_data, damage, in_range):
        hp = enemy_combat_data.hp
        hp -= damage

        thrownobject = random.choice(ewcfg.thrownobjects_list)

        response = "**"
        if in_range:
            if hp <= 0:
                response += self.weapon.str_attack_coup.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
            elif (self.hpmax / self.hp) > 3:
                response += self.weapon.str_attack_weak.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
            else:
                response += self.weapon.str_attack.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
        else:
            if hp <= 0:
                response += self.special.str_special_attack_coup.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                    object=thrownobject
                )
            elif (self.hpmax / self.hp) > 3:
                response += self.special.str_special_attack_weak.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                    object=thrownobject
                )
            else:
                response += self.special.str_special_attack.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                    object=thrownobject
                )
        response += "**"
        response += " :boom:"

        return response

    # apply damage and obtain response
    def take_damage(self, enemy_combat_data, damage, active_dos, in_range):

        # apply damage
        self.hp -= damage
        hp = self.hp

        # crush sap on physical attacks only
        sap_crush = 0
        if in_range:
            sap_crush = min(self.hardened_sap, active_dos)
            self.hardened_sap -= sap_crush

        # store shock taken for next turn
        self.shock += 2 * active_dos

        # get proper response
        response = ""
        if self.hp > 0:
            if in_range:
                if self.resistance != "":
                    response = self.resistance

                if self.analogous != "":
                    response += " {}".format(self.analogous)

                if self.splitcomplementary_physical != "":
                    response += " {}".format(self.splitcomplementary_physical)

            else:
                if self.weakness != "":
                    response = self.weakness

                if self.splitcomplementary_special != "":
                    response += " {}".format(self.splitcomplementary_special)

            if hp / damage > 10:
                response += " {} barely notices the damage.".format(self.name)
            elif hp / damage > 6:
                response += " {} is hurt, but shrugs it off.".format(self.name)
            elif hp / damage > 4:
                response += " {} felt that one!".format(self.name)
            elif hp / damage >= 3:
                response += " {} really felt that one!".format(self.name)
            elif hp / damage < 3:
                response += " {} reels from the force of the attack!!".format(self.name)

            if sap_crush > 0:
                response += " (-{} hardened sap)".format(sap_crush)

        return response

    # obtain movement response
    def change_distance(self, enemy_combat_data, in_range):
        response = ""
        if in_range:
            if (self.hpmax / self.hp) > 3:
                response = self.legs.str_retreat_weak.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
            else:
                response = self.legs.str_retreat.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
        else:
            if (self.hpmax / self.hp) > 3:
                response = self.legs.str_advance_weak.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
            else:
                response = self.legs.str_advance.format(
                    active=self.name,
                    inactive=enemy_combat_data.name,
                )
        return response

    # harden sap and obtain response
    def harden_sap(self, dos):
        response = ""

        sap_hardened = min(dos, self.grit - self.hardened_sap)
        self.hardened_sap += sap_hardened

        if sap_hardened <= 0:
            response = "{} fails to harden any sap!".format(self.name)
        else:
            response = "{} hardens {} sap!".format(self.name, sap_hardened)

        return response


# Slimeoids lose more clout for losing at higher levels.
def calculate_clout_loss(clout):
    if clout >= 100:
        clout -= 6
    elif clout >= 40:
        clout -= 5
    elif clout >= 30:
        clout -= 4
    elif clout >= 20:
        clout -= 3
    elif clout >= 10:
        clout -= 2
    elif clout >= 1:
        clout -= 1

    return clout


def calculate_clout_gain(clout):
    clout += 2

    if clout > 100:
        clout = 100

    return clout


# Run the battle for a pair of slimeoids
async def battle_slimeoids(id_s1, id_s2, challengee_name, challenger_name, channel, battle_type, pvp_battle, size_limit):
    # fetch slimeoid data
    challengee_slimeoid = EwSlimeoid(id_slimeoid=id_s1)
    challenger_slimeoid = EwSlimeoid(id_slimeoid=id_s2)

    client = ewutils.get_client()

    # Nerf level to 10 if it's above 11.
    print(size_limit)
    if(size_limit):
        challengee_level = min(challengee_slimeoid.level, size_limit)
        challenger_level = min(challenger_slimeoid.level, size_limit)
    else:
        challengee_level = challengee_slimeoid.level
        challenger_level = challenger_slimeoid.level

    # calculate starting hp
    s1hpmax = 50 + (challengee_level * 20)
    s2hpmax = 50 + (challenger_level * 20)

    # calculate starting sap
    s1sapmax = challengee_level * 2
    s2sapmax = challenger_level * 2

    # initialize combat data for challengee
    s1_combat_data = EwSlimeoidCombatData(
        name=str(challengee_slimeoid.name),
        weapon=sl_static.offense_map.get(challengee_slimeoid.weapon),
        armor=sl_static.defense_map.get(challengee_slimeoid.armor),
        special=sl_static.special_map.get(challengee_slimeoid.special),
        legs=sl_static.mobility_map.get(challengee_slimeoid.legs),
        brain=sl_static.brain_map.get(challengee_slimeoid.ai),
        hue=hue_static.hue_map.get(challengee_slimeoid.hue),
        coating=challengee_slimeoid.coating,
        moxie=challengee_slimeoid.atk + 1,
        grit=challengee_slimeoid.defense + 1,
        chutzpah=challengee_slimeoid.intel + 1,
        hpmax=s1hpmax,
        hp=s1hpmax,
        sapmax=s1sapmax,
        sap=s1sapmax,
        slimeoid=challengee_slimeoid,
        owner=challengee_name,
    )

    # initialize combat data for challenger
    s2_combat_data = EwSlimeoidCombatData(
        name=str(challenger_slimeoid.name),
        weapon=sl_static.offense_map.get(challenger_slimeoid.weapon),
        armor=sl_static.defense_map.get(challenger_slimeoid.armor),
        special=sl_static.special_map.get(challenger_slimeoid.special),
        legs=sl_static.mobility_map.get(challenger_slimeoid.legs),
        brain=sl_static.brain_map.get(challenger_slimeoid.ai),
        hue=hue_static.hue_map.get(challenger_slimeoid.hue),
        coating=challenger_slimeoid.coating,
        moxie=challenger_slimeoid.atk + 1,
        grit=challenger_slimeoid.defense + 1,
        chutzpah=challenger_slimeoid.intel + 1,
        hpmax=s2hpmax,
        hp=s2hpmax,
        sapmax=s2sapmax,
        sap=s2sapmax,
        slimeoid=challenger_slimeoid,
        owner=challenger_name,
    )

    s1_combat_data.apply_size_nerf(s2_combat_data, size_limit)
    s2_combat_data.apply_size_nerf(s1_combat_data, size_limit)

    s1_combat_data.apply_weapon_matchup(s2_combat_data)
    s2_combat_data.apply_weapon_matchup(s1_combat_data)

    s1_combat_data.apply_hue_matchup(s2_combat_data)
    s2_combat_data.apply_hue_matchup(s1_combat_data)

    # decide which slimeoid gets to move first
    s1_active = False
    in_range = False

    if challengee_slimeoid.defense > challenger_slimeoid.defense:
        s1_active = True
    elif challengee_slimeoid.defense == challenger_slimeoid.defense:
        coinflip = random.randrange(1, 3)
        if coinflip == 1:
            s1_active = True

    # flavor text for arena battles
    if battle_type == ewcfg.battle_type_arena:
        response = "**{} sends {} out into the Battle Arena!**".format(challenger_name, s2_combat_data.name)
        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(1)
        response = "**{} sends {} out into the Battle Arena!**".format(challengee_name, s1_combat_data.name)
        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(1)
        response = "\nThe crowd erupts into cheers! The battle between {} and {} has begun! :crossed_swords:".format(s1_combat_data.name, s2_combat_data.name)
        #		response += "\n{} {} {} {} {} {}".format(str(s1moxie),str(s1grit),str(s1chutzpah),str(challengee_slimeoid.weapon),str(challengee_slimeoid.armor),str(challengee_slimeoid.special))
        #		response += "\n{} {} {} {} {} {}".format(str(s2moxie),str(s2grit),str(s2chutzpah),str(challenger_slimeoid.weapon),str(challenger_slimeoid.armor),str(challenger_slimeoid.special))
        #		response += "\n{}, {}".format(str(challengee_resistance),str(challengee_weakness))
        #		response += "\n{}, {}".format(str(challenger_resistance),str(challenger_weakness))
        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(3)

    turncounter = 100
    # combat loop
    while s1_combat_data.hp > 0 and s2_combat_data.hp > 0 and turncounter > 0:
        # Limit the number of turns in battle.
        turncounter -= 1

        response = ""
        battlecry = random.randrange(1, 3)

        first_turn = (turncounter % 2) == 1

        # slimeoids regenerate their sap every odd turn
        if first_turn:
            s1_combat_data.sap = s1_combat_data.sapmax - s1_combat_data.hardened_sap
            s2_combat_data.sap = s2_combat_data.sapmax - s2_combat_data.hardened_sap

        # assign active and passive role for the turn
        if s1_active:
            active_data = s1_combat_data
            passive_data = s2_combat_data
        else:
            active_data = s2_combat_data
            passive_data = s1_combat_data

        # obtain action and how much sap to spend on it for both slimeoids
        active_strat, active_sap_spend = active_data.brain.get_strat(combat_data=active_data, active=True, in_range=in_range, first_turn=first_turn)
        passive_strat, passive_sap_spend = passive_data.brain.get_strat(combat_data=passive_data, active=False, in_range=in_range, first_turn=first_turn)

        # potentially add brain-based flavor text
        if active_strat == ewcfg.slimeoid_strat_attack and battlecry == 1:
            if (active_data.hpmax / active_data.hp) > 3:
                response = active_data.brain.str_battlecry_weak.format(
                    slimeoid_name=active_data.name
                )
            else:
                response = active_data.brain.str_battlecry.format(
                    slimeoid_name=active_data.name
                )
            await fe_utils.send_message(client, channel, response)
            await asyncio.sleep(1)

        elif active_strat == ewcfg.slimeoid_strat_evade and battlecry == 1:
            if (active_data.hpmax / active_data.hp) > 3:
                response = active_data.brain.str_movecry_weak.format(
                    slimeoid_name=active_data.name
                )
            else:
                response = active_data.brain.str_movecry.format(
                    slimeoid_name=active_data.name
                )
            await fe_utils.send_message(client, channel, response)
            await asyncio.sleep(1)

        # announce active slimeoid's chosen action
        response = ""
        if active_strat == ewcfg.slimeoid_strat_attack:
            if in_range:
                response = "{} attempts to strike {} in close combat!".format(active_data.name, passive_data.name)
            else:
                response = "{} attempts to strike {} from a distance!".format(active_data.name, passive_data.name)

        elif active_strat == ewcfg.slimeoid_strat_evade:
            if in_range:
                response = "{} attempts to avoid being hit, while gaining distance from {}.".format(active_data.name, passive_data.name)
            else:
                response = "{} attempts to avoid being hit, while closing the distance to {}.".format(active_data.name, passive_data.name)

        elif active_strat == ewcfg.slimeoid_strat_block:
            response = "{} focuses on blocking incoming attacks.".format(active_data.name)

        response += " (**{} sap**)".format(active_sap_spend)

        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(1)

        # announce passive slimeoid's chosen action
        response = ""
        if passive_strat == ewcfg.slimeoid_strat_attack:
            if in_range:
                response = "{} attempts to strike {} in close combat!".format(passive_data.name, active_data.name)
            else:
                response = "{} attempts to strike {} from a distance!".format(passive_data.name, active_data.name)

        elif passive_strat == ewcfg.slimeoid_strat_evade:
            if in_range:
                response = "{} attempts to avoid being hit, while gaining distance from {}.".format(passive_data.name, active_data.name)
            else:
                response = "{} attempts to avoid being hit, while closing the distance to {}.".format(passive_data.name, active_data.name)

        elif passive_strat == ewcfg.slimeoid_strat_block:
            response = "{} focuses on blocking incoming attacks.".format(passive_data.name)

        response += " (**{} sap**)".format(passive_sap_spend)

        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(1)

        # if the chosen actions are in direct competition, the roll is opposed. only one of them can succeed
        # otherwise both actions are resolved separately
        roll_opposed = False

        if active_strat == ewcfg.slimeoid_strat_attack:
            roll_opposed = passive_strat in [ewcfg.slimeoid_strat_evade, ewcfg.slimeoid_strat_block]
        elif active_strat == ewcfg.slimeoid_strat_evade:
            roll_opposed = passive_strat in [ewcfg.slimeoid_strat_attack, ewcfg.slimeoid_strat_evade]
        elif active_strat == ewcfg.slimeoid_strat_block:
            roll_opposed = passive_strat in [ewcfg.slimeoid_strat_attack]

        active_dos = active_data.attempt_action(strat=active_strat, sap_spend=active_sap_spend, in_range=in_range)

        # simultaneous attacks are a special case. the passive slimeoid only rolls the dice, after the active slimeoid's attack has been resolved
        if passive_strat != ewcfg.slimeoid_strat_attack:
            passive_dos = passive_data.attempt_action(strat=passive_strat, sap_spend=passive_sap_spend, in_range=in_range)
            if roll_opposed:
                active_dos -= passive_dos
                passive_dos = -active_dos

                # on an opposed roll, priority for the next turn (the active role) is passed to the winner of the roll
                if active_dos < 0:
                    s1_active = not s1_active
        else:
            passive_dos = 0

        # resolve active slimeoid's attack
        if active_strat == ewcfg.slimeoid_strat_attack:
            # the attack was successful
            if active_dos > 0:
                # calculate damage
                if in_range:
                    damage = int(active_dos * 30 / (passive_data.hardened_sap + 1))
                else:
                    damage = int(active_dos * 20)

                response = active_data.execute_attack(passive_data, damage, in_range)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

                response = passive_data.take_damage(active_data, damage, active_dos, in_range)
                if len(response) > 0:
                    await fe_utils.send_message(client, channel, response)
                    await asyncio.sleep(1)

            elif not roll_opposed:
                response = "{} whiffs its attack!".format(active_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)
            elif passive_strat == ewcfg.slimeoid_strat_evade:
                response = "{} dodges {}'s attack!".format(passive_data.name, active_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)
            elif passive_strat == ewcfg.slimeoid_strat_block:
                response = "{} blocks {}'s attack!".format(passive_data.name, active_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # if the active slimeoid's attack killed the passive slimeoid
        if passive_data.hp <= 0:
            break

        if passive_strat == ewcfg.slimeoid_strat_attack:
            passive_dos = passive_data.attempt_action(strat=passive_strat, sap_spend=passive_sap_spend, in_range=in_range)

            if roll_opposed:
                active_dos -= passive_dos
                passive_dos = -active_dos

                if active_dos < 0:
                    s1_active = not s1_active

        # resolve passive slimeoid's attack
        if passive_strat == ewcfg.slimeoid_strat_attack:
            # attack was successful
            if passive_dos > 0:
                # calculate damage
                if in_range:
                    damage = int(passive_dos * 30 / (active_data.hardened_sap + 1))
                else:
                    damage = int(passive_dos * 20)

                response = passive_data.execute_attack(active_data, damage, in_range)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

                response = active_data.take_damage(passive_data, damage, passive_dos, in_range)
                if len(response) > 0:
                    await fe_utils.send_message(client, channel, response)
                    await asyncio.sleep(1)

            elif not roll_opposed:
                response = "{} whiffs its attack!".format(passive_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)
            elif active_strat == ewcfg.slimeoid_strat_evade:
                response = "{} dodges {}'s attack!".format(active_data.name, passive_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)
            elif active_strat == ewcfg.slimeoid_strat_block:
                response = "{} blocks {}'s attack!".format(active_data.name, passive_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # resolve active slimeoid's movement
        if active_strat == ewcfg.slimeoid_strat_evade:
            if active_dos > 0:
                response = active_data.change_distance(passive_data, in_range)
                in_range = not in_range
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)
            elif active_dos == 0 and passive_strat == ewcfg.slimeoid_strat_evade:
                in_range = not in_range
                response = "{} and {} circle each other, looking for an opening...".format(active_data.name, passive_data.name)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # resolve active slimeoid's defense
        if active_strat == ewcfg.slimeoid_strat_block:
            if active_dos > 0:
                response = active_data.harden_sap(active_dos)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # resolve passive slimeoid's movement
        if passive_strat == ewcfg.slimeoid_strat_evade:
            if passive_dos > 0:
                response = passive_data.change_distance(active_data, in_range)
                in_range = not in_range
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # resolve passive slimeoid's defense
        if passive_strat == ewcfg.slimeoid_strat_block:
            if passive_dos > 0:
                response = passive_data.harden_sap(passive_dos)
                await fe_utils.send_message(client, channel, response)
                await asyncio.sleep(1)

        # re-fetch slimeoid data
        challenger_slimeoid = EwSlimeoid(id_slimeoid=id_s2)
        challengee_slimeoid = EwSlimeoid(id_slimeoid=id_s1)

        s1_combat_data.slimeoid = challengee_slimeoid
        s2_combat_data.slimeoid = challenger_slimeoid

        # Check if slimeoids have died during the fight
        if challenger_slimeoid.life_state == ewcfg.slimeoid_state_dead:
            s2_combat_data.hp = 0
        elif challengee_slimeoid.life_state == ewcfg.slimeoid_state_dead:
            s1_combat_data.hp = 0

        await asyncio.sleep(2)

    # the challengee has lost
    if s1_combat_data.hp <= 0:
        result = 1
        response = "\n" + s1_combat_data.legs.str_defeat.format(
            slimeoid_name=s1_combat_data.name
        )
        response += " {}".format(ewcfg.emote_slimeskull)
        response += "\n" + s2_combat_data.brain.str_victory.format(
            slimeoid_name=s2_combat_data.name
        )

        challenger_slimeoid = EwSlimeoid(id_slimeoid=id_s2)
        challengee_slimeoid = EwSlimeoid(id_slimeoid=id_s1)

        # Losing slimeoid loses clout and has a time_defeated cooldown.
        if channel.name == ewcfg.channel_arena:
            challengee_slimeoid.clout = calculate_clout_loss(challengee_slimeoid.clout)
            challengee_slimeoid.time_defeated = int(time.time())
            challengee_slimeoid.persist()

        if channel.name == ewcfg.channel_arena:
            challenger_slimeoid.clout = calculate_clout_gain(challenger_slimeoid.clout)
            challenger_slimeoid.persist()

        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(2)
    # the challenger has lost
    else:
        result = -1
        response = "\n" + s2_combat_data.legs.str_defeat.format(
            slimeoid_name=s2_combat_data.name
        )
        response += " {}".format(ewcfg.emote_slimeskull)
        response += "\n" + s1_combat_data.brain.str_victory.format(
            slimeoid_name=s1_combat_data.name
        )

        challenger_slimeoid = EwSlimeoid(id_slimeoid=id_s2)
        challengee_slimeoid = EwSlimeoid(id_slimeoid=id_s1)

        # store defeated slimeoid's defeat time in the database
        if channel.name == ewcfg.channel_arena:
            challenger_slimeoid.clout = calculate_clout_loss(challenger_slimeoid.clout)
            challenger_slimeoid.time_defeated = int(time.time())
            challenger_slimeoid.persist()

        if channel.name == ewcfg.channel_arena:
            challengee_slimeoid.clout = calculate_clout_gain(challengee_slimeoid.clout)
            challengee_slimeoid.persist()

        await fe_utils.send_message(client, channel, response)
        await asyncio.sleep(2)
    return result


def get_slimeoid_count(user_id = None, server_id = None):
    if user_id != None and server_id != None:
        count = 0
        slimeoid_data = EwSlimeoid(id_user=user_id, id_server=server_id)
        secondary_user = str(user_id) + "freeze"
        name_list = []
        if slimeoid_data.name != "":
            count += 1

        items = bknd_item.inventory(id_user=user_id, id_server=server_id, item_type_filter=ewcfg.it_item)

        bottles = []
        for item in items:
            item_data = EwItem(id_item=item.get('id_item'))
            if item_data.item_props.get('context') == ewcfg.context_slimeoidbottle:
                count += 1

        try:
            conn_info = bknd_core.databaseConnect()
            conn = conn_info.get('conn')
            cursor = conn.cursor()

            sql = "SELECT {} FROM slimeoids WHERE {} = %s"
            cursor.execute(sql.format(ewcfg.col_name, ewcfg.col_id_user), [secondary_user])

            count += cursor.rowcount
        finally:
            # Clean up the database handles.
            cursor.close()
            bknd_core.databaseClose(conn_info)
            return count

""" Check whether a slimeoid battle is possible. 
challenger: An EwUser
challengee: An EwUser or EwEnemy
challenger_slimeoid: An EwSlimeoid object in case you already have it initialised
challengee_slimeoid: An EwSlimeoid object in case you already have it initialised
bet: The slime bet on the battle. Only PvP matches have bets.
"""

def can_slimeoid_battle(challenger: EwUser = None, challengee = None, challenger_slimeoid: EwSlimeoid = None, challengee_slimeoid: EwSlimeoid = None, bet: int = 0):
    response = ""
    time_now = int(time.time())
    # Gotta have a challenger, otherwise do nothing
    if challenger:
        challenger_data = challenger
        challenger_player = EwPlayer(id_user=challenger_data.id_user)
        ally_slimeoid = None
        target_slimeoid = None

        # If supplied a slimeoid, use that - otherwise we just grab it
        if challenger_slimeoid:
            ally_slimeoid = challenger_slimeoid
        else:
            ally_slimeoid = EwSlimeoid(member=challenger)

        # Challenger
        
        # Check for slimeoid's type - for flavor text
        if ally_slimeoid.sltype == ewcfg.sltype_nega:
            slimeoidtype = "Negaslimeoid"
        else:
            slimeoidtype = "Slimeoid"

        if ally_slimeoid.life_state != ewcfg.slimeoid_state_active:
            response = "You do not have a Slimeoid ready to battle with!"

        # Checks if the player is dead and if they're trying to battle with a slimeoid
        elif challenger_data.life_state == ewcfg.life_state_corpse and ally_slimeoid.sltype != ewcfg.sltype_nega:
            response = "Your Slimeoid won't battle for you while you're dead."

        elif (time_now - ally_slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
            time_until = ewcfg.cd_slimeoiddefeated - (time_now - ally_slimeoid.time_defeated)
            response = "Your {} is still recovering from its last defeat! It'll be ready in {} seconds.".format(slimeoidtype, int(time_until))

        elif ewutils.active_slimeoidbattles.get(ally_slimeoid.id_slimeoid):
            response = "You are already in the middle of a challenge."
        
        elif challengee:
            # If the opponent isn't a player, set pvp to false. Set data.
            if isinstance(challengee, EwEnemy):
                challengee_data = challengee
                is_pvp = False
            else:
                challengee_data = challengee
                challengee_player = EwPlayer(id_user=challengee.id_user)
                is_pvp = True

            if challengee_slimeoid:
                target_slimeoid = challengee_slimeoid
            else:
                target_slimeoid = EwSlimeoid(member=challengee)

            # Check for slimeoid's type - for flavor text.
            if target_slimeoid.sltype == ewcfg.sltype_nega:
                slimeoidtype = "Negaslimeoid"
            else:
                slimeoidtype = "Slimeoid"

            # If slimeoid isn't alive, then they can't battle.
            if target_slimeoid.life_state != ewcfg.slimeoid_state_active:
                response = "{} does not have a Slimeoid ready to battle with!".format(challengee_player.display_name if is_pvp else challengee_data.display_name)
            
            elif challenger_data.poi != challengee_data.poi:
                response = "Both players must be in the same place."

            # Checks if each player has enough slime if there is a bet
            elif (challenger_data.slimes < bet or challenger_data.slimes < 0) and bet != 0:
                response = "You don't have enough slime!"
            elif (challengee_data.slimes < bet or challengee_data.slimes < 0) and bet != 0:
                response = "They don't have enough slime!"

            # If a player is a ghost and has a living slimeoid, then they can't battle.
            elif challengee_data.life_state == ewcfg.life_state_corpse and challengee_slimeoid.sltype != ewcfg.sltype_nega:
                response = "{}'s Slimeoid won't battle for them while they're dead.".format(challengee_player.display_name).replace("@", "\{at\}")

            elif (time_now - target_slimeoid.time_defeated) < ewcfg.cd_slimeoiddefeated:
                time_until = ewcfg.cd_slimeoiddefeated - (time_now - target_slimeoid.time_defeated)
                response = "{}'s {} is still recovering from its last defeat! It'll be ready in {} seconds.".format(challengee_player.display_name, slimeoidtype, int(time_until))

            elif ewutils.active_slimeoidbattles.get(target_slimeoid.id_slimeoid):
                response = "They are already in the middle of a challenge."

        return response
