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

                #Make an instantiation of the DiscordModule class with the current post/user info to handle discord actions
                dm = DiscordModule(client, results.username)
                await dm.sendForumPost(results)
                await dm.checkRoles()
            
        except Exception as e:
            traceback.print_exc(chain=True)
            message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            await dm.sendDevMessage(message)

        finally:
            await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)

if __name__ == "__main__":
    client.loop.create_task(pollForum())
    client.run(TOKEN)

