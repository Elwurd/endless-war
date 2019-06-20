import math
import random

import ewcfg
import ewitem
import ewutils

from ew import EwUser
from ewitem import EwItem

"""
	Cosmetic item model object
"""
class EwCosmeticItem:
	# The proper name of the cosmetic item
	id_cosmetic = ""

	# The string name of the cosmetic item
	str_name = ""

	# The text displayed when you look at it
	str_desc = ""

	# How rare the item is, can be "Plebeian", "Patrician", or "Princeps"
	rarity = ""

	# The ingredients necessary to make this item via milling.
	ingredients = ""

	def __init__(
		self,
		id_cosmetic = "",
		str_name = "",
		str_desc = "",
		rarity = "",
		ingredients = ""
	):
		self.id_cosmetic = id_cosmetic
		self.str_name = str_name
		self.str_desc = str_desc
		self.rarity = rarity
		self.ingredients = ingredients

"""
	Smelt command
"""
async def smelt(cmd):
	poudrins = ewitem.inventory(
		id_user = cmd.message.author.id,
		id_server = cmd.message.server.id,
		item_type_filter = ewcfg.it_slimepoudrin
	)

	if len(poudrins) < 2:
		response = "You don't have enough poudrins to smelt."
	else:
		for i in range(2):
			ewitem.item_delete(id_item = poudrins[i].get('id_item'))

		patrician_rarity = 20
		patrician_smelted = random.randint(1, patrician_rarity)
		patrician = False

		if patrician_smelted == 1:
			patrician = True

		cosmetics_list = []

		for result in ewcfg.cosmetic_items_list:
			if result.ingredients == "":
				cosmetics_list.append(result)
			else:
				pass

		items = []

		for cosmetic in cosmetics_list:
			if patrician and cosmetic.rarity == ewcfg.rarity_patrician:
				items.append(cosmetic)
			elif not patrician and cosmetic.rarity == ewcfg.rarity_plebeian:
				items.append(cosmetic)

		item = items[random.randint(0, len(items) - 1)]

		ewitem.item_create(
			item_type = ewcfg.it_cosmetic,
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
			item_props = {
				'id_cosmetic': item.id_cosmetic,
				'cosmetic_name': item.str_name,
				'cosmetic_desc': item.str_desc,
				'rarity': item.rarity,
				'adorned': 'false'
			}
		)
		response = "You smelted a {item_name}!".format(item_name = item.str_name)
	await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))

async def adorn(cmd):
	item_id = ewutils.flattenTokenListToString(cmd.tokens[1:])

	try:
		item_id_int = int(item_id)
	except:
		item_id_int = None

	if item_id != None and len(item_id) > 0:
		response = "You don't have one."

		items = ewitem.inventory(
			id_user = cmd.message.author.id,
			id_server = cmd.message.server.id,
			item_type_filter = ewcfg.it_cosmetic
		)

		item_sought = None
		for item in items:
			if item.get('id_item') == item_id_int or item_id in ewutils.flattenTokenListToString(item.get('name')):
				item_sought = item
				break

		if item_sought != None:
			id_item = item_sought.get('id_item')
			item_def = item_sought.get('item_def')
			name = item_sought.get('id_cosmetic')
			item_type = item_sought.get('item_type')

			adorned_items = 0
			for it in items:
				i = EwItem(it.get('id_item'))
				if i.item_props['adorned'] == 'true':
					adorned_items += 1

			user_data = EwUser(member = cmd.message.author)
			item = EwItem(id_item = id_item)

			if item.item_props['adorned'] == 'true':
				item.item_props['adorned'] = 'false'
				response = "You successfully dedorn your " + item.item_props['cosmetic_name'] + "."
			else:
				if adorned_items >= math.ceil(user_data.slimelevel / ewcfg.max_adorn_mod):
					response = "You can't adorn anymore cosmetics."
				else:
					item.item_props['adorned'] = 'true'
					response = "You successfully adorn your " + item.item_props['cosmetic_name'] + "."

			item.persist()

		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, response))
	else:
		await ewutils.send_message(cmd.client, cmd.message.channel, ewutils.formatMessage(cmd.message.author, 'Adorn which cosmetic? Check your **!inventory**.'))
