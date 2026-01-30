"""
Loadout generator for Helldivers 2 - Discord bot
Author: Christian Sedlak
edX username: SlimSedi
GitHub username: SlimSedi
City: Vienna
Country: Austria
Date: 2024-12-31
Description: This script is a discord bot, that generates a loadout for the game "Helldivers 2", accounting for viability against enemy faction and planetary conditions, while avoiding redundacies.

Portions of the code were written with the assistance of ChatGPT (OpenAI, 2024).
Original JSON and PNG files from https://github.com/Stonemercy/Galactic-Wide-Web
primary.json, secondary.json, grenades.json, stratagems.json and traits.json modified by me.
"""

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import json
import random


load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")

# Set the bot's command prefix and allow all intents (for reading message contents). Delete default help command
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive = True, help_command=None) 


async def short_loadout(ctx, arg, faction, loadout):
    embeded_msg = discord.Embed(title="Loadout", description=f"The finest selection of tools to destroy the {faction} on {arg}", color=discord.Color.red())
    embeded_msg.set_thumbnail(url="attachment://freedom.gif")
    embeded_msg.add_field(name="Primary", value=loadout[0]["name"], inline="True")
    embeded_msg.add_field(name="Secondary", value=loadout[1]["name"], inline="True")
    embeded_msg.add_field(name="Grenade", value=loadout[2]["name"], inline="True")
    embeded_msg.add_field(name="Stratagem", value=loadout[3]["name"], inline="True")
    embeded_msg.add_field(name="Stratagem", value=loadout[4]["name"], inline="True")
    embeded_msg.add_field(name="Stratagem", value=loadout[5]["name"], inline="True")
    embeded_msg.add_field(name="Stratagem", value=loadout[6]["name"], inline="True")
    embeded_msg.set_footer(text=f"Good luck out there, {ctx.author.name}!", icon_url="attachment://pfp.png")

    files = [
        discord.File("resources/freedom.gif", filename="freedom.gif"),
        discord.File("resources/pfp.png", filename="pfp.png")
    ]

    await ctx.send(embed=embeded_msg, files=files)


async def long_loadout(ctx, loadout):
    # List of fixed titles for each loadout item
    titles = ["Primary", "Secondary", "Grenade", "Stratagem 1", "Stratagem 2", "Stratagem 3", "Stratagem 4"]

    embeds = []
    files = []

    # Loop through the loadout items and assign each one a fixed title from the `titles` list
    for i, item in enumerate(loadout):
        # Create a new embed for each item (Primary, Secondary, etc.)
        embeded_msg = discord.Embed(
            title=titles[i],  # Use the title from the `titles` list
            color=discord.Color.red()
        )

        # Prepare the image file path for the first three iterations (the weapons)
        if i < 3:
            file_name = f"resources/weapons/{item['name'].replace(' ', '-')}.png"

            # Set the thumbnail
            embeded_msg.set_thumbnail(url=f"attachment://{item['name'].replace(' ', '-')}.png")

            embeded_msg.add_field(name=item["name"], value="", inline=False)

            # Append to embeds[]
            embeds.append(embeded_msg)

            # Append to files[]
            files.append(discord.File(file_name, filename=f"{item['name'].replace(' ', '-')}.png"))

        # Stratagems.png have different naming convention and path
        else:
            file_name = f"resources/stratagems/{item['name'].replace(' ', '_').replace('/', '_')}.png"

            # Set the thumbnail using the attachment URL format
            embeded_msg.set_thumbnail(url=f"attachment://{item['name'].replace(' ', '_').replace('/', '_')}.png")

            embeded_msg.add_field(name=item["name"], value="", inline=False)

            # Append to embeds[]
            embeds.append(embeded_msg)

            # Append to files[]
            files.append(discord.File(file_name, filename=f"{item['name'].replace(' ', '_').replace('/', '_')}.png"))
        
        
    # Send all the embeds
    await ctx.send(embeds=embeds, files=files)


def populate(file_name: str, list: list, faction: str):
    with open(f'{file_name}', 'r') as file:
        data = json.load(file)

        for item_id, item in data.items():
            if faction == "Terminids" and 13 in item["traits"]:
                if "name" in item:
                    list.append(item)
                    #print(f"{item["name"]} logged")

                # else: stratagem.json
                else:
                    list.append({"name": item_id, **item})  # **item unpacks the item dictionary
                    #print(f"Item with ID '{item_id}' logged")

            elif faction == "Automatons" and 14 in item["traits"]:
                if "name" in item:
                    list.append(item)
                    #print(f"{item["name"]} logged")
                else:
                    list.append({"name": item_id, **item})  
                    #print(f"Item with ID '{item_id}' logged")

            elif faction == "Illuminates" and 15 in item["traits"]:
                if "name" in item:
                    list.append(item)
                    #print(f"{item["name"]} logged")
                else:
                    list.append({"name": item_id, **item})
                    #print(f"Item with ID '{item_id}' logged")




@bot.event
async def on_ready():
    print("Bot ready")

@bot.command(aliases=["hi", "servus"])
async def hello(ctx): # ctx = context (information) about user input
    await ctx.send(f"griaß di gott, {ctx.author.mention}!") # author = user who sent the command, mention = @user

@bot.command(aliases=["h"])
async def help(ctx):
   await ctx.send("To generate a loadout, type '!loadout' or '!l', followed by the name of a planet\n\nExample: !l shelt\n\nIf the planet name consists of more than one word, put it in quotation marks\n\nExample: !l \"bore rock\"\n\nUse the suffix \"short\" for a more concise formatting of the loadout")


@bot.command(aliases=["l"])
async def loadout(ctx, arg: str, arg2: str = "default"): # arg = planet name

    faction: str = "none"
    envir = []
    planet_index: str = "0"
    planet_found = False


# Get enemy faction and environmental hazards from selected planet

    # from https://helldiverstrainingmanual.com/api/v1/war/campaign where "name" = arg
    get_faction = requests.get("https://helldiverstrainingmanual.com/api/v1/war/campaign")

    if get_faction.status_code == 200:

        data = get_faction.json()

        for item in data:
                if item.get("name").lower() == arg.lower():
                    # Extract the "faction" value
                    faction = item.get("faction")
                    # Extract planet_index
                    planet_index = str(item.get("planetIndex"))  # Ensure it's a string
                    if faction != "none":
                        print(f"The faction of {arg} is: {faction}")
                    else:
                        print(f"Faction not found for planet {arg}.")
                    planet_found = True
                    break  # Exit once the matching planet is found

        if not planet_found:
            await ctx.send(f"Planet '{arg}' not found or planet not an active warzone")
            return # Exit if name not found

    else:
        print(f"Failed to fetch data. Status code: {get_faction.status_code}")
    
    # from https://helldiverstrainingmanual.com/api/v1/planets where "name" = arg
    get_envir = requests.get("https://helldiverstrainingmanual.com/api/v1/planets")

    if get_envir.status_code == 200:

        data = get_envir.json()

        for index, planet in data.items():
            if index == planet_index:  # Compare current index with the planet_index
                if planet["environmentals"]:
                    # Iterate over the list of environmentals and get the 'name'
                    for env in planet["environmentals"]:
                         # Check if the 'name' of the environmental condition matches either 'Extreme Cold' or 'Intense Heat'
                        if env.get("name") == "Extreme Cold" or env.get("name") == "Intense Heat":
                            # Append the environmental condition name to the 'envir' list
                            envir.append(env.get("name"))
                            print("Environmental condition logged")
                        else:
                            print("Irrelevant environmental conditions found.")

                else:
                    print("No environmental conditions found.")
                break  # Exit once the matching planet is found



# Populate lists of weapons and stratagems that are viable against the enemy faction

    primary = []
    populate("json/weapons/primary.json", primary, faction)

    secondary = []
    populate("json/weapons/secondary.json", secondary, faction)

    grenades = []
    populate("json/weapons/grenades.json", grenades, faction)

    stratagems = []
    populate("json/stratagems.json", stratagems, faction)

# define logic for loadout generation

    loadout = []
    

    def get_primary():
        counter = 0
        while True:
            random_primary = random.randint(0, len(primary) - 1) # Select a new random primary
            # If planet is hot and weapon is heat sensitive, start over
            if 9 in primary[random_primary]["traits"] and len(envir) == 1 and "Intense Heat" in envir:
                continue # Try again
            
            # If planet is cold and weapon is not heat sensitive, try one more time to increase chance to get heat sensitive weapon
            if 9 not in primary[random_primary]["traits"] and len(envir) == 1 and "Extreme Cold" in envir:
                if counter != 1:
                    counter += 1
                    print("retry primary")
                    continue
                else:
                    loadout.append(primary[random_primary])
                    break
            loadout.append(primary[random_primary])
            break
        
    def get_secondary():
        counter = 0
        while True:
            random_secondary = random.randint(0, len(secondary) - 1)  # Select a new random secondary
            
            # If the secondary is heat sensitive and the environment is "Intense Heat" OR primary is shotgun and secondary would also be shotgun, skip it
            if (9 in secondary[random_secondary]["traits"] and len(envir) == 1 and "Intense Heat" in envir) or \
                (5 in secondary[random_secondary]["fire_mode"] and loadout[0]["type"] == 2) or \
                (18 in secondary[random_secondary]["traits"] and 18 in loadout[0]["traits"]):
                continue  # Try again
            # If planet is cold and weapon is not heat sensitive, try one more time to increase chance to get heat sensitive weapon
            if 9 not in secondary[random_secondary]["traits"] and len(envir) == 1 and "Extreme Cold" in envir:
                if counter != 1:
                    counter += 1
                    print("retry secondary")
                    continue
                else:
                    loadout.append(secondary[random_secondary])
                    break
            loadout.append(secondary[random_secondary])
            break
    
    def get_stratagem():
        counter = 0
        while True:
            random_stratagem = random.randint(0, len(stratagems) - 1)  # Select a new random stratagem
            
            # If the stratagem has trait 9 and the environment is "Intense Heat", retry
            if 9 in stratagems[random_stratagem]["traits"] and len(envir) == 1 and "Intense Heat" in envir:
                continue  # Try again
            # Check if the stratagem has trait 16 or 17, and ensure no conflict with loadout items
            conflict = False
            for item in loadout:
                if (16 in item["traits"] and 16 in stratagems[random_stratagem]["traits"]) or \
                (17 in item["traits"] and 17 in stratagems[random_stratagem]["traits"]) or \
                (item["name"] == stratagems[random_stratagem]["name"]):
                    conflict = True
                    break
            # If planet is cold and weapon is not heat sensitive, try one more time to increase chance to get heat sensitive weapon
            if not conflict and 9 not in stratagems[random_stratagem]["traits"] and len(envir) == 1 and "Extreme Cold" in envir:
                if counter != 1:
                    counter += 1
                    print("retry stratagem")
                    continue
                else:
                    loadout.append(stratagems[random_stratagem])
                    counter = 0
                    break
            # If no conflict, append the stratagem and break the loop
            if not conflict:
                loadout.append(stratagems[random_stratagem])
                break
    
    # Populate loadout
    explosive = False
    while True:
        get_primary()
        get_secondary()
        # get grenades
        random_grenade = random.randint(0, len(grenades) - 1)
        loadout.append(grenades[random_grenade])
        # get 4 stratagems
        for _ in range(4):
            get_stratagem()

        # If no weapon or stratagem has destructive trait, retry
        for item in loadout:
            if 18 in item["traits"]:
                explosive = True
                print("explosive found")

        if explosive:
            break

        print("wipe loadout")
        loadout = []


    if arg2 == "short":
        await short_loadout(ctx, arg, faction, loadout)
    else:
        await long_loadout(ctx, loadout)


bot.run(TOKEN)