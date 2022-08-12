from ew.backend import core as bknd_core
from ew.backend import item as bknd_item
from ew.backend.book import EwBook
from ew.backend.book import EwBookSale
from ew.backend.item import EwItem
from ew.backend.market import EwMarket
from ew.cmd.apt import aptcmds as apt_cmds
from ew.static import cfg as ewcfg
from ew.static import poi as poi_static
from ew.utils import core as ewutils
from ew.utils import frontend as fe_utils
from ew.utils.combat import EwUser
from ew.utils.frontend import EwResponseContainer
from .bookutils import readers, get_page, int_is_zine


async def begin_manuscript(cmd):
    user_data = EwUser(member=cmd.message.author)
    title = cmd.message.content[(len(cmd.tokens[0])):].strip()

    cost = 20000

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript or poi.id_poi == ewcfg.poi_id_clinicofslimoplasty:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.slimes < cost:
        response = "You don't have enough slime to create a manuscript. ({:,}/{:,})".format(user_data.slimes, cost)

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to begin your masterpiece!"

    elif title == "":
        response = "Specify a title."

    elif len(title) > 50:
        response = "Alright buddy, reel it in. That title is just too long. ({:,}/50)".format(len(title))

    else:

        if user_data.manuscript != -1:
            response = "You already have a manuscript deployed you eager beaver!"
        else:
            book = EwBook(member=cmd.message.author, book_state=0)
            book.author = cmd.message.author.display_name
            book.title = title
            user_data.manuscript = book.id_book
            user_data.change_slimes(n=-cost, source=ewcfg.source_spending)

            book.persist()
            user_data.persist()

            response = "You exchange 20,000 slime for a shoddily-bound manuscript. You scrawl the name \"{} by {}\" into the cover.".format(book.title, book.author)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def set_pen_name(cmd):
    user_data = EwUser(member=cmd.message.author)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to alter the pen name of your masterpiece!"

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    else:
        book = EwBook(member=cmd.message.author, book_state=0)
        if book.author != cmd.message.author.display_name:
            book.author = cmd.message.author.display_name

            book.persist()

            response = "You scratch out the author name and scrawl \"{}\" under it.".format(book.author)
        else:
            response = "If you would like to change your pen name, you must change your nickname."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def set_title(cmd):
    user_data = EwUser(member=cmd.message.author)

    title = cmd.message.content[(len(cmd.tokens[0])):].strip()

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to alter the title of your masterpiece!"

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    elif title == "":
        response = "Please specify the title you want to change it to."

    elif len(title) > 50:
        response = "Alright buddy, reel it in. That title is just too long. ({:,}/50)".format(len(title))

    else:
        book = EwBook(member=cmd.message.author, book_state=0)
        book.title = title

        book.persist()

        response = "You scratch out the title and scrawl \"{}\" over it.".format(book.title)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def set_genre(cmd):
    user_data = EwUser(member=cmd.message.author)

    genre = cmd.message.content[(len(cmd.tokens[0])):].strip()

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to alter the title of your masterpiece!"

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    elif genre not in ewcfg.book_genres:
        response = "Please specify the genre you want to change it to. You can choose from {}.".format(ewutils.formatNiceList(ewcfg.book_genres))

    else:
        for i in [i for i, x in enumerate(ewcfg.book_genres) if x == genre]:
            id_genre = i

        book = EwBook(member=cmd.message.author, book_state=0)

        if id_genre in [10, 11] and not cmd.message.author.guild_permissions.administrator:
            response = "You're not a doctor. The publishing company's gonna skin your ass, so you better not."

        else:
            book.genre = id_genre
            book.persist()

            response = "You scribble {} onto the back cover.".format(genre)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def edit_page(cmd):
    user_data = EwUser(member=cmd.message.author)

    response = ""

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to write your masterpiece!"

    elif cmd.tokens_count == 1:
        response = "You must specify a valid page to edit."

    elif cmd.tokens_count < 3:
        response = "What are you writing down exactly?"

    else:
        page = cmd.tokens[1]
        content = cmd.message.content[(len(cmd.tokens[0]) + len(cmd.tokens[1]) + 2):]
        max_length_page = 1500

        if page == "cover":
            page = '0'

        if not page.isdigit():
            response = "You must specify a valid page to edit."

        elif content == "":
            response = "What are you writing down exactly?"

        elif len(content) > max_length_page:
            response = "Alright buddy, reel it in. That just won't fit on a single page. ({:,}/{:,})".format(len(content), max_length_page)

        else:
            page = int(page)
            book = EwBook(member=cmd.message.author, book_state=0)

            if page not in range(0, book.pages + 1):
                response = "You must specify a valid page to edit."

            else:
                accepted = True

                if book.book_pages.get(page, "") != "":
                    accepted = False
                    response = "There is already writing on this page. Are you sure you want to overwrite it? **!accept** or **!refuse**"

                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    try:
                        message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                         message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                        if message != None:
                            if message.content.lower() == ewcfg.cmd_accept:
                                accepted = True
                            if message.content.lower() == ewcfg.cmd_refuse:
                                accepted = False
                    except:
                        accepted = False
                if not accepted:
                    response = "The page remains unchanged."
                else:
                    book.book_pages[page] = content

                    book.persist()
                    response = "You spend some time contemplating your ideas before scribbling them onto the page."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def view_page(cmd):
    user_data = EwUser(member=cmd.message.author)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    elif cmd.tokens_count == 1:
        response = "You must specify a valid page to view."

    else:
        page = cmd.tokens[1]

        if page == 'cover':
            page = '0'

        elif not page.isdigit():
            response = "You must specify a valid page to view."

        elif int(page) not in range(0, 11):
            response = "You must specify a valid page to view."

        else:
            page = int(page)
            book = EwBook(member=cmd.message.author, book_state=0)
            content = book.book_pages.get(page, "")

            if content == "":
                response = "This page is blank. Try !editpage {}.".format(page)
            else:
                response = '"{}"'.format(content)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def check_manuscript(cmd):
    user_data = EwUser(member=cmd.message.author)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    else:
        book = EwBook(member=cmd.message.author, book_state=0)
        title = book.title
        author = book.author
        pages = book.pages
        length = 0

        for page in range(1, book.pages + 1):
            length += len(book.book_pages.get(page, ""))

        cover = book.book_pages.get(0, "")

        if cover == "":
            cover_text = ""

        else:
            cover_text = " The cover is {}".format(cover)

        response = "{} by {}. It is {} pages and {:,} characters long.{}".format(title, author, pages, length, cover_text)

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def publish_manuscript(cmd):
    user_data = EwUser(member=cmd.message.author)

    market_data = EwMarket(id_server=user_data.id_server)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    else:
        book = EwBook(member=cmd.message.author, book_state=0)
        # check if zine is unreasonably short
        length = 0
        for page in book.book_pages.keys():
            length += len(book.book_pages[page])

        if book.genre == -1:
            response = "Before you publish your zine, you must first set a genre with !setgenre. The genre choices are {}.".format(ewutils.formatNiceList(ewcfg.book_genres))

        elif len(book.book_pages.keys()) < 3 or length < 10:
            response = "Who are you trying to fool? This zine is obviously too short!"

        else:
            accepted = False

            response = "Are you sure you want to publish your manuscript? This cannot be undone. **!accept** or **!refuse**"

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

            try:
                message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                 message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                if message != None:
                    if message.content.lower() == ewcfg.cmd_accept:
                        accepted = True
                    if message.content.lower() == ewcfg.cmd_refuse:
                        accepted = False
            except:
                accepted = False

            if not accepted:
                response = "The manuscript was not published."

            else:
                book.book_state = 1
                book.date_published = market_data.day
                length = 0

                for page in range(1, book.pages + 1):
                    length += len(book.book_pages.get(page, ""))

                book.length = length
                user_data.manuscript = -1

                user_data.persist()
                book.persist()

                bknd_item.item_create(
                    item_type=ewcfg.it_book,
                    id_user=user_data.id_user,
                    id_server=book.id_server,
                    item_props={
                        "title": book.title,
                        "author": book.author,
                        "date_published": book.date_published,
                        "id_book": book.id_book,
                        "book_desc": "A zine by {}, published on {}. It's the author's copy.".format(book.author, book.date_published)
                    })

                book_sale = EwBookSale(id_book=book.id_book, member=cmd.message.author)
                book_sale.bought = 1

                book_sale.persist()

                response = "You've published your manuscript! Anybody can now buy your creation and you'll get royalties!"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def read_book(cmd):
    dm = cmd.message.guild is None

    user_data = EwUser(member=cmd.message.author)

    if not dm:
        response = "ENDLESS WAR politely asks that you !read in his DMs."

    elif len(cmd.tokens) < 2:
        response = "What zine do you want to read?"

    else:
        if len(cmd.tokens) < 3:
            book_title = ewutils.flattenTokenListToString(cmd.tokens)
            page_number = 0
        else:
            book_title = ewutils.flattenTokenListToString(cmd.tokens[1:len(cmd.tokens) - 1])
            page_number = ewutils.getIntToken(cmd.tokens)

        book_sought = bknd_item.find_item(item_search=book_title, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_book)

        if book_sought:
            book = EwItem(id_item=book_sought.get('id_item'))
            id_book = book.item_props.get("id_book")
            book = EwBook(id_book=id_book)

            if page_number not in range(0, book.pages + 1):
                page_number = 0

            accepted = True
            if book.genre == 3:

                accepted = False
                response = "ENDLESS WAR sees you about to open up a porn zine and wants to make sure you're 18 years or older. Use **!accept** to open or **!refuse** to abstain."

                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                try:
                    message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                     message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                    if message != None:
                        if message.content.lower() == ewcfg.cmd_accept:
                            accepted = True
                        if message.content.lower() == ewcfg.cmd_refuse:
                            accepted = False
                except:
                    accepted = False

            if book.book_state < 0:
                response = "You simply can't make out the letters on the page. Maybe it's better this way."

            elif accepted:
                page_contents = get_page(id_book, page_number)

                if page_number == 0 and page_contents == "":
                    page_contents = get_page(id_book, 1)

                page_text = "turn to page {}".format(page_number)

                if page_number == 0:
                    page_text = "look at the cover"

                response = "You {} and begin to read.\n\n\"{} \"".format(page_text, page_contents)
                readers[user_data.id_user] = (id_book, page_number)

                if page_contents == "":
                    response = "You open up to page {} only to find that it's blank!".format(page_number)

                if page_number != 0:
                    response += "\n\nUse **!previouspage** to go back one page."

                if page_number != book.pages:
                    response += "\n\nUse **!nextpage** to go forward one page."

            else:
                response = "You decide not to indulge yourself."

        else:
            response = "You don't have that zine. Make sure you use **!read [zine title] [page]**"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def next_page(cmd):
    dm = cmd.message.guild is None

    user_data = EwUser(member=cmd.message.author)

    if not dm:
        response = "ENDLESS WAR politely asks that you !read in his DMs."

    elif user_data.id_user in readers.keys():
        id_book = readers[user_data.id_user][0]
        book = EwBook(id_book=id_book)
        page_number = readers[user_data.id_user][1]

        if page_number == book.pages:
            response = "You've reached the end of the zine."

        else:
            page_number += 1
            page_contents = get_page(id_book, page_number)
            page_text = "turn to page {}".format(page_number)

            if page_number == 0:
                page_text = "look at the cover"

            response = "You {} and begin to read.\n\n\"{} \"".format(page_text, page_contents)
            readers[user_data.id_user] = (id_book, page_number)

            if page_contents == "":
                response = "You open up to page {} only to find that it's blank!".format(page_number)

            if page_number != 0:
                response += "\n\nUse **!previouspage** to go back one page."

            if page_number != book.pages:
                response += "\n\nUse **!nextpage** to go forward one page."

    else:
        response = "You haven't opened a zine yet!"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def previous_page(cmd):
    dm = cmd.message.guild is None

    user_data = EwUser(member=cmd.message.author)

    if not dm:
        response = "ENDLESS WAR politely asks that you !read in his DMs."

    elif user_data.id_user in readers.keys():
        id_book = readers[user_data.id_user][0]
        book = EwBook(id_book=id_book)
        page_number = readers[user_data.id_user][1]

        if page_number == 0:
            response = "You've reached the start of the zine."

        else:
            page_number -= 1
            page_contents = get_page(id_book, page_number)
            page_text = "turn to page {}".format(page_number)

            if page_number == 0:
                page_text = "look at the cover"

            response = "You {} and begin to read.\n\n\"{} \"".format(page_text, page_contents)
            readers[user_data.id_user] = (id_book, page_number)

            if page_contents == "":
                response = "You open up to page {} only to find that it's blank!".format(page_number)

            if page_number != 0:
                response += "\n\nUse **!previouspage** to go back one page."

            if page_number != book.pages:
                response += "\n\nUse **!nextpage** to go forward one page."
    else:
        response = "You haven't opened a zine yet!"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def browse_zines(cmd):
    if len(cmd.tokens) > 1:
        sort_token = cmd.tokens[1].replace("_", "")

    else:
        sort_token = "null"

    user_data = EwUser(member=cmd.message.author)
    poi = poi_static.id_to_poi.get(user_data.poi)

    if poi.is_apartment:
        return await apt_cmds.browse(cmd)

    if not poi.write_manuscript:
        response = "You can't browse for zines here! Try going to the cafe. If you're looking for educational zines, try the colleges. If you can't read, then you might want to try the comic shop."

        await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

    else:
        if not sort_token.isdigit():
            book_list = []
            resp_cont = EwResponseContainer(id_server=cmd.guild.id)
            query_suffix = ""
            query_sort = "id_book"
            more_selects = ""
            quality = "= 1"

            if user_data.poi in ["nlac-university", "neo-milwaukee-state"]:
                query_suffix = "AND b.genre = 1 "

            elif user_data.poi in ["glocksbury-comics"]:
                query_suffix = "AND b.genre = 2 "

            elif user_data.poi in [ewcfg.poi_id_clinicofslimoplasty]:
                query_suffix = "AND b.genre = 10 "

            if sort_token in ("bookname", "name", "title", "booktitle", "zinename", "zinetitle"):
                query_sort = "title"

            elif sort_token in ("author", "authorname", "artist", "artistname", "illustrator"):
                query_sort = "author"

            elif sort_token in ("date", "datepublished", "day", "time", "published", "publish", "publishdate"):
                query_sort = "date_published"
                more_selects = ", b.date_published"

            elif sort_token in ewcfg.book_genres:
                genre = ""

                for i in [i for i, x in enumerate(ewcfg.book_genres) if x == sort_token]:
                    genre = i

                query_suffix = "AND b.genre = {} ".format(genre)

            elif sort_token in ('reverse', 'inverse', 'descend', 'desc', 'descending', 'backwards'):
                query_sort += " DESC"

            elif sort_token in ('length', 'len', 'pages', 'long', 'longest'):
                query_sort = "length DESC"
                more_selects = ", b.length"

            elif sort_token in ('sales', 'sale', 'sell', 'bestsellers', 'topsellers', 'bestselling'):
                query_sort = "sales DESC"
                more_selects = ", b.sales"

            elif sort_token in ('rating', 'quality', 'ratings', 'rate', 'fucks', 'rate', 'fuck', 'toprated', 'best', 'highestrated'):
                query_sort = "rating DESC, rates DESC"
                more_selects = ", b.rating, b.rates"

            elif sort_token in ('bad', 'terrible', 'shit', 'shitty', 'worst', 'worstrated', 'bottom'):
                quality = "= 2"

            elif sort_token in ('all', 'every'):
                quality = "> 0"
                query_suffix = ""
                query_sort = "id_book"
                more_selects = ""

            if len(cmd.tokens) > 2:
                if cmd.tokens[2] in ('reverse', 'inverse', 'descend', 'desc', 'descending', 'backwards'):
                    if not query_sort.endswith(" DESC"):
                        query_sort += " DESC"

                    else:
                        query_sort = query_sort[:len(query_sort) - 5] + " ASC"
            try:
                conn_info = bknd_core.databaseConnect()
                conn = conn_info.get('conn')
                cursor = conn.cursor()

                cursor.execute((
                        "SELECT b.id_book, b.title, b.author{} ".format(more_selects) +
                        "FROM books AS b " +
                        "WHERE b.id_server = %s AND b.genre <> 11 AND b.book_state {} {}".format(quality, query_suffix) +
                        "ORDER BY b.{}".format(query_sort)
                ), (
                    cmd.guild.id,
                ))

                data = cursor.fetchall()
                if data != None:
                    for row in data:
                        more_info = ""

                        if query_sort.startswith("date_published"):
                            more_info = " (Published on day {})".format(row[3])

                        elif query_sort.startswith("length"):
                            more_info = " (Length: {} characters)".format(row[3])

                        elif query_sort.startswith("sales"):
                            more_info = " (Sales: {} copies)".format(row[3])

                        elif query_sort.startswith("rating"):
                            if row[3] == '0' and row[4] == 0:
                                more_info = " (Rating: No fucks given yet)"

                            else:
                                more_info = " (Rating: {} fucks across {} ratings)".format(row[3], row[4])

                        book_list.append("\n{}: {} by {}{}".format(
                            row[0],
                            row[1].replace("`", "").replace("\n", ""),
                            row[2].replace("`", "").replace("\n", ""),
                            more_info,
                        ))

            finally:
                # Clean up the database handles.
                cursor.close()
                bknd_core.databaseClose(conn_info)

            if len(book_list) != 0:
                resp_num = 0
                resp_count = 0
                resp_list = []

                # weird looking loop (i assure you it works tho)
                for book in book_list:
                    resp_count += 1

                    if len(resp_list) != resp_num + 1:
                        resp_list.append("")
                    resp_list[resp_num] += book

                    if resp_count == 10:
                        resp_count = 0
                        resp_num += 1

                for resp_block in resp_list:
                    resp_cont.add_channel_response(cmd.message.channel, resp_block)

                # Send the response to the player.
                resp_cont.format_channel_response(cmd.message.channel, cmd.message.author)

                await resp_cont.post(channel=cmd.message.channel)
            else:
                response = "There aren't any zines in circulation at the moment."

                await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))
        else:
            id_book = int(sort_token)

            if int_is_zine(id_book, cmd.guild.id):
                book = EwBook(id_book=id_book)
                title = book.title
                author = book.author
                genre = ewcfg.book_genres[book.genre]

                response = "\n{} is a {} zine by {}.\n".format(title, genre, author)

                cover = book.book_pages.get(0, "")
                pages = book.pages
                length = book.length
                date = book.date_published

                response += "It is {} pages and {:,} characters long and was published on Day {}. ".format(pages, length, date)

                sales = book.sales
                rating = book.rating
                rates = book.rates

                if sales == 0:
                    response += "It has not yet been bought by anyone.\n"

                else:
                    response += "It has sold {:,} copies.\n".format(sales)

                if rates == 0:
                    response += "Nobody has given it any fucks.\n"

                else:
                    response += "It has received {} ratings with an average of {} fucks given out of 5.\n".format(rates, rating)

                if cover != "":
                    if genre == "porn":
                        response += "The cover looks like this: ||{}||".format(cover)
                    else:
                        response += "The cover looks like this: {}".format(cover)

            else:
                response = "That's not a valid zine ID."

            await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def order_zine(cmd):
    user_data = EwUser(member=cmd.message.author)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You can't buy zines here! Try going to the cafe. If you're looking for educational books, try the colleges. If you can't read, then you might want to try the comic shop."

    elif len(cmd.tokens) == 1:
        response = "Specify a zine to purchase. Find zine IDs with !browse."

    elif not bknd_item.check_inv_capacity(user_data=user_data, item_type=ewcfg.it_book):
        response = "You can't carry any more zines."

    else:
        if cmd.tokens[1].isdigit():
            id_book = int(cmd.tokens[1])

            if int_is_zine(id_book, cmd.guild.id):
                book = EwBook(id_book=id_book)
                accepted = True
                if book.genre == 3:
                    accepted = False
                    response = "THIS ZINE IS PORNOGRAPHY. CONFIRM THAT YOU ARE AT LEAST 18 YEARS OLD. **!accept** or **!refuse**"

                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    try:
                        message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                         message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                        if message != None:
                            if message.content.lower() == ewcfg.cmd_accept:
                                accepted = True
                            if message.content.lower() == ewcfg.cmd_refuse:
                                accepted = False
                    except:
                        accepted = False

                if not accepted:
                    response = "No porn for you."

                elif accepted:
                    if book.genre != 10 and poi.id_poi == ewcfg.poi_id_clinicofslimoplasty:
                        response = "Specify a zine to purchase. Find zine IDs with !browse."
                        return await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    user_data = EwUser(member=cmd.message.author)

                    #if book.genre != 10:
                    #    price = ewcfg.zine_cost
                    #else:
                    #    price = ewcfg.zine_cost / 4

                    #if user_data.slimes < price:
                    poudrins = bknd_item.find_item(item_search="slimepoudrin", id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None, item_type_filter=ewcfg.it_item)

                    if poudrins == None:
                        response = "YOU CAN'T AFFORD IT. YOU NEED A POUDRIN."

                    else:
                        bknd_item.item_create(
                            item_type=ewcfg.it_book,
                            id_user=user_data.id_user,
                            id_server=cmd.guild.id,
                            item_props={
                                "title": book.title,
                                "author": book.author,
                                "date_published": book.date_published,
                                "id_book": book.id_book,
                                "book_desc": "A book by {}, published on {}.".format(book.author, book.date_published)
                            })
                        book_sale = EwBookSale(id_book=book.id_book, member=cmd.message.author)

                        if book.id_user != user_data.id_user:
                            if book_sale.bought == 0:
                                book_sale.bought = 1
                                book.sales += 1
                                book_sale.persist()
                                book.persist()

                        bknd_item.item_delete(id_item=poudrins.get('id_item'))
                        #user_data.change_slimes(n=-(price), source=ewcfg.source_spending)

                        user_data.persist()

                        if book.genre != 10:
                            author = EwUser(id_user=book.id_user, id_server=book.id_server)

                            if author.id_user != user_data.id_user and bknd_item.check_inv_capacity(user_data=user_data, item_type=ewcfg.it_item):
                                bknd_item.item_create(
                                    item_type=ewcfg.it_item,
                                    id_user=author.id_user,
                                    id_server=cmd.guild.id,
                                    item_props={
                                        'context': 'poudrin',
                                        'item_name': 'Royalty Poudrin',
                                        'item_desc': 'You received this less powerful poudrin from some fool who decided to buy your zine. !crush it for 5k slime.',
                                        'id_item': 'royaltypoudrin'
                                    })

                        response = "You manage to locate {} by {} in the vast array of zines on the bookshelf, so you bring it to the counter and hand over {:,} slime to the employee. Now it's time to !read it.".format(book.title, book.author, ewcfg.zine_cost)

            else:
                response = "Specify a zine to purchase. Find zine IDs with !browse."

        else:
            response = "Specify a zine to purchase. Find zine IDs with !browse."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def rate_zine(cmd):
    if len(cmd.tokens) < 2:
        response = "What zine do you want to rate?"

    else:
        if len(cmd.tokens) >= 3:
            rating = ewutils.getIntToken(cmd.tokens)
            book_title = ewutils.flattenTokenListToString(cmd.tokens[1:len(cmd.tokens) - 1])

            if rating == None:
                response = "How many fucks do you want to give the zine? (1-5)"

            elif rating not in range(1, 6):
                response = "Easy now, keep your fucks between 1 and 5."

            else:
                book_sought = bknd_item.find_item(item_search=book_title, id_user=cmd.message.author.id, id_server=cmd.guild.id if cmd.guild is not None else None)

                if book_sought:
                    book_item = EwItem(id_item=book_sought.get('id_item'))
                    id_book = book_item.item_props.get("id_book")
                    book = EwBook(id_book=id_book)
                    sale = EwBookSale(id_book=id_book, member=cmd.message.author)

                    if sale.bought == 1:
                        if sale.rating == 0:
                            book.rates += 1
                        sale.rating = rating
                        sale.persist()
                        try:
                            conn_info = bknd_core.databaseConnect()
                            conn = conn_info.get('conn')
                            cursor = conn.cursor()

                            cursor.execute((
                                "SELECT {} FROM book_sales WHERE {} = %s AND {} = %s AND {} != 0".format(
                                    ewcfg.col_rating,
                                    ewcfg.col_id_server,
                                    ewcfg.col_id_user,
                                    ewcfg.col_rating,
                                )
                            ), (
                                cmd.guild.id,
                                cmd.message.author.id,
                            ))

                            data = cursor.fetchall()
                            ratings = []
                            total_rating = 0

                            if data != None:
                                for row in data:
                                    ratings.append(row)
                                    total_rating += row[0]

                        finally:
                            # Clean up the database handles.
                            cursor.close()
                            bknd_core.databaseClose(conn_info)

                        book.rating = str(total_rating / len(ratings))[:4]

                        # zine is excluded from normal browsing
                        if book.book_state == 1:
                            if book.rates >= 10 and float(book.rating) <= 2.0:
                                book.book_state = 2
                            elif book.rates >= 4 and float(book.rating) <= 1.5:
                                book.book_state = 2

                        # zine is included back into normal browsing
                        elif book.book_state == 2:
                            if float(book.rating) > 2.0 and book.rates > 10:
                                book.book_state = 1
                            elif float(book.rating) > 1.5 and book.rates > 5:
                                book.book_state = 1

                        book.persist()

                        response = "{}, you carve a {} into the back of the zine in order to indicate how many fucks you give about it.".format(ewcfg.rating_flavor[rating], rating)

                    else:
                        response = "You've never bought this book."

                else:
                    response = "You don't have that zine on you."
        else:
            response = "How many fucks do you want to give the zine? (1-5)"

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def set_length(cmd):
    user_data = EwUser(member=cmd.message.author)

    poi = poi_static.id_to_poi.get(user_data.poi)

    if not poi.write_manuscript:
        response = "You'd love to work on your zine, however your current location doesn't strike you as a particularly good place to write. Try heading over the the Cafe, the Comic Shop, or one of the colleges (NLACU/NMS)."

    elif user_data.hunger >= user_data.get_hunger_max() and user_data.life_state != ewcfg.life_state_corpse:
        response = "You are just too hungry to alter the length of your masterpiece!"

    elif user_data.manuscript == -1:
        response = "You have yet to create a manuscript. Try !createmanuscript"

    elif len(cmd.tokens) == 1:
        response = "Specify how many pages you want it to be ({} and {} pages).".format(ewcfg.minimum_pages, ewcfg.maximum_pages)

    else:
        length = cmd.tokens[1]

        if not length.isdigit():
            response = "Your manuscript can be between {} and {} pages".format(ewcfg.minimum_pages, ewcfg.maximum_pages)

        else:
            book = EwBook(member=cmd.message.author, book_state=0)
            length = int(length)

            if book.pages == length:
                response = "Your manuscript is already {} pages long.".format(length)

            elif length > ewcfg.maximum_pages or length < ewcfg.minimum_pages:
                response = "Your manuscript can be between {} and {} pages".format(ewcfg.minimum_pages, ewcfg.maximum_pages)

            else:
                pages_with_content = []

                for page in book.book_pages.keys():
                    if book.book_pages.get(page) is not None:
                        if page > length:
                            pages_with_content.append(page)

                accepted = True

                if len(pages_with_content) != 0:
                    accepted = False
                    page_list = ewutils.formatNiceList(pages_with_content)
                    response = "There is writing on these pages: {}. If you change the number of pages to {}, you will cut these pages out. Will you still do it? **!accept** or **!refuse**".format(page_list, length)

                    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))

                    try:
                        message = await cmd.client.wait_for('message', timeout=20, check=lambda message: message.author == cmd.message.author and
                                                                                                         message.content.lower() in [ewcfg.cmd_accept, ewcfg.cmd_refuse])

                        if message != None:
                            if message.content.lower() == ewcfg.cmd_accept:
                                accepted = True
                            if message.content.lower() == ewcfg.cmd_refuse:
                                accepted = False

                    except:
                        accepted = False

                if not accepted:
                    response = "The pages remain unchanged."

                else:
                    if length > book.pages:
                        response = "You haphazardly slap on a few extra pages at the end of your manuscript so you can write more bullshit."

                    else:
                        response = "You violently tear some pages out of your manuscript."

                    book.pages = length

                    if len(pages_with_content) != 0:
                        for page in pages_with_content:
                            del book.book_pages[page]

                    book.persist()

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def take_down_zine(cmd):
    if len(cmd.tokens) < 2:
        response = "Specify a zine you want to delete."

    else:
        book = cmd.tokens[1]
        author = cmd.message.author

        if book.isdigit():
            book = int(book)

        if not author.guild_permissions.administrator:
            admin = False

        else:
            admin = True

        if int_is_zine(book, cmd.guild.id):
            book = EwBook(id_book=book)

            if (not admin and book.id_user == cmd.message.author.id) and book.book_state > 0:
                book.book_state = -1
                book.persist()
                response = "{} by {} can no longer be bought. You can undo this at any time (!untakedown {}).".format(book.title, book.author, book.id_book)

            elif admin and book.book_state > 0:
                book.book_state = -2
                book.persist()
                response = "{} by {} can no longer be bought. You can undo this at any time (!untakedown {}).".format(book.title, book.author, book.id_book)

            else:
                response = "You don't have permission to delete that zine!"

        else:
            response = "Invalid Zine ID."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def untake_down_zine(cmd):
    if len(cmd.tokens) < 2:
        response = "Specify a zine you want to undelete."

    else:
        book = cmd.tokens[1]
        author = cmd.message.author

        if book.isdigit():
            book = int(book)

        if not author.guild_permissions.administrator:
            admin = False

        else:
            admin = True

        if int_is_zine(id_book=book, id_server=cmd.guild.id, negative=True):
            book = EwBook(id_book=book)

            if book.book_state >= 0:
                response = "That zine hasn't been deleted."

            elif not admin and book.book_state == -1:
                book.book_state = 1
                book.persist()
                response = "{} by {} can be bought once more.".format(book.title, book.author)

            elif admin and book.book_state == -2:
                book.book_state = 1
                book.persist()
                response = "{} by {} can be bought once more.".format(book.title, book.author)

            else:
                response = "You don't have permission to undelete that zine!"

        else:
            response = "Invalid Zine ID."

    await fe_utils.send_message(cmd.client, cmd.message.channel, fe_utils.formatMessage(cmd.message.author, response))


async def null_cmd(cmd):
    return
