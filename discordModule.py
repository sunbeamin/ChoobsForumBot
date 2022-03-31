import discord
import os
from dotenv import load_dotenv
from typing import NamedTuple
import re
from tabulate import tabulate
import discord
from discord.ext import commands

import db
import constants


#Load our enviroment variables 
load_dotenv()
CHANNEL_ID      = os.getenv('DISCORD_CHANNEL')
LOOTCHANNEL_ID  = os.getenv('DISCORD_LOOT_CHANNEL_ID')
GUILD_ID        = os.getenv('DISCORD_GUILD')
ROLE_ID_JUNIOR  = os.getenv('DISCORD_FORUM_ROLE_JUNIOR')
ROLE_ID_MEDIOR  = os.getenv('DISCORD_FORUM_ROLE_MEDIOR')
ROLE_ID_SENIOR  = os.getenv('DISCORD_FORUM_ROLE_SENIOR')
ROLE_ID_GOD     = os.getenv('DISCORD_FORUM_ROLE_GOD')
DEV_ID          = os.getenv('DISCORD_DEVELOPER_ID')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)
guild = None
channel = None
lootChannel = None

#Class used for holding the role discord id and its name 
class Role(NamedTuple):
    id: int
    name: constants.ForumRole

#Make a tuple of all the roles
roleList = (Role(id=ROLE_ID_JUNIOR, name=constants.ForumRole.Junior),
            Role(id=ROLE_ID_MEDIOR, name=constants.ForumRole.Medior),
            Role(id=ROLE_ID_SENIOR, name=constants.ForumRole.Senior),
            Role(id=ROLE_ID_GOD, name=constants.ForumRole.God),)

@client.event
async def on_ready():
    #Singleton variables for interacting with the discord server
    global client
    global guild
    global channel
    global lootChannel

    print('We have logged in as {0.user}'.format(client))
    guild = client.get_guild(int(GUILD_ID))
    channel = client.get_channel(int(CHANNEL_ID))
    lootChannel = client.get_channel(int(LOOTCHANNEL_ID))

@client.command(
    help="Gathers a list of the most active forum posters"
)
async def hiscores(ctx):
    rowIDs = range(1,11)
    #Retrieve a list of the top 10 users and their respective postcount. tabulate it to look nicer
    try:
        hiscoresList = db.getPostCountHiscores()
        hiscoreString = tabulate(hiscoresList, headers=["Rank", "Name", "Count"], tablefmt="fancy_grid", showindex=rowIDs)
        await ctx.send(f"```{hiscoreString}```")
    except Exception as e:
        await ctx.send(f"Could not gather a hiscores list")
        await sendDevMessage(e)

# @client.command(
#     help="Lists the Discord roles earned by posting on the forum"
# )
# async def forumroles(ctx):
#     global guild
#     msg = f"{guild.get_role(int(roleList[constants.ForumRole.God].id)).mention}\n{guild.get_role(int(roleList[constants.ForumRole.Senior].id)).mention}\n{guild.get_role(int(roleList[constants.ForumRole.Medior].id)).mention}\n{guild.get_role(int(roleList[constants.ForumRole.Junior].id)).mention}"
#     try:
#         await ctx.send(msg)
#     except Exception as e:
#         await ctx.send(f"Could not gather roles")
#         await sendDevMessage(e)

@client.command(
    help="Lists the loot that can be dropped by posting on the forum"
)
async def loot(ctx):
    global guild
    msg = [("OSRS Bond", "1/500"), ("1250 Discord XP", "1/125"), ("10$ Amazon Giftcard", "1/2000")]
    try:
        tabulatedList = tabulate(msg, headers=["Loot", "Droprate"], tablefmt="fancy_grid")
        await ctx.send(f"```{tabulatedList}```")
    except Exception as e:
        await ctx.send(f"Could not gather loot list")
        await sendDevMessage(e)

class UserModule:
    """
    This class is or handling discord related operations 
    such as setting assigned roles or sending messages
    """
    def __init__(self, user=None):
        #Save the singleton variables to our object so we can easily interface
        global client
        global guild
        global channel
        global lootChannel
        self.client = client
        self.guild = guild
        self.channel = channel
        self.lootChannel = lootChannel
        if user != None:
            self.user = user
        else:
            raise Exception(f"Cannot instantiate discord class. No or incorrect user given")
        self.discordUser = self.getDiscordUser()
        
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass 

    async def sendForumPost(self, post, loot):

        #Increment the postcounter for the user who posted
        postcount = db.getPostCount(self.user)
        db.setPostCount(self.user, postcount)
        self.checkRoles(postcount)

        #Embed the data into a nice format
        if loot is "Nothing":
            embed=discord.Embed(
            title=f"Iron Choobs Forum",
                url=post.forumURL,
                color=discord.Color.blue())
            embed.set_thumbnail(url="https://ws.shoutcast.com/images/contacts/0/07a6/07a648bc-68cb-4ad5-aadb-bf118339abdd/radios/c0cd2c27-a667-4275-82b8-2a744b66ca62/c0cd2c27-a667-4275-82b8-2a744b66ca62.png")
            embed.add_field(name="User", value=post.username, inline=True)
            embed.add_field(name="Post Count", value=postcount, inline=True)
            embed.add_field(name="Post", value=f"```{post.forumPost} ```", inline=False)
        else:
            embed=discord.Embed(
            title=f"Iron Choobs Forum",
                url=post.forumURL,
                color=discord.Color.green())
            embed.set_thumbnail(url="https://ws.shoutcast.com/images/contacts/0/07a6/07a648bc-68cb-4ad5-aadb-bf118339abdd/radios/c0cd2c27-a667-4275-82b8-2a744b66ca62/c0cd2c27-a667-4275-82b8-2a744b66ca62.png")
            embed.add_field(name="User", value=post.username, inline=True)
            embed.add_field(name="Post Count", value=postcount, inline=True)
            embed.add_field(name="Post", value=f"```{post.forumPost} ```", inline=False)
            embed.add_field(name="Loot", value=f"```{loot} ```", inline=False)
            if self.discordUser is not None:
                await self.channel.send(f"{self.discordUser.mention} has received loot by posting on the forum!")
        await self.channel.send(embed=embed)

    async def checkRoles(self, postcount):
        #Determine if post count is high enough to assign role to user
        newRole = None
        if (postcount >= constants.ForumRoleThreshold.God):
            newRole = roleList[constants.ForumRole.God]
        elif (postcount >= constants.ForumRoleThreshold.Senior):
            newRole = roleList[constants.ForumRole.Senior]
        elif (postcount >= constants.ForumRoleThreshold.Medior):
            newRole = roleList[constants.ForumRole.Medior]
        elif (postcount >= constants.ForumRoleThreshold.Junior):
            newRole = roleList[constants.ForumRole.Junior]

        #If the roleId is set (i.e. any of the above conditions is valid)
        #AND the role to set is not the role already set (prevents re-setting roles every time)
        if (newRole != None):
            assignedRole = db.getAssignedRole(self.user)
            if ((newRole.id != None) and (assignedRole != newRole.name)): 
                
                # Set the new role locally in the db
                db.setAssignedRole(name=self.user, role=int(newRole.name))

                if(self.discordUser == None):
                    err = f"I tried to assign the role of **{self.guild.get_role(int(newRole.id))}**! to {self.user}\nbut I couldn't find a Discord user which matches this name"
                    await self.channel.send(err)
                    raise Exception(err)
                else:
                    #Remove old assigned forum roles by iterating through the existing roles and matching to new role
                    for r in roleList:
                        if(r.name != newRole.name):
                            await self.discordUser.remove_roles(self.guild.get_role(int(r.id)))

                    #Add role to user and mention assignment in a message
                    await self.discordUser.add_roles(self.guild.get_role(int(newRole.id)))
                    await self.channel.send(f"{self.discordUser.mention} has just reached the role of **{self.guild.get_role(int(newRole.id))}**!")
    
    def getDiscordUser(self):
        allDiscordMembers = self.client.get_all_members()

        #Check if the name of the forum poster, matches any discord users name.
        #Name is matches as long as {results.username} is present in a users nick
        formattedDiscName = self.user.replace(u'\xa0', u' ')
        for user in allDiscordMembers:
            if(user.nick == None):
                foundUser = re.search(f"{formattedDiscName}", user.name)
            else:
                foundUser = re.search(f"{formattedDiscName}", user.nick)
            if(foundUser != None):
                return user 
        return None

    async def sendLootMessage(self, message):
        await self.lootChannel.send(message)
    
    async def sendAchievement(self, achievement):
        icon = f"https://wiseoldman.net/img/runescape/icons_small/{achievement.metric}.png"
        embed=discord.Embed(
        title=f"Iron Choobs Achievements",
            url="https://wiseoldman.net/groups/2303/achievements",
            color=discord.Color.gold())
        embed.set_thumbnail(url=icon)
        embed.add_field(name="User", value=achievement.user, inline=True)
        embed.add_field(name="Achievement", value=achievement.name, inline=True)
        await self.channel.send(embed=embed)
    
async def sendDevMessage(message):
    global client
    user = client.get_user(int(DEV_ID))
    await user.send(f"```{message}```")