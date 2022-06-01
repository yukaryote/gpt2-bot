import torch
import os

import discord
from dotenv import load_dotenv
import random
import string
import re
import requests
from io import BytesIO
import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

model_path = "models/jade/pytorch_model.bin"


class DustyClient(discord.Client):
    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=GUILD)
        print(f'{self.user} has connected to 'f'{guild.name} (id: {guild.id}\n)')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
                f'Mrrrow welcome to tEp, {member.name}'
                )

    async def on_message(self, message):
        if message.author == self.user:
            return

        pet_head_quotes = ['Dusty rolls onto his back, inviting you to pet his belly.', 'Dusty purrs contently.', 'Dusty jumps onto your lap.', 'Dusty bunts your hand.', 'Dusty closes his eyes and purrs.', 'Dusty gets annoyed and struts away.', 'Dusty bites your hand.']
        good_food = ["kibble", "fish", "mayonnaise", "grilled_chees", "mayo", "anarchy"]
        food_quotes = ["Dusty eats contently.", "Dusty refuses your food."]

        message_lower = message.content.lower()

        if message_lower.startswith("dusty."):
            parsed = message_lower[6:]
            print(parsed)
            if parsed == "pet()":
                response = random.choice(pet_head_quotes)
                await message.channel.send(response)
            elif parsed.startswith("feed(") and parsed.endswith(")"):
                food = re.sub("[^\w]", " ",parsed[5:-1]).split()
                print("food:", food)
                if not food:
                    await message.channel.send("Dusty munches on whatever the fuck you offered.")
                    return
                for f in food:
                    response = random.choice(food_quotes + ["Dusty does not like {} and barfs on the piano.".format(f)])
                    await message.channel.send(response)
                    return
            elif parsed == "givedustythreeextralegs()":
                await message.channel.send("Dusty writhes in pain...")
                await message.channel.send("His two back legs have sprouted legs, and another leg flaps limply from his forehead like a sail in the wind.")
                await message.channel.send("The forehead leg flaps faster and faster until Dusty hovers above the ground. He proceeds to fly to Pyongyang to enjoy government-mandated blackouts.")
            elif parsed == "deepfake()":
                url = "https://thiscatdoesnotexist.com"
                uncache = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
                url = url + "/?=" + uncache
                '''
                response = requests.get(url)
                picture = discord.File(BytesIO(response.content))
                e = discord.Embed()
                e.set_image(url=url)
                await message.channel.send(file=picture, embed=e)
                '''
                await message.channel.send(url)
            elif parsed == "help()":
                await message.channel.send("Usage: send messages like dusty.[function] to awaken Dusty.")
                await message.channel.send("Functions are: feed([food]), pet(), deepfake(), givedustythreeextralegs()")
            else:
                await message.channel.send("Dusty does not understand your mortal speech.")

client = DustyClient()
client.run(TOKEN)