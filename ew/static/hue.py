from . import cfg as ewcfg

from ..model.slimeoid import EwHue

# All color attributes in the game.
hue_list = [
    EwHue(
        id_hue=ewcfg.hue_id_white,
        alias=[
            "whitedye",
            "poketubers"
        ],
        str_saturate="It begins to glow a ghostly white!",
        str_name="white",
        str_desc="Its pale white body and slight luminescence give it a supernatural vibe.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_yellow,
        alias=[
            "yellowdye",
            "pulpgourds"
        ],
        str_saturate="It begins to shine a bright yellow!",
        str_name="yellow",
        str_desc="Its bright yellow hue is delightfully radiant.",
        effectiveness={
            ewcfg.hue_id_orange: ewcfg.hue_analogous,
            ewcfg.hue_id_lime: ewcfg.hue_analogous,
            ewcfg.hue_id_negative: ewcfg.hue_analogous,
            ewcfg.hue_id_purple: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_cobalt: ewcfg.hue_special_complementary,
            ewcfg.hue_id_blue: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },

    ),
    EwHue(
        id_hue=ewcfg.hue_id_orange,
        alias=[
            "orangedye",
            "sourpotatoes"
        ],
        str_saturate="It turns a warm orange!",
        str_name="orange",
        str_desc="Its warm orange hue makes you want to cuddle up beside it with a nice book.",
        effectiveness={
            ewcfg.hue_id_red: ewcfg.hue_analogous,
            ewcfg.hue_id_yellow: ewcfg.hue_analogous,
            ewcfg.hue_id_blue: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_cyan: ewcfg.hue_special_complementary,
            ewcfg.hue_id_cobalt: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_red,
        alias=[
            "reddye",
            "blood",
            "cabbage"
        ],
        str_saturate="It darkens a deep shade of crimson red!",
        str_name="red",
        str_desc="Its deep burgundy hue reminds you of a rare steak’s leaked myoglobin.",
        effectiveness={
            ewcfg.hue_id_pink: ewcfg.hue_analogous,
            ewcfg.hue_id_orange: ewcfg.hue_analogous,
            ewcfg.hue_id_cobalt: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_teal: ewcfg.hue_special_complementary,
            ewcfg.hue_id_cyan: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },

    ),
    EwHue(
        id_hue=ewcfg.hue_id_magenta,
        alias=[
            "magentadye",
            "joybeans"
        ],
        str_saturate="It turns a vivid magenta!",
        str_name="magenta",
        str_desc="Its vivid magenta hue fills you with energy and excitement every time you see it.",
        effectiveness={
            ewcfg.hue_id_pink: ewcfg.hue_analogous,
            ewcfg.hue_id_purple: ewcfg.hue_analogous,
            ewcfg.hue_id_teal: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_lime: ewcfg.hue_special_complementary,
            ewcfg.hue_id_green: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_purple,
        alias=[
            "purpledye",
            "purplekilliflower",
            "killer"
        ],
        str_saturate="It turns a dark purple!",
        str_name="purple",
        str_desc="Its dark purple hue gives it a brooding, edgy appearance. It will huff and groan when given orders, like a teenager rebelling against his mom in the most flaccid way possible.",
        effectiveness={
            ewcfg.hue_id_blue: ewcfg.hue_analogous,
            ewcfg.hue_id_magenta: ewcfg.hue_analogous,
            ewcfg.hue_id_green: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_yellow: ewcfg.hue_special_complementary,
            ewcfg.hue_id_lime: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_blue,
        alias=[
            "bluedye",
            "razornuts"
        ],
        str_saturate="It turns a deep blue!",
        str_name="blue",
        str_desc="Its deep blue hue reminds you of those “ocean” things you’ve heard so much of in the movies and video games that have washed ashore the coast of the Slime Sea.",
        effectiveness={
            ewcfg.hue_id_cobalt: ewcfg.hue_analogous,
            ewcfg.hue_id_purple: ewcfg.hue_analogous,
            ewcfg.hue_id_lime: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_orange: ewcfg.hue_special_complementary,
            ewcfg.hue_id_yellow: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_green,
        alias=[
            "greendye",
            "pawpaw",
            "juvie"
        ],
        str_saturate="It turns a shade of green that barely distinguishes itself from a Slimeoid’s standard hue.",
        str_name="green",
        str_desc="Its unimpressive green hue does nothing to separate itself from the swathes of the undyed Slimeoids of the working class.",
        effectiveness={
            ewcfg.hue_id_lime: ewcfg.hue_analogous,
            ewcfg.hue_id_teal: ewcfg.hue_analogous,
            ewcfg.hue_id_pink: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_purple: ewcfg.hue_special_complementary,
            ewcfg.hue_id_magenta: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_teal,
        alias=[
            "tealdye",
            "sludgeberries"
        ],
        str_saturate="It turns a deep teal! It looks so purdy now!",
        str_name="teal",
        str_desc="Its caliginous teal hue gives you a sudden lust for prosecuting criminals in the legal system, before coming to your senses and realizing there is no legal system here.",
        effectiveness={
            ewcfg.hue_id_green: ewcfg.hue_analogous,
            ewcfg.hue_id_cyan: ewcfg.hue_analogous,
            ewcfg.hue_id_red: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_magenta: ewcfg.hue_special_complementary,
            ewcfg.hue_id_pink: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_rainbow,
        alias=[
            "rainbowdye",
            "suganmanuts"
        ],
        str_saturate="It turns a fantastic shade of... well, everything!!",
        str_name="***Rainbow***",
        str_desc="Its ***Rainbow*** hue dazzles and amazes you. It comprises the whole color spectrum in a crude, Photoshop-tier gradient. It’s so obnoxious… and yet, decadent!",
        effectiveness={
            ewcfg.hue_id_negative: ewcfg.hue_full_complementary
        },        
    ),
    EwHue(
        id_hue=ewcfg.hue_id_pink,
        alias=[
            "pinkdye",
            "pinkrowddishes"
        ],
        str_saturate="It turns a vibrant shade of pink!",
        str_name="pink",
        str_desc="Its vibrant pink hue imbues the Slimeoid with an uncontrollable lust for destruction. You will often see it flailing about happily, before knocking down a mailbox or kicking some adult in the shin.",
        effectiveness={
            ewcfg.hue_id_magenta: ewcfg.hue_analogous,
            ewcfg.hue_id_red: ewcfg.hue_analogous,
            ewcfg.hue_id_cyan: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_green: ewcfg.hue_special_complementary,
            ewcfg.hue_id_teal: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_grey,
        alias=[
            "greydye",
            "dankwheat"
        ],
        str_saturate="It turns a dull, somber grey.",
        str_name="grey",
        str_desc="Its dull grey hue depresses you, lulling you into inaction and complacency. ",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_cobalt,
        alias=[
            "cobaltdye",
            "brightshade"
        ],
        str_saturate="It turns a shimmering cobalt!",
        str_name="cobalt",
        str_desc="Its shimmering cobalt hue can reflect images if properly polished.",
        effectiveness={
            ewcfg.hue_id_cyan: ewcfg.hue_analogous,
            ewcfg.hue_id_blue: ewcfg.hue_analogous,
            ewcfg.hue_id_yellow: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_red: ewcfg.hue_special_complementary,
            ewcfg.hue_id_orange: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_black,
        alias=[
            "blackdye",
            "blacklimes"
        ],
        str_saturate="It turns pitch black!",
        str_name="black",
        str_desc="Its pitch black, nearly vantablack hue absorbs all the light around it, making this Slimeoid appear as though a hole was ripped right out of reality.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_lime,
        alias=[
            "limedye",
            "phosphorpoppies"
        ],
        str_saturate="It turns a heavily saturated lime!",
        str_name="lime",
        str_desc="Its heavily saturated lime hue assaults your eyes in a way not unlike the Slime Sea. That is to say, painfully.",
        effectiveness={
            ewcfg.hue_id_yellow: ewcfg.hue_analogous,
            ewcfg.hue_id_green: ewcfg.hue_analogous,
            ewcfg.hue_id_magenta: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_blue: ewcfg.hue_special_complementary,
            ewcfg.hue_id_purple: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_cyan,
        alias=[
            "cyandye",
            "direapples"
        ],
        str_saturate="It turns a light cyan!",
        str_name="cyan",
        str_desc="Its light cyan hue imbues it with a slightly anxious demeanor. It is sure to avoid sewer manholes when walking down the street.",
        effectiveness={
            ewcfg.hue_id_teal: ewcfg.hue_analogous,
            ewcfg.hue_id_cobalt: ewcfg.hue_analogous,
            ewcfg.hue_id_orange: ewcfg.hue_atk_complementary,
            ewcfg.hue_id_pink: ewcfg.hue_special_complementary,
            ewcfg.hue_id_red: ewcfg.hue_full_complementary,
            ewcfg.hue_id_rainbow: ewcfg.hue_full_complementary
        },
    ),
    EwHue(
        id_hue=ewcfg.hue_id_brown,
        alias=[
            "browndye",
        ],
        str_saturate="It turns an earthly brown!",
        str_name="brown",
        str_desc="Its earthly brown hue imbues it with a humble, down-to-earth personality.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_copper,
        alias=[
            "copperpaint",
        ],
        str_saturate="It was given a coating of bright copper!",
        str_name="copper",
        str_desc="It seems to feel good about its copper coating.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_chrome,
        alias=[
            "chromepaint",
        ],
        str_saturate="It was given a coating of silvery chrome!",
        str_name="chrome",
        str_desc="It's content with its chrome coating.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_gold,
        alias=[
            "goldpaint",
        ],
        str_saturate="It was given a coating of dazzling gold!",
        str_name="gold",
        str_desc="It prides itself on its shiny golden coating.",
        is_neutral=True,
    ),
    EwHue(
        id_hue=ewcfg.hue_id_negative,
        alias=[
            "negaslimeoid",
            "negativedye",
            "||negativedye||",
        ],
        str_saturate="It turns a seemingly negative hue!",
        str_name="negative",
        str_desc="It's a photonegative stain on the landscape.",
        effectiveness={
            ewcfg.hue_id_rainbow: ewcfg.hue_analogous,
            ewcfg.hue_id_yellow: ewcfg.hue_full_complementary, # "pissbois die"
        },
    ),
]

# A map of id_hue to EwHue objects.
hue_map = {}

# A list of hue names
hue_names = []

# Populate hue map, including all aliases.
for hue in hue_list:
    hue_map[hue.id_hue] = hue
    hue_names.append(hue.id_hue)

    for alias in hue.alias:
        hue_map[alias] = hue  # A map of id_hue to EwHue objects.
