from ew.static import cfg as ewcfg
from . import itemcmds
from .itemcmds import item_look

cmd_map = {

    # Fiddle with souls
    ewcfg.cmd_extractsoul: itemcmds.soulextract,
    ewcfg.cmd_returnsoul: itemcmds.returnsoul,
    ewcfg.cmd_squeeze: itemcmds.squeeze,

    # show player inventory
    ewcfg.cmd_inventory: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt1: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt2: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt3: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt4: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt5: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt6: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt7: itemcmds.inventory_print,
    ewcfg.cmd_communitychest: itemcmds.inventory_print,

    # get an item's description
    ewcfg.cmd_inspect: itemcmds.item_look,
    ewcfg.cmd_inspect_alt1: itemcmds.item_look,
    ewcfg.cmd_plainlook: itemcmds.item_look,

    # use an item
    ewcfg.cmd_use: itemcmds.item_use,

    # Edit props from discord
    ewcfg.cmd_editprops: itemcmds.manually_edit_item_properties,

    # give an item to another player
    ewcfg.cmd_give: itemcmds.give,

    # drop item into your current district
    ewcfg.cmd_discard: itemcmds.discard,
    ewcfg.cmd_discard_alt1: itemcmds.discard,

    # delete a food item from your inventory
    ewcfg.cmd_trash: itemcmds.trash,

    # delete a person
    ewcfg.cmd_zuck: itemcmds.zuck,

    # Retype items
    ewcfg.cmd_pot: itemcmds.flowerpot,
    ewcfg.cmd_unpot: itemcmds.unpot,
    ewcfg.cmd_propstand: itemcmds.propstand,
    ewcfg.cmd_releaseprop: itemcmds.releaseprop,
    ewcfg.cmd_aquarium: itemcmds.aquarium,
    ewcfg.cmd_releasefish: itemcmds.releasefish,

    # stow/snag for chests and apartment storage
    ewcfg.cmd_store: itemcmds.store_item,
    ewcfg.cmd_take: itemcmds.remove_item,

    ewcfg.cmd_scrawl: itemcmds.add_message,
    ewcfg.cmd_strip: itemcmds.strip_message,

    # Make a costume for Double Halloween

    # Admin/Debug cmds
    ewcfg.cmd_forgemasterpoudrin: itemcmds.forge_master_poudrin,
    ewcfg.cmd_createitem: itemcmds.create_item,
    ewcfg.cmd_createmulti: itemcmds.create_multi,
    ewcfg.cmd_moveitem: itemcmds.manual_transfer,

    ewcfg.cmd_createall: itemcmds.create_all,


    ewcfg.cmd_manualsoulbind: itemcmds.manual_soulbind,
    ewcfg.cmd_collect: itemcmds.collect,
    ewcfg.cmd_extract: itemcmds.remove_from_collection,

    # SLIMERNALIA
    ewcfg.cmd_unwrap: itemcmds.unwrap,
    ewcfg.cmd_unearth:itemcmds.unearth,
    ewcfg.cmd_bury:itemcmds.bury

}

if ewcfg.dh_active:
    cmd_map[ewcfg.cmd_makecostume]= itemcmds.makecostume

dm_cmd_map = {

    # show player !inventory
    ewcfg.cmd_inventory: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt1: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt2: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt3: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt4: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt5: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt6: itemcmds.inventory_print,
    ewcfg.cmd_inventory_alt7: itemcmds.inventory_print,
    ewcfg.cmd_communitychest: itemcmds.inventory_print,

    # !inspect
    ewcfg.cmd_inspect: itemcmds.item_look,
    ewcfg.cmd_inspect_alt1: itemcmds.item_look,
    ewcfg.cmd_plainlook: itemcmds.item_look,
}

apt_dm_cmd_map = {

    # !use
    ewcfg.cmd_use: itemcmds.item_use,

    # !extract/returnsoul
    ewcfg.cmd_extractsoul: itemcmds.soulextract,
    ewcfg.cmd_returnsoul: itemcmds.returnsoul,

    # give an item to another player
    ewcfg.cmd_give: itemcmds.give,

    # !squeeze
    ewcfg.cmd_squeeze: itemcmds.squeeze,

    # Retype items
    ewcfg.cmd_pot: itemcmds.flowerpot,
    ewcfg.cmd_unpot: itemcmds.unpot,
    ewcfg.cmd_propstand: itemcmds.propstand,
    ewcfg.cmd_releaseprop: itemcmds.releaseprop,
    ewcfg.cmd_aquarium: itemcmds.aquarium,
    ewcfg.cmd_releasefish: itemcmds.releasefish,
    ewcfg.cmd_collect:itemcmds.collect,

}
