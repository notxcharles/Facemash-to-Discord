import config
import discord
import mysql.connector
from scipy.stats import norm
import numpy as np


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
    rankings = []
    for result in mysql_cursor.fetchall():
        dict = {"entry": {
            "name": result[2],
            "score": result[3],
            "probability": 0
        }}

        rankings.append(dict)
    if debugMode: print("rankings: ", rankings)
    return rankings
    
        


def generateNormaldistribution(rankings):
    scores = []
    for i in range(len(rankings)):
        scores.append(int(rankings[i]["entry"]["score"]))
    mean = float(np.mean(scores))
    standard_deviation = float(np.std(scores))
    if debugMode: print("m ", mean, " sd ", standard_deviation)
    return mean, standard_deviation, rankings



def normalDistributionProbability(mean, standard_deviation, rankings):
    # https://www.askpython.com/python/normal-distribution
    for i in range(len(rankings)):
        score = int(rankings[i]["entry"]["score"])
        if score != 0:
            probability = norm(mean, standard_deviation).cdf(score)
            rankings[i]["entry"]["probability"] = probability
    if debugMode: print(rankings[i]["entry"], probability)
    return rankings


class DiscordClient(discord.Client):
    async def on_ready(self):
        if debugMode: print("Logged on as {0}".format(self.user))

    async def on_message(self, message):
        if debugMode: print("Message from {0.author}: {0.content}".format(message))
        if (message.content == "update") and (message.author.id in config.discord_details["canUpdate"]):
            await message.reply("Updating")

            rankings = getRatings()
            returns = generateNormaldistribution(rankings)
            rankingsWithProbability = normalDistributionProbability(returns[0], returns[1], returns[2])

            discordGuildID = config.discord_details["server_id"]
            discordGuild = client.get_guild(discordGuildID)

            numberOfCategories = len(config.discord_details["channel_categories"])
            for i in range(numberOfCategories):
                upperLimit = (i+1)/numberOfCategories
                lowerLimit = i/numberOfCategories
                print(lowerLimit, "-", upperLimit)
                
                discordCategory = discord.utils.get(discordGuild.categories, id=config.discord_details["channel_categories"][i])  
                
                for v in range(len(rankingsWithProbability)):
                    if rankings[v]["entry"]["probability"] <= upperLimit and rankings[v]["entry"]["probability"] > lowerLimit:
                        if debugMode: print(rankings[v]["entry"]["name"],rankings[v]["entry"]["probability"])
                        discordTextChannel = discord.utils.get(discordGuild.text_channels, name=rankings[v]["entry"]["name"].replace(" ","-"))
                        if discordTextChannel:
                            await discordTextChannel.edit(category=discordCategory)
                            if debugMode: print("Moved", rankings[v]["entry"]["name"].replace(" ","-"))
                        else:
                            if debugMode: print("Channel with name", rankings[v]["entry"]["name"].replace(" ","-"), "not found")
            await message.reply("Update complete")


client = DiscordClient()
client.run(config.discord_details["bot_token"])