import config
import discord
import mysql.connector


mysql_db = mysql.connector.connect(
    host = config.mysql_database["hostname"],
    database = config.mysql_database["database_name"],
    user = config.mysql_database["username"],
    password = config.mysql_database["password"]
)
    
class DiscordClient(discord.Client):
    async def on_ready(self):
        print("Logged on")

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))



client = DiscordClient()
client.run(config.discord_details["bot_token"])