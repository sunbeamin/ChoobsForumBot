import os
import asyncio
from dotenv import load_dotenv
import traceback
import discordModule as disc

import forumScraper
import constants

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

async def pollForum():
    await disc.client.wait_until_ready()
    
    while True:
        try:
            if(disc.channel != None):
                print("Checking forum...")
                results = forumScraper.getLatestForumPost()
                #The results object will only hold data if the scraper has retrieved a new message
                if(results.forumPost != None):
                    print("Choobs Forum Bot is sending a message!")

                    #Make an instantiation of the DiscordModule class with the current post/user info to handle discord actions
                    dm = disc.UserModule(results.username)
                    await dm.sendForumPost(results)
                    await dm.checkRoles()
            
        except Exception as e:
            traceback.print_exc(chain=True)
            message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            await disc.sendDevMessage(message)

        finally:
            await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)

if __name__ == "__main__":
    disc.client.loop.create_task(pollForum())
    disc.client.run(TOKEN)

