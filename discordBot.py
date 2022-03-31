import os
import asyncio
from dotenv import load_dotenv
import traceback
import discordModule as disc
import loot

import forumScraper
import constants
import achievements

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

async def pollForum():
    await disc.client.wait_until_ready()
    iterator = 0
    
    while True:
        #Print a message every minute to indicate the bot is still running
        if(iterator is 6):
            print("Polling forum...")
            iterator = 0
        try:
            if(disc.channel != None):
                forumResult = forumScraper.getLatestForumPost()
                #The results object will only hold data if the scraper has retrieved a new message
                if(forumResult.forumPost != None):
                    print("Choobs Bot is sending a forum post!")

                    #Make an instantiation of the DiscordModule class with the current post/user info to handle discord actions
                    dm = disc.UserModule(forumResult.username)
                    rolledLoot = await loot.rollLoot(dm)
                    await dm.sendForumPost(forumResult, rolledLoot)
                            
        except Exception as e:
            traceback.print_exc(chain=True)
            message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            await disc.sendDevMessage(message)

        finally:
            await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)
            iterator = iterator + 1

async def pollAchievements():
    await disc.client.wait_until_ready()
    iterator = 0
    
    while True:
        #Print a message every minute to indicate the bot is still running
        if(iterator is 6):
            print("Polling achievements...")
            iterator = 0
        try:
            if(disc.channel != None):
                achievement = achievements.getLatestAchievement()
                #The results object will only hold data if the scraper has retrieved a new message
                if(achievement.user != None):
                    print("Choobs Bot is sending an achievement!")
                    #Make an instantiation of the DiscordModule class with the current user info to handle discord actions
                    dm = disc.UserModule(achievement.user)
                    await dm.sendAchievement(achievement)
                            
        except Exception as e:
            traceback.print_exc(chain=True)
            message = ''.join(traceback.format_exception(None, e, e.__traceback__))
            await disc.sendDevMessage(message)

        finally:
            await asyncio.sleep(constants.DISCORD_BOT_FORUM_POLL_RATE_S)
            iterator = iterator + 1

if __name__ == "__main__":
    disc.client.loop.create_task(pollForum())
    disc.client.loop.create_task(pollAchievements())
    disc.client.run(TOKEN)

