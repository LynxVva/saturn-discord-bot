import os
import re
import time
from copy import deepcopy

from assets import *
from assets.cmd import get_permissions
from assets.time import convert_to_timestamp, general_convert_time, utc
from dateutil.relativedelta import relativedelta
from discord.ext import tasks

log = logging.getLogger(__name__)


async def create_export_file(bot, ctx, messages, channel):
    try:
        await _create_efile(bot, ctx, messages, channel)

    except FileNotFoundError:
        try:
            os.mkdir(f"{bot.path}/assets/txt_files")

        except FileExistsError:
            pass

        await _create_efile(bot, ctx, messages, channel)


async def _create_efile(bot, ctx, messages, channel):
    with open(f'{bot.path}/assets/txt_files/{channel.id}-export.txt', 'w', encoding='utf-8') as f:
        f.write(
            f"{len(messages)} messages exported from the #{channel} channel by {ctx.author}:\n\n")
        for message in messages:
            content = message.clean_content
            if not message.author.bot:
                f.write(f"{message.author} {convert_to_timestamp(message.created_at)} EST"
                        f" (ID - {message.author.id})\n"
                        f"{content} (Message ID - {message.id})\n\n")

            else:
                f.write(f"{message.author} {convert_to_timestamp(message.created_at)} EST"
                        f" (ID - {message.author.id})\n"
                        f"{'Embed/file sent by a bot' if not content else content}\n\n")

# noinspection SpellCheckingInspection


class Utility(commands.Cog):
    """
    The Utility module. Includes useful things, like starboards and modmail.

    Not to be confused with the Fun module.
    """

    def __init__(self, bot):
        self.bot = bot
        self.polls = {}
        self.numbers = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣',
                        '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')
        self.yes_no = ('👍', '👎')
        self.snipe_task = self.clear_snipe_cache.start()

    def cog_unload(self):
        self.snipe_task.cancel()

    @tasks.loop(seconds=10)
    async def clear_snipe_cache(self):
        current_time = utc()
        snipes = deepcopy(self.bot.snipes)

        for key, value in snipes.items():
            clear_time = value['time'] + relativedelta(seconds=600)

            if current_time >= clear_time:
                self.bot.snipes.pop(value['_id'])

    @clear_snipe_cache.before_loop
    async def before_clear_snipe_cache(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name='ynpoll',
        aliases=['ynpl', 'yesnopoll', 'yesnopl'],
        description='Create a simple yes/no poll.'
    )
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def yes_no_poll(self, ctx, channel: typing.Optional[discord.TextChannel], *, question):
        channel = channel or ctx.channel

        em = SaturnEmbed(
            title=question,
            description=":thumbsup: Yes\n\n:thumbsdown: No",
            colour=GOLD,
            timestamp=utc()
        )
        em.set_footer(text=f"Yes/no poll by {ctx.author}")
        msg = await channel.send(embed=em)
        self.polls[msg.id] = {
            "type": "ynpoll",
            "question": question,
            "choices": ("Yes", "No"),
            "channel": msg.channel.id,
            "author": ctx.author.id,
            "guild": ctx.guild.id,
        }
        for emoji in self.yes_no:
            await msg.add_reaction(emoji)

    @commands.group(
        name='poll',
        aliases=['pl', 'question'],
        description="Start a poll for others to vote on. The questions should be in double quotes.",
        invoke_without_command=True
    )
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def poll(self, ctx, channel: typing.Optional[discord.TextChannel], question, *choices):
        channel = channel or ctx.channel

        if not len(choices) or not len(question):
            em = SaturnEmbed(
                description=f"{CROSS} Please include both a question and choices. Format looks like\n"
                            f'```poll "dogs or cats?" dogs cats```',
                color=RED)
            return await ctx.send(embed=em)
        if len(choices) > 10 or len(choices) < 2:
            em = SaturnEmbed(
                description=f"{CROSS} The amount of choices provided is not within acceptable boundaries.\n"
                            f"```Number of choices must be in between 1 and 10```",
                color=RED)
            return await ctx.send(embed=em)

        em = SaturnEmbed(
            title=question,
            description='\n\n'.join(
                ["{0} {1}".format(self.numbers[num], choice.replace('"', ''))
                 for num, choice in enumerate(choices)]
            ),
            colour=BLUE,
            timestamp=utc()
        )
        em.set_footer(text=f"Poll by {ctx.author}")
        msg = await channel.send(embed=em)
        self.polls[msg.id] = {
            "type": "poll",
            "question": question,
            "choices": choices,
            "channel": msg.channel.id,
            "author": ctx.author.id,
            "guild": ctx.guild.id,
        }
        valid_emotes = self.numbers[:(len(choices))]
        for emoji in valid_emotes:
            await msg.add_reaction(emoji)

    @poll.command(name='polls')
    async def _polls(self, ctx):
        await ctx.send(self.polls)

    @poll.command(
        name='show',
        aliases=['results', 'res', 'result', 'sh'],
        description="Show the results of a poll."
    )
    async def show_poll_results(self, ctx, poll_id):
        # discord message url like https://discord.com/channels/num/num/num
        if re.search(MESSAGE_LINK_REGEX, str(poll_id)):
            items = poll_id.split('/')[4:]
            guild_id, channel_id, message_id = ctx.guild.id, int(
                items[1]), int(items[2])
            try:
                if await self.bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id) and self.polls[message_id]:
                    return await self.show_poll(ctx, message_id, channel_id)
            except (KeyError, discord.NotFound):
                pass
            em = SaturnEmbed(
                description=f"{CROSS} No poll with an id of `{message_id}` was found.",
                color=RED)
            return await ctx.send(embed=em)
        else:
            try:
                if self.polls[int(poll_id)]:
                    poll = self.polls[int(poll_id)]
                    if poll["guild"] == ctx.guild.id:
                        return await self.show_poll(ctx, int(poll_id), poll["channel"])
            except (ValueError, KeyError):
                em = SaturnEmbed(
                    description=f"{CROSS} No poll with an id of `{poll_id}` was found.",
                    color=RED)
                return await ctx.send(embed=em)
            em = SaturnEmbed(
                description=f"{CROSS} No poll with an id of `{poll_id}` was found.",
                color=RED)
            await ctx.send(embed=em)

    async def get_poll_results(self, percent):
        WHITE_SQUARE = "<:white_rectangle_vote:850463534638170172>"
        BLACK_SQUARE = "<:black_rectangle_vote:850463519538544740>"

        return (BLACK_SQUARE * percent) + (WHITE_SQUARE * (10 - percent))

    async def show_poll(self, ctx, message_id, channel_id):
        message = await self.bot.get_guild(ctx.guild.id).get_channel(channel_id).fetch_message(message_id)
        _poll = self.polls[message.id]
        reactions = []

        for reaction in message.reactions:
            if _poll["type"] == "poll":
                if str(reaction.emoji) in self.numbers:
                    reactions.append(reaction)

            elif _poll["type"] == "ynpoll":
                if str(reaction.emoji) in self.yes_no:
                    reactions.append(reaction)

        em = SaturnEmbed(
            title=_poll["question"],
            colour=MAIN,
            timestamp=message.created_at
        )
        total_votes = 0
        for reaction in reactions:
            for user in await reaction.users().flatten():
                if not user.bot:
                    total_votes += 1

        for num, choice in enumerate(_poll["choices"]):
            count = len(
                [user for user in await reactions[num].users().flatten() if not user.bot])

            try:
                tens_percentage = round((count / total_votes) * 10)
                total_percentage = round(count / total_votes * 100)

            except ZeroDivisionError:
                tens_percentage, total_percentage = 0, 0

            em.add_field(
                name=choice.replace('"', ''),
                value="{} {} votes (**{}%**)".format(await self.get_poll_results(tens_percentage), count, total_percentage)
            )

        em.set_footer(text="Results of the poll by {}".format(
            ctx.guild.get_member(_poll["author"])))
        await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.bot.ready:
            try:
                if self.polls[payload.message_id]:
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

                    for reaction in message.reactions:
                        if (not payload.member.bot and
                            payload.member in await reaction.users().flatten() and
                                reaction.emoji != payload.emoji.name):

                            await message.remove_reaction(reaction.emoji, payload.member)

                        break

            except KeyError:
                pass

    @commands.command(
        name='uptime',
        aliases=['onlinesince', 'onlinetime'],
        description='Check the bot\'s uptime.'
    )
    async def view_uptime(self, ctx):
        time = (utc() - self.bot.start_time).total_seconds()
        formatted_time = str(general_convert_time(time))

        await ctx.reply(
            embed=SaturnEmbed(
                description=f"{self.bot.__name__} has been online for **{formatted_time}**",
                colour=MAIN
            )
        )

    @commands.command(
        name='ping',
        aliases=['latency'],
        description='Used to check if the bot is alive')
    async def ping(self, ctx):
        ws_latency = float(f"{self.bot.latency * 1000:.2f}")
        if ws_latency < 60:
            colour = GREEN

        elif ws_latency < 101:
            colour = GOLD

        else:
            colour = RED

        rt_start = epoch()
        msg = await ctx.send("Pinging...")
        rt_end = epoch()

        rt_latency = rt_end - rt_start

        db_start = epoch()
        data = self.bot.config.find_one({"_id": ctx.guild.id})
        db_end = epoch()

        db_latency = db_end - db_start

        em = SaturnEmbed(
            title="Pong!",
            description=f"**Websocket -** `{ws_latency}ms`\n"
                        f"**Round Trip -** `{rt_latency * 1000:,.2f}ms`\n"
                        f"**Database -** `{db_latency * 1000:,.2f}ms`",
            colour=colour)

        await msg.edit(content=None, embed=em)

    # noinspection SpellCheckingInspection
    @commands.command(
        name="version",
        aliases=['vers'],
        description="Show the bot's current version.")
    async def _vers(self, ctx):
        await ctx.reply(
            embed=SaturnEmbed(
                description=f"{self.bot.__name__} is currently running on version **{self.bot.__version__}**",
                colour=MAIN
            )
        )

    @commands.command(
        name="membercount",
        aliases=['members', 'numberofmembers'],
        description="Show the guild's member count.")
    async def member_count(self, ctx):
        async with ctx.channel.typing():
            bots = len([m for m in ctx.guild.members if m.bot])
            bots_with_perms = len(
                [m for m in ctx.guild.members if m.bot and m.guild_permissions.kick_members])
            users = len(ctx.guild.members) - bots
            mods = len(
                [m for m in ctx.guild.members if m.guild_permissions.kick_members]) - bots_with_perms

            em = SaturnEmbed(
                colour=MAIN,
                timestamp=utc()
            )
            em.description = f"""
            **Members** - {users}
            **Bots** - {bots}
            **Moderators** - {mods}
            """
            em.set_author(
                name=f'Member Statistics for {ctx.guild}', icon_url=ctx.guild.icon_url)
            await ctx.send(embed=em)

    @commands.command(
        name="userinfo",
        aliases=["memberinfo", "ui", "mi"],
        description='Information about a user')
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def user_info(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User]]):
        member = member or ctx.author

        embed = SaturnEmbed(
            description=member.mention,
            colour=member.colour if isinstance(
                member, discord.Member) else MAIN,
            timestamp=utc())

        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(icon_url=member.avatar_url, name=member)

        created_delta = (utc() - member.created_at.replace(
            tzinfo=datetime.timezone.utc)).total_seconds()

        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Joined Discord", value=general_convert_time(
            created_delta) + ' ago', inline=True)
        if isinstance(member, discord.Member):
            join_delta = (
                utc() - member.joined_at.replace(tzinfo=datetime.timezone.utc)).total_seconds()
            member_roles = member.roles[1:]
            roles = " ".join(reversed([f"<@&{r.id}>" for r in member_roles]))

            embed.add_field(name=f"Joined {ctx.guild}", value=general_convert_time(
                join_delta) + ' ago', inline=True)
            if roles:
                embed.add_field(
                    name="Roles ({})".format(int(len(member_roles))),
                    value=roles
                )

            member_perms = await get_permissions(ctx, member)
            display_perms = []

            for permission, value in member_perms.items():
                if value:
                    display_perms.append(
                        ' '.join(
                            [item.title()
                             for item in str(permission).split('_')]
                        )
                    )

                continue

            embed.add_field(
                name="Permissions ({})".format(int(len(display_perms))),
                value=", ".join(display_perms)
            )

        await ctx.send(embed=embed)

    @commands.command(
        name='serverinfo',
        aliases=['si', 'gi', 'guildinfo']
    )
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def server_info(self, ctx):
        guild = ctx.guild
        em = SaturnEmbed(
            colour=MAIN,
        )
        em.set_author(name=guild.name, icon_url=guild.icon_url)
        em.set_thumbnail(url=guild.icon_url)

        if guild.banner:
            em.set_image(url=guild.banner_url)

        em.add_field(name="Server ID", value=guild.id, inline=True)
        em.add_field(name="Server Owner",
                     value=guild.owner.mention, inline=True)
        if guild.description:
            em.add_field(name="Description", value=guild.description)

        online = len([member for member in guild.members if not (
            member.status == discord.Status.offline)])
        offline = len(guild.members) - online

        em.add_field(name="Member Count ({})".format(len(guild.members)), value="{2} {0} online\n{3} {1} offline".format(
            online, offline, ONLINE, OFFLINE))

        text_channels = len([channel for channel in guild.channels if isinstance(
            channel, discord.TextChannel)])

        voice_channels = len([channel for channel in guild.channels if isinstance(
            channel, discord.VoiceChannel)])

        stage_channels = len([channel for channel in guild.channels if isinstance(
            channel, discord.StageChannel)])

        em.add_field(name="Channel Count ({})".format(text_channels + voice_channels + stage_channels),
                     value="{3} {0} text \n{4} {1} voice\n{5} {2} stage".format(
            text_channels, voice_channels, stage_channels, TEXT_CHANNEL, VOICE_CHANNEL, STAGE_CHANNEL))
        em.add_field(name="Role Count", value=len(guild.roles), inline=True)
        em.add_field(name="Emoji Count", value=len(guild.emojis), inline=True)

        em.add_field(name="Ban Count", value="{} {}".format(
            BAN_HAMMER, len(await guild.bans())))

        boosts = guild.premium_subscription_count
        if boosts < 2:
            boost_level = 0

        elif 15 > boosts >= 2:
            boost_level = 1

        elif 30 > boosts >= 15:
            boost_level = 2

        else:
            boost_level = 3

        em.add_field(name="Boost Count",
                     value="{} {} (Level {} Perks)".format(BOOST, boosts, boost_level))
        em.add_field(name="Server Perks", value="\n".join(
            [str(feature.split('_')).title()[2:-2] for feature in guild.features]))

        await ctx.send(embed=em)

    # TODO: add reminder command yay

    @commands.command(
        name='source',
        aliases=['code', 'src'],
        description='Show the source link to Saturn\'s code.'
    )
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def view_bot_source(self, ctx):
        em = SaturnEmbed(
            description=f'[Click here]({self.bot.src}) to view the source code.',
            colour=MAIN)
        em.set_author(
            name='BSD 3-Clause License',
            url="https://github.com/SynchronousDev/saturn-discord-bot/blob/master/LICENSE",
            icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=em)

    @commands.command(
        name='roles',
        description='View your roles.'
    )
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def view_roles(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User]]):
        member = member or ctx.author

        roles = " ".join(reversed([f"<@&{r.id}>" for r in member.roles[1:]]))
        em = SaturnEmbed(
            description=str(
                roles if roles else f"{member.mention} has no roles!"),
            colour=member.colour,
            timestamp=utc()
        )
        em.set_image(url=member.avatar_url)
        em.set_author(icon_url=member.avatar_url,
                      name=f"{member.name}'s roles")
        await ctx.send(embed=em)

    @commands.command(
        name='export',
        aliases=['channelcontents', 'export-contents',
                 'exportcontents', 'downloadchannelcontents', 'dcc'],
        description="Export a channel's content into a .txt file."
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def export_channel_contents(self, ctx, channel: typing.Optional[discord.TextChannel],
                                      limit: typing.Optional[int] = 100):
        channel = channel or ctx.channel

        em = SaturnEmbed(
            description=f"{INFO} This might take a while, please wait...",
            colour=BLUE)
        msg = await ctx.send(embed=em)
        async with channel.typing():
            messages = await channel.history(limit=limit, oldest_first=True).flatten()

            try:
                await create_export_file(self.bot, ctx, messages, channel)

            except FileNotFoundError:
                await asyncio.sleep(0.5)
                await create_export_file(self.bot, ctx, messages, channel)

            file = discord.File(
                f'{self.bot.path}/assets/txt_files/{channel.id}-export.txt')

        try:
            await msg.delete()

        except (discord.NotFound, discord.Forbidden):
            pass
        
        em = SaturnEmbed(
            title='Channel Export',
            description=f"Message contents of <#{channel.id}>\n"
                        f"Download the attached .txt file to view the contents.",
            colour=MAIN,
            timestamp=utc()
        )
        em.set_thumbnail(url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/"
                             "thumbs/120/mozilla/36/memo_1f4dd.png")
        await ctx.send(embed=em)
        await asyncio.sleep(0.5)
        await ctx.send(file=file)

    @commands.command(
        name='avatar',
        aliases=['pfp', 'userpfp', 'av'],
        description="Shows a user's avatar")
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def get_avatar(self, ctx, member: typing.Optional[discord.Member]):
        if member is None:
            member = ctx.author

        avatar = SaturnEmbed(
            color=member.color)
        avatar.set_image(url=member.avatar_url)
        await ctx.send(embed=avatar)

    @commands.command(
        name='snipe',
        aliases=['snp', 'snip'],
        description='Retrieve deleted messages.'
    )
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def get_snipes(self, ctx, member: typing.Optional[discord.Member],
                         channel: typing.Optional[discord.TextChannel]):
        em = SaturnEmbed(
            colour=BLUE,
        )
        em.description = f"{INFO} Couldn't find any deleted messages " \
                         f"{f'from {member.mention}' if member else ''}" \
                         f" in the last 10 minutes."

        if self.bot.snipes:
            for key, value in reversed(self.bot.snipes.items()):
                if value['guild'] == ctx.guild.id:
                    if channel:
                        if value['channel'] == channel.id:
                            pass

                        else:
                            continue

                    if member:
                        if value['author'] == member.id:
                            pass

                        else:
                            continue

                    user = self.bot.get_user(value['author'])
                    em.set_author(name=user,
                                  icon_url=user.avatar_url)
                    em.description = value['content']
                    em.timestamp = value['time']
                    em.colour = ctx.author.colour
                    break

        await ctx.send(embed=em)

    @commands.command(
        name='editsnipe',
        aliases=['esnp', 'esnip'],
        description='Retrieve edited messages.'
    )
    @commands.cooldown(1, 2, commands.BucketType.member)
    async def get_editsnipes(self, ctx, member: typing.Optional[discord.Member],
                             channel: typing.Optional[discord.TextChannel]):
        em = SaturnEmbed(
            colour=BLUE,
        )
        em.description = f"{INFO} Couldn't find any edited messages " \
                         f"{f'from {member.mention}' if member else ''}" \
                         f" in the last 10 minutes."

        if self.bot.edit_snipes:
            for key, value in reversed(self.bot.edit_snipes.items()):
                if value['guild'] == ctx.guild.id:
                    if channel:
                        if value['channel'] == channel.id:
                            pass

                        else:
                            continue

                    if member:
                        if value['author'] == member.id:
                            pass

                        else:
                            continue

                    user = self.bot.get_user(value['author'])
                    em.set_author(name=user,
                                  icon_url=user.avatar_url)
                    em.description = f"**Before** - {value['before']}\n" \
                                     f"**After** - {value['after']}"
                    em.timestamp = value['time']
                    em.colour = ctx.author.colour
                    break

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Utility(bot))
