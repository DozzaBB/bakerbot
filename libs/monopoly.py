import libs.utilities as utilities

import discord

class Monopoly:
    """Monopoly class: houses everything Monopoly-related."""
    def __init__(self) -> None:
        self.players = {}

    async def run(self, message: discord.Message) -> None:
        """Starts the game. This should be the last function that is run."""
        playerJoiner = MonopolyPlayerJoiner(self)
        await playerJoiner.run(message)
        await playerJoiner.wait()

        pieceSelector = MonopolyPieceSelector(self)
        await pieceSelector.run(message)
        await pieceSelector.wait()

        board = MonopolyBoard(self)
        await board.run(message)
        await board.wait()

class MonopolyBoard(discord.ui.View):
    """A subclass of `discord.ui.View` for the board UI in a Monopoly game."""
    def __init__(self, game: Monopoly) -> None:
        super().__init__()
        self.game = game

    async def run(self, message: discord.Message) -> None:
        """Starts the Monopoly board screen."""
        content = "https://i.pinimg.com/originals/a9/31/4a/a9314a10181ad43d6a25c6019c19c397.jpg"
        await message.edit(content=content, embed=None, view=self)

class MonopolyPieceSelector(discord.ui.View):
    """A subclass of `discord.ui.View` for the piece selection screen in a Monopoly game."""
    def __init__(self, game: Monopoly) -> None:
        super().__init__()
        self.selected = 0
        self.game = game

    async def common(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called by each button when a user selects a piece."""
        player = self.game.players.get(interaction.user.id, None)

        if player is None:
            nope = "You are not apart of this game!"
            return await interaction.response.send_message(content=nope, ephemeral=True)
        elif player.piece is not None:
            nope = "You've already selected a piece!"
            return await interaction.response.send_message(content=nope, ephemeral=True)

        self.selected += 1
        button.disabled = True
        player.piece = button.emoji
        await interaction.response.edit_message(view=self)

        if self.selected == len(self.game.players.keys()):
            self.stop()

    @discord.ui.button(label="Wheelbarrow", emoji="<:wheelbarrow:868328816098021437>")
    async def wheelbarrow(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects the this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Thimble", emoji="<:thimble:868328817545064500>")
    async def thimble(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Car", emoji="<:car:868328818019029063>")
    async def car(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Thimble", emoji="<:thimble:868328817545064500>")
    async def thimble(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Battleship", emoji="<:battleship:868328817444397116>")
    async def battleship(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Iron", emoji="<:iron:868328816756531200>")
    async def iron(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Boot", emoji="<:boot:868328816374849536>")
    async def boot(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    @discord.ui.button(label="Hat", emoji="<:hat:868328816353902624>")
    async def hat(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user selects this as their piece."""
        await self.common(button, interaction)

    async def run(self, message: discord.Message) -> None:
        """Starts the piece selection screen."""
        self.enabled = len(self.children)
        content = "Press any button to select a piece."
        await message.edit(content=content, embed=None, view=self)

class MonopolyPlayerJoiner(discord.ui.View):
    """A subclass of `discord.ui.View` for the player join screen in a Monopoly game."""
    def __init__(self, game: Monopoly) -> None:
        super().__init__()
        self.embed = discord.Embed()
        self.game = game

    def mentions(self) -> str:
        """Returns a list of strings that mentions all players."""
        strings = " ".join(p.member.mention for p in self.game.players.values())
        mention = strings or "No players!"
        return mention

    @discord.ui.button(label="Click here to join!")
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user presses the join button."""
        if interaction.user.id in self.game.players or len(self.game.players.keys()) >= 8:
            nope = "Can't add you to the game: you're already playing or the maximum number of players has been reached."
            return await interaction.response.send_message(content=nope, ephemeral=True)

        player = MonopolyPlayer(interaction.user)
        self.game.players[interaction.user.id] = player
        self.embed.set_field_at(0, name="Players", value=self.mentions())
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label="Click here to start!", style=discord.ButtonStyle.green)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Called when a user pressses the start button."""
        if len(self.game.players.keys()) < 1: # TODO: make this 2.
            nope = "There aren't enough players to start."
            return await interaction.response.send_message(content=nope, ephemeral=True)
        elif interaction.user.id not in self.game.players.keys():
            nope = "You cannot start this game as you are not apart of it."
            return await interaction.response.send_message(content=nope, ephemeral=True)

        self.stop()

    async def run(self, message: discord.Message) -> None:
        """Starts the player joining screen."""
        self.embed.set_footer(text="Unfortunately, no sponsorship from Hasbro.", icon_url=utilities.Icons.info)
        self.embed.set_thumbnail(url="https://m.media-amazon.com/images/I/81oC5pYhh2L.jpg")
        self.embed.add_field(name="Players", value=self.mentions())

        self.embed.title = "Bakerbot: Monopoly, but it's open-source!"
        self.embed.colour = utilities.Colours.regular
        self.embed.timestamp = discord.utils.utcnow()
        await message.edit(content=None, embed=self.embed, view=self)

class MonopolyPlayer:
    """A class representing a Monopoly player."""
    def __init__(self, member: discord.Member) -> None:
        self.member = member
        self.piece = None
