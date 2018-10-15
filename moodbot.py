#!/usr/bin/env python3.6

import argparse
import asyncio
import datetime
import logging
import sys

import discord

from secrets import TOKEN

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-d", "--debug", action="store_true",
                    help="enable additional debug logging")
PARSER.add_argument("-l", "--logfile", type=str,
                    help="file to write log output")
PARSER.add_argument("-S", "--selfie", action="store_true",
                    help="run job to clear any selfie channel messages older than 7 days")
ARGS = PARSER.parse_args()

CLIENT = discord.Client()

FORMATTER = "%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s"
if ARGS.logfile and ARGS.logfile != "-":
    logging.basicConfig(filename=ARGS.logfile, format=FORMATTER)
else:
    logging.basicConfig(stream=sys.stdout, format=FORMATTER)

LOGGER = logging.getLogger('moodbot')
if ARGS.debug:
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

@CLIENT.event
async def on_message(message):
    # don't take messages if running selfie job
    if ARGS.selfie:
        return

    # we do not want the bot to reply to itself
    if message.author == CLIENT.user:
        return

    #LOGGER.debug("GOT MESSAGE in CH {0.channel.id}: {0.author.name}: {0.content}".format(message))
    # delete messages <280 char in memos channel
    if message.channel.id == "396014169784057858":
        LOGGER.debug("GOT MESSAGE IN MEMOS: {0.content}".format(message))
        if len(message.content) < 280:
            try:
                LOGGER.debug("Deleting message: {0.author.name}: {0.content}".format(message))
                await CLIENT.delete_message(message)
            except discord.Forbidden:
                LOGGER.error("ERROR: not permissioned to delete message")
    else:
        if message.content.startswith("!hello"):
            msg = "Hello {0.author.mention}".format(message)
            await CLIENT.send_message(message.channel, msg)

async def purge_selfies():
    selfie_channel = CLIENT.get_channel("500745462337241125")
    if not selfie_channel:
        LOGGER.error("Could not find selfie channel!")
        return
    now_dt = datetime.datetime.utcnow()
    start_dt = now_dt - datetime.timedelta(weeks=1)
    end_dt = now_dt - datetime.timedelta(weeks=2)
    limit = 10000
    await CLIENT.send_message(selfie_channel, "Purging selfies older than {}!".format(str(start_dt)))
    while True:
        LOGGER.info('Running selfie purge job!')
        purged = await CLIENT.purge_from(selfie_channel, limit=limit, before=start_dt, after=end_dt)
        if len(purged) < limit:
            LOGGER.info("Purged {} messages, finished!".format(len(purged)))
            break
        else:
            LOGGER.info("Purged {} messages, doing another round!".format(len(purged)))

@CLIENT.event
async def on_ready():
    LOGGER.info('Logged in as: {} / {}'.format(CLIENT.user.name, CLIENT.user.id))
    if ARGS.selfie:
        await purge_selfies()
        await CLIENT.close()

def main():
    LOGGER.info('Starting moodbot!')
    CLIENT.run(TOKEN)
    return 0

if __name__ == "__main__":
    sys.exit(main())
