import os
from itertools import cycle
from pathlib import Path

import motor.motor_asyncio
import mystbin
from discord.errors import Forbidden
from discord.ext import tasks
from dotenv import load_dotenv

from assets import *
from assets.cmd import get_permissions, get_prefix
from assets.time import utc

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
	"%(asctime)s | %(levelname)s | %(module)s | %(message)s")

handler = logging.FileHandler(
	filename='saturn.log', encoding='utf-8', mode='w')
handler.setFormatter(formatter)

logger.addHandler(handler)

intents = discord.Intents.all()
mentions = discord.AllowedMentions.all()
mentions.everyone = False


# noinspection PyMethodMayBeStatic
class Saturn(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=get_prefix,
			description="A multipurpose discord bot made in python.",
			intents=intents,
			case_insensitive=True,
			owner_ids=[int(owner_id)
					   for owner_id in os.environ.get("OWNERIDS").split(" ")],
			allowed_mentions=mentions
		)
		self.ready = False
		self.__name__ = 'Saturn'
		self.src = 'https://github.com/SynchronousDev/saturn-discord-bot'

		self.path = str(Path(__file__).parents[0])
		self.__version__ = '1.1.0'

		self.mongo_connection_url = os.environ.get("MONGO")
		self.TOKEN = os.environ.get("TOKEN")

		self.edit_snipes = {}
		self.snipes = {}
		self.banned_users = {}
		self.muted_users = {}
		self.message_cache = {}

		self.mongo = motor.motor_asyncio.AsyncIOMotorClient(
			str(self.mongo_connection_url))
		self.db = self.mongo[self.__name__]
		self.config = self.db["config"]
		self.mutes = self.db["mutes"]
		self.blacklists = self.db["blacklists"]
		self.tags = self.db["tags"]
		self.mod = self.db["mod"]
		self.bans = self.db["bans"]
		self.starboard = self.db["starboard"]

		self.paste = mystbin.Client()

		self.topgg_client = topgg.DBLClient(self, os.environ.get(
			"TOPGGTOKEN"), autopost=False)
		self.topgg_webhook = topgg.WebhookManager(
			self).dbl_webhook("/dblwebhook", os.environ.get("TOPGGAUTH"))
		self.topgg_webhook.run(5678)

	def run(self):
		print(f"Running {self.__name__}...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message)

		if ctx.command and ctx.guild:
			perms = await get_permissions(ctx, ctx.guild.me)

			if not perms['send_messages']:
				em = SaturnEmbed(
					description=f"{WARNING} Oops! I can't send messages! Please update my permissions and try again.",
					colour=GOLD) 
				return await ctx.author.send(embed=em)

			elif not perms['embed_links']:
				return await ctx.send("Hey! Please enable the `Embed Links` permission for me!")

			elif (
				(not perms['external_emojis']) or
				(not perms['attach_files']) or
				(not perms['add_reactions'])
			):
				em = SaturnEmbed(
					description=f"{WARNING} Oops! Please make sure that I have the following permissions:"
								f"```Send Messages, Embed Links, Use External Emojis, Attach Files, Add Reactions```",
					colour=GOLD)
				return await ctx.send(embed=em)

			if await self.blacklists.find_one({"_id": ctx.author.id}):
				em = SaturnEmbed(
					description=f"{CROSS} You are blacklisted from the bot.",
					colour=RED)
				await ctx.author.send(embed=em)

			elif not self.ready:
				em = SaturnEmbed(
					description=f"{WARNING} I'm not quite ready to receive commands yet!",
					colour=GOLD)
				return await ctx.send(embed=em)

		await self.invoke(ctx)

	async def on_connect(self):
		self.change_pres.start()
		self.update_topgg_guild_count.start()
		print(f"{self.__name__} connected")

	async def on_disconnect(self):
		self.change_pres.cancel()
		self.update_topgg_guild_count.cancel()
		print(f"{self.__name__} disconnected")

	# noinspection PyAttributeOutsideInit
	async def on_ready(self):
		self.default_guild = self.get_guild(793577103794634842)
		self.stdout = self.default_guild.get_channel(833871407544008704)
		self.start_time = utc()

		if not self.ready:
			self.ready = True
			for _file in os.listdir(self.path + '/cogs'):
				if _file.endswith('.py') and not _file.startswith('_'):
					print(f"Loading {_file[:-3]} cog...")
					# load all of the cogs
					self.load_extension(f"cogs.{_file[:-3]}")

			# i have jishaku here because i find it quite useful
			self.load_extension('jishaku')

			mutes, bans = [], []
			print("Initializing mute and ban cache...")
			async for _doc in self.mutes.find({}):
				mutes.append(_doc)
			for mute in mutes:
				self.muted_users[mute["_id"]] = mute
			async for _doc in self.bans.find({}):
				bans.append(_doc)
			for ban in bans:
				self.banned_users[ban["_id"]] = ban

			print(f"{self.__name__} is ready")
			em = SaturnEmbed(
				description=f"{CHECK} Connected and ready!",
				colour=GREEN)
			await self.stdout.send(embed=em)

		else:
			print(f"{self.__name__} reconnected")
			em = SaturnEmbed(
				description=f"{INFO} Reconnected!",
				colour=BLUE)
			await self.stdout.send(embed=em)

	async def on_message(self, message):
		await self.process_commands(message)

	@tasks.loop(minutes=1)
	async def update_topgg_guild_count(self):
		if self.user.id == 799328036662935572:  # this is so the beta bot doesn't post the guild count
			try:
				await self.topgg_client.post_guild_count()

			except Exception as e:
				logger.warning("Failed to post guild count to top.gg:\n{} {}".format(type(e).__name__, e))

	@tasks.loop(seconds=45)
	async def change_pres(self):
		presences = (
			f"{PREFIX}help | v{self.__version__}",
			f"{PREFIX}help | {len(self.guilds)} guilds",
			f"{PREFIX}help | {len(self.users)} users",
		)

		for i in range(3):
			await self.change_presence(
				activity=discord.Game(name=presences[i]))
			await asyncio.sleep(15)

if __name__ == '__main__':
	# Load all of the cogs and initialize the databases
	Saturn = Saturn()
	Saturn.run()  # run the bot
	# I can do this because it will not print until the event loop stops
	print("Event loop closed.")
	# all processes after this will not be run until the bot stops so oof
