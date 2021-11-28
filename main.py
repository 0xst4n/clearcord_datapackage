import discord, time, os, datetime, json
from termcolor import colored, cprint
import colorama
from discord.ext import commands

import logging, re, warnings
logging.captureWarnings(True)
warnings.filterwarnings('always', category=DeprecationWarning,
                        module=r'^{0}\.'.format(re.escape(__name__)))
warnings.warn("This is a DeprecationWarning",category=DeprecationWarning)

colorama.init()
 
prefix = '*'
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, self_bot=True)

data_package = None
token = None
before_date = None

if not token:
    cprint("\nFind out how to find your user token here: https://github.com/Tyrrrz/DiscordChatExporter/wiki/Obtaining-Token-and-Channel-IDs#how-to-get-a-user-token", "green")
    token = input("Token for your account: ")

if not data_package:
    cprint("\nGive the path to the root of your discord data package (unzipped)", "green")
    data_package = input("Path: ")

if not before_date:
    cprint("\nOnly delete messages before this date, default is messages older than 30 days", "green")
    before_date = input("Give the date to delete messages before (yyyy-mm-dd): ")
    if not before_date:
        before_date = datetime.datetime.today() - datetime.timedelta(days=30)
    else:
        try:
            before_date = datetime.datetime.strptime(before_date, '%Y-%m-%d')
        except ValueError:
            before_date = datetime.datetime.today() - datetime.timedelta(days=30)
            print()
cprint(f"Deleting messages before {before_date}\n", "blue")

ignore_friends = True
cprint("Tell me if you also want to delete messages in friend DMs", "cyan")
ignore_friends = input("Delete friend DMs (yes/no): ")
if ignore_friends.lower() == "yes":
    ignore_friends = False
    cprint("\nDeleting messages in friend DMs too!\n", "red")
else:
    cprint("\nFriend DMs will be kept intact\n", "cyan")


@bot.event
async def on_ready():
    cprint(f"Clearcord_datapackage is running.", 'blue')

    dm_text_channels = []
    server_text_channels = []

    if not os.path.exists(f"{data_package}/messages/index.json"):
        cprint(f"Could not find {data_package}/messages/index.json... exiting", "red")
        os._exit(1)

    with open(f"{data_package}/messages/index.json") as json_file:
        data = json.load(json_file)
        cprint("Loading channels..", "green")
        for k, v in data.items():
            if not v:
                continue
            try:
                channel = await bot.fetch_channel(k)
                if channel.type == discord.ChannelType.text or channel.type == discord.ChannelType.group:
                    server_text_channels.append(channel)
                elif channel.type == discord.ChannelType.private:
                    other_user = channel.recipient
                    dm_text_channels.append(other_user)
                elif channel.type == discord.ChannelType.group:
                    # do group thing
                    pass
            except discord.errors.Forbidden as e:
                cprint(f"{k} - You've probably left the server this channel is in.", "magenta")
                continue
            except discord.errors.NotFound as e:
                cprint(f"{k} - This channel has most likely ceased to exist.", "magenta")
                continue

    for dmc in dm_text_channels:
        await clear_dm_channel(dmc, before_date)

    cprint("\nChecking the server channels\n", "blue")

    for sc in server_text_channels:
        await clear_server_text_channel(sc, before_date)
    
    cprint("\nDone!", "blue")
    os._exit(1)

async def clear_dm_channel(channel, before_date, ignore_friends=True):
    if channel.is_friend() and ignore_friends:
        cprint(f"Ignoring {channel}, because friend", "blue")
        return

    # todo add filtering for Group DM

    message_count = 0
    first = True
    async for message in channel.history(limit=None, oldest_first=True):
        if message.author == bot.user:
            if first:
                cprint(f"Starting on {channel}.. depending on how many messages this might take a while!", "green")
                first = False
            if message.created_at < before_date:
                try:
                    await message.delete()
                    message_count+=1
                    pass
                except:
                    cprint(f"Couldn't delete message {channel.name}:{message.id}, probably non-text message (e.g starting a call)", "magenta")
    
    if message_count > 0:
        cprint(f'{message_count} messages deleted in {channel.name}\'s channel', "green")
    else:
        cprint(f"No messages found in {channel.name}", "yellow")

async def clear_server_text_channel(channel, before_date):
    cprint(f"Looking in {channel.guild} - {channel} - {channel.id}..", "green")
    try:
        deleted = await channel.purge(limit=300000, check=is_me, bulk=True, before=before_date)
        if len(deleted) > 0:
            cprint(f"Deleted {len(deleted)} messages in {channel.guild} - {channel} :", "green")
        else:
            cprint(f"No messages found in {channel}", "yellow")
    except Exception as e:
        print(e)
        cprint(f"Can't delete in {channel.guild} - {channel}", "red")

def is_me(m):
    return m.author == bot.user
    
bot.run(token, bot=False)