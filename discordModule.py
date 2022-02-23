import discord
import os
from dotenv import load_dotenv
from typing import NamedTuple
import re

import db
import constants


#Load our enviroment variables 
load_dotenv()
CHANNEL_ID      = os.getenv('DISCORD_CHANNEL')
GUILD_ID        = os.getenv('DISCORD_GUILD')
ROLE_ID_JUNIOR  = os.getenv('DISCORD_FORUM_ROLE_JUNIOR')
ROLE_ID_MEDIOR  = os.getenv('DISCORD_FORUM_ROLE_MEDIOR')
ROLE_ID_SENIOR  = os.getenv('DISCORD_FORUM_ROLE_SENIOR')
ROLE_ID_GOD     = os.getenv('DISCORD_FORUM_ROLE_GOD')
DEV_ID          = os.getenv('DISCORD_DEVELOPER_ID')

#Class used for holding the role discord id and its name 
class Role(NamedTuple):
    id: int
    name: constants.ForumRole

#Make a tuple of all the roles
roleList = (Role(id=ROLE_ID_JUNIOR, name=constants.ForumRole.Junior),
            Role(id=ROLE_ID_MEDIOR, name=constants.ForumRole.Medior),
            Role(id=ROLE_ID_SENIOR, name=constants.ForumRole.Senior),
            Role(id=ROLE_ID_GOD, name=constants.ForumRole.God),)

class DiscordModule:
    """
    This class is a context manager for handling discord
    related operations such as assigned roles or sending messages
    """
    def __init__(self, client, user=None):
        if client != None:
            self.client = client
            self.guild = client.get_guild(int(GUILD_ID))
            self.channel = client.get_channel(int(CHANNEL_ID))
            self.user = user
            try:
                self.postcount = db.getPostCount(user)
            except db.NotFoundError:
                self.postcount = 0
        else:
            raise Exception(f"Cannot instantiate discord class. No or incorrect client given")
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        pass 

    async def sendForumPost(self, post):

        #Increment the postcounter for the user who posted
        self.postcount = self.postcount + 1
        db.setPostCount(self.user, self.postcount)

        #Embed the data into a nice format
        embed=discord.Embed(
        title=f"Iron Choobs Forum",
            url=post.forumURL,
            color=discord.Color.blue())
        embed.set_thumbnail(url="https://ws.shoutcast.com/images/contacts/0/07a6/07a648bc-68cb-4ad5-aadb-bf118339abdd/radios/c0cd2c27-a667-4275-82b8-2a744b66ca62/c0cd2c27-a667-4275-82b8-2a744b66ca62.png")
        embed.add_field(name="User", value=post.username, inline=True)
        embed.add_field(name="Post Count", value=self.postcount, inline=True)
        embed.add_field(name="Post", value=f"```{post.forumPost} ```", inline=False)
        await self.channel.send(embed=embed)

    async def checkRoles(self):
        #Determine if post count is high enough to assign role to user
        newRole = None
        if (self.postcount >= constants.ForumRoleThreshold.God):
            newRole = roleList[constants.ForumRole.God]
        elif (self.postcount >= constants.ForumRoleThreshold.Senior):
            newRole = roleList[constants.ForumRole.Senior]
        elif (self.postcount >= constants.ForumRoleThreshold.Medior):
            newRole = roleList[constants.ForumRole.Medior]
        elif (self.postcount >= constants.ForumRoleThreshold.Junior):
            newRole = roleList[constants.ForumRole.Junior]

        #If the roleId is set (i.e. any of the above conditions is valid)
        #AND the role to set is not the role already set (prevents re-setting roles every time)
        if (newRole != None):
            assignedRole = db.getAssignedRole(self.user)
            if ((newRole.id != None) and (assignedRole != newRole.name)): 
                
                # Set the new role locally in the db
                db.setAssignedRole(name=self.user, role=int(newRole.name))

                #Get the discord user based on forum name
                discordUser = self.getDiscordUser()

                if(discordUser == None):
                    err = f"I tried to assign the role of **{self.guild.get_role(int(newRole.id))}**! to {self.user}\nbut I couldn't find a Discord user which matches this name"
                    await self.channel.send(err)
                    raise Exception(err)
                else:
                    #Remove old assigned forum roles by iterating through the existing roles and matching to new role
                    for r in roleList:
                        if(r.name != newRole.name):
                            await discordUser.remove_roles(self.guild.get_role(int(r.id)))

                    #Add role to user and mention assignment in a message
                    await discordUser.add_roles(self.guild.get_role(int(newRole.id)))
                    await self.channel.send(f"{discordUser.mention} has just reached the role of **{self.guild.get_role(int(newRole.id))}**!")
    
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
    
async def sendDevMessage(client, message):
    user = client.get_user(int(DEV_ID))
    await user.send(f"```{message}```")