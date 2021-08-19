from importlib import util
import discord.ext.commands as commands
import importlib
import aiohttp
import ujson
import sys

class Bakerbot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.session = aiohttp.ClientSession()

        with open("secrets.json", "r") as file:
            self.secrets = ujson.load(file)

    def reload(self) -> None:
        """Reloads the bot's internal state without logging out of Discord."""
        with open("secrets.json", "r") as file:
            self.secrets = ujson.load(file)

        reloadables = [module for name, module in sys.modules.items() if name.startswith("libs.")]
        extensions = [extension for extension in self.extensions.keys()]

        for reloadable in reloadables:
            importlib.reload(reloadable)

        for extension in extensions:
            self.reload_extension(extension)

    def run(self) -> None:
        """Starts the bot. This should be the last function that is called."""
        if (token := self.secrets.get("discord-token", None)) is None:
            raise RuntimeError("discord-token not found in secrets.json.")

        super().run(token)
