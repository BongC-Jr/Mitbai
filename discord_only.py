#import os
#from dotenv import load_dotenv
#import discord
#
#load_dotenv()
#
#intents = discord.Intents.default()
#intents.message_content = True
#
#client = discord.Client(intents=intents)
#
#@client.event
#async def on_ready():
#    print("We have logged in as {0.user}".format(client))
#
#@client.event
#async def on_message(message):
#    if message.author == client.user:
#        return
#
#    if message.content.startswith('$hello'):
#      await message.channel.send('Hi!')
#
#client.run(os.getenv('TOKEN'))

import discord
from discord.ext import commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load keys
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_KEY"))

# Configure Gemini (Using 1.5 Flash - it is faster and free)
model = genai.GenerativeModel('gemini-2.5-flash')
chat_sessions = {}

# Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
#bot = discord.Client(intents=intents) #

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.event
async def on_message(message):
    # Don't respond to ourselves
    if message.author == bot.user:
        return

    # Check if the bot is mentioned or if it's a DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            try:
                # Get or create chat history for this specific user
                user_id = message.author.id
                if user_id not in chat_sessions:
                    chat_sessions[user_id] = model.start_chat(history=[])

                # Clean the message (remove the bot mention)
                clean_text = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '')

                # Send to Gemini
                response = chat_sessions[user_id].send_message(clean_text)
                
                # Discord character limit is 2000
                if len(response.text) > 2000:
                    for i in range(0, len(response.text), 2000):
                        await message.reply(response.text[i:i+2000])
                else:
                    await message.reply(response.text)

            except Exception as e:
                await message.reply(f"⚠️ Error: {str(e)}")

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))


    
