import random
from dotenv import load_dotenv
import os

ADVISOR_ID      = os.getenv('DISCORD_ADVISOR_ROLE')
lootMessage = None
lootType = None

#Loot callbacks! These functions are considered private
def __nothing(dm):
    global lootMessage
    global lootType
    lootType = "Nothing"
    lootMessage = None
    print("Nothing")

def __bond(dm):
    print("OSRS Bond\n")
    global lootMessage
    global lootType
    lootType = "OSRS Bond 💰"
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Bond 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - {dm.discordUser.mention} has won a bond through the forum loot system. \nUsers RuneScape name is **{dm.user}**\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Bond 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - A user (Discord name not found) has won a bond through the forum loot system.\nUsers RuneScape name is **{dm.user}**\n----------------------------------------------------------"

def __discXP(dm):
    print("1250 Discord XP\n")
    global lootMessage
    global lootType
    lootType = "1250 Discord XP 🎫"
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: XP 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - please type the following commands to fulfill the ticket:\n!give-xp {dm.discordUser.mention} 1250\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: XP 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - Discord user could not be found but users Runescape name is **{dm.user}**\nPlease find the users discord and type the following commands to fulfill the ticket:\n!give-xp 'discord user' 1250\n----------------------------------------------------------"

def __giftcard(dm):
    global lootMessage
    global lootType
    lootType = "10$ Amazon Giftcard 💵"
    print("Amazon giftcard\n")
    if dm.discordUser is not None:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Amazon Giftcard 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - {dm.discordUser.mention} has won a 10$ Amazon giftcard through the forum loot system.\n----------------------------------------------------------"
    else:
        lootMessage = f"----------------------------------------------------------\n**New Forum Loot Ticket: Amazon Giftcard 🎫**\n{dm.guild.get_role(int(ADVISOR_ID)).mention} - A user (Discord name not found) has won a 10$ Amazon giftcard through the forum loot system.\nDiscord user could not be found but users Runescape name is **{dm.user}**\n----------------------------------------------------------"

loot = [(1, __nothing), (1, __bond), (1, __discXP), (1, __giftcard)]

async def rollLoot(dm):
    global lootMessage
    global lootType
    weights, loots = zip(*loot)
    bigloot = random.choices(loots, weights, k=1)
    print(f"User {dm.user} has received loot: ")
    bigloot[0](dm)
    if lootMessage is not None:
        await dm.sendLootMessage(lootMessage)
    return lootType


    
