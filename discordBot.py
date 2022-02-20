import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from tabulate import tabulate
import traceback
from discordModule import DiscordModule

import forumScraper
import db
import constants

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEV_ID          = os.getenv('DISCORD_DEVELOPER_ID')

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def hiscores(ctx):
    rowIDs = range(1,11)
    #Retrieve a list of the top 10 users and their respective postcount. tabulate it to look nicer
    try:
        hiscoresList = db.getPostCountHiscores()
        hiscoreString = tabulate(hiscoresList, headers=["Rank", "Name", "Count"], tablefmt="fancy_grid", showindex=rowIDs)
        await ctx.send(f"```{hiscoreString}```")
    except Exception as e:
        await ctx.send(f"Could not gather a hiscores list")

async def pollForum():
    await client.wait_until_ready()
    
    while True:
        print("Checking forum...")
        try:
            results = forumScraper.getLatestForumPost()
            #The results object will only hold data if the scraper has retrieved a new message
            if(results.forumPost != None):
                print("Choobs Forum Bot is sending a message!")

                #Increment the postcounter for the user who posted
                #If the user is not yet in our db, add the user
                userPostCount = db.incrementUserPostCounter(results.username)

                #Make an instantiation of the DiscordModule class with the current post/user info to handle discord actions
                dm = DiscordModule(client, results.username, userPostCount)
                await dm.sendForumPost(results)
                await dm.checkRoles()
            
        except Exception as e:
            traceback.print_exc(chain=True)
            user = client.get_user(int(DEV_ID))
            await user.send(''.join(traceback.format_exception(None, e, e.__traceback__)))

        finally:
            await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)

if __name__ == "__main__":
    client.loop.create_task(pollForum())
    client.run(TOKEN)

