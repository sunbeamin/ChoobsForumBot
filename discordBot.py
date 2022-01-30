from itertools import count
from collections import namedtuple
from typing import NamedTuple
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import sqlite3
import re
from tabulate import tabulate

import forumScraper
import databaseHelper
import constants


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Load our enviroment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL')
GUILD_ID = os.getenv('DISCORD_GUILD')
ROLE_ID_JUNIOR = os.getenv('DISCORD_FORUM_ROLE_JUNIOR')
ROLE_ID_MEDIOR = os.getenv('DISCORD_FORUM_ROLE_MEDIOR')
ROLE_ID_SENIOR = os.getenv('DISCORD_FORUM_ROLE_SENIOR')

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

db = databaseHelper.ChoobsDatabase(os.path.join(BASE_DIR, "ChoobsForum.db"))

class Role(NamedTuple):
    id: int
    name: constants.ForumRole

#Make a tuple of all the roles
roleList = (Role(id=ROLE_ID_JUNIOR, name=constants.ForumRole.Junior),
            Role(id=ROLE_ID_MEDIOR, name=constants.ForumRole.Medior),
            Role(id=ROLE_ID_SENIOR, name=constants.ForumRole.Senior),)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def hiscores(ctx):
    rowIDs = range(1,11)
    #Retrieve a list of the top 10 users and their respective postcount. tabulate it to look nicer
    hiscoresList = db.getPostCountHiscores()
    hiscoreString = tabulate(hiscoresList, headers=["Rank", "Name", "Count"], tablefmt="fancy_grid", showindex=rowIDs)

    await ctx.send(f"```{hiscoreString}```")

async def pollForum():
    await client.wait_until_ready()
    
    while True:
        print("Checking forum...")
        results = forumScraper.getLatestForumPost()

        #The results object will only hold data if the scraper has retrieved a new message
        if(results.forumPost != None):
            print("Choobs Forum Bot is sending a message!")

            #Retrieve the channel and guild (server) we want to send to.
            guild = client.get_guild(int(GUILD_ID))
            channel = client.get_channel(int(CHANNEL_ID))
            
            #Properly format the username:
            results.username = results.username.replace(u'\xa0', u' ')

            #Increment the postcounter for the user who posted
            #If the user is not yet in our db, add the user
            userPostCount = db.incrementUserPostCounter(results.username)

            #Determine if post count is high enough to assign role to user
            newRole = None
            if (userPostCount >= constants.ForumRoleThreshold.Senior):
                newRole = roleList[constants.ForumRole.Senior]
            elif (userPostCount >= constants.ForumRoleThreshold.Medior):
                newRole = roleList[constants.ForumRole.Medior]
            elif (userPostCount >= constants.ForumRoleThreshold.Junior):
                newRole = roleList[constants.ForumRole.Junior]

            #If the roleId is set (i.e. any of the above conditions is valid)
            #AND the role to set is not the role already set (prevents re-setting roles every time)
            if (newRole != None):
                assignedRole = db.getAssignedRole(results.username)
                if ((newRole.id != None) and (assignedRole != newRole.name)): 
                    #Retrieve ALL users in the server, 
                    allDiscordMembers = client.get_all_members()

                    #Check if the name of the forum poster, matches any discord users name.
                    #Allows formats like "name 1 | name 2" in this manner
                    for user in allDiscordMembers:
                        foundUser = re.search(f"{results.username}", user.nick)
                        if(foundUser != None):
                            userDiscord = user
                            break

                    # Set the new role locally in the db
                    db.setAssignedRole(name=results.username, role=int(newRole.name))

                    if(userDiscord == None):
                        await channel.send(f"I tried to assign the role of **{guild.get_role(int(newRole.id))}**! to {results.username}\nbut I couldn't find a Discord user which matches this name")
                    else:
                        #Remove old assigned forum roles by iterating through the existing roles and matching to new role
                        for r in roleList:
                            if(r.name != newRole.name):
                                await userDiscord.remove_roles(guild.get_role(int(r.id)))

                        #Add role to user and mention assignment in a message
                        await userDiscord.add_roles(guild.get_role(int(newRole.id)))
                        await channel.send(f"{userDiscord.mention} has just reached the role of **{guild.get_role(int(newRole.id))}**!")

            
            #Embed the data into a nice format
            embed=discord.Embed(
            title=f"Iron Choobs Forum",
                url=results.forumURL,
                color=discord.Color.blue())
            embed.set_thumbnail(url="https://ws.shoutcast.com/images/contacts/0/07a6/07a648bc-68cb-4ad5-aadb-bf118339abdd/radios/c0cd2c27-a667-4275-82b8-2a744b66ca62/c0cd2c27-a667-4275-82b8-2a744b66ca62.png")
            embed.add_field(name="User", value=results.username, inline=True)
            embed.add_field(name="Post Count", value=userPostCount, inline=True)
            embed.add_field(name="Post", value=f"```{results.forumPost} ```", inline=False)

            await channel.send(embed=embed)

        await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)

if __name__ == "__main__":
    client.loop.create_task(pollForum())
    client.run(TOKEN)

