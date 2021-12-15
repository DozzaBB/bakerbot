from backends import discord as expcord
import exceptions
import utilities
import model

from discord.ext import commands
import discord
import asyncio
import random

class Random(commands.Cog):
    """Random ideas that I come up with every now and again."""
    def __init__(self, bot: model.Bakerbot) -> None:
        self.lock = asyncio.Lock()
        self.sniper = MessageResender(bot)
        self.asker = WhoAsked(bot)
        self.bot = bot

    @commands.group(aliases=["discord"])
    async def discordo(self, ctx: commands.Context) -> None:
        """The parent command for Discord experiments."""
        summary = ("You've encountered Bakerbot's Discord experimentation lab! "
                   "See `$help random` for a full list of available subcommands.")

        await utilities.Commands.group(ctx, summary)

    @discordo.command()
    async def typing(self, ctx: commands.Context) -> None:
        """Starts typing in every available text channel."""
        coroutines = [channel.trigger_typing() for channel in ctx.guild.text_channels]
        await asyncio.gather(*coroutines)

    @discordo.command()
    async def live(self, ctx: commands.Context, *, channel: discord.VoiceChannel) -> None:
        """Anybody want an Opcode 18 payload?"""
        if not ("discord-user-token" in self.bot.secrets and "discord-user-id" in self.bot.secrets):
            raise exceptions.SecretNotFound("discord-user secrets not specified in secrets.json.")

        identifier = self.bot.secrets["discord-user-id"]
        token = self.bot.secrets["discord-user-token"]

        if expcord.User.lock.locked():
            fail = utilities.Embeds.status(False)
            fail.description = "Already streaming!"
            return await ctx.reply(embed=fail)

        if ctx.guild.get_member(identifier) is None:
            fail = utilities.Embeds.status(False)
            fail.description = "Someone is missing..."
            fail.set_footer(text="Consider inviting them?", icon_url=utilities.Icons.CROSS)
            return await ctx.reply(embed=fail)

        async with expcord.User(ctx, token, identifier) as remote:
            await remote.connect(channel)
            await remote.stream()
            await asyncio.sleep(10)
            await remote.disconnect()

class MessageResender:
    """A wrapper around `on_message_delete()` for sniping deleted messages."""
    def __init__(self, bot: model.Bakerbot) -> None:
        self.guilds = set()
        self.bot = bot
        bot.add_listener(self.on_message_delete)

    def __contains__(self, item: object) -> bool:
        return item in self.guilds

    def register(self, guild_id: int) -> None:
        """Registers a guild for deleted message sniping."""
        self.guilds.add(guild_id)

    def unregister(self, guild_id: int) -> None:
        """Unregisters a guild for deleted message sniping."""
        self.guilds.remove(guild_id)

    async def on_message_delete(self, message: discord.Message) -> None:
        """Resends deleted messages to channels."""
        if message.author.id != self.bot.user.id and message.guild is not None and message.guild.id in self.guilds:
            embed = utilities.Embeds.package(message, link=False)
            await message.channel.send(embed=embed)

class WhoAsked:
    """A wrapper around `on_message()` to ask: who asked?"""
    def __init__(self, bot: model.Bakerbot) -> None:
        self.guilds = set()
        self.bot = bot
        bot.add_listener(self.on_message)

    def __contains__(self, item: object) -> bool:
        return item in self.guilds

    def register(self, guild_id: int) -> None:
        """Registers a guild for asking."""
        self.guilds.add(guild_id)

    def unregister(self, guild_id: int) -> None:
        """Unregisters a guild for asking."""
        self.guilds.remove(guild_id)

    async def on_message(self, message: discord.Message) -> None:
        """OK, but who asked?"""
        if message.guild is not None and message.guild.id in self.guilds and random.randint(0, 1000) == 0:
            await message.reply("ok but who asked?")

def setup(bot: model.Bakerbot) -> None:
    cog = Random(bot)
    bot.add_cog(cog)
