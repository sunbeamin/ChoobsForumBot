import discord
from discord.ext import commands
import os
import asyncio

import forumScraper

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DISCORD_CHANNEL')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

async def pollForum():
    await client.wait_until_ready()

    while True:
        print("Checking forum...")
        results = forumScraper.getLatestForumPost()

        #The results object will only hold data if the scraper has retrieved a new message
        if(results.forumPost != None):
            print("Choobs Forum Bot is sending a message!")
            #Retrieve the channel we want to send to. Replace this with the ID of the desired Discord channel
            channel = client.get_channel(int(CHANNEL))
            
            #Embed the data into a nice format
            embed=discord.Embed(
            title="Iron Choobs Forum",
                url=results.forumURL,
                description="A new post has been placed on the Iron Choobs forum!",
                color=discord.Color.blue())
            embed.set_thumbnail(url="https://ws.shoutcast.com/images/contacts/0/07a6/07a648bc-68cb-4ad5-aadb-bf118339abdd/radios/c0cd2c27-a667-4275-82b8-2a744b66ca62/c0cd2c27-a667-4275-82b8-2a744b66ca62.png")
            embed.add_field(name="**User**", value=results.username, inline=False)
            embed.add_field(name="**Timestamp**", value=results.timestamp, inline=False)
            embed.add_field(name="**Post content**", value=f"```{results.forumPost} ```", inline=False)
            embed.add_field(name="**URL**", value=results.forumURL, inline=False)
            embed.set_footer(text="If my bot is acting up, DM me @sun beamin")

            await channel.send(embed=embed)

        await asyncio.sleep(60)

if __name__ == "__main__":
    client.loop.create_task(pollForum())
    client.run(TOKEN)

