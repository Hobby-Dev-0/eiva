import asyncio
import datetime
import importlib
import inspect
import logging
import math
import os
import re
import sys
import time
import traceback
from pathlib import Path
from time import gmtime, strftime

from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from Eivabot import *
from Eivabot.helpers import *
from Eivabot.config import *
from Eivabot.utils import *


# ENV
ENV = bool(os.environ.get("ENV", False))
if ENV:
    from Eivabot.config import Config
else:
    if os.path.exists("Config.py"):
        from Config import Development as Config


# load plugins
def load_module(shortname):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        import Eivabot.utils

        path = Path(f"Eivabot/plugins/{shortname}.py")
        name = "Eivabot.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LOGS.info("EivaBot - Successfully imported " + shortname)
    else:
        import Eivabot.utils

        path = Path(f"Eivabot/plugins/{shortname}.py")
        name = "Eivabot.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.bot = bot
        mod.tgbot = bot.tgbot
        mod.command = command
        mod.logger = logging.getLogger(shortname)
        # support for uniborg
        sys.modules["uniborg.util"] = Eivabot.utils
        mod.Config = Config
        mod.borg = bot
        mod.Eivabot = bot
        mod.edit_or_reply = edit_or_reply
        mod.eor = edit_or_reply
        mod.delete_Eiva = delete_Eiva
        mod.eod = delete_Eiva
        mod.Var = Config
        mod.admin_cmd = Eiva_cmd
        # support for other userbots
        sys.modules["userbot.utils"] = Eivabot.utils
        sys.modules["userbot"] = Eivabot
        # support for paperplaneextended
        sys.modules["userbot.events"] = Eivabot
        spec.loader.exec_module(mod)
        # for imports
        sys.modules["Eivabot.plugins." + shortname] = mod
        LOGS.info("⚡ ΣIVΛBθƬ⚡ - Successfully Imported " + shortname)


# remove plugins
def remove_plugin(shortname):
    try:
        try:
            for i in LOAD_PLUG[shortname]:
                bot.remove_event_handler(i)
            del LOAD_PLUG[shortname]

        except BaseException:
            name = f"Eivabot.plugins.{shortname}"

            for i in reversed(range(len(bot._event_builders))):
                ev, cb = bot._event_builders[i]
                if cb.__module__ == name:
                    del bot._event_builders[i]
    except BaseException:
        raise ValueError

# Eivabot
