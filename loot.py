import random
from dotenv import load_dotenv
import os

ADVISOR_ID      = os.getenv('DISCORD_ADVISOR_ROLE')
lootMessage = None

#Loot callbacks! These functions are considered private
def __nothing(dm):
    global lootMessage
    lootMessage = None
    print("Nothing")

def __bond(dm):
    global lootMessage
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Bond 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - {dm.discordUser.mention} has won a bond through the forum loot system. Users RuneScape name is **{dm.user}**\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Bond 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - A user (Discord name could not be found) has won a bond through the forum loot system. Users RuneScape name is **{dm.user}**\n----------------------------------------------------------"

def __discXP(dm):
    global lootMessage
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: XP 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - please type the following commands to fulfill the ticket:\n!give-xp {dm.discordUser.mention} 7500\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: XP 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - Discord user could not be found but users Runescape name is **{dm.user}**\nPlease find the users discord and type the following commands to fulfill the ticket:\n!give-xp 'discord user' 7500\n----------------------------------------------------------"

def __coins(dm):
    global lootMessage
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Coins 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - please type the following commands to fulfill the ticket:\n!give-coins {dm.discordUser.mention} 19999\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Coins 🎫**\n@{dm.guild.get_role(int(ADVISOR_ID)).mention} - Discord user could not be found but users Runescape name is **{dm.user}**\nPlease find the users discord and type the following commands to fulfill the ticket:\n!give-coins 'discord user' 15000\n----------------------------------------------------------"

loot = [(20, __nothing), (1, __bond), (10, __discXP), (5, __coins)]

async def rollLoot(dm):
    global lootMessage
    weights, loots = zip(*loot)
    bigloot = random.choices(loots, weights, k=1)
    print(f"User {dm.user} has received loot:")
    bigloot[0](dm)
    if lootMessage is not None:
        await dm.sendLootMessage(lootMessage)
    
