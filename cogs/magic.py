from backends import discord as expcord
import exceptions
import utilities
import model

from discord.ext import commands
import typing as t
import asyncio
import discord
import random

class Magic(commands.Cog):
    """You can find dumb ideas from Team Magic here."""
    def __init__(self, bot: model.Bakerbot):
        self.magic = 473426067823263749
        self.sniper = MessageResender(bot, self.magic)
        self.disconnecter = Disconnecter(bot, self.magic)
        self.asker = WhoAsked(bot, self.magic)
        self.dozza = Dozza(bot, self.magic)
        self.bot = bot

        self.bot.loop.create_task(self.register_extras())

    async def register_extras(self) -> None:
        """Registers Team Magic into certain event handlers."""
        await self.bot.wait_until_ready()
        if (board := self.bot.get_cog("Starboard")) is not None:
            board.register(self.magic, 524100289897431040, 899503266386292758, 3)

    async def cog_check(self, ctx: commands.Context) -> None:
        """Ensures that commands are being run either by the owner or Team Magic."""
        owner = await self.bot.is_owner(ctx.author)
        return owner or (ctx.guild is not None and ctx.guild.id == self.magic)

    @commands.group(invoke_without_subcommand=True)
    async def magic(self, ctx: commands.Context) -> None:
        """The parent command for all things Team Magic related."""
        summary = ("You've encountered Team Magic's command group!"
                    "See `$help magic` for a full list of available subcommands.")

        await utilities.Commands.group(ctx, summary)

    @magic.command()
    async def nodelete(self, ctx: commands.Context) -> None:
        """Enables/disables the `on_message_delete()` listener for Team Magic."""
        self.sniper.enabled = not self.sniper.enabled
        await ctx.reply(f"`on_message_delete()` listener is (now?) set to: `{self.sniper.enabled}`")

    @magic.command()
    async def demux(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str) -> None:
        """A demultiplexing experiment using Discord webhooks."""
        endpoints = await channel.webhooks()
        user, avatar = ctx.author.display_name, self.bot.user.avatar.url
        tasks = [hook.send(message, username=user, avatar_url=avatar) for hook in endpoints]
        await asyncio.gather(*tasks)

    @magic.command()
    async def hookify(self, ctx: commands.Context, source: discord.TextChannel, destination: t.Optional[discord.TextChannel]) -> None:
        """So it turns out you can have more than 10 webooks in a channel..."""
        hooks = await source.webhooks()

        if destination is None:
            webhooks = "\n".join(str(w.id) for w in hooks)
            return await ctx.reply(webhooks)

        for i in range(10 - len(hooks)):
            rand = random.randint(0, 2**32)
            name = f"bakerbot hook #{rand}"
            await expcord.Webhooks.create(source, name)

        # Refresh the list of hooks after we create more.
        for webhook in (await source.webhooks()):
            await expcord.Webhooks.move(webhook, destination)

        await ctx.reply("Webhooks created and moved.")

    @magic.command()
    async def gandalf(self, ctx: commands.Context, member: discord.Member) -> None:
        """Prevents a member from joining a voice channel."""
        mentions = discord.AllowedMentions.none()

        if member.id in self.disconnecter.targets:
            self.disconnecter.targets.remove(member.id)
            await ctx.reply(f"{member.mention} shall pass!", allowed_mentions=mentions)
        else:
            self.disconnecter.targets.add(member.id)
            if member.voice is not None and member.voice.channel is not None:
                await member.move_to(None)

            await ctx.reply(f"{member.mention} shall not pass!", allowed_mentions=mentions)

    @magic.command()
    async def whoasked(self, ctx: commands.Context) -> None:
        """OK, but who asked?"""
        self.asker.enabled = not self.asker.enabled
        boolean = "enabled" if self.asker.enabled else "disabled"
        await ctx.reply(f"Asking is now {boolean}.")

    @magic.command()
    async def shitting(self, ctx: commands.Context) -> None:
        """Live shitting event."""
        if not ("discord-user-token" in self.bot.secrets and "discord-user-id" in self.bot.secrets):
            raise exceptions.SecretNotFound("discord-user secrets not specified in secrets.json.")

        identifier = self.bot.secrets["discord-user-id"]
        token = self.bot.secrets["discord-user-token"]

        if ctx.guild.get_member(identifier) is None:
            fail = utilities.Embeds.status(False)
            fail.description = "Someone is missing..."
            fail.set_footer(text="Consider inviting them?", icon_url=utilities.Icons.CROSS)
            return await ctx.reply(embed=fail)

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            fail = utilities.Embeds.status(False)
            fail.description = "You aren't in a voice channel!"
            return await ctx.reply(embed=fail)

        title = "live shitting event"
        description = "improved shitting setup for higher-quality shitting"
        await expcord.User.create_event(ctx.author.voice.channel, token, title, description)

class WhoAsked:
    """A wrapper around `on_message()` for Team Magic."""
    def __init__(self, bot: model.Bakerbot, guild: int) -> None:
        self.guild = guild
        self.enabled = True

        bot.add_listener(self.on_message)

    async def on_message(self, message: discord.Message) -> None:
        """OK, but who asked?"""
        if self.enabled and message.guild is not None and message.guild.id == self.guild and random.randint(0, 1000) == 0:
            await message.reply("ok but who asked?")

class MessageResender:
    """A wrapper around `on_message_delete()` for Team Magic."""
    def __init__(self, bot: model.Bakerbot, guild: int) -> None:
        self.ignore = set()
        self.guild = guild
        self.enabled = False

        bot.loop.create_task(self.initialise(bot))
        bot.add_listener(self.on_message_delete)

    async def initialise(self, bot: model.Bakerbot) -> None:
        """Initialises a `MessageResender` instance."""
        if bot.user is None:
            await bot.wait_until_ready()

        self.ignore.add(bot.user.id)

    async def on_message_delete(self, message: discord.Message) -> None:
        """Team Magic-specific listener for resending deleted messages."""
        if self.enabled and message.author.id not in self.ignore and message.guild.id == self.guild:
            embed = discord.Embed(colour=utilities.Colours.REGULAR, timestamp=message.created_at)
            embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
            embed.set_footer(text="NUTS!", icon_url=utilities.Icons.INFO)
            embed.description = message.content
            await message.channel.send(embed=embed)

class Disconnecter:
    """A wrapper around `on_voice_state_update()` for Team Magic."""
    def __init__(self, bot: model.Bakerbot, guild: int) -> None:
        self.guild = guild
        self.targets = set()
        bot.add_listener(self.on_voice_state_update)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """Team Magic-specific listener for preventing members from joining voice channels."""
        if member.id in self.targets and after.channel is not None:
            await member.move_to(None)

class Dozza:
    """A wrapper around `on_message()` just for the Big Dominic."""
    def __init__(self, bot: model.Bakerbot, guild: int) -> None:
        self.guild = guild
        self.identifier = 212076374226108417
        self.bot = bot
        bot.add_listener(self.on_message)

    def identifier_check(self, message: discord.Message) -> bool:
        """The predicate for checking if the message is for the Big Dominic."""
        return self.identifier in [member.id for member in message.mentions]

    async def post(self, message: discord.Message) -> None:
        """Posts a message to Big Dominic's inbox."""
        if (dozza := self.bot.get_user(self.identifier)) is not None:
            embed = utilities.Embeds.package(message)
            await dozza.send(embed=embed)

    async def on_message(self, message: discord.Message) -> None:
        """Personal message inbox."""
        if message.guild is not None and message.guild.id == self.guild:
            if self.identifier_check(message):
                await self.post(message)

            elif message.reference is not None and message.reference.message_id is not None:
                resolved = await message.channel.fetch_message(message.reference.message_id)
                if self.identifier_check(resolved):
                    await self.post(resolved)

def setup(bot):
    cog = Magic(bot)
    bot.add_cog(cog)
