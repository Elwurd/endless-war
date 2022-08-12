import random
import time

from ew.backend import core as bknd_core
from .district import EwDistrict
from .frontend import EwResponseContainer
from ew.backend.dungeons import EwGamestate
from ew.backend.market import EwCompany
from ew.backend.market import EwMarket
from ew.backend.market import EwStock
from ew.backend.player import EwPlayer
from ew.static import cfg as ewcfg
import ew.static.vendors as vendors
import ew.static.cosmetics as cosmetics
import ew.static.food as static_food
import ew.static.items as static_items
from ew.utils import core as ewutils

try:
    from ew.cmd import debug as ewdebug
except:
    from ew.cmd import debug_dummy as ewdebug

try:
    import ew.static.rstatic as static_relic
except:
    import ew.static.rstatic_dummy as static_relic

try:
    from ew.utils import rutils as relic_utils
except:
    from ew.utils import rutils_dummy as relic_utils

""" update stock values according to market activity """


async def stock_market_tick(stock_data, id_server):
    market_data = EwMarket(id_server=id_server)
    company_data = EwCompany(id_server=id_server, stock=stock_data.id_stock)
    crashstate = EwGamestate(id_server=id_server, id_state='stockcrashdive').bit

    # Nudge the value back to stability.
    market_rate = stock_data.market_rate
    if market_rate >= 1030:
        market_rate -= 10
    elif market_rate <= 970:
        market_rate += 10

    # Invest/Withdraw effects
    coin_rate = 0
    #stock_at_last_tick = EwStock(id_server=id_server, stock=stock_data.id_stock, timestamp=market_data.time_lasttick)
    #latest_stock = EwStock(id_server=id_server, stock=stock_data.id_stock)
    if stock_data.previous_entry != 0:
        total_shares = [stock_data.total_shares, stock_data.previous_entry[4]]
    else:
        total_shares = [stock_data.total_shares, EwStock(id_server=id_server, stock=stock_data.id_stock, timestamp=market_data.time_lasttick).total_shares]

    # Add profit bonus.
    profits = company_data.recent_profits
    profit_bonus = profits / 100  # - 1 * ((latest_stock.exchange_rate / ewcfg.default_stock_exchange_rate) ** 0.2)
    profit_bonus = min(50, max(profit_bonus, -50))
    market_rate += (profit_bonus / 2)

    if total_shares[0] != total_shares[1]:
        # Positive if net investment, negative if net withdrawal.
        coin_change = (total_shares[0] - total_shares[1])
        coin_rate = ((coin_change * 1.0) / total_shares[1] if total_shares[1] != 0 else 1)

        if coin_rate > 1.0:
            coin_rate = 1.0
        elif coin_rate < -0.5:
            coin_rate = -0.5

        coin_rate = round((coin_rate * ewcfg.max_iw_swing) if coin_rate > 0 else (
                coin_rate * 2 * ewcfg.max_iw_swing))

    market_rate += coin_rate

    # Tick down the boombust cooldown.
    if stock_data.boombust < 0:
        stock_data.boombust += 1
    elif stock_data.boombust > 0:
        stock_data.boombust -= 1

    # Adjust the market rate.
    fluctuation = 0  # (random.randrange(5) - 2) * 100
    noise = (random.randrange(19) - 9) * 2
    subnoise = (random.randrange(13) - 6)

    # Some extra excitement!
    if noise == 0 and subnoise == 0:
        boombust = (random.randrange(3) - 1) * 200

        if crashstate == 1 and boombust > 0:
            boombust = -boombust

        # If a boombust occurs shortly after a previous boombust, make sure it's the opposite effect. (Boom follows bust, bust follows boom.)
        if (stock_data.boombust > 0 and boombust > 0) or (stock_data.boombust < 0 and boombust < 0):
            boombust *= -1

        if boombust != 0:
            stock_data.boombust = ewcfg.cd_boombust

            if boombust < 0:
                stock_data.boombust *= -1
    else:
        boombust = 0

    market_rate += fluctuation + noise + subnoise + boombust

    if market_rate > 500 and crashstate == 1:
        market_rate = round(market_rate / 1.25)

    if market_rate < 300:
        market_rate = (300 + noise + subnoise)

    # percentage = ((market_rate / 10) - 100)
    # percentage_abs = percentage * -1

    exchange_rate_increase = round((market_rate - ewcfg.default_stock_market_rate) * min(stock_data.exchange_rate, ewcfg.default_stock_exchange_rate) / ewcfg.default_stock_market_rate)

    percentage = exchange_rate_increase / stock_data.exchange_rate
    percentage_abs = percentage * -1

    # negative exchange rate causes problems, duh
    # exchange_rate_increase = max(exchange_rate_increase, -stock_data.exchange_rate + 1000)

    points = abs(exchange_rate_increase / 1000.0)

    stock_data.exchange_rate += exchange_rate_increase
    stock_data.market_rate = market_rate

    # Give some indication of how the market is doing to the users.
    response = ewcfg.stock_emotes.get(stock_data.id_stock) + ' ' + ewcfg.stock_names.get(stock_data.id_stock) + ' '

    if stock_data.exchange_rate < 1000:
        response += 'has gone bankrupt!'
        if stock_data.total_shares > 0:
            majority_shareholder = get_majority_shareholder(stock=stock_data.id_stock, id_server=id_server)
            player_data = EwPlayer(id_user=majority_shareholder)
            shares = getUserTotalShares(stock=stock_data.id_stock, id_user=majority_shareholder, id_server=stock_data.id_server)
            shares_lost = round(shares * 0.9)
            stock_data.total_shares -= shares_lost
            updateUserTotalShares(stock=stock_data.id_stock, id_user=majority_shareholder, id_server=stock_data.id_server, shares=shares - shares_lost)
            response += ' The majority shareholder {} is held responsible. SlimeCorp seizes 90% of their shares in the company to pay for the damages.'.format(player_data.display_name)
            stock_data.exchange_rate = 10000
        else:
            response += ' SlimeCorp pumps several billion slimecoin into bailing the company out and a new image campaign.'
            stock_data.exchange_rate = ewcfg.default_stock_exchange_rate
            stock_data.market_rate = ewcfg.default_stock_market_rate
    else:
        # Market is up ...
        if market_rate > 1200:
            response += 'is skyrocketing!!! Slime stock is up {p:.3g} points!!!'.format(p=points)
        elif market_rate > 1100:
            response += 'is booming! Slime stock is up {p:.3g} points!'.format(p=points)
        elif market_rate > 1000:
            response += 'is doing well. Slime stock is up {p:.3g} points.'.format(p=points)
        # Market is down ...
        elif market_rate < 800:
            response += 'is plummeting!!! Slime stock is down {p:.3g} points!!!'.format(p=points)
        elif market_rate < 900:
            response += 'is stagnating! Slime stock is down {p:.3g} points!'.format(p=points)
        elif market_rate < 1000:
            response += 'is a bit sluggish. Slime stock is down {p:.3g} points.'.format(p=points)
        # Perfectly balanced
        else:
            response += 'is holding steady. No change in slime stock value.'

    response += ' ' + ewcfg.stock_emotes.get(stock_data.id_stock)

    stock_data.persist()

    company_data.total_profits += company_data.recent_profits
    company_data.recent_profits = 0
    company_data.persist()

    # Send the announcement.
    return response


"""" returns the total number of shares a player has in a certain stock """


def getUserTotalShares(id_server, stock, id_user):
    values = 0

    try:

        data = bknd_core.execute_sql_query("SELECT {shares} FROM shares WHERE {id_server} = %s AND {id_user} = %s AND {stock} = %s".format(
            stock=ewcfg.col_stock,
            shares=ewcfg.col_shares,
            id_server=ewcfg.col_id_server,
            id_user=ewcfg.col_id_user
        ), (
            id_server,
            id_user,
            stock,
        ))

        for row in data:
            values = row[0]

    except Exception as e:
        ewutils.logMsg(f"Failed to get user total shares for {id_user}: {e}")
        pass
    finally:
        return values


"""" updates the total number of shares a player has in a certain stock """


def updateUserTotalShares(id_server = None, stock = None, id_user = None, shares = 0):
    if id_server != None and stock != None and id_user != None:

        try:

            bknd_core.execute_sql_query("REPLACE INTO shares({id_server}, {id_user}, {stock}, {shares}) VALUES(%s, %s, %s, %s)".format(
                stock=ewcfg.col_stock,
                shares=ewcfg.col_shares,
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                id_server,
                id_user,
                stock,
                shares,
            ))
        except:
            pass


""" get user ID of player with most shares in a stock """


def get_majority_shareholder(id_server = None, stock = None):
    result = None
    if id_server is not None and stock is not None:
        try:

            data = bknd_core.execute_sql_query("SELECT {id_user}, {shares} FROM shares WHERE {id_server} = %s AND {stock} = %s ORDER BY {shares} DESC LIMIT 1".format(
                stock=ewcfg.col_stock,
                shares=ewcfg.col_shares,
                id_server=ewcfg.col_id_server,
                id_user=ewcfg.col_id_user
            ), (
                id_server,
                stock,
            ))

            if len(data) > 0:
                if data[0][1] > 0:
                    result = data[0][0]

        except:
            pass
        finally:
            return result

""" Update all the stocks currently available in the Stock Exchange """

async def update_stocks(id_server = None):
    if id_server:
        exchange_data = EwDistrict(district=ewcfg.poi_id_stockexchange, id_server=id_server)
        resp_cont = EwResponseContainer(ewcfg.get_client(), id_server=id_server)
        for stock in ewcfg.stocks:
            s = EwStock(id_server, stock)
            # we don't update stocks when they were just added
            if s.timestamp != 0:
                s.timestamp = int(time.time())
                market_response = await stock_market_tick(s, id_server)
                resp_cont.add_channel_response(ewcfg.channel_stockexchange, market_response)
                resp_cont.add_channel_response(ewcfg.channel_stockexchange_p, market_response)

        await resp_cont.post()
                


""" Clear the bazaar and then refresh stock. """

async def refresh_bazaar(id_server = None):
    if id_server:
        # Update the list of available bazaar items by clearing the current list and adding the new items
        market_data = EwMarket(id_server)
        market_data.bazaar_wares.clear()

        bazaar_foods = []
        bazaar_cosmetics = []
        bazaar_general_items = []
        bazaar_furniture = []
        bazaar_relics = []


        for item in vendors.vendor_inv.get(ewcfg.vendor_bazaar):
            if item in static_items.item_names:
                bazaar_general_items.append(item)

            elif item in static_food.food_names:
                bazaar_foods.append(item)

            elif item in cosmetics.cosmetic_names:
                bazaar_cosmetics.append(item)

            elif item in static_items.furniture_names:
                bazaar_furniture.append(item)


            elif item in static_relic.relic_names and relic_utils.canCreateRelic(item=item, id_server=id_server) is not None:
                bazaar_relics.append(item)

        if (ewdebug.bazaarTurnout() == 1) and (len(bazaar_relics) > 0):
            market_data.bazaar_wares['relic1'] = random.choice(bazaar_relics)

        market_data.bazaar_wares['slimecorp1'] = ewcfg.weapon_id_umbrella
        market_data.bazaar_wares['slimecorp2'] = ewcfg.cosmetic_id_raincoat

        market_data.bazaar_wares['generalitem'] = random.choice(bazaar_general_items)

        market_data.bazaar_wares['food1'] = random.choice(bazaar_foods)
        # Don't add repeated foods
        bw_food2 = None
        while bw_food2 is None or bw_food2 in market_data.bazaar_wares.values():
            bw_food2 = random.choice(bazaar_foods)

        market_data.bazaar_wares['food2'] = bw_food2

        market_data.bazaar_wares['cosmetic1'] = random.choice(bazaar_cosmetics)
        # Don't add repeated cosmetics
        bw_cosmetic2 = None
        while bw_cosmetic2 is None or bw_cosmetic2 in market_data.bazaar_wares.values():
            bw_cosmetic2 = random.choice(bazaar_cosmetics)

        market_data.bazaar_wares['cosmetic2'] = bw_cosmetic2

        bw_cosmetic3 = None
        while bw_cosmetic3 is None or bw_cosmetic3 in market_data.bazaar_wares.values():
            bw_cosmetic3 = random.choice(bazaar_cosmetics)

        market_data.bazaar_wares['cosmetic3'] = bw_cosmetic3

        market_data.bazaar_wares['furniture1'] = random.choice(bazaar_furniture)

        bw_furniture2 = None
        while bw_furniture2 is None or bw_furniture2 in market_data.bazaar_wares.values():
            bw_furniture2 = random.choice(bazaar_furniture)

        market_data.bazaar_wares['furniture2'] = bw_furniture2

        bw_furniture3 = None
        while bw_furniture3 is None or bw_furniture3 in market_data.bazaar_wares.values():
            bw_furniture3 = random.choice(bazaar_furniture)

        market_data.bazaar_wares['furniture3'] = bw_furniture3

        if random.random() < 0.05:  # 1 / 20
            market_data.bazaar_wares['minigun'] = ewcfg.weapon_id_minigun

        if random.random() < 0.05:  # 1 / 20
            market_data.bazaar_wares['bustedrifle'] = ewcfg.item_id_bustedrifle
        
        market_data.persist()
