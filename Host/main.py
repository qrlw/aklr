import discord
import sqlite3
from discord.ext import commands
from discord import Embed
from datetime import datetime, timedelta
import random

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

conn = sqlite3.connect('keys.db')
c = conn.cursor()

c.execute('''
          CREATE TABLE IF NOT EXISTS keys (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              key TEXT
          )
          ''')

cooldowns = {}

# User ID with no cooldown restrictions
allowed_user_id = 1206722719882674176

# Separator used in the keys file
key_separator = '\n-------------------\n'

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

def update_keys_file(keys_content):
    with open('keys.txt', 'w') as file:
        file.write(keys_content)

@bot.command(name='gen')
async def generate_key(ctx):
    # Check if the command user has the specified user ID
    if ctx.author.id != allowed_user_id:
        # Check cooldown for other users
        if ctx.author.id in cooldowns and datetime.now() - cooldowns[ctx.author.id] < timedelta(days=1):
            await ctx.send(f"You can only use !gen once every 24 hours. Please wait.")
            return

    # Check if keys are available
    c.execute('SELECT key FROM keys')
    available_keys = c.fetchall()

    if not available_keys:
        await ctx.send('No more keys available.')
        return

    # Read keys from the keys.txt file
    with open('keys.txt', 'r') as file:
        all_keys_content = file.read()

    # Split the keys based on the separator
    all_keys = all_keys_content.split(key_separator)

    # Filter out keys that have already been sent
    unsent_keys = [key.strip() for key in all_keys if key.strip() not in [k[0] for k in available_keys]]

    if not unsent_keys:
        await ctx.send('No more Nitros available please tell the owner.')
        return

    # Select a random unsent key
    generated_key = random.choice(unsent_keys)

    # Update the keys.txt file to remove the generated key
    all_keys.remove(generated_key)
    updated_keys_content = key_separator.join(all_keys)
    update_keys_file(updated_keys_content)

    # Create an embedded message with a purple color and the title "Key Gen"
    embed = Embed(title="Nitro Gen", description=f'Your generated Nitro Link: {generated_key}', color=discord.Color.purple())

    # Add a footer with the specified message and icon
    icon_url = 'https://cdn.discordapp.com/attachments/1213253778426433606/1213256993565835324/static_1.png?ex=65f4d0a0&is=65e25ba0&hm=6fd94eb0a6563ebb83b4b232865dc3cb77b909f6979d7482db8e078045aab256&'
    footer_text = 'You can use !gen again in 24 hours.'
    embed.set_footer(text=footer_text, icon_url=icon_url)

    await ctx.author.send(embed=embed)

    # Remove the key from the database
    c.execute('DELETE FROM keys WHERE key = ?', (generated_key,))
    conn.commit()

    # Set cooldown for other users
    if ctx.author.id != allowed_user_id:
        cooldowns[ctx.author.id] = datetime.now()

# Run the bot
bot.run('MTIxMzI1MTE4NzUzMzY3NjYyNg.GtAaXf.1wPeYSFKe2j2bAHzHz4JyBCgOUHgmvNvO5ZE4Y')