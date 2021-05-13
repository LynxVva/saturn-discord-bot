import discord

# Colours, emotes, and useful stuff

# MAIN = 0xF6009B
MAIN = discord.Colour.default()
RED = discord.Colour.red()
GREEN = discord.Colour.green()
DIFF_GREEN = 0x677c1e
DIFF_RED = 0xFF0000
GOLD = discord.Colour.gold()
BLUE = 0x24ACF2
SLIGHTLY_LIGHTER_BLUE = 0x0091FF
SLIGHTLY_DARKER_BLUE = 0x0087D2
DARKER_BLUE = 0x11618B

# Some default emotes
# not too shabby
BLANK = '\uFEFF'

ERROR = '<:error:822122069139521567>'
CHECK = '<:check:822122069176221726>'
WARNING = '<:warn:818199916312002631>'
INFO = '<:info:821565551939420170>'
PREFIX = "s!"
LOCK = ':lock:'
UNLOCK = ':unlock:'
WEAK_SIGNAL = ':red_circle:'
MEDIUM_SIGNAL = ':yellow_circle:'
STRONG_SIGNAL = ':green_circle:'
NO_REPEAT = '⏭'
REPEAT_ONE = '🔂'
REPEAT_ALL = '🔁'

# Pagination emotes
# PAG_FRONT = '<:pagfront:824379359867306078>'
# PAG_PREVIOUS = '<:pagleft:824379360324747364>'
# PAG_NEXT = '<:pagright:824379360302596196>'
# PAG_BACK = '<:pagback:824379493732974622>'
# PAG_STOP = '<:pagstop:824379359564529804>'
# PAG_NUMBERS = '<:pagnumbers:824379360194068520>'
# PAG_INFO = '<:paginfo:824379360059850753>'
PAG_FRONT = '⏪'
PAG_PREVIOUS = '◀️'
PAG_NEXT = '▶️'
PAG_BACK = '⏩'
PAG_STOP = '⏹️'
PAG_NUMBERS = '🔢'
PAG_INFO = 'ℹ️'

MUTE = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/' \
       'speaker-with-cancellation-stroke_1f507.png'
UNMUTE = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/' \
         'speaker-with-three-sound-waves_1f50a.png'
WARN = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/' \
       'warning-sign_26a0.png'
NO_ENTRY = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/' \
           'no-entry_26d4.png'
UNBAN = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/mozilla/36/' \
        'door_1f6aa.png'
NOTE = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/" \
       "thumbs/120/mozilla/36/memo_1f4dd.png"
INFO_URL = 'https://cdn.discordapp.com/emojis/821565551939420170.png?v=1'
# weird emotes and stuff yay?

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s(" \
            r")<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
SPOTIFY_URL_REGEX = r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*track[/:]*[A-Za-z0-9?=]+"
SPOTIFY_PLAYLIST_URL_REGEX = r"[\bhttps://open.\b]*spotify[\b.com\b]*[/:]*playlist[/:]*[A-Za-z0-9?=]+"
YOUTUBE_URL_REGEX = r"(?:https?:\/\/)?(?:youtu\.be\/|(?:www\.|m\.)?youtube\.com\/" \
                    r"(?:watch|v|embed)(?:\.php)?(?:\?.*v=|\/))([a-zA-Z0-9\_-]+)"
INVITE_URL_REGEX = r"discord(?:\.com|app\.com|\.gg)/(?:invite/)?([a-zA-Z0-9\-]{2,32})"
MESSAGE_LINK_REGEX = r"discord.com/channels/\d{18}/\d{18}/\d{18}"
# i barely understand these regexes

ADMIN_INVITE = "https://discord.com/oauth2/authorize?client_id=799328036662935572&permissions=8&redirect_uri" \
               "=https://127.0.0.1:5000/login&scope=bot"
NORMAL_INVITE = "https://discord.com/oauth2/authorize?client_id=799328036662935572&permissions=536145143&redirect_uri" \
                "=https://127.0.0.1:5000/login&scope=bot"

DUEL_HEAL_MESSAGES = [
    "{} drinks a chug jug!",
    "{} washes their hands!",
    "{} eats a chicken nugget!",
    "{} pulls out a first aid kit!",
    "{} drinks an exploding toilet!",
    "{} prays to the dueling gods!",
    "{} reveals toilet paper and gets fan support!",
    "{} found an exploit in the code and exploited it!",
    "{} freezes time!",
    "{} vibes to music!",
    "{} gets a gift from the gods!",
    "{} heals!",
    "{} eats a golden apple!",
    "{} ate a hp apple to keep the doctor away!",
]
DUEL_ATTACK_MESSAGES = [
    "{} does an impressive combo on {}!",
    '{} says "NO APPLES FOR YOU!" and steals {}\'s apples!',
    "{} throws an exploding toilet at {}!",
    "{} steals all of {}'s lunch money and throws them into the sun!",
    "{} absolutely DESTROYS {}!",
    "{} forces {} to look at Synchronous' code!",
    "{} pulls out a machine gun and BLIZZASTED {} into shreds!",
    "{} snipes {} from 2 MILES AWAY!",
    "{} breathes COVID-19 into {}'s face!",
    "{} clicks a suspicious link sent from {}!",
    "{} thought {} was the imposter!",
    "{} was the imposter and stabbed {}!",
    "{} throws around {} like a small child!",
    "{} karate-chopped {} and broke all 206 bones of his body!",
    "{} nukes {}!",
    "{} went a bit too far and dismembered {}!",
    "{} punched {} so hard he got knocked into the next year!",
    "{} slammed {} into Davy Jones' locker!",
    "{} got a jetpack and flew it straight over {}'s head!",
    "{} did some weird stuff and {} turned into a pile of ashes!",
    "{} drove a car straight into {}!",
    "{} throws {} into the void!",
    "{} gives {} multiple paper cuts! Yeouch!",
    "{} ejects {} into space!",
    "{} boiled up a huge pot of water and poured it onto {}!",
    "{} did some crap from Harry Potter and teleported {} to Pluto!",
    "{} slapped {} with a big stinky fish!",
    "{} forced {} to watch YouTube rewind!",
    "{1} accidentally walked off a cliff!",
    "{} took a leaf out of Mad-Eye Moody's book and turned {} into a ferret!",
    "{} pulled out a stick and whipped it at {}!",
    "{} drove a Jeep Wrangler over {} many times!",
    "{} pulled out a baseball bat and sent {}'s head flying!",
    "{} rickrolled {}!",
    "{} spammed {}.exe, and it stopped responding!",
    "{} teleported {} to Jupiter!",
    "{} called upon the gods, and they obliterated {}!",
    "{} forced {} to spam in front of the automod!",
    "{} sliced {} open with a katana and poured salt over his wound! Ouch!",
    "{} hacked {} and downloaded a virus!",
    "{} tested {} on RegExs!",
    "{} shot {} in the head, point blank!",
    "{} teleported {} to the sun!",
    "{} squashed {} like a bug!",
    "{} shoved {} into a 50 kilometre hole!",
]
