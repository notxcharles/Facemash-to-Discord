import config
import discord
import mysql.connector

debugMode = True

mysql_db = mysql.connector.connect(
    host = config.mysql_database["hostname"],
    database = config.mysql_database["database_name"],
    user = config.mysql_database["username"],
    password = config.mysql_database["password"]
)

def getRatings(): # Read SQL table and save the results (columns 2 and 3, name: rating)
    mysql_cursor = mysql_db.cursor()
    operation = "SELECT * FROM `{0}`".format(config.mysql_database["table_name"])
    mysql_cursor.execute(operation)
    rankings = {}
    for result in mysql_cursor.fetchall():
        rankings[result[2]] = int(result[3])
    if debugMode: print("rankings: ", rankings)
        



class DiscordClient(discord.Client):
    async def on_ready(self):
        if debugMode: print("Logged on as {0}".format(self.user))

    async def on_message(self, message):
        if debugMode: print("Message from {0.author}: {0.content}".format(message))
        if (message.content == "update") and (message.author.id in config.discord_details["canUpdate"]):
            print("ok")
            getRatings()





client = DiscordClient()
client.run(config.discord_details["bot_token"])