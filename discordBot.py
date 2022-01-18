from itertools import count
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import sqlite3
from tabulate import tabulate

import forumScraper
import databaseHelper
import constants


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Load our enviroment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')
ROLE_JUNIOR = os.getenv('DISCORD_FORUM_ROLE_JUNIOR')
ROLE_MEDIOR = os.getenv('DISCORD_FORUM_ROLE_MEDIOR')
ROLE_SENIOR = os.getenv('DISCORD_FORUM_ROLE_SENIOR')

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

db = databaseHelper.ChoobsDatabase(os.path.join(BASE_DIR, "ChoobsForum.db"))

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

            #Increment the postcounter for the user who posted
            #If the user is not yet in our db, add the user
            userPostCount = db.incrementUserPostCounter(results.username)

            #Determine if post count is high enough to assign role to user
            #TODO Match user roleId with new roleId, if they don't match. assign
            roleId = None
            if (userPostCount >= constants.FORUM_ROLE_SENIOR_THRESHOLD):
                roleId = ROLE_SENIOR
            elif (userPostCount >= constants.FORUM_ROLE_MEDIOR_THRESHOLD):
                roleId = ROLE_MEDIOR
            elif (userPostCount >= constants.FORUM_ROLE_JUNIOR_THRESHOLD):
                roleId = ROLE_JUNIOR

            if (roleId != None): 
                userDiscordId = discord.utils.get(client.get_all_members(), nick=results.username.replace(u'\xa0', u' '))

            #Retrieve the channel we want to send to. Replace this with the ID of the desired Discord channel
            channel = client.get_channel(int(CHANNEL))
            
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

