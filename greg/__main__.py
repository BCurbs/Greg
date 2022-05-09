"""Initializes the bot and deals with the configuration file"""

import asyncio
import json
import os
import sys

import discord
import sentry_sdk
from sentry_sdk import capture_exception
from greg.bot import GREG_LOGGER
from .db import db_init, db_migrate

config = {
    'prefix': '&',
    'developers': [],
    'discord_token': "Put Discord API Token here.",
    'debug': False,
    'invite_override': ""
}
config_file = 'config.json'

if os.path.isfile(config_file):
    with open(config_file) as f:
        config.update(json.load(f))

with open('config.json', 'w') as f:
    json.dump(config, f, indent='\t')

if config['sentry_url'] != "":
    sentry_sdk.init(
        str(config['sentry_url']),
        traces_sample_rate=1.0,
    )

asyncio.get_event_loop().run_until_complete(db_init(config['db_url']))

if 'discord_token' not in config:
    sys.exit('Discord token must be supplied in configuration')

if sys.version_info < (3, 6):
    sys.exit('Greg requires Python 3.6 or higher to run. This is version %s.' % '.'.join(sys.version_info[:3]))

from . import Greg  # After version check

intents = discord.Intents.default()
intents.members = True
intents.presences = config['presences_intents']

bot = Greg(config, intents=intents, max_messages=config['cache_size'])
errors = []
for ext in os.listdir('greg/cogs'):
    if not ext.startswith(('_', '.')):
        try:
            bot.load_extension('greg.cogs.' + ext[:-3])  # Remove '.py'
            bot.loaded_extensions.append('greg.cogs.' + ext[:-3])
        except AttributeError as e:
            GREG_LOGGER.error(f"Failed to load extension greg.cogs.{ext[:-3]}")
            capture_exception()

asyncio.get_event_loop().run_until_complete(db_migrate())

bot.run()

# restart the bot if the bot flagged itself to do so
if bot._restarting:
    script = sys.argv[0]
    if script.startswith(os.getcwd()):
        script = script[len(os.getcwd()):].lstrip(os.sep)

    if script.endswith('__main__.py'):
        args = [sys.executable, '-m', script[:-len('__main__.py')].rstrip(os.sep).replace(os.sep, '.')]
    else:
        args = [sys.executable, script]
    os.execv(sys.executable, args + sys.argv[1:])
