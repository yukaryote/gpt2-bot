import torch
import os

import discord
from dotenv import load_dotenv
import random
import argparse

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

MODEL_CLASSES = {
    "gpt2": (GPT2LMHeadModel, GPT2Tokenizer),
    "ctrl": (CTRLLMHeadModel, CTRLTokenizer),
    "openai-gpt": (OpenAIGPTLMHeadModel, OpenAIGPTTokenizer),
    "xlnet": (XLNetLMHeadModel, XLNetTokenizer),
    "transfo-xl": (TransfoXLLMHeadModel, TransfoXLTokenizer),
    "xlm": (XLMWithLMHeadModel, XLMTokenizer),
}

MAX_LENGTH = int(10000)


def adjust_length_to_model(length, max_sequence_length):
    if length < 0 and max_sequence_length > 0:
        length = max_sequence_length
    elif 0 < max_sequence_length < length:
        length = max_sequence_length  # No generation bigger than model size
    elif length < 0:
        length = MAX_LENGTH  # avoid infinite loop
    return length


class DustyClient(discord.Client):
    def __init__(self, path, type="gpt2"):
        super().__init__()
        self.model_name_or_path = os.path.join(path)
        self.model_type, self.tokenizer_class = MODEL_CLASSES[type]
        self.tokenizer = self.tokenizer_class.from_pretrained(self.model_name_or_path)
        self.model = self.model_type.from_pretrained(self.model_name_or_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("device", self.device)
        self.model.to(self.device)
        self.length = adjust_length_to_model(length=20, max_sequence_length=self.model.config.max_position_embeddings)
        self.prefix = ""
        self.stop_token = "<EOS>"

        self.temperature = 1.
        self.k = 0.
        self.p = 0.9
        self.repetition_penalty = 1.

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
        prompt_text = message.content
        encoded_prompt = self.tokenizer.encode(self.prefix + prompt_text, add_special_tokens=False, return_tensors="pt")
        encoded_prompt = encoded_prompt.to(self.device)

        if encoded_prompt.size()[-1] == 0:
            input_ids = None
        else:
            input_ids = encoded_prompt

        output_sequences = self.model.generate(
            input_ids=input_ids,
            max_length=self.length + len(encoded_prompt[0]),
            temperature=self.temperature,
            top_k=self.k,
            top_p=self.p,
            repetition_penalty=self.repetition_penalty,
            do_sample=True,
            num_return_sequences=1,
        )

        # Remove the batch dimension when returning multiple sequences
        if len(output_sequences.shape) > 2:
            output_sequences.squeeze_()

        generated_sequences = []
        for generated_sequence_idx, generated_sequence in enumerate(output_sequences):
            print(f"=== GENERATED SEQUENCE {generated_sequence_idx + 1} ===")
            generated_sequence = generated_sequence.tolist()

            # Decode text
            text = self.tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
            # Remove all text after the stop token
            text = text[: text.find(self.stop_token) if self.stop_token else None]
            # Add the prompt at the beginning of the sequence. Remove the excess text that was used for pre-processing
            total_sequence = (
                    text[len(self.tokenizer.decode(encoded_prompt[0], clean_up_tokenization_spaces=True)):]
            )

            generated_sequences.append(total_sequence)
            print(total_sequence)
            await message.channel.send(total_sequence)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="bots/jade_model/", help="path to bot you want to use")
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    load_dotenv(os.path.join(args.path, ".env"))
    TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD = os.getenv("DISCORD_GUILD")

    client = DustyClient(args.path)
    client.run(TOKEN)