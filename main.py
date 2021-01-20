from libs.models import Bakerbot
from pathlib import Path

import datetime as dt
import discord
import logging
import btoken

if __name__ == "__main__":
    # Discord intents (helps reduce API requests).
    intents = discord.Intents.default()
    intents.presences = False
    intents.typing = False
    intents.members = True

    # Setup the bot's activity.
    activity = discord.Game(name="with the API.", start=dt.datetime.utcnow())

    # Setup the logger to output messages to log.txt.
    handler = logging.FileHandler(filename=Path("./log.txt"), encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter("[%(levelname)s @ %(asctime)s] %(message)s"))
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)

    # Bot object, kinda important to keep around :p
    bot = Bakerbot(command_prefix="$", help_command=None, case_insensitive=True, intents=intents, activity=activity)

    # Load extensions from the cogs folder.
    for path in Path("./cogs").glob("**/*.py"):
        bot.load_extension(f"cogs.{path.stem}")

    # Start the bot.
    bot.run(btoken.token)
