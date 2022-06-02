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
from transformers import (
    CTRLLMHeadModel,
    CTRLTokenizer,
    GPT2LMHeadModel,
    GPT2Tokenizer,
    OpenAIGPTLMHeadModel,
    OpenAIGPTTokenizer,
    TransfoXLLMHeadModel,
    TransfoXLTokenizer,
    XLMTokenizer,
    XLMWithLMHeadModel,
    XLNetLMHeadModel,
    XLNetTokenizer,
)

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

model_path = "models/jade/pytorch_model.bin"

MODEL_CLASSES = {
    "gpt2": (GPT2LMHeadModel, GPT2Tokenizer),
    "ctrl": (CTRLLMHeadModel, CTRLTokenizer),
    "openai-gpt": (OpenAIGPTLMHeadModel, OpenAIGPTTokenizer),
    "xlnet": (XLNetLMHeadModel, XLNetTokenizer),
    "transfo-xl": (TransfoXLLMHeadModel, TransfoXLTokenizer),
    "xlm": (XLMWithLMHeadModel, XLMTokenizer),
}


class DustyClient(discord.Client):
    def __init__(self, type="gpt2"):
        super().__init__()
        self.model_name_or_path = type
        self.model_type = MODEL_CLASSES[type]
        self.model = self.model_type.from_pretrained(
            self.model_name_or_path
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("device", self.device)
        self.model.to(self.device)

    async def on_ready(self):
        guild = discord.utils.get(self.guilds, name=GUILD)
        print(f'{self.user} has connected to 'f'{guild.name} (id: {guild.id}\n)')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
                f'Maowmaowmaow welcome to tEp, {member.name}'
                )

    async def on_message(self, message):
        if message.author == self.user:
            return

        message_lower = message.content.lower()

        await message.channel.send(self.model.eval())


client = DustyClient()
client.run(TOKEN)