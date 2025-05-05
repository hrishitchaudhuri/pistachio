import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from states import BotState

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

pistachio = commands.Bot(command_prefix='!', intents=intents)
CURRENT_STATE = BotState.SLEEPING

################################################################

READER = None
NOT_RED = []
NOT_GREEN = []
LAST_ADDED = NOT_RED

CURRENT_BUZZ = None
CURRENT_TEAM = None

TOSSUP_COUNTER = 0

################################################################

@pistachio.command()
async def init(ctx):
    global CURRENT_STATE
    if CURRENT_STATE != BotState.SLEEPING:
        await ctx.send("[ ERR] You are in the middle of a game.")
    else:
        await ctx.send("[ INFO] Beginning game. Please add at least [ONE] user per team, and assign a [READER]")
        CURRENT_STATE = BotState.SETUP
    return

@pistachio.command()
async def set(ctx, user : discord.Member, team):
    global CURRENT_STATE
    if CURRENT_STATE == BotState.SLEEPING:
        await ctx.send("[ ERR] Please start a game.")
        return
    
    global READER, NOT_RED, NOT_GREEN, LAST_ADDED

    #TODO : WAYYYYY more error handling. Check for
    #           (1) users already exist? remove assignment from array and move to other
    #           (2) add roles within server?
    rdr_role = discord.utils.get(ctx.guild.roles, name="Reader")
    n_red_role = discord.utils.get(ctx.guild.roles, name="Not Red Team")
    n_grn_role = discord.utils.get(ctx.guild.roles, name="Not Green Team")

    if team == "reader":
        if READER: # we don't want more than one reader at any point!
            if rdr_role in READER.roles: # IDEALLY, this is a redundant check
                await READER.remove_roles(rdr_role)
                await ctx.send(f'[ INFO] {user.mention} is no longer [READER]')
        if rdr_role not in user.roles:
            # unset any team roles
            if n_red_role in user.roles:
                await user.remove_roles(n_red_role)
            if n_grn_role in user.roles:
                await user.remove_roles(n_grn_role)
            await user.add_roles(rdr_role)
            READER = user
            await ctx.send(f"[ INFO] {user.mention} set as [READER]")
        
    elif team == "nr":
        if rdr_role in user.roles:
            await user.remove_roles(rdr_role)
        if n_grn_role in user.roles:
            await user.remove_roles(n_grn_role)
            NOT_GREEN.remove(user)
        if n_red_role not in user.roles:
            await user.add_roles(n_red_role)
            NOT_RED.append(user)
            LAST_ADDED = NOT_RED
            await ctx.send(f"[ INFO] {user.mention} assigned to [NOT_RED]")
    elif team == "ng":
        if rdr_role in user.roles:
            await user.remove_roles(rdr_role)
        if n_red_role in user.roles:
            await user.remove_roles(n_red_role)
            NOT_RED.remove(user)
        if n_grn_role not in user.roles:
            await user.add_roles(n_grn_role)
            NOT_GREEN.append(user)
            LAST_ADDED = NOT_GREEN
            await ctx.send(f"[ INFO] {user.mention} assigned to [NOT_GREEN]")
    else:
        if any(role in user.roles for role in [rdr_role, n_grn_role, n_red_role]):
            await ctx.send(f"[ ERR] {user.mention} already has a role.")
            return
        LAST_ADDED.append(user)
        if LAST_ADDED == NOT_GREEN:
            await user.add_roles(n_grn_role)
            await ctx.send(f"[ INFO] {user} assigned to [NOT_GREEN]")
            LAST_ADDED = NOT_RED
        else:
            await user.add_roles(n_red_role)
            await ctx.send(f"[ INFO] {user} assigned to [NOT_RED]")
            LAST_ADDED = NOT_GREEN

    ready = NOT_GREEN & NOT_RED & READER
    if ready:
        CURRENT_STATE = BotState.READY

@pistachio.command
async def start(ctx):
    global CURRENT_STATE
    if CURRENT_STATE > BotState.READY:
        await ctx.send("[ ERR] Game is already in progress.")
        return
    elif CURRENT_STATE < BotState.READY:
        await ctx.send("[ ERR] Please initialize a game.")
        return
    
    CURRENT_STATE = BotState.TOSSUP
    global TOSSUP_COUNTER, READER

    TOSSUP_COUNTER += 1
    await ctx.send(f"[ INFO] {READER} reading TU {TOSSUP_COUNTER}.")
    return

@pistachio.command
async def buzz(ctx):
    global CURRENT_STATE
    if CURRENT_STATE != BotState.TOSSUP:
        await ctx.send("[ ERR] Wait for a tossup to be read before buzzing.")

    global CURRENT_BUZZ, CURRENT_TEAM
    CURRENT_BUZZ = ctx.author
    if CURRENT_BUZZ in NOT_RED:
        CURRENT_TEAM = "nr"
    elif CURRENT_BUZZ in NOT_GREEN:
        CURRENT_TEAM = "ng"
    else:
        await ctx.send("[ ERR] Buzzer is not registered.")

@pistachio.command
async def v(ctx):
    pass
    


pistachio.run(TOKEN)